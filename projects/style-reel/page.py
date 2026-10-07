"""Build the page that shows the reel: build/site/page.html, with the clips and posters beside it.

    uv run python projects/style-reel/page.py

Only the styles whose clips have been rendered (build/web/<id>.mp4) go on the page; the rest are listed as
still to come.
"""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WEB, SITE = ROOT / "build" / "web", ROOT / "build" / "site"
RIG = "The puppet rig"

STYLES = [
    dict(id="flat", name="Flat vector", tag="puppet rig", base=RIG, effort="About the same", grade="Strong",
         drawn="Smooth shapes, no outlines, two tones to a surface. Each man is a rig of about forty shapes built "
               "from a few dozen points and posed by numbers: lean, head turn, brows, lids, both hands.",
         moves="At the full 24 frames a second. Moves ease in, overshoot and settle; the mouth follows the words sound "
               "by sound, not just loudness; blinks, and a nod on the beat.",
         cost="A new person is one more head and body for the rig, 60 to 70 lines of outline tuned by eye, much like "
              "a pixel caricature. After that the acting is cheap: a pose is one line. The picture for each bar costs "
              "about what it does now, a little more because clean shapes at this size show their flaws.",
         read="The one I would move to. The faces are large and can act, the lip-sync is real, and five other styles on "
              "this page are this same rig drawn another way, so the look can still change from video to video."),
    dict(id="comic", name="Comic book", tag="puppet rig", base=RIG + ", inked", effort="About the same", grade="Strong",
         drawn="The same rig, inked: a black line that is not quite steady, flat colour, dots for the shadows, and "
               "paper multiplied over the page. Panels, a lettered balloon and sound effects do the staging.",
         moves="Like a motion comic. Poses snap and hold, new things arrive with a jolt, and only the mouth keeps time.",
         cost="The same as flat vector: the ink, the dots and the paper are automatic. Lettering a sound effect is a "
              "line of code a bar.",
         read="Strong, and it suits a rap battle: the balloon is the lyric, and a punchline can land as a new panel. "
              "Over three minutes the page layout would have to keep changing to stay alive."),
    dict(id="cutout", name="Paper cut-out", tag="puppet rig", base=RIG + ", as paper", effort="About the same", grade="Strong",
         drawn="The same rig, cut from coloured paper. Every shape gets a scissored edge, a sheet of paper that is "
               "never quite the same colour twice, and a soft shadow on whatever lies under it. The board is a print "
               "taped to the wall, and the lyric is laid down a strip to a word.",
         moves="On twos, like stop motion: twelve pictures a second, and between them every piece is nudged a hair "
               "off true, so nothing sits dead still. New things are placed, not flown in.",
         cost="The same as flat vector. The edges, shadows, grain and jitter are automatic, and flat shapes are all "
              "the look needs, which is exactly what the rig makes.",
         read="The best return of the lot. The handmade look hides the stiffness a puppet drawn in code has, so a "
              "cheap move reads as a choice. I would happily make a whole video this way."),
    dict(id="sketch", name="Pencil sketch", tag="puppet rig", base=RIG + ", as line", effort="About the same", grade="Good",
         drawn="The same rig as a drawing: a graphite line gone over twice, coloured-pencil hatching where the fills "
               "were, dotted notebook paper. The house draws itself on part by part, and the lyric is written out "
               "as it is sung.",
         moves="The line boils: every three frames it is traced again, a little differently, as hand-drawn animation "
               "is. Poses change on twos.",
         cost="The same as flat vector to make. The price is paid later: a boiling line is hard to compress (at "
              "full quality this clip is 24 MB against 1.4 MB for flat vector), and YouTube would soften it.",
         read="Charming for a verse or a flashback. Over a whole video the wobble would tire, and the hatching looks "
              "more digital than a real pencil. Best as a second look inside another style."),
    dict(id="riso", name="Two-colour print", tag="puppet rig", base=RIG + ", as ink layers", effort="About the same",
         grade="Good",
         drawn="The same rig, separated into two inks, pink and blue, on cream paper, the way a risograph prints. "
               "Every tone is a screen of dots in one ink or both, the blue plate carries the outlines, the two "
               "plates never quite line up, and the ink goes on unevenly.",
         moves="On twos, with the registration slipping from sheet to sheet, so the picture shimmers like a stack of "
               "prints being flipped.",
         cost="The same as flat vector, plus one decision for every new thing: how much of each ink it gets. Telling "
              "skin, hair and props apart with two colours takes some thought.",
         read="A strong poster look, and nothing else in a feed looks like it. It cannot tell people apart by colour, "
              "so the two men lean on hair and outline; with four people on screen it would get hard to say who is who."),
    dict(id="neon", name="Neon sign", tag="puppet rig", base=RIG + ", as tubes", effort="A little more", grade="Good",
         drawn="The rig's outlines bent into glass tubes on a brick wall: a core burnt nearly white, a coloured glow, "
               "and light spilling on the bricks. Whatever is in front hides the tubes behind it, and tubes that "
               "have not come on yet wait as dark glass.",
         moves="A tube is lit or it is not, so nothing glides. Signs strike with a stutter, the men switch between "
               "poses eight times a second, and the six tubs are counted on one at a time.",
         cost="The men cost the same as in flat vector. Props cost a little more, because each has to read as a few "
              "outlines with no fill to help. It is among the slowest to render here, about a second a frame, which is "
              "still only about four minutes for a whole video.",
         read="Striking, and a natural fit for a hook or a title. Faces lose most of their acting to the outline, so I "
              "would use it for a section, not a whole battle."),
    dict(id="shadow", name="Shadow puppets", tag="own drawing", base="Its own profile puppets", effort="About half",
         grade="Strong",
         drawn="Its own puppets, in profile: black card with the details cut out, jointed at the shoulder, elbow and "
               "jaw and worked on rods, in front of a lamp-lit paper screen. Props rise on sticks, and anything "
               "further from the screen is softer.",
         moves="As a puppeteer would: limbs swing from their pivots, the hair hangs and follows late, the jaw is "
               "hinged to the words, and a prop sharpens as it comes up to the screen.",
         cost="My estimate is about half the drawing of a pixel video. A prop is an outline and a few cuts, with no "
              "colour or shading to choose, and two puppets carry the whole song. The hard part of a new person is "
              "a profile that is recognisable in silhouette.",
         read="The best-looking frame on the page for the least drawing. The limits are real: no expression beyond "
              "the jaw and a head tilt, and every joke has to read as an outline, so screenshots, chat and anything "
              "on a screen are out."),
    dict(id="hose", name="Rubber hose", tag="own drawing", base="Its own full-body figures", effort="1.5 to 2 times",
         grade="Strong",
         drawn="Its own full-body figures in the manner of a 1930s cartoon: pie-cut eyes, white gloves, limbs like "
               "hoses and one thick even line, in greys on scratched, flickering film. The lyric is a sing-along "
               "strip with a bouncing ball.",
         moves="Everything bobs to the beat, the house and the tubs included. Poses go from one to the next with a "
               "bounce, and limbs bend as curves, not at joints.",
         cost="My estimate is one and a half to two times a pixel video. Full bodies take more posing than busts, "
              "and every prop has to arrive and then keep bobbing. A new person is about 170 lines.",
         read="The funniest of them: the style is itself a joke about two grown men arguing online. It is also the "
              "most work, and a whole video would want walks and more hand shapes than this clip has."),
    dict(id="voxel", name="Voxel diorama", tag="3D", base="Its own 3D renderer", effort="The same, less once sets repeat",
         grade="Good",
         drawn="A real 3D scene: an island of small cubes floating in the sky, the two men at their desks at either "
               "end, with sunlight, cast shadows and signs that glow. It is drawn by a small software renderer "
               "written for this reel in numpy and Skia, not by a game engine.",
         moves="One three-quarter view, held. The men are posed with blocky arms, and each head is swapped between "
               "a handful of models for the mouth and the expression. The tubs drop out of the sky and land, and "
               "the scoreboard comes up out of the lawn.",
         cost="My estimate is about the same as a pixel video for the first one, since every bar still needs a prop "
              "or two modelled and checked by eye, and about half once sets and props are being reused. A whole "
              "video would take about a quarter of an hour to render, against under a minute now.",
         read="The surprise of the set: it reads as a little world, and the camera could cut to a new angle with no "
              "new drawing. Faces are the weak point. They are a dozen cubes across and the mouths are swapped "
              "whole, so I would not trust it with a joke that hangs on an expression."),
    dict(id="type", name="Kinetic type", tag="no characters", base="Type alone", effort="Under half", grade="Strong",
         drawn="No people at all: the words are the picture. Heavy type set on one grid, a few pictograms (a "
               "pediment, six tubs, a flag, flies) and two flat colours to a section.",
         moves="Each word lands on its own time, a touch early so that it reads as it is heard, and pushes the "
               "layout along. The big numbers arrive with a hit. The camera never moves.",
         cost="My estimate is under half a pixel video: a bar is a layout of ten to twenty lines and now and then a "
              "pictogram. The danger is sameness, so a whole song would need eight to ten families of layout.",
         read="The cheapest by a distance, and the jokes read with the sound off. It gives up what these videos are "
              "about, two recognisable people, so I see it as intros, hooks and punchlines inside another style."),
    dict(id="pixel", name="Pixel art", tag="what we have", base="The current pipeline", effort="The baseline", grade="Good",
         drawn="What the videos use now, cut from the finished Play the Video. Every picture is placed pixel by pixel "
               "in code on a small canvas and scaled up.",
         moves="Stepped: a handful of poses for each man, a picture swapped in on the word, a mouth that opens with "
               "the loudness of the voice.",
         cost="The baseline. Play the Video is about 4,300 lines, some 3,000 of them drawing: mostly one picture for "
              "every bar.",
         read="Proven over eight videos, and forgiving: a crude shape reads fine this small. The ceiling is low, though. "
              "The faces stay tiny and cannot act much."),
]
MADE = ("Python, with Skia for the vector drawing and numpy for the print, paper and light treatments. Each style is "
        "one function from a time in the song to a 1920x1080 picture, which is the contract the pixel-art videos "
        "already use: parallel rendering, any-frame previews and the lyric timing all carry over. The word and beat "
        "times are the real ones from the finished video. The costs are estimates from building this one bar in each "
        "style, not from making a whole video.")


def main():
    template = (ROOT / "page.html").read_text()
    for sub in ("clips", "posters"):
        (SITE / sub).mkdir(parents=True, exist_ok=True)
    ready, waiting = [], []
    for s in STYLES:
        if (WEB / f"{s['id']}.mp4").exists() and s["drawn"]:
            shutil.copyfile(WEB / f"{s['id']}.mp4", SITE / "clips" / f"{s['id']}.mp4")
            shutil.copyfile(WEB / f"{s['id']}.jpg", SITE / "posters" / f"{s['id']}.jpg")
            ready.append(s)
        else:
            waiting.append(s["name"].lower())
    pending = f"Still to come: {', '.join(waiting)}." if waiting else ""
    page = template.replace("/*STYLES*/[]/*END*/", json.dumps(ready, ensure_ascii=False))
    page = page.replace('/*PENDING*/""/*END*/', json.dumps(pending)).replace('/*MADE*/""/*END*/', json.dumps(MADE))
    (SITE / "page.html").write_text(page)
    size = sum(f.stat().st_size for f in SITE.rglob("*") if f.is_file()) / 1e6
    print(f"{SITE / 'page.html'}: {len(ready)} styles ({', '.join(s['id'] for s in ready)}), {size:.1f} MB; waiting: {len(waiting)}")


if __name__ == "__main__":
    main()
