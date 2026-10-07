"""What the streams do by themselves. Each time the song changes stream, the one we left raids the one we
join: an alert, and the other man's regulars pouring into the chat in their own colour."""
from gagkit import *  # noqa: F403

HELLO = ("RAID", ":heart: RAID", "HI ROACHES", "RAID :fire:", "WE'RE HERE"), ("RAID", ":roach: RAID", "HI COMRADES", "RAID :lul:", "IT IS WHAT IT IS")


def _raid(sec):
    host = TL.VIEW[sec]
    other = TL.OTHER[host]
    t0 = TL.section_start(sec)
    count = chatlog.viewers(other, t0)
    names = chatlog.NAMES[other]
    for j, text in enumerate(HELLO[other == "asmon"]):
        chatlog.add(host, t0 + 0.3 + 0.24 * j, names[(3 * j + len(sec)) % len(names)], text, stream.ACCENT[other] + "_hi")

    @span(t0, t0 + 3.2)
    def raid(c, L):
        yield "front"
        alert(c, c.t - t0 - 0.05, f"{stream.NAME[other]} IS RAIDING", f"WITH {count} VIEWERS", "bell", 2.8)

    return raid


for _sec in ("v2", "v3", "v4"):
    _raid(_sec)
