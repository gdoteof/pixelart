"""Who lives at the sanctuary: small sprites, each drawn facing right (mirror them to face left).

    winnie    the cow, a Red Angus: one of her, solid red, no horns        48 x 32
    hawk      the red-tailed hawk, perched                                  22 x 30
    emu       the emu's head and neck, come to see what is going on         18 x 44
    tortoise  the sulcata, in no hurry                                      36 x 20
    wolf      a wolf, sitting                                               30 x 34
    scorpion  an emperor scorpion                                           28 x 18
    chinchilla  a chinchilla, mostly fluff                                  16 x 13
"""
from functools import lru_cache

from engine import Canvas


@lru_cache(maxsize=None)
def winnie(chew=0, tail=0):
    """The cow, side on. `chew` 0/1 works her jaw, `tail` 0/1 flicks it."""
    f = Canvas(48, 32)
    for x, c in ((10, "angus"), (15, "angus_sh"), (30, "angus_sh"), (35, "angus")):       # the legs
        f.rect((x, 20, x + 3, 30), c)
        f.rect((x, 29, x + 3, 30), "black")
    f.line([(6, 11), (3 - tail, 16), (2 - 2 * tail, 22)], "angus_sh", w=2)                # the tail
    f.rect((1 - 2 * tail, 22, 3 - 2 * tail, 25), "angus_sh")
    f.ell((5, 8, 40, 24), "angus")                                                        # the barrel
    f.ell((8, 18, 36, 25), "angus_sh")
    f.ell((7, 9, 38, 21), "angus")
    f.line([(11, 10), (30, 9)], "angus_hi")
    f.poly([(33, 10), (41, 5), (46, 8), (47, 16 + chew), (44, 20 + chew), (38, 19), (34, 16)], "angus")   # the head
    f.ell((41, 13 + chew, 47, 20 + chew), "muzzle")
    f.px((45, 16 + chew), "ink"); f.px((43, 17 + chew), "ink")
    f.px((42, 9), "ink"); f.px((42, 8), "angus_hi")
    f.poly([(35, 5), (39, 3), (40, 7), (36, 8)], "angus_sh")                              # the ear, and its tag
    f.rect((36, 7, 37, 9), "yellow")
    return f.done()


@lru_cache(maxsize=None)
def hawk(look=0, wings=0):
    """The hawk, perched: `look` 1 turns her head to the camera, `wings` 1 lifts them."""
    f = Canvas(34, 30)
    ox = 6
    if wings:
        f.poly([(ox + 8, 12), (ox - 6, 4), (ox - 4, 12), (ox + 2, 18)], "hawk_sh")
        f.poly([(ox + 14, 12), (ox + 27, 4), (ox + 25, 12), (ox + 18, 18)], "hawk_sh")
        f.line([(ox - 4, 6), (ox + 4, 14)], "hawk"); f.line([(ox + 25, 6), (ox + 17, 14)], "hawk")
    f.poly([(ox + 5, 22), (ox + 9, 24), (ox + 7, 29), (ox + 3, 28)], "hawk_tail")          # the tail
    f.poly([(ox + 8, 7), (ox + 14, 6), (ox + 17, 11), (ox + 18, 18), (ox + 16, 24), (ox + 11, 26), (ox + 6, 23), (ox + 5, 15),
            (ox + 6, 10)], "hawk")
    f.poly([(ox + 11, 11), (ox + 16, 12), (ox + 18, 18), (ox + 16, 24), (ox + 12, 25), (ox + 11, 19)], "hawk_bib")
    f.pxs([(ox + 13, 17), (ox + 15, 18), (ox + 14, 20), (ox + 16, 20), (ox + 13, 22)], "hawk")          # the belly band
    f.line([(ox + 7, 12), (ox + 7, 21)], "hawk_sh")
    f.ell((ox + 9, 2, ox + 16, 10), "hawk")                                               # the head
    if look:
        f.px((ox + 11, 5), "gold"); f.px((ox + 14, 5), "gold")
        f.rect((ox + 12, 6, ox + 13, 8), "gold_sh")
    else:
        f.poly([(ox + 16, 5), (ox + 19, 6), (ox + 17, 8)], "gold"); f.px((ox + 19, 7), "ink")
        f.px((ox + 14, 5), "ink"); f.px((ox + 13, 4), "hawk_sh"); f.px((ox + 14, 4), "hawk_sh")
    f.rect((ox + 10, 26, ox + 11, 28), "gold"); f.rect((ox + 14, 26, ox + 15, 28), "gold")
    return f.done()


@lru_cache(maxsize=None)
def emu(blink=0):
    """The emu: a long blue-grey neck out of a shag of feathers, and a look."""
    f = Canvas(22, 46)
    f.ell((0, 30, 20, 50), "emu")                                                         # what shows of the body
    for x, y in ((3, 33), (7, 31), (12, 32), (16, 35), (5, 38), (10, 37), (15, 40)):
        f.line([(x, y), (x - 1, y + 4)], "emu_sh")
    f.line([(10, 32), (9, 20), (11, 10)], "emu_neck", w=4)                                # the neck
    f.line([(8, 30), (8, 20)], "emu_sh")
    f.ell((7, 2, 16, 11), "emu_sh")                                                       # the head
    f.poly([(15, 5), (21, 7), (15, 9)], "beak")
    f.line([(8, 2), (12, 0)], "emu_sh"); f.line([(10, 2), (14, 0)], "emu_sh")
    if blink:
        f.line([(11, 5), (13, 5)], "ink")
    else:
        f.rect((11, 4, 13, 6), "orange"); f.px((12, 5), "ink")
    return f.done()


@lru_cache(maxsize=None)
def tortoise(step=0, cap=False):
    """The sulcata, side on: `step` 0/1 moves the legs, `cap` gives her a driver's cap."""
    f = Canvas(38, 24)
    oy = 4
    f.rect((7 + step, oy + 13, 11 + step, oy + 18), "tort"); f.rect((23 - step, oy + 13, 27 - step, oy + 18), "tort")
    f.line([(2, oy + 13), (5, oy + 12)], "tort")                                          # the tail
    f.poly([(28, oy + 10), (33, oy + 6), (37, oy + 7), (37, oy + 11), (33, oy + 13), (28, oy + 13)], "tort")   # the head
    f.px((35, oy + 8), "ink"); f.line([(34, oy + 11), (37, oy + 11)], "shell_sh")
    f.poly([(4, oy + 13), (6, oy + 6), (12, oy + 2), (21, oy + 2), (27, oy + 6), (30, oy + 13)], "shell")   # the shell
    f.line([(4, oy + 13), (30, oy + 13)], "shell_sh")
    for x in (10, 17, 24):                                                                # its plates
        f.poly([(x - 3, oy + 9), (x, oy + 5), (x + 3, oy + 9), (x, oy + 11)], "shell_hi")
        f.d.polygon([(x - 3, oy + 9), (x, oy + 5), (x + 3, oy + 9), (x, oy + 11)], outline=f.c("shell_sh"))
    if cap:
        f.poly([(30, oy + 6), (32, oy + 3), (36, oy + 3), (37, oy + 6)], "black"); f.line([(35, oy + 7), (38, oy + 7)], "black")
    return f.done()


@lru_cache(maxsize=None)
def wolf(shades=False, eyes=True):
    """A wolf, sitting, head to the camera's right: `shades` puts her on the security detail."""
    f = Canvas(30, 34)
    f.poly([(4, 32), (2, 24), (5, 20), (8, 26)], "wolf_sh")                               # the tail
    f.poly([(7, 32), (6, 20), (10, 13), (17, 12), (21, 17), (21, 32)], "wolf")            # the body
    f.poly([(14, 18), (20, 17), (21, 32), (15, 32)], "wolf_hi")                           # the chest
    f.rect((16, 26, 18, 32), "wolf_hi"); f.rect((20, 26, 22, 32), "wolf_hi")              # the forelegs
    f.line([(19, 26), (19, 32)], "wolf_sh")
    f.poly([(12, 4), (14, 0), (17, 4)], "wolf_sh"); f.poly([(19, 4), (22, 0), (24, 5)], "wolf_sh")    # the ears
    f.poly([(11, 6), (15, 3), (22, 3), (25, 7), (29, 11), (28, 14), (22, 15), (16, 15), (11, 12)], "wolf")   # the head
    f.poly([(22, 9), (29, 11), (28, 14), (22, 14)], "wolf_hi")                            # the muzzle
    f.px((29, 11), "ink"); f.line([(23, 14), (27, 14)], "wolf_sh")
    if shades:
        f.rect((15, 6, 24, 9), "black"); f.px((16, 7), "grey_hi"); f.line([(11, 7), (15, 7)], "black")
    elif eyes:
        f.px((20, 8), "gold"); f.px((21, 8), "ink")
    return f.done()


@lru_cache(maxsize=None)
def scorpion(bow=None, step=0):
    """An emperor scorpion: claws out in front, the tail curled over. `bow` is a colour for a ribbon."""
    f = Canvas(30, 20)
    for i, x in enumerate((9, 12, 15, 18)):                                               # the legs
        d = (i + step) % 2
        f.line([(x, 14), (x - 2, 17 + d)], "scorp"); f.line([(x, 11), (x - 2, 9 - d)], "scorp")
    f.ell((6, 9, 21, 16), "scorp")                                                        # the body, in plates
    for x in (10, 13, 16):
        f.line([(x, 10), (x, 15)], "scorp_hi")
    f.line([(7, 12), (3, 11), (1, 7), (3, 3), (7, 2)], "scorp", w=2)                      # the tail, and its sting
    f.poly([(7, 1), (10, 3), (7, 4)], "scorp_hi")
    f.line([(20, 10), (24, 7)], "scorp", w=2); f.line([(20, 15), (24, 18)], "scorp", w=2)    # the arms
    f.ell((23, 3, 29, 8), "scorp"); f.ell((23, 14, 29, 19), "scorp")                      # the claws
    f.px((28, 5), "scorp_hi"); f.px((28, 16), "scorp_hi")
    f.px((20, 11), "white"); f.px((20, 14), "white")
    if bow:
        f.poly([(11, 6), (14, 8), (11, 10)], bow); f.poly([(17, 6), (14, 8), (17, 10)], bow)
    return f.done()


@lru_cache(maxsize=None)
def chinchilla(blink=0):
    f = Canvas(18, 15)
    f.ell((1, 4, 14, 14), "chin")                                                         # the fluff
    f.ell((3, 9, 12, 14), "chin_sh"); f.ell((2, 5, 13, 12), "chin")
    f.ell((9, 0, 13, 5), "chin_sh"); f.ell((13, 1, 17, 6), "chin_sh")                     # the ears
    f.px((11, 3), "pink"); f.px((15, 4), "pink")
    f.ell((9, 4, 17, 11), "chin")                                                         # the face
    if blink:
        f.line([(13, 7), (14, 7)], "ink")
    else:
        f.rect((13, 6, 14, 7), "ink")
    f.px((17, 8), "pink")
    f.line([(15, 9), (17, 10)], "grey_hi"); f.line([(1, 12), (0, 14)], "chin_sh")
    return f.done()
