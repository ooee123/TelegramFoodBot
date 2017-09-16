from messages.Text import Text
from messages.Sticker import Sticker

def buildMessage(json):
    if "text" in json:
        # Is text
        return Text(json)
    elif "sticker" in json:
        # Is a sticker
        return Sticker(json)
