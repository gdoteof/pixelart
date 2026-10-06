"""A seated figure built from layers: a torso, a head and two arms posed by named gestures.

The figure is drawn chest up, facing right in three-quarter view, and mirrored to face left. Each layer
is outlined on its own, so an arm in front of the body still reads: the far arm (when it hangs behind),
the torso, the far arm (when it comes forward), the head, the near arm, and the far arm again when it
must cover the face.

A project supplies the art and the palette: its ink-outlining Canvas class, and a `Body` per character
that says how to draw the torso and the head and what the arms look like:

    RIG = Rig(Canvas)
    FELIX = Body("felix", torso=hoodie, head=felix_head, skin=("fskin", "fskin_sh"), sleeve="hood")
    img, anchors = RIG.figure(FELIX, arms="point", facing=-1, eyes="wide", mouth="o")

The rig is 84x96 with a 40x40 head. A bigger figure is a bigger rig, with its own art:
`Rig(Canvas, size=(126, 144), neck=(60, 63), chin=(33, 55), head_size=(60, 60), scale=1.5)`.

`arms` names a pose of the two arms (GESTURES):

    desk clasp steeple acc0 acc1 acc2 pinch point thumb shrug cross hold show beg hold1 wave fist chop
    finger palm chin drink chest hair type phone ear facepalm guns thumbs2 bro up2 hush wipe reach press
"""
from dataclasses import dataclass
from functools import lru_cache
from typing import Callable

from PIL import Image

from pixelart.anim import rnd
from pixelart.sprites import mirror

SHOULDERS = ((18, 48), (59, 47))    # the reference body's shoulders, near and far: GESTURES are drawn for these

# (near elbow, near hand, near hand shape), (far elbow, far hand, far hand shape), the far arm's layer
_ON_DESK = ((14, 66), (28, 74), "open")
_FAR_DESK = ((60, 66), (50, 74), "open")
GESTURES = {
    "desk":     (_ON_DESK, _FAR_DESK, "front"),
    "clasp":    (((15, 66), (37, 72), "clasp"), ((61, 64), (42, 72), "clasp"), "front"),
    "steeple":  (((14, 66), (36, 60), "finger"), ((63, 64), (44, 60), "finger"), "front"),
    "acc0":     (((13, 64), (35, 58), "edge"), ((64, 62), (45, 58), "edge"), "front"),    # hands together: a clap
    "acc1":     (((12, 64), (28, 57), "edge"), ((65, 62), (52, 57), "edge"), "front"),
    "acc2":     (((10, 62), (19, 55), "edge"), ((67, 60), (63, 55), "edge"), "front"),
    "pinch":    (_ON_DESK, ((65, 63), (58, 51), "pinch"), "front"),
    "point":    (_ON_DESK, ((69, 49), (81, 47), "point"), "back"),
    "thumb":    (_ON_DESK, ((67, 62), (65, 47), "thumb"), "back"),
    "shrug":    (((9, 62), (3, 54), "palm"), ((67, 62), (76, 54), "palm"), "back"),
    "cross":    (((15, 64), (52, 59), "fist"), ((63, 62), (28, 59), "fist"), "front"),
    "hold":     (((12, 62), (29, 54), "fist"), ((65, 60), (52, 54), "fist"), "front"),
    "show":     (((11, 64), (20, 70), "fist"), ((67, 62), (60, 70), "fist"), "front"),
    "beg":      (((12, 60), (36, 45), "clasp"), ((64, 60), (42, 45), "clasp"), "front"),
    "hold1":    (_ON_DESK, ((68, 58), (65, 44), "fist"), "back"),
    "wave":     (_ON_DESK, ((70, 52), (72, 36), "open"), "back"),
    "fist":     (_ON_DESK, ((70, 54), (66, 35), "fist"), "back"),
    "chop":     (_ON_DESK, ((65, 60), (76, 58), "edge"), "back"),
    "finger":   (_ON_DESK, ((65, 62), (63, 46), "finger"), "front"),
    "palm":     (_ON_DESK, ((66, 62), (76, 58), "palm"), "back"),
    "chin":     (((14, 62), (37, 42), "fist"), ((58, 66), (50, 74), "open"), "front"),
    "drink":    (((12, 60), (39, 45), "fist"), _FAR_DESK, "front"),
    "chest":    (((14, 64), (32, 56), "open"), _FAR_DESK, "front"),
    "hair":     (((8, 44), (24, 14), "open"), _FAR_DESK, "front"),
    "type":     (((14, 66), (31, 72), "edge"), ((60, 66), (47, 71), "edge"), "front"),
    "phone":    (((12, 62), (33, 54), "fist"), ((62, 62), (46, 54), "fist"), "front"),
    "ear":      (((10, 58), (26, 32), "fist"), _FAR_DESK, "front"),
    "facepalm": (_ON_DESK, ((64, 56), (50, 28), "open"), "over"),
    "guns":     (((14, 60), (30, 50), "point"), ((68, 52), (80, 46), "point"), "back"),
    "thumbs2":  (((10, 62), (16, 50), "thumb"), ((67, 62), (66, 47), "thumb"), "back"),
    "bro":      (_ON_DESK, ((67, 60), (72, 45), "bro"), "back"),                           # a fist at the camera
    "up2":      (((7, 44), (3, 27), "fist"), ((71, 42), (77, 25), "fist"), "back"),        # both arms in the air
    "hush":     (((13, 62), (42, 45), "finger"), _FAR_DESK, "front"),                      # a finger to the lips
    "wipe":     (((10, 56), (33, 31), "fist"), _FAR_DESK, "front"),                        # a knuckle at the eye
    "reach":    (_ON_DESK, ((71, 53), (78, 56), "open"), "back"),                          # a hand over a button
    "press":    (_ON_DESK, ((71, 56), (78, 65), "open"), "back"),                          # and down on it
}


@dataclass(frozen=True)
class Body:
    """One character's body, as the rig needs it. Colours are names in the project's palette."""
    name: str
    torso: Callable                 # torso(canvas): draw the torso, facing right
    head: Callable                  # head(**expression) -> an outlined head sprite, facing right
    skin: tuple                     # (skin, its shade)
    sleeve: str
    cuff: str | None = None         # a shirt cuff at the wrist, if one shows
    forearm: str | None = None      # the forearm's colour when the sleeve stops at the elbow (a T-shirt)
    forearm_w: int | None = None    # and its width, when it isn't just a pixel thinner than the upper arm
    sleeve_w: int = 6
    hand: int = 4
    shoulders: tuple = SHOULDERS
    eye: tuple = (19, 21)           # the near eye and the mouth in head pixels, for the anchors
    mouth: tuple = (28, 33)


class Rig:
    """Builds figures on a `size` canvas: `neck` is where the chin lands on the body, `chin` the chin in
    head pixels. `canvas(w, h)` makes one of the project's sprite canvases, whose done() outlines in ink.
    `scale` enlarges the gestures (drawn for the 84x96 rig) and the hands' details for a bigger rig, whose
    size, neck, chin, head_size and bodies are given in its own pixels."""

    def __init__(self, canvas, size=(84, 96), neck=(40, 42), chin=(22, 37), head_size=(40, 40), gestures=GESTURES,
                 scale=1):
        self.canvas, self.size, self.neck, self.chin, self.head_size = canvas, size, neck, chin, head_size
        self.scale = scale
        self.shoulders = tuple(self._pt(s) for s in SHOULDERS)
        self.gestures = {name: ((self._pt(a[0]), self._pt(a[1]), a[2]), (self._pt(b[0]), self._pt(b[1]), b[2]), layer)
                         for name, (a, b, layer) in gestures.items()}
        self._build = lru_cache(maxsize=1024)(self._build)

    def _len(self, v):
        """A length drawn for the 84x96 rig, in this rig's pixels."""
        return v if self.scale == 1 else int(v * self.scale + 0.5)

    def _pt(self, xy):
        return (self._len(xy[0]), self._len(xy[1]))

    def gesture(self, body, arms):
        """The two arms as (shoulder, elbow, hand, shape) and the far arm's layer, for this body."""
        near, far, layer = self.gestures[arms]
        out = []
        for (e, h, kind), t, s in ((near, self.shoulders[0], body.shoulders[0]), (far, self.shoulders[1], body.shoulders[1])):
            dx, dy = s[0] - t[0], s[1] - t[1]
            out.append((s, (e[0] + dx, e[1] + dy), (h[0] + dx, h[1] + dy), kind))
        return out[0], out[1], layer

    def hand_draw(self, f, body, e, h, kind):
        """A hand at h, its forearm coming from e. Shapes: open clasp fist point finger thumb pinch palm
        edge bro."""
        skin, sh = body.skin
        n = body.hand
        r = n // 2
        u = self._len
        fw = 1 if self.scale < 1.4 else 2                                # a finger's width
        x, y = h
        dx, dy = x - e[0], y - e[1]
        d = max(1.0, (dx * dx + dy * dy) ** 0.5)
        if kind == "clasp":                                              # both hands, fingers laced
            f.ell((x - r - u(2), y - r, x + r + u(2), y + r + 1), skin)
            f.line([(x, y - r), (x, y + r)], sh)
        elif kind == "open":
            f.ell((x - r, y - r, x + r, y + r + 1), skin)
            f.px((x - r, y + r), sh)
        elif kind == "palm":                                             # flat, palm up
            f.ell((x - r - 1, y - 1, x + r + 1, y + u(1)), skin)
            f.line([(x - r, y + u(1)), (x + r, y + u(1))], sh)
        elif kind == "edge":                                             # flat, edge on: a chop, a clap
            f.rect((x - u(1), y - r - 1, x, y + r + 1), skin)
            f.line([(x, y - r), (x, y + r)], sh)
        elif kind == "bro":                                              # a fist at the camera, knuckles first
            a, b, c = u(3), u(2), u(4)
            f.rect((x - r - a, y - r - b, x + r + a, y + r + a), skin)
            f.line([(x - r - b, y - r + 1), (x + r + b, y - r + 1)], sh)
            for kx in range(x - r - 1, x + r + a, a):
                f.line([(kx, y - r - b + 1), (kx, y - r)], sh)
            f.line([(x - r - a, y + r + a), (x + r + a, y + r + a)], sh)
            f.rect((x - r - c, y, x - r - a, y + r + 1), skin)           # the thumb, across
        else:
            f.rect((x - r, y - r, x + r, y + r), skin)                   # a fist, and what sticks out of it
            f.line([(x - r, y + r), (x + r, y + r)], sh)
            if kind == "point":
                f.line([(x, y - (r > 1)), (round(x + dx / d * (r + u(3))), round(y - (r > 1) + dy / d * (r + u(3))))],
                       skin, w=fw)
            elif kind == "finger":
                f.rect((x + r - fw, y - r - u(3) - (n > 3), x + r - 1, y - r), skin)
            elif kind == "thumb":
                f.rect((x - r, y - r - u(3), x - r + fw, y - r), skin)
            elif kind == "pinch":                                        # thumb and finger in a ring
                if fw == 1:
                    f.pxs([(x, y - r - 1), (x + 1, y - r - 2), (x + 2, y - r - 1), (x + 1, y - r)], skin)
                else:
                    f.ell((x - 1, y - r - 5, x + 4, y - r), skin)
                    f.d.rectangle((x + 1, y - r - 3, x + 2, y - r - 2), fill=(0, 0, 0, 0))

    def arm_layer(self, body, s, e, h, kind):
        """One arm (sleeve, cuff and hand) on its own outlined layer."""
        w = body.sleeve_w
        f = self.canvas(*self.size)
        f.line([s, e], body.sleeve, w=w)
        f.ell((s[0] - w // 2, s[1] - w // 2, s[0] + w // 2, s[1] + w // 2), body.sleeve)
        f.ell((e[0] - w // 2, e[1] - w // 2, e[0] + w // 2, e[1] + w // 2), body.sleeve)
        f.line([e, h], body.forearm or body.sleeve, w=body.forearm_w or w - 1)
        if body.cuff:
            dx, dy = h[0] - e[0], h[1] - e[1]
            d = max(1.0, (dx * dx + dy * dy) ** 0.5)
            k = body.hand // 2 + 2
            c = self._len(2)
            cx, cy = round(h[0] - dx / d * k), round(h[1] - dy / d * k)
            f.ell((cx - c, cy - c, cx + c, cy + c), body.cuff)
        self.hand_draw(f, body, e, h, kind)
        return f.done()

    def hands_layer(self, body, arms):
        f = self.canvas(*self.size)
        for _, e, h, kind in arms:
            self.hand_draw(f, body, e, h, kind)
        return f.done()

    def _flip(self, xy, facing):
        return xy if facing > 0 else (self.size[0] - 1 - xy[0], xy[1])

    def _build(self, body, arms, lean, bob, facing, expr):
        near, far, layer = self.gesture(body, arms)
        img = Image.new("RGBA", self.size, (0, 0, 0, 0))
        if layer == "back":
            img.alpha_composite(self.arm_layer(body, *far))
        f = self.canvas(*self.size)
        body.torso(f)
        img.alpha_composite(f.done())
        if layer == "front":
            img.alpha_composite(self.arm_layer(body, *far))
        hx, hy = self.neck[0] - self.chin[0] + lean, self.neck[1] - self.chin[1] + bob
        img.alpha_composite(body.head(**dict(expr)), (hx, hy))
        img.alpha_composite(self.arm_layer(body, *near))
        if layer == "over":
            img.alpha_composite(self.arm_layer(body, *far))
        hands = self.hands_layer(body, (near, far))
        if facing < 0:
            img, hands = mirror(img), mirror(hands)
        fl = self._flip
        anchors = {"hand_near": fl(near[2], facing), "hand_far": fl(far[2], facing),
                   "head": fl((hx + self.head_size[0] // 2, hy), facing),
                   "eye": fl((hx + body.eye[0], hy + body.eye[1]), facing),
                   "mouth": fl((hx + body.mouth[0], hy + body.mouth[1]), facing),
                   "chest": fl((self.neck[0], self.neck[1] + self._len(16)), facing)}
        return img, hands, anchors

    def figure(self, body, arms="desk", lean=0, bob=0, facing=1, held=None, **expr):
        """A figure (RGBA) and its anchors in sprite pixels: hand_near, hand_far, head (top centre), eye,
        mouth, chest. held = (prop image, anchor name or (x, y)) is drawn in front of the body and under
        the hands, unmirrored and centred on the point: "hands" is the midpoint of both hands, "hands_top"
        holds it up by its bottom corners, and (anchor, n) raises it n pixels above an anchor. A prop
        wider than the canvas pads it: the anchors (and "held", the prop's centre) allow for that."""
        img, hands, anchors = self._build(body, arms, lean, bob, facing, tuple(sorted(expr.items())))
        if not held:
            return img, anchors
        prop, at = held
        w, h = self.size
        if at in ("hands", "hands_top"):
            (ax, ay), (bx, by) = anchors["hand_near"], anchors["hand_far"]
            at = ((ax + bx) // 2, (ay + by) // 2 - (prop.height // 2 - 3 if at == "hands_top" else 0))
        elif isinstance(at, str):
            at = anchors[at]
        elif isinstance(at[0], str):
            ax, ay = anchors[at[0]]
            at = (ax, ay - at[1])
        x0, y0 = at[0] - prop.width // 2, at[1] - prop.height // 2
        pad = max(0, -x0, -y0, x0 + prop.width - w, y0 + prop.height - h)
        out = Image.new("RGBA", (w + 2 * pad, h + 2 * pad))
        out.alpha_composite(img, (pad, pad))
        out.alpha_composite(prop, (x0 + pad, y0 + pad))
        out.alpha_composite(hands, (pad, pad))
        return out, {k: (x + pad, y + pad) for k, (x, y) in dict(anchors, held=at).items()}


def pick(options, slot, *key):
    """The gesture for a slot (every two beats, say) from weighted options ((name, weight), ...): the same
    every time for its key, and never the same twice running."""
    total = sum(w for _, w in options)

    def draw(k):
        r = rnd(*key, k) * total
        for g, w in options:
            r -= w
            if r < 0:
                return g
        return options[-1][0]

    g = draw(slot)
    if g == draw(slot - 1):
        g = draw(slot + 1000)
    return g
