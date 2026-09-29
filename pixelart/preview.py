"""Preview frames: python -m pixelart.preview PROJECT NAME t1 t2 a:b:step ...

Writes PROJECT/build/preview/NAME_<t>.png for each time (seconds) plus
NAME_sheet.png, a contact sheet captioned with the time and the project's label(t).
"""
import sys
from multiprocessing import Pool

from pixelart.project import load
from pixelart.sheet import contact_sheet


def parse_times(args):
    ts = []
    for a in args:
        if ":" in a:
            lo, hi, step = (float(x) for x in a.split(":"))
            x = lo
            while x <= hi + 1e-9:
                ts.append(round(x, 3))
                x += step
        else:
            ts.append(float(a))
    return ts


def render_one(job):
    root, name, t = job
    p = load(root)
    path = p.build / "preview" / f"{name}_{t:08.3f}.png"
    p.render_frame(t).save(path)
    return str(path), t, p.label(t)[:70]


def main():
    root, name, ts = sys.argv[1], sys.argv[2], parse_times(sys.argv[3:])
    p = load(root)
    out_dir = p.build / "preview"
    out_dir.mkdir(parents=True, exist_ok=True)
    with Pool(min(len(ts), 8)) as pool:
        res = pool.map(render_one, [(str(p.root), name, t) for t in ts])
    print(contact_sheet([(path, f"t={t:.2f}  {text}") for path, t, text in res],
                        out_dir / f"{name}_sheet.png"))


if __name__ == "__main__":
    main()
