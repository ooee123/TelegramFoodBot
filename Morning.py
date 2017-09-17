#!/usr/bin/python3
import sys
import os
from datetime import datetime
from time import time
from Bot import Bot
import json
from json import JSONEncoder

from messages.Sticker import Sticker
from messages.BotCommand import BotCommand
from messages.Text import Text

MORNING_STICKER = "CAADAgADEQEAAtQ7SgJzg0f_OmyrNQI"

def main():
    if len(sys.argv) < 3:
        print("Usage {0} <bot_token> <chatroom_id> <morning.json>".format(sys.argv[0]))
        sys.exit(-1)
    token = sys.argv[1]
    chatroom = int(sys.argv[2])
    morningJSON = sys.argv[3]
    if os.path.isfile(morningJSON):
        users = json.load(open(morningJSON, "r"))
        newUsers = {}
        for user_id in users.keys():
            newUsers[int(user_id)] = MorningEntry(users[user_id]["name"], users[user_id])
        users = newUsers
    else:
        users = {}
        
    bot = Bot(token, chatroom, timeout=60)
    
    while True:
        messages = bot.getNewMessages()
        stickerMessages = getStickerMessages(messages)

        for stickerMessage in stickerMessages:
            if stickerMessage.getSticker() == MORNING_STICKER:
                sender = int(stickerMessage.sender["id"])
                timestamp = int(stickerMessage.date)
                if sender not in users:
                    users[sender] = MorningEntry(stickerMessage.sender["first_name"])
                users[sender].setLastMorning(timestamp)

        json.dump(users, open(morningJSON, "w"), cls=MyJSONEncoder)

        botCommands = getBotCommands(messages)
        
        for botCommand in botCommands:
            if botCommand.text == "/morningStats":
                string = ""
                print(users)
                for user in users.keys():
                    
                    print(string)
                    string = string + "\n{name}: {totalMornings}".format(name=users[user].getName(), totalMornings=users[user].getTotalMornings())
                print(string)
                bot.connection.sendMessage(string)

def printJSON(message):
    print(json.dumps(message, indent=4, sort_keys=True, separators=(',', ': ')))

def getStickerMessages(messages):
    return [m for m in messages if isinstance(m, Sticker)]

def getTextMessages(messages):
    return filterMessageByType(messages, Text)

def getBotCommands(messages):
    return filterMessageByType(messages, BotCommand)

def filterMessageByType(messages, messageType):
    return [m for m in messages if isinstance(m, messageType)]

class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, MorningEntry):
            return obj.json
        else:
            return json.JSONEncoder.default(self, obj)

class MorningEntry():
    def __init__(self, name, json={"totalMornings": 0, "lastMorning": 0}):
        self.json = json
        self.json["name"] = name

    def getName(self):
        return self.json["name"]

    def getTotalMornings(self):
        return self.json["totalMornings"]

    def setTotalMornings(self, totalMornings):
        self.json["totalMornings"] = totalMornings

    def getLastMorning(self):
        return self.json["lastMorning"]
        #return self.date

    def setLastMorning(self, timestamp):
        lastMorning = self.getLastMorning()
        if self.countsAsNewDay(lastMorning, timestamp):
            self.setTotalMornings(self.getTotalMornings() + 1)
        self.json["lastMorning"] = timestamp

    def countsAsNewDay(self, lastTimestamp, timestamp):
        newDate = datetime.fromtimestamp(timestamp)
        newHour = newDate.hour
        newDay = newDate.toordinal()

        lastDate = datetime.fromtimestamp(lastTimestamp)
        #lastHour = lastDate.hour
        lastDay = lastDate.toordinal()

        if newHour < 4:
            newDay = newDay - 1

        return newDay > lastDay

main()
