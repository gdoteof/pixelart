"""What the two chats type, and when.

Each stream has a chat of its own (pixelart.chatlog). It idles along on its regulars' habits and erupts
when its streamer lands a punchline; gags add scripted lines with `add`. `tail(host, t)` is what is on
screen at t.
"""
import timeline as TL
from pixelart.chatlog import ChatLog
from stream import CHAT_ROWS, NAME_COLORS

NAMES = {"hasan": ("ZYNGOD", "KAYA4", "MARXBRO", "LATTE", "UNIONJ", "DSAKEV", "POGPOT", "TANKTOP", "RENT0", "LEFTY",
                   "OATMILK", "PARASOC"),
         "asmon": ("ROACH77", "DRPEPR", "BALD4", "TMOG", "LOOTBOX", "GRUG", "RATKING", "WOWDAD", "NPC42", "STEAK",
                   "BURRITO", "DUNGEON")}
IDLE = {"hasan": ("W", "REAL", "TRUE", "LMAO", "FACTS", ":lul:", ":fire:", "W TAKE", "SO TRUE", ":heart:", "KAYA W",
                  "CHAT?", "OMG", "PREACH", "UNPAUSE"),
        "asmon": ("W", "BASED", "TRUE", "LUL", ":lul:", "DUDE", "REAL", "FACTS", ":roach:", ":frog:", "GG", "YEP", "LOGIC",
                  "PLAY IT", "UNPAUSE")}
HIT = (":skull:", "LMAO", "OOF", "COOKED", "RIP", ":lul: :lul:", "DONE", ":fire: :fire:", "NO WAY", "OUCH", ":skull: :skull:",
       "GET HIM", "OH NO", "DEAD", "L", "WOW")

LOG = ChatLog(TL.MEN, TL.DURATION, NAMES, IDLE, HIT, TL.HITS, {"hasan": 31200, "asmon": 58900}, NAME_COLORS, CHAT_ROWS)
add, tail, both, viewers, count = LOG.add, LOG.tail, LOG.both, LOG.viewers, LOG.count
