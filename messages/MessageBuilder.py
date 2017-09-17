from messages.Text import Text
from messages.Sticker import Sticker
from messages.BotCommand import BotCommand

def buildMessage(json):
    if "text" in json:
        if "entities" in json:
            for entity in json["entities"]:
                if "type" in entity:
                    if entity["type"] == "bot_command":
                        # Is BotCommand
                        return BotCommand(json)
        # Is text
        return Text(json)
    elif "sticker" in json:
        # Is a sticker
        return Sticker(json)
