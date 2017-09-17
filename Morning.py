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

class Morning:
    def __init__(self, token, chatroom, morningJSON):
        self.morningJSON = morningJSON
        self.users = self.loadMorningJSON()
        self.bot = Bot(token, chatroom, timeout=60)

    def loadMorningJSON(self):
        if os.path.isfile(self.morningJSON):
            users = json.load(open(self.morningJSON, "r"))
            newUsers = {}
            for user_id in users.keys():
                newUsers[int(user_id)] = MorningEntry(users[user_id]["name"], users[user_id])
            return newUsers
        else:
            return {}

    def saveMorningJSON(self):
        json.dump(self.users, open(self.morningJSON, "w"), cls=MyJSONEncoder)

    def processStickers(self, messages):
        stickerMessages = getStickerMessages(messages)
        for stickerMessage in stickerMessages:
            if stickerMessage.getSticker() == MORNING_STICKER:
                sender_id = int(stickerMessage.sender["id"])
                if sender_id not in self.users:
                    self.users[sender_id] = MorningEntry(stickerMessage.sender["first_name"])
                self.users[sender_id].setLastMorning(int(stickerMessage.date))

    def processBotCommands(self, messages):
        botCommands = getBotCommands(messages)
        for botCommand in botCommands:
            if botCommand.text == "/morningStats":
                strings = [str(self.users[s]) for s in self.users.keys()]
                string = "\n".join(strings)
                self.bot.connection.sendMessage(string)

    def start(self):
        if True:
            messages = self.bot.getNewMessages()
            self.processStickers(messages)
            self.processBotCommands(messages)
            self.saveMorningJSON()

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
    def __init__(self, name, json={"totalMornings": 0, "lastMorning": 0, "currentStreak": 0, "highestStreak": 0}):
        json["name"] = name
        self.json = json

    def getName(self):
        return self.json["name"]

    def getTotalMornings(self):
        return self.getDefaultZero("totalMornings")

    def setTotalMornings(self, totalMornings):
        self.json["totalMornings"] = totalMornings

    def getLastMorning(self):
        return self.getDefaultZero("lastMorning")

    def getCurrentStreak(self):
        return self.getDefaultZero("currentStreak")

    def getHighestStreak(self):
        return self.getDefaultZero("highestStreak")

    def setCurrentStreak(self, streak):
        self.json["currentStreak"] = streak
        if streak > self.json["highestStreak"]:
            self.json["highestStreak"] = streak

    def getDefaultZero(self, attribute):
        if attribute not in self.json:
            self.json[attribute] = 0
        return self.json[attribute]
    

    def setLastMorning(self, timestamp):
        if self.countsAsNewDay(timestamp):
            if self.isContinuingStreak(timestamp):
                self.setCurrentStreak(self.getCurrentStreak() + 1)
            else:
                self.setCurrentStreak(1)
            self.setTotalMornings(self.getTotalMornings() + 1)
        self.json["lastMorning"] = timestamp

    def isContinuingStreak(self, timestamp):
        return self.getOrdinalDayThatCounts(timestamp) == self.getOrdinalDayThatCounts(self.getLastMorning()) + 1

    def countsAsNewDay(self, timestamp):
        newDay = self.getOrdinalDayThatCounts(timestamp)
        lastDay = self.getOrdinalDayThatCounts(self.getLastMorning())
        return newDay > lastDay

    def getOrdinalDayThatCounts(self, timestamp):
        newDate = datetime.fromtimestamp(timestamp)
        newHour = newDate.hour
        newDay = newDate.toordinal()

        if newHour < 4:
            newDay = newDay - 1

        return newDay

    def __str__(self):
        return "{name}: Total: {total}, Streak: {streak}, High: {high}".format(name=self.getName(), total=self.getTotalMornings(), streak=self.getCurrentStreak(), high=self.getHighestStreak())

def main():
    if len(sys.argv) < 3:
        print("Usage {0} <bot_token> <chatroom_id> <morning.json>".format(sys.argv[0]))
        sys.exit(-1)
    token = sys.argv[1]
    chatroom = int(sys.argv[2])
    morningJSON = sys.argv[3]
    morning = Morning(token, chatroom, morningJSON)
    morning.start()

main()
