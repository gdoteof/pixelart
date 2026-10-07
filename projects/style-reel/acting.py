"""What the two men do through the bar: poses on the cues, and how they get from one to the next.

pose(who, t) is the performance as written: eased moves that overshoot and settle, the singer's mouth on
the words, blinks, a nod on the beat. A style that animates another way asks for it: `snap=True` jumps from
pose to pose and holds, and a style on twos or threes passes a held time (script.hold).
"""
import math
from dataclasses import replace

import script as S
from puppet import Pose, mix

E = S.EV
# Asmongold sings: points out the house, counts the tubs, shrugs at "austere", holds up five fingers, then
# thumbs at himself and closes his eyes, proud of it.
A_IDLE = Pose(look_x=0.4, smile=0.2)
A_POINT = Pose(turn=0.5, look_x=0.8, brow=0.6, lean=3, rx=2.3, ry=1.5, grip_r="point", aim_r=-14)
A_COUNT = Pose(turn=0.55, look_x=0.9, look_y=0.4, brow=0.3, lean=4, rx=2.3, ry=1.78, grip_r="point", aim_r=-26)
A_SHRUG = Pose(head=9, turn=0.2, skew=1.0, lid=0.3, smile=0.3, rx=1.65, ry=2.2, grip_r="open", lx=-1.6, ly=2.25, grip_l="open",
                tuck_l=True, tuck_r=True)
A_FIVE = Pose(head=-3, brow=0.6, smile=0.4, lx=-1.35, ly=1.15, grip_l="open", aim_l=-90)
A_MINE = Pose(head=-5, brow=0.5, smile=0.6, lean=-2, lx=-0.62, ly=2.25, grip_l="thumb", aim_l=-38)
A_PROUD = Pose(head=-7, nod=-0.5, lid=1.0, brow=0.8, smile=1.0, lean=-3, lx=-0.62, ly=2.25, grip_l="thumb", aim_l=-38)
A_FLY = Pose(head=-4, nod=-0.6, look_x=0.3, look_y=-1.0, brow=0.9, smile=0.2, lx=-0.62, ly=2.25, grip_l="thumb", aim_l=-38)
ASMON = [(S.T0, A_IDLE, 0.1), (67.52, A_POINT, 0.2), (68.64, A_COUNT, 0.16), (69.98, A_SHRUG, 0.22),
         (70.72, A_FIVE, 0.2), (71.92, A_MINE, 0.22), (72.68, A_PROUD, 0.18), (74.0, A_FLY, 0.2)]

# Hasan listens: the smirk, a look at the board, the eye-roll, then the sum dawns on him and so does the smell.
H_SMUG = Pose(smile=0.7, look_x=-0.3)
H_WHAT = Pose(turn=-0.5, look_x=-0.9, brow=-0.2, frown=0.5, smile=-0.2)
H_COUNT = Pose(turn=-0.5, look_x=-0.9, look_y=0.6, frown=0.3, smile=-0.35, head=-3)
H_ROLL = Pose(head=-9, look_x=0.3, look_y=-1.0, brow=0.6, lid=0.2, smile=-0.45, lean=2)
H_DOUBT = Pose(turn=-0.6, look_x=-1.0, skew=1.0, lid=0.12, smile=-0.25, lean=-2)
H_SHOCK = Pose(turn=-0.6, look_x=-1.0, wide=1.0, brow=1.0, lean=4, mw=0.6, mh=0.55, teeth=0.2, tongue=0.2)
H_RECOIL = Pose(lean=10, head=8, turn=0.2, lid=0.55, frown=1.0, brow=-0.6, smile=-1.0, lx=-0.02, ly=0.44,
                grip_l="pinch", mw=1.0, mh=0.2, teeth=1.0)
HASAN = [(S.T0, H_SMUG, 0.1), (E["mansion"] + 0.06, H_WHAT, 0.2), (E["tubs"][0], H_COUNT, 0.2), (E["austere"] + 0.02, H_ROLL, 0.24),
         (E["line2"] + 0.16, H_DOUBT, 0.26), (E["had"] + 0.04, H_SHOCK, 0.14), (E["year"], H_RECOIL, 0.24)]

TRACK = {"asmon": ASMON, "hasan": HASAN}
BLINKS = {"asmon": (67.30, 69.96, 71.62), "hasan": (67.86, 69.42, 71.84, 72.50)}


def pose(who, t, snap=False):
    """The man's pose at t."""
    keys = TRACK[who]
    cur = keys[0][1]
    for t0, target, dur in keys[1:]:
        if t < t0:
            break
        x = 1.0 if snap else (t - t0) / dur
        cur = mix(cur, target, S.ease_out(x), S.back(x, 2.2) if x < 1 else 1.0)
    p = cur
    extra = {}
    if who == "asmon":
        if S.singing(t):
            p = p.say(S.mouth(t))
        elif t > S.SING1:                                 # the grin he ends on
            k = S.clamp((t - S.SING1) / 0.12)
            extra.update(mw=1.12, mh=0.26 * k, teeth=1.0)
        if not snap:                                      # he jabs a finger at each tub as it lands
            jab = sum(math.exp(-((t - c) / 0.035) ** 2) for c in (*E["tubs"], E["half"]))
            if p.ry is not None:
                extra["ry"] = p.ry + 0.10 * jab
        extra["dy"] = p.dy + (0.0 if snap else 0.035 * S.thump(t, 9))
    else:
        extra["head"] = p.head + (0.0 if snap else 1.2 * S.thump(t, 8))
    if any(0 <= t - b < 0.11 for b in BLINKS[who]):
        extra["lid"] = 1.0
    return replace(p, **extra) if extra else p
