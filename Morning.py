#!/usr/bin/python3
import sys
import os
from datetime import datetime
from time import time
import json

from JsonSerializable import JsonSerializable
from JsonSerializable import MyJSONEncoder
from plot import plot
import telegram
from telegram.ext import BaseFilter
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters 
from Config import Config

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

MORNING_STICKER = "CAADAgADEQEAAtQ7SgJzg0f_OmyrNQI"

class Morning:
    
    def initConfig(self):
        return {"morningOf": 0, "users": {}}

    def __init__(self, token, chatroom):
        self.chatroom = chatroom
        self.updater = Updater(token=token)
        self.config = Config("{chatroom}.conf.json".format(chatroom=str(chatroom)), init=self.initConfig)
        self.users = self.initMorningJSON(self.config.getAttribute("users"))
        self.config.setAttribute("users", self.users)

    # Input: Filepath to morning.json
    # Return: Dictionary of user_id to MorningEntry
    # Map<Integer, MorningEntry>
    def initMorningJSON(self, morningJSON):
        if not morningJSON:
            return {}
        else:
            users = morningJSON
            newUsers = {}
            for user_id in users.keys():
                newUsers[int(user_id)] = MorningEntry(users[user_id]["name"], users[user_id])
            return newUsers

    def morningSticker(self, bot, update, args={}):
        senderId = update.message.from_user.id 
        senderName = update.message.from_user.first_name
        messageDate = update.message.date.timestamp()
        
        if senderId not in self.users.keys():
            self.users[senderId] = MorningEntry(senderName)
        self.users[senderId].setLastMorning(messageDate)
        lastMorningOf = self.config.getAttribute("morningOf")
        todayMorningOf = getOrdinalDayThatCounts(messageDate)
        if todayMorningOf > lastMorningOf:
            self.users[senderId].incrementFirstMornings()
            self.config.setAttribute("morningOf", todayMorningOf)
        self.config.saveConfig()
        
    def morningStats(self, bot, update, args={}):
        sortedMornings = sorted(self.users.values(), key=lambda entry: entry.getTotalMorningsCount(), reverse=True)
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
        morning_sticker_handler = MessageHandler(MorningStickerFilter(), self.morningSticker)
        dispatcher.add_handler(morning_sticker_handler)
        morningStats_handler = CommandHandler('morningStats', self.morningStats)
        dispatcher.add_handler(morningStats_handler)
        morningGraph_handler = CommandHandler('morningGraph', self.morningGraph)
        dispatcher.add_handler(morningGraph_handler)

        self.updater.start_polling()

class MorningStickerFilter(BaseFilter):
    def filter(self, message):
        return message.sticker and MORNING_STICKER == message.sticker.file_id

def jsonToStr(message):
    return json.dumps(message, indent=4, sort_keys=True, separators=(',', ': '), cls=MyJSONEncoder)

class MorningEntry(JsonSerializable):
    def __init__(self, name, json=None):
        if json == None:
            json = {"currentStreak": 0, "highestStreak": 0, "firstToMorningCount": 0, "firstMorningPerDay": {}}
        json["name"] = name
        self.json = json

    def getName(self):
        return self.json["name"]

    def getTotalMorningsCount(self):
        return len(self.getFirstMorningPerDay())

    def getLastMorning(self):
        firstMorningPerDay = self.getFirstMorningPerDay()
        if not firstMorningPerDay:
            return 1
        else:
            return max(firstMorningPerDay.values())

    def getCurrentStreak(self):
        return self.getDefaultZero("currentStreak")

    def getHighestStreak(self):
        return self.getDefaultZero("highestStreak")

    def setCurrentStreak(self, streak):
        self.json["currentStreak"] = streak

    def getFirstToMorningCount(self):
        return self.getDefaultZero("firstToMorningCount")

    def incrementFirstMornings(self):
        self.json["firstToMorningCount"] += 1

    def getDefaultZero(self, attribute):
        return self.getElseDefault(attribute, 0)

    def getElseDefault(self, attribute, default):
        if attribute not in self.json.keys():
            self.json[attribute] = default
        return self.json[attribute]

    def setLastMorning(self, timestamp):
        if self.countsAsNewDay(timestamp):
            self.setFirstMorningOnDay(timestamp)
            if self.isContinuingStreak(timestamp):
                self.json["currentStreak"] += 1
            else:
                self.json["currentStreak"] = 1
            self.json["highestStreak"] = max(self.json["highestStreak"], self.json["currentStreak"])

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
        self.getFirstMorningPerDay()[day] = timestamp

    def __json__(self):
        return self.json

    def __str__(self):
        return "{name}: Total: {total}, Streak: {streak}, High: {high}".format(name=self.getName(), total=self.getTotalMorningsCount(), streak=self.getCurrentStreak(), high=self.getHighestStreak())

def main():
    if len(sys.argv) < 2:
        print("Usage {0} <bot_token> <chatroom_id>".format(sys.argv[0]))
        sys.exit(-1)
    token = sys.argv[1]
    chatroom = int(sys.argv[2])
    morning = Morning(token, chatroom)
    morning.start()

def getOrdinalDayThatCounts(timestamp):
    newDate = datetime.fromtimestamp(timestamp)
    newHour = newDate.hour
    newDay = newDate.toordinal()
    if newHour < 4:
        newDay = newDay - 1
    return newDay

main()
