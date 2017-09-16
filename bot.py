#!/usr/bin/python3
import sys
import json
from ChatroomConnection import ChatroomConnection
from Config import Config
from messages import MessageBuilder
from messages.Sticker import Sticker

def main():
    if len(sys.argv) < 2:
        print("Usage {0} <bot_token>".format(sys.argv[0]))
        sys.exit(-1)

    token = sys.argv[1]
    chatroom = int(open("chatroom_id").read())

    connection = ChatroomConnection(token, chatroom)
    config = Config("config.json")
    lastOffset = config.getLastOffset()
    newUpdates = connection.getUpdates(offset = lastOffset + 1)["result"]

    messages = [MessageBuilder.buildMessage(update["message"]) for update in newUpdates]
    newLastOffset = lastOffset
    for newUpdate in newUpdates:
        printJSON(newUpdate)
        updateID = getUpdateID(newUpdate)
        newLastOffset = max(newLastOffset, updateID)

    config.setLastOffset(maxUpdate)
    print("Message len %s" % len(messages)) 
    stickers = [m for m in messages if isinstance(m, Sticker)]
    print("Sticker len %s" % len(stickers))


def printJSON(message):
    print(json.dumps(message, indent=4, sort_keys=True, separators=(',', ': ')))

def getUpdateID(update):
    return int(update["update_id"])

def processMessage(message):
    msg = MessageBuilder.buildMessage(message)

main()
