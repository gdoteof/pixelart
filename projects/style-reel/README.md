# Style reel

One couplet of [Play the Video](../play-the-video) drawn in eleven styles, to see what these videos could
look like besides pixel art. Every clip is the same 7.7 seconds (verse 2, Asmongold on Hasan's house): the
same audio and the same joke, landing on the same words, so the styles can be compared like for like.

> Your mansion's got five and a half baths: how austere;
> five and a half more than I've had all year.

| | Style | Built on | Effort for a whole video, against pixel art |
|---|---|---|---|
| `flat` | Flat vector | the puppet rig | about the same |
| `comic` | Comic book | the rig, inked | about the same |
| `cutout` | Paper cut-out | the rig, as paper | about the same |
| `sketch` | Pencil sketch | the rig, as line | about the same |
| `riso` | Two-colour print | the rig, as two inks | about the same |
| `neon` | Neon sign | the rig, as tubes | a little more |
| `shadow` | Shadow puppets | its own profile puppets | about half |
| `hose` | Rubber hose | its own full-body figures | 1.5 to 2 times |
| `voxel` | Voxel diorama | its own 3D renderer | about the same, less once sets are reused |
| `type` | Kinetic type | type alone | under half |
| `pixel` | Pixel art | the finished video | the baseline |

The efforts are estimates from building this one bar in each style, not from making a whole video.

## Running it

```sh
uv run python projects/style-reel/prep.py                              # the bar's audio and vocal envelope
uv run --with skia-python python projects/style-reel/reel.py flat      # build/clips/flat.mp4, and a 720p copy
uv run --with skia-python python projects/style-reel/reel.py flat --sheet           # twelve frames on one sheet
uv run --with skia-python python projects/style-reel/reel.py flat --frame 69.9      # one frame, full size
uv run python projects/style-reel/combine.py                           # style-reel.mp4: every style, a card before each
uv run python projects/style-reel/page.py                              # build/site/: the page with the player
```

- Skia does the vector drawing. It is not a dependency of the repo: `--with skia-python` fetches it for the run.
- `prep.py` needs Play the Video's stems (its `analyze` step), and the `pixel` style cuts its frames out of
  the finished `play-the-video.mp4`.
- A frame takes 0.1 s (flat) to about a second (neon, voxel) per worker, so a clip renders in a few seconds.

## How it is put together

A style is a module `style_<id>.py` with a `NAME` and `frame(t)`: a function from a time in the song to the
1920x1080 picture, which is the contract the videos' own `video.py` has. Nothing carries over from one
frame to the next, so frames render in parallel and any frame can be previewed alone.

- `script.py`: the bar. The word times and beats from the finished video, the cues the gag hangs on
  (`EV`), easing, and the mouth: a shape for every sound of every word, scaled by how loud the voice is.
- `sk.py`: Skia helpers (curves through points, shape arithmetic, type, paper and grain).
- `puppet.py`: the rig. A front view of each man as about forty shapes, posed by a `Pose` (lean, head
  turn, brows, lids, mouth, two hands that reach where they are told). It returns the shapes and says
  nothing about how they are drawn.
- `acting.py`: the two performances, as poses on a timeline. `props.py`: the house, the tubs, the flag,
  the scoreboard's numbers, the flies.
- Six styles (`flat`, `comic`, `cutout`, `sketch`, `riso`, `neon`) draw that one performance in their own
  way and move it in their own way: smooth, snapped like a comic, nudged like stop motion, boiling like
  a pencil line, slipping like a print, switched like a sign.
- The other four build their own figures: `shadow` (jointed card puppets in profile), `hose` (with
  `hose_cast.py`), `voxel` (with `voxel_engine.py` and `voxel_models.py`) and `type` (no figures at all).
