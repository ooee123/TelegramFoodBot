import json
from ChatroomConnection import ChatroomConnection
from Config import Config
from messages import MessageBuilder
from messages.Sticker import Sticker

class Bot:

    def __init__(self, token, chatroom, timeout=0):
        self.connection = ChatroomConnection(token, chatroom)
        self.config = Config("{chatroom}.conf.json".format(chatroom=str(chatroom)))
        self.timeout = timeout
    
    def getNewMessages(self):
        lastOffset = self.config.getLastOffset()
        newUpdates = self.connection.getUpdates(offset = lastOffset + 1, timeout=self.timeout)["result"]
        messages = [MessageBuilder.buildMessage(update["message"]) for update in newUpdates]
        newLastOffset = lastOffset
        for newUpdate in newUpdates:
            newLastOffset = max(newLastOffset, getUpdateID(newUpdate))
        self.config.setLastOffset(newLastOffset)
        return messages

def printJSON(message):
    print(json.dumps(message, indent=4, sort_keys=True, separators=(',', ': ')))

def getUpdateID(update):
    return int(update["update_id"])
