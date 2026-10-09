"""The outro, over the gift shop's counter: thank you for visiting."""
from gagkit import *  # noqa: F403
from pictures import *  # noqa: F403


@lru_cache(maxsize=None)
def exit_sign(stage, blink):
    p = Pic("cream")
    p.d.rectangle((1, 1, PW - 2, PH - 4), outline=col("maya_sh"))
    if stage == 0:
        p.silk((PW // 2, 8), "THANK YOU", "maya_sh", anchor="ma"); p.silk((PW // 2, 17), "FOR", "wood_sh", anchor="ma")
        p.press((PW // 2, 26), "VISITING", "maya_sh", anchor="ma")
        p.heart(47, 39, "red")
        return p.img
    p.rect((6, 5, 42, 19), "green"); p.d.rectangle((6, 5, 42, 19), outline=INK)             # the way out
    p.press((24, 8), "EXIT", "white", anchor="ma")
    p.line([(48, 12), (86, 12)], "ink", w=2); p.poly([(86, 7), (93, 12), (86, 17)], "ink")
    p.silk((PW // 2, 26), "THROUGH THE", "wood_sh", anchor="ma")
    p.press((PW // 2, 34), "GIFT SHOP", "emiru_sh" if blink else "maya_sh", anchor="ma")
    return p.img


@gag("outro", 0)
def exit_through_the_gift_shop(c, L):
    show(c, exit_sign(1 if L.on("Please") else 0, int(c.t * 3) % 2), "ANNOUNCEMENT", "PA")
    for who in WOMEN:
        pose(c, who, arms="wave" if not L.on("Please") else "window", brows="up")
    yield "front"


@lru_cache(maxsize=None)
def link_in_bio(k):
    p = Pic("bg")
    p.grad((0, 0, PW, PH), "emiru_sh", "maya_sh", steps=5)
    p.rbox((3, 8, 96, 28), "white", "ink", 4)
    p.press((PW // 2, 14), "LINK IN BIO", "ink", anchor="ma")
    x, y = 70 - 6 * k, 40 - 8 * k                                          # the cursor, on its way
    p.poly([(x, y), (x, y + 11), (x + 3, y + 8), (x + 6, y + 13), (x + 8, y + 12), (x + 5, y + 7), (x + 9, y + 7)], "white")
    p.d.polygon([(x, y), (x, y + 11), (x + 3, y + 8), (x + 6, y + 13), (x + 8, y + 12), (x + 5, y + 7), (x + 9, y + 7)], outline=INK)
    if k >= 2:
        p.pxs([(x - 3, y - 2), (x + 3, y - 4), (x - 5, y + 2)], "gold_hi")
    return p.img


@gag("outro", 1)
def the_link_is_in_the_bio(c, L):
    show(c, link_in_bio(min(2, int(max(L.age("link"), 0) / 0.25))), "ONE MORE THING", "AD")
    for who in WOMEN:
        pose(c, who, arms="window" if not L.on("bio") else "thumbs2", brows="up", mouth="grin" if L.age("bio") > 0.4 else c.st[who]["mouth"])
    yield "front"


END_T = TL.section_start("end")


@span(END_T, TL.DURATION)
def goodbye(c, L):
    """The end card: the title in the window, and the two of them waving."""
    a = c.t - END_T
    for i, who in enumerate(WOMEN):
        pose(c, who, arms="wave" if int((a + 0.3 * i) * 2.5) % 2 == 0 else "palm", brows="up", mouth="grin")
    yield "front"
