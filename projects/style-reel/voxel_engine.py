"""A small software renderer for voxel models: numpy for the geometry, Skia to fill the faces.

A model is a lattice of coloured unit cubes, culled to the faces that have no cube against them. Inside one
model the faces are painted far to near, in an order that is exact for a lattice seen from any point (a ray
from the eye only ever moves away from it along each lattice axis). Between models a depth buffer decides,
so models can touch, overlap and move as they like. The faces are filled with their own numbers, not their
colours: depth and colour are looked up from the number afterwards.

Shading is per face (sky light, sunlight by how the face looks at the sun, and a darkening where voxels meet
that is baked into the mesh); the sun's shadow is per pixel, from a shadow map. The picture is drawn at
several times its size and reduced.
"""
import itertools
import math

import numpy as np
import skia
from PIL import Image

NORMALS = np.array([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)], np.int32)
QUADS = np.array([          # each face's corners, from the cube's low corner
    [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)],
    [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)],
    [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)],
    [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],
    [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
    [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)],
], np.float32)
UP = np.array([0.0, 1.0, 0.0])
EMPTY = -1e30
_keys = itertools.count(1)


# --- models -------------------------------------------------------------------------------------

def _span(v):
    return range(v, v + 1) if isinstance(v, int) else range(v[0], v[1])


class Vox:
    """A voxel model being built: {(x, y, z): (r, g, b)}, y up. Spans are (from, to) with `to` left out,
    or one number for a single layer."""

    def __init__(self):
        self.v = {}
        self.lit = set()                    # voxels that glow: drawn in their own colour, unshaded

    def put(self, x, y, z, c, glow=False):
        self.v[(x, y, z)] = c
        if glow:
            self.lit.add((x, y, z))
        else:
            self.lit.discard((x, y, z))
        return self

    def box(self, xs, ys, zs, c, glow=False):
        for x in _span(xs):
            for y in _span(ys):
                for z in _span(zs):
                    self.put(x, y, z, c, glow)
        return self

    def cut(self, xs, ys, zs):
        for x in _span(xs):
            for y in _span(ys):
                for z in _span(zs):
                    self.v.pop((x, y, z), None)
                    self.lit.discard((x, y, z))
        return self

    def paint(self, xs, ys, zs, c, glow=False):
        """Recolour the voxels that are already there."""
        for x in _span(xs):
            for y in _span(ys):
                for z in _span(zs):
                    if (x, y, z) in self.v:
                        self.put(x, y, z, c, glow)
        return self

    def add(self, other, dx=0, dy=0, dz=0):
        for (x, y, z), c in other.v.items():
            self.put(x + dx, y + dy, z + dz, c, (x, y, z) in other.lit)
        return self


class Mesh:
    __slots__ = ("corner", "centre", "nidx", "rgb", "ao", "glow", "key", "lo", "hi")


def mesh(vox, jitter=0.03, seed=1):
    """The model's outside faces, each with its corners, colour and how hemmed in it is by its neighbours."""
    pos = np.array(list(vox.v.keys()), np.int32)
    col = np.array([c[:3] for c in vox.v.values()], np.float32)
    glow = np.fromiter((k in vox.lit for k in vox.v), bool, len(pos))
    # each voxel a touch lighter or darker, by where it is: two builds of a model that differ in a few
    # voxels (a mouth open, a mouth shut) then agree everywhere else
    h = pos.astype(np.int64) @ np.array([73856093, 19349663, 83492791], np.int64) + seed * 7919
    h = (h * 2654435761) & 0xFFFFFFFF
    h = ((h ^ (h >> 15)) * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) & 0xFFFF).astype(np.float32) / 65535.0
    col = col * (1 + (h[:, None] - 0.5) * 2 * jitter * ~glow[:, None])
    lo = pos.min(0) - 1
    occ = np.zeros(pos.max(0) - lo + 2, bool)
    p = pos - lo
    occ[p[:, 0], p[:, 1], p[:, 2]] = True
    parts = []
    for ni, n in enumerate(NORMALS):
        q = p + n
        show = ~occ[q[:, 0], q[:, 1], q[:, 2]]
        qs = q[show]
        u, v = (ni // 2 + 1) % 3, (ni // 2 + 2) % 3

        def at(du, dv):
            r = qs.copy()
            r[:, u] += du
            r[:, v] += dv
            return occ[r[:, 0], r[:, 1], r[:, 2]].astype(np.float32)

        side = at(1, 0) + at(-1, 0) + at(0, 1) + at(0, -1)
        diag = at(1, 1) + at(1, -1) + at(-1, 1) + at(-1, -1)
        base = pos[show].astype(np.float32)
        parts.append((base[:, None, :] + QUADS[ni][None], base + 0.5, np.full(len(base), ni, np.uint8), col[show],
                      np.clip(1 - 0.13 * side - 0.05 * diag, 0.45, 1), glow[show]))
    m = Mesh()
    m.corner, m.centre, m.nidx, m.rgb, m.ao, m.glow = (np.concatenate([part[i] for part in parts]) for i in range(6))
    m.key = next(_keys)
    m.lo, m.hi = pos.min(0).astype(float), pos.max(0).astype(float) + 1
    return m


# --- transforms ---------------------------------------------------------------------------------

def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def SC(sx, sy=None, sz=None):
    return np.diag([sx, sx if sy is None else sy, sx if sz is None else sz, 1.0])


def _rot(deg, i, j):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4)
    m[i, i], m[i, j], m[j, i], m[j, j] = c, -s, s, c
    return m


def RX(deg):
    """Turn about x: positive tips +y toward +z."""
    return _rot(deg, 1, 2)


def RY(deg):
    """Turn about y: positive swings +z toward +x."""
    return _rot(deg, 2, 0)


def RZ(deg):
    """Turn about z: positive tips +x toward +y."""
    return _rot(deg, 0, 1)


class Inst:
    """A model placed in the world."""
    __slots__ = ("mesh", "M", "cast")

    def __init__(self, mesh, M, cast=True):
        self.mesh, self.M, self.cast = mesh, M, cast


# --- views --------------------------------------------------------------------------------------

def _basis(forward):
    f = forward / np.linalg.norm(forward)
    r = np.cross(f, UP)
    r /= np.linalg.norm(r)
    return np.stack([r, np.cross(r, f), f])


class Camera:
    """A perspective view: `fov` is the vertical field of view in degrees."""

    def __init__(self, eye, target, fov, w, h):
        self.eye = np.asarray(eye, float)
        self.R = _basis(np.asarray(target, float) - self.eye)
        self.f = (h / 2) / math.tan(math.radians(fov) / 2)
        self.cx, self.cy = w / 2, h / 2

    def project(self, P):
        """World points (..., 3) to (x, y, nearness): nearness is 1/depth, which is flat across a plane."""
        v = (P - self.eye) @ self.R.T
        iz = 1.0 / v[..., 2]
        return self.cx + self.f * v[..., 0] * iz, self.cy - self.f * v[..., 1] * iz, iz


class Sun:
    """The light, and the view from it: straight down its rays onto a square map of the scene."""

    def __init__(self, toward, centre, extent, size):
        self.toward = np.asarray(toward, float) / np.linalg.norm(toward)
        self.R = _basis(-self.toward)
        self.centre = np.asarray(centre, float)
        self.k, self.size = size / (2 * extent), size
        self.eye = self.centre + self.toward * 1e5

    def project(self, P):
        v = (P - self.centre) @ self.R.T
        return self.size / 2 + self.k * v[..., 0], self.size / 2 - self.k * v[..., 1], -v[..., 2]


# --- drawing ------------------------------------------------------------------------------------

def raster(m, M, view, W, H):
    """Paint one model's faces into a patch of the view. Returns (x0, y0, numbers, nearness, faces, corners):
    the patch's corner, each pixel's face number (0 is none; face k is faces[k - 1]) and nearness, and the
    faces' world corners."""
    Minv = np.linalg.inv(M)
    eye = Minv[:3, :3] @ view.eye + Minv[:3, 3]
    seen = ((eye - m.corner[:, 0]) * NORMALS[m.nidx]).sum(1) > 1e-7
    sel = np.nonzero(seen)[0]
    if not len(sel):
        return None
    sel = sel[np.argsort(-((m.centre[sel] - eye) ** 2).sum(1), kind="stable")]
    P = m.corner[sel] @ M[:3, :3].T + M[:3, 3]
    sx, sy, sw = view.project(P)
    x0, y0 = max(0, int(math.floor(sx.min()))), max(0, int(math.floor(sy.min())))
    x1, y1 = min(W, int(math.ceil(sx.max())) + 1), min(H, int(math.ceil(sy.max())) + 1)
    if x1 <= x0 or y1 <= y0:
        return None
    sx, sy = sx - x0, sy - y0
    buf = np.zeros((y1 - y0, x1 - x0, 4), np.uint8)
    surf = skia.Surface(buf, colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kPremul_AlphaType)
    canvas, paint = surf.getCanvas(), skia.Paint(AntiAlias=False)
    k = np.arange(1, len(sel) + 1, dtype=np.uint32)
    colours = (0xFF000000 | ((k & 255) << 16) | (k & 0xFF00) | ((k >> 16) & 255)).tolist()
    for xs, ys, c in zip(sx.tolist(), sy.tolist(), colours):
        path = skia.Path()
        path.moveTo(xs[0], ys[0])
        path.lineTo(xs[1], ys[1])
        path.lineTo(xs[2], ys[2])
        path.lineTo(xs[3], ys[3])
        path.close()
        paint.setColor(c)
        canvas.drawPath(path, paint)
    del canvas, surf
    ids = (buf.view(np.uint32)[..., 0] & 0xFFFFFF).astype(np.intp)
    # each face's nearness as a plane over the patch
    ax, ay, bx, by = sx[:, 1] - sx[:, 0], sy[:, 1] - sy[:, 0], sx[:, 3] - sx[:, 0], sy[:, 3] - sy[:, 0]
    aw, bw = sw[:, 1] - sw[:, 0], sw[:, 3] - sw[:, 0]
    det = ax * by - bx * ay
    ok = np.abs(det) > 1e-9
    det = np.where(ok, det, 1.0)
    ga = np.where(ok, (aw * by - bw * ay) / det, 0.0)
    gb = np.where(ok, (ax * bw - bx * aw) / det, 0.0)
    gc = sw[:, 0] - ga * sx[:, 0] - gb * sy[:, 0]
    A = np.concatenate([[0.0], ga]).astype(np.float32)
    B = np.concatenate([[0.0], gb]).astype(np.float32)
    C = np.concatenate([[EMPTY], gc]).astype(np.float32)
    X = (np.arange(x1 - x0, dtype=np.float32) + 0.5)[None, :]
    Y = (np.arange(y1 - y0, dtype=np.float32) + 0.5)[:, None]
    near = A[ids] * X + B[ids] * Y + C[ids]
    return x0, y0, ids, near, sel, P


_shadows = {}


def shadow_map(insts, sun):
    """How near the sun each point of its view gets: the nearest face of anything that casts a shadow.
    A model that has not moved since another frame is not drawn again."""
    sm = np.full((sun.size, sun.size), EMPTY, np.float32)
    for inst in insts:
        if not inst.cast:
            continue
        key = (id(sun), inst.mesh.key, inst.M.tobytes())
        if key not in _shadows:
            if len(_shadows) > 600:
                _shadows.clear()
            r = raster(inst.mesh, inst.M, sun, sun.size, sun.size)
            _shadows[key] = None if r is None else (r[0], r[1], r[3])
        if _shadows[key] is not None:
            x0, y0, near = _shadows[key]
            patch = sm[y0:y0 + near.shape[0], x0:x0 + near.shape[1]]
            np.maximum(patch, near, out=patch)
    return sm


class Light:
    def __init__(self, sky=(0.52, 0.55, 0.62), sun=(0.66, 0.61, 0.53)):
        self.sky, self.sun = np.array(sky, np.float32), np.array(sun, np.float32)


def _pack(rgb, a):
    rgb = np.clip(rgb, 0, 255).astype(np.uint32)
    return rgb[:, 0] | (rgb[:, 1] << 8) | (rgb[:, 2] << 16) | (np.clip(a, 0, 255).astype(np.uint32) << 24)


def shade(inst, sel, light, sun):
    """Each face's two colours, packed: what the sky gives it (alpha: the face is there), and what the sun
    adds where it reaches (alpha: how squarely the face looks at the sun). A face that glows gets nothing
    from the sun and says so with a full alpha over black, which no lit face has."""
    m = inst.mesh
    nt = (np.linalg.inv(inst.M)[:3, :3].T @ NORMALS.T).T
    nt /= np.linalg.norm(nt, axis=1, keepdims=True)
    n = nt[m.nidx[sel]]
    ndl = np.clip(n @ sun.toward, 0, 1)
    glow = m.glow[sel][:, None]
    sky = ((0.78 + 0.22 * n[:, 1]) * m.ao[sel])[:, None] * light.sky
    base = np.where(glow, m.rgb[sel], m.rgb[sel] * sky)
    direct = np.where(glow, 0.0, m.rgb[sel] * ndl[:, None] * light.sun)
    return _pack(base, np.full(len(sel), 255)), _pack(direct, np.where(glow[:, 0], 255, ndl * 255))


def render(insts, cam, sun, light, W, H):
    """The scene at W x H as (sky colour, sun colour, nearness, shadow map): the colours are packed RGBA,
    0 where there is nothing."""
    sm = shadow_map(insts, sun)
    near = np.zeros((H, W), np.float32)
    base = np.zeros((H, W), np.uint32)
    direct = np.zeros((H, W), np.uint32)
    for inst in insts:
        r = raster(inst.mesh, inst.M, cam, W, H)
        if r is None:
            continue
        x0, y0, ids, w, sel, _ = r
        lut_b, lut_d = (np.concatenate([[0], lut]).astype(np.uint32) for lut in shade(inst, sel, light, sun))
        box = (slice(y0, y0 + w.shape[0]), slice(x0, x0 + w.shape[1]))
        front = w > near[box]
        np.copyto(near[box], w, where=front)
        np.copyto(base[box], lut_b[ids], where=front)
        np.copyto(direct[box], lut_d[ids], where=front)
    return base, direct, near, sm


TAPS = [(0.0, 0.0)] + [(1.6 * math.cos(a), 1.6 * math.sin(a)) for a in np.arange(6) * math.pi / 3] + \
       [(3.1 * math.cos(a), 3.1 * math.sin(a)) for a in (np.arange(6) + 0.5) * math.pi / 3]


def resolve(base, direct, near, sm, cam, sun, ss):
    """Reduce the picture to its final size and light it: (rgb float (h, w, 3) times alpha, alpha 0..1,
    depth, how much of the pixel glows). The shadow is looked up per pixel, thirteen taps around the point
    for a soft edge."""
    h, w = base.shape

    def small(packed):
        im = Image.frombuffer("RGBA", (w, h), packed, "raw", "RGBA", 0, 1)
        return np.asarray(im.reduce(ss) if ss > 1 else im).astype(np.float32)

    b, d = small(base), small(direct)
    iz = near[ss // 2::ss, ss // 2::ss]
    there = iz > 0
    z = np.where(there, 1.0 / np.where(there, iz, 1.0), 0.0).astype(np.float32)
    X = ((np.arange(w // ss, dtype=np.float32) * ss + ss // 2 + 0.5) - cam.cx) / cam.f
    Y = -((np.arange(h // ss, dtype=np.float32) * ss + ss // 2 + 0.5) - cam.cy) / cam.f
    # the point seen at each pixel, in the sun's view
    Rc, Rs = cam.R, sun.R
    A = (Rs @ Rc.T).astype(np.float32)                      # view axes in the sun's frame
    o = (Rs @ (cam.eye - sun.centre)).astype(np.float32)
    xv, yv = X[None, :] * z, Y[:, None] * z
    px = o[0] + A[0, 0] * xv + A[0, 1] * yv + A[0, 2] * z
    py = o[1] + A[1, 0] * xv + A[1, 1] * yv + A[1, 2] * z
    pz = o[2] + A[2, 0] * xv + A[2, 1] * yv + A[2, 2] * z
    sx, sy, sw = sun.size / 2 + sun.k * px, sun.size / 2 - sun.k * py, -pz
    ndl = d[..., 3] / 255
    sw = sw + 0.20 + 0.75 * (1 - ndl)                        # lift the point off its own face
    lit = np.zeros(z.shape, np.float32)
    for dx, dy in TAPS:
        ix = np.clip((sx + dx).astype(np.intp), 0, sun.size - 1)
        iy = np.clip((sy + dy).astype(np.intp), 0, sun.size - 1)
        lit += sm[iy, ix] <= sw
    lit /= len(TAPS)
    rgb = b[..., :3] + d[..., :3] * lit[..., None]
    glow = ndl * np.clip(1 - d[..., :3].max(-1) / 8, 0, 1)
    return rgb, b[..., 3] / 255, z, glow
