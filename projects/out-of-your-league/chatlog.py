"""What the chats type, and when.

Each stream has a chat of its own (pixelart.chatlog), and the frame the two share has a third. A chat idles
along on its regulars' habits and erupts when a punchline lands; gags add scripted lines with `add`.
`tail(host, t)` is what is on screen at t.
"""
import timeline as TL
from pixelart.chatlog import ChatLog
from stream import CHAT_ROWS, NAME_COLORS

_EMIRU = ("WIGSNATCH", "PORO4", "KANSASGG", "MEOWMIX", "BOTLANE", "GLUEGUN", "LOCKEDIN", "SEWCRACKD", "ADCDIFF",
          "CATEARS", "WICHITA", "FOAMSMITH")
_MAYA = ("STOMPYFAN", "WINNIEMOO", "FEEDERBOT", "NOODLE4", "FALCONER", "LEAFLET", "BIRDNERD", "MOOMOO", "DONKEYKO",
         "CHINFLUFF", "TRAILCAM", "HAYBALE")
NAMES = {"emiru": _EMIRU, "maya": _MAYA, "pair": _EMIRU[::2] + _MAYA[::2]}
IDLE = {"emiru": ("W", "QUEEN", "REAL", "LOCKED IN", ":cat:", ":heart:", "MOTHER", "SLAY", "TRUE", "OMG", "EMI W", "BARS",
                  ":fire:", "SO REAL", "ATE"),
        "maya": ("W", "MOO", ":cow:", ":leaf:", "QUEEN", "FEED WINNIE", "REAL", ":heart:", "TRUE", "BARS", "STOMPY W",
                 "SO TRUE", ":fire:", "OMG", "BIRB"),
        "pair": ("W", "QUEENS", ":cat:", ":cow:", ":heart:", "W DUO", "BARS", "MOTHERS", ":fire:", "REAL", ":leaf:", "MOO",
                 "SLAY", "ATE", "DUO")}
HIT = (":skull:", "LMAO", "BARS", "COOKED", "ATE", ":lul: :lul:", "OMG", ":fire: :fire:", "NO WAY", "SHE ATE",
       ":skull: :skull:", "QUEEN", "OH NO", "DEAD", "W", "MOTHER")

LOG = ChatLog(("emiru", "maya", "pair"), TL.DURATION, NAMES, IDLE, HIT, TL.HITS,
              {"emiru": 41200, "maya": 18400, "pair": 96300}, NAME_COLORS, CHAT_ROWS)
add, tail, viewers, count = LOG.add, LOG.tail, LOG.viewers, LOG.count

# Each chat is already going when the song starts.
for _i, (_name, _text) in enumerate((("WIGSNATCH", "HI EMI"), ("PORO4", ":cat:"), ("LEAFLET", "MAYA!!"), ("MEOWMIX", "W DUO"),
                                     ("BOTLANE", "LETS GO"), ("CATEARS", ":heart: :heart:"), ("KANSASGG", "SHE'S LIVE"))):
    add("emiru", -3.0 + 0.4 * _i, _name, _text)
