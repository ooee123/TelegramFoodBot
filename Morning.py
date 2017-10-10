#!/usr/bin/python3
import sys
import os
from datetime import datetime
from time import time
import json
from json import JSONEncoder

from JsonSerializable import JsonSerializable
from plot import plot
import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters 
from Config import Config

MORNING_STICKER = "CAADAgADEQEAAtQ7SgJzg0f_OmyrNQI"

class Morning:
    def __init__(self, token, chatroom, morningJSON):
        self.chatroom = chatroom
        self.updater = Updater(token=token)
        self.config = Config("{chatroom}.conf.json".format(chatroom=str(chatroom)))
        self.morningJSON = morningJSON
        self.users = self.loadMorningJSON(self.morningJSON)

    # Input: Filepath to morning.json
    # Return: Dictionary of user_id to MorningEntry
    # Map<Integer, MorningEntry>
    def loadMorningJSON(self, morningJSON):
        if os.path.isfile(morningJSON):
            users = json.load(open(morningJSON, "r"))
            newUsers = {}
            for user_id in users.keys():
                newUsers[int(user_id)] = MorningEntry(users[user_id]["name"], users[user_id])
            return newUsers
        else:
            return {}

    def saveMorningJSON(self):
        json.dump(self.users, open(self.morningJSON, "w"), cls=MyJSONEncoder)

    def morningSticker(self, bot, update, args={}):
        senderId = update.message.from_user.id 
        senderName = update.message.from_user.first_name
        messageDate = update.message.date.timestamp()
        if senderId not in self.users:
            self.users[senderId] = MorningEntry(senderName)
        self.users[senderId].setLastMorning(messageDate)
        #self.users[senderId].setName(senderName)
        lastMorningOf = self.config.getAttribute("morningOf")
        todayMorningOf = getOrdinalDayThatCounts(messageDate)
        if todayMorningOf > lastMorningOf:
            self.users[senderId].addFirstMornings()
            self.config.setAttribute("morningOf", todayMorningOf)
        
    def morningStats(self, bot, update, args={}):
        sortedMornings = sorted(self.users.values(), key=lambda entry: entry.getTotalMornings(), reverse=True)
        strings = [str(morning) for morning in sortedMornings]
        text = "\n".join(strings)
        bot.send_message(chat_id=self.chatroom, text=text)

    def morningGraph(self, bot, update, args={}):
        senderId = update.message.from_user.id 
        if senderId in self.users:
            senderName = self.users[senderId].getName()
            saveas = senderName + ".png"
            firstMorningPerDay = self.users[senderId].getFirstMorningPerDay()
            plot.plotFirstMorningPerDay(firstMorningPerDay, saveas, senderName)
            bot.send_photo(chat_id=self.chatroom, photo=open(saveas, "rb"))

    def start(self):
        dispatcher = self.updater.dispatcher
        morning_sticker_handler = MessageHandler(Filters.sticker, self.morningSticker)
        dispatcher.add_handler(morning_sticker_handler)
        morningStats_handler = CommandHandler('morningStats', self.morningStats)
        dispatcher.add_handler(morningStats_handler)
        morningGraph_handler = CommandHandler('morningGraph', self.morningGraph)
        dispatcher.add_handler(morningGraph_handler)

        self.updater.start_polling()

def jsonToStr(message):
    return json.dumps(message, indent=4, sort_keys=True, separators=(',', ': '), cls=MyJSONEncoder)

class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JsonSerializable):
            return obj.__json__()
        else:
            return json.JSONEncoder.default(self, obj)

class MorningEntry(JsonSerializable):
    def __init__(self, name, json={"totalMornings": 0, "lastMorning": 0, "currentStreak": 0, "highestStreak": 0, "firstMornings": 0, "firstMorningPerDay": {}}):
        json["name"] = name
        self.json = json

    def getName(self):
        return self.json["name"]

    def setName(self, name):
        self.json["name"] = name

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

    def getFirstMornings(self):
        return self.getDefaultZero("firstMornings")

    def addFirstMornings(self):
        self.json["firstMornings"] = self.getFirstMornings() + 1

    def getDefaultZero(self, attribute):
        return self.getElseDefault(attribute, 0)

    def getElseDefault(self, attribute, default):
        if attribute not in self.json:
            self.json[attribute] = default
        return self.json[attribute]

    def setLastMorning(self, timestamp):
        if self.countsAsNewDay(timestamp):
            if self.isContinuingStreak(timestamp):
                self.setCurrentStreak(self.getCurrentStreak() + 1)
            else:
                self.setCurrentStreak(1)
            self.setTotalMornings(self.getTotalMornings() + 1)
            self.setFirstMorningOnDay(timestamp)
        self.json["lastMorning"] = timestamp

    def isContinuingStreak(self, timestamp):
        return getOrdinalDayThatCounts(timestamp) == getOrdinalDayThatCounts(self.getLastMorning()) + 1

    def countsAsNewDay(self, timestamp):
        newDay = getOrdinalDayThatCounts(timestamp)
        lastDay = getOrdinalDayThatCounts(self.getLastMorning())
        return newDay > lastDay

    def getFirstMorningPerDay(self):
        return self.getElseDefault("firstMorningPerDay", {})

    def setFirstMorningOnDay(self, timestamp):
        day = str(getOrdinalDayThatCounts(timestamp))
        #firstMorningPerDay = self.getFirstMorningsPerDay()
        #if day not in firstMorningPerDay.keys():
            #firstMorningPerDay[day] = timestamp
        self.getFirstMorningPerDay()[day] = timestamp

    def __json__(self):
        return self.json

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

def getOrdinalDayThatCounts(timestamp):
    newDate = datetime.fromtimestamp(timestamp)
    newHour = newDate.hour
    newDay = newDate.toordinal()
    if newHour < 4:
        newDay = newDay - 1
    return newDay

main()
