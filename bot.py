#!/usr/bin/python3
import sys
import json
from ChatroomConnection import ChatroomConnection
from Config import Config

def main():
    if len(sys.argv) < 2:
        print("Usage {0} <bot_token>".format(sys.argv[0]))
        sys.exit(-1)

    token = sys.argv[1]
    chatroom = int(open("chatroom_id").read())

    connection = ChatroomConnection(token, chatroom)
    config = Config("stickers.json")
    print(config.getLastOffset())
    newMessages = connection.getUpdates(offset = config.getLastOffset())["results"]

    for newMessage in newMessages:
        

    printJSON(newMessages)
    config.setLastOffset(getUpdateID(newMessages[-1]) + 1)

    connection.sendMessage("Hello")

def printJSON(message):
    print(json.dumps(message, indent=4, sort_keys=True, separators=(',', ': ')))

def getUpdateID(message):
    return int(message["update_id"])

main()
