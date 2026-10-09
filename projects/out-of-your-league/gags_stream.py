"""What happens on the streams that isn't any one bar's: the hello before the first of them."""
from gagkit import *  # noqa: F403

FIRST = TL.LINES[0]["t0"]


@span(0.0, FIRST - 0.1)
def hello(c, L):
    """The beat is in and the first bar is three seconds off: she waves, and chat sees who has joined."""
    pose(c, "emiru", arms="wave" if c.t < 2.2 else "desk", mouth="grin" if c.t < 2.2 else "smile", brows="up")
    pose(c, "maya", arms="wave" if 0.6 < c.t < 2.4 else "desk", mouth="grin")
    yield "front"
    alert(c, c.t - 0.3, "MAYA JOINED THE CALL", "SAY HI, CHAT", icon="leaf", dur=2.6, accent="maya")
