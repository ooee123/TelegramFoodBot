from datetime import datetime
import time
import json

from JsonSerializable import JsonSerializable
from plot import plot

MORNING_STICKER = "CAADAgADEQEAAtQ7SgJzg0f_OmyrNQI"

class Morning:

    def __init__(self, token, chatroom, config):
        self.chatroom = chatroom
        self.config = self.initConfig(config)
        self.users = config.get("users")

    def initConfig(self, config):
        if config.get("morningOf") == None:
            config.set("morningOf", 0)
        users = config.get("users")
        if users == None:
            config.set("users", {})
        else:
            newUsers = {}
            for user_id in users.keys():
                newUsers[int(user_id)] = MorningEntry(users[user_id]["name"], users[user_id])
            config.set("users", newUsers)
        return config
            
    def morningSticker(self, bot, update, args={}):
        senderId = update.message.from_user.id 
        senderName = update.message.from_user.first_name
        messageDate = int(update.message.date.timestamp())
        if senderId not in self.users.keys():
            self.users[senderId] = MorningEntry(senderName)
        self.users[senderId].setLastMorning(messageDate)
        lastMorningOf = self.config.get("morningOf")
        todayMorningOf = getOrdinalDayThatCounts(messageDate)
        if todayMorningOf > lastMorningOf:
            self.users[senderId].incrementFirstMornings()
            self.config.set("morningOf", todayMorningOf)
        self.config.saveConfig()
        
    def morningStats(self, bot, update, args={}):
        sortedMornings = sorted(self.users.values(), key=lambda entry: entry.getTotalMorningsCount(), reverse=True)
        todayOrdinalDay = getOrdinalDayThatCounts(time.time())
        strings = [morning.statsString(todayOrdinalDay) for morning in sortedMornings]
        text = "\n".join(strings)
        if text:
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

class MorningEntry(JsonSerializable):
    def __init__(self, name, json=None):
        if json == None:
            json = {"firstToMorningCount": 0, "firstMorningPerDay": []}
        json["name"] = name
        self.json = json
        days = [getOrdinalDayThatCounts(timestamp) for timestamp in json["firstMorningPerDay"]]
        highestStreak = 0
        currentStreak = 0
        previousDay = 0
        for currentDay in days:
            if currentDay - previousDay == 1:
                currentStreak += 1
            else:
                currentStreak = 1
            if currentStreak > highestStreak:
                highestStreak = currentStreak
            previousDay = currentDay

        today = getOrdinalDayThatCounts(time.time())
        if today - previousDay > 1:
            self.currentStreak = 0
        self.days = days
        self.highestStreak = highestStreak
        self.currentStreak = currentStreak

    def getName(self):
        return self.json["name"]

    def getTotalMorningsCount(self):
        return len(self.json["firstMorningPerDay"])

    def getLastMorning(self):
        if len(self.json["firstMorningPerDay"]) == 0:
            return 0
        else:
            return max(self.json["firstMorningPerDay"])

    def getCurrentStreak(self):
        return self.currentStreak

    def getHighestStreak(self):
        return self.highestStreak

    def getFirstToMorningCount(self):
        return self.json["firstToMorningCount"]

    def incrementFirstMornings(self):
        self.json["firstToMorningCount"] += 1

    def setLastMorning(self, timestamp):
        if self.countsAsNewDay(timestamp):
            self.setFirstMorningOnDay(timestamp)
            if self.isContinuingStreak(timestamp):
                self.currentStreak += 1
            else:
                self.currentStreak = 1
            self.highestStreak = max(self.highestStreak, self.currentStreak)

    def isContinuingStreak(self, timestamp):
        return getOrdinalDayThatCounts(timestamp) == getOrdinalDayThatCounts(self.getLastMorning()) + 1

    def countsAsNewDay(self, timestamp):
        newDay = getOrdinalDayThatCounts(timestamp)
        lastDay = getOrdinalDayThatCounts(self.getLastMorning())
        return newDay > lastDay

    def getFirstMorningPerDay(self):
        return self.json["firstMorningPerDay"]

    def setFirstMorningOnDay(self, timestamp):
        day = getOrdinalDayThatCounts(timestamp)
        if day not in self.days:
            self.json["firstMorningPerDay"].append(timestamp)

    def __json__(self):
        return self.json

    def __str__(self):
        return self.json

    def statsString(self, todayOrdinalDay):
        lastOrdinalDay = getOrdinalDayThatCounts(self.getLastMorning())
        if todayOrdinalDay - lastOrdinalDay > 1:
            self.currentStreak = 0
        return "{name}: Ttl: {total}, Str: {streak}, Hi: {high}".format(name=self.getName(), total=self.getTotalMorningsCount(), streak=self.getCurrentStreak(), high=self.getHighestStreak())

def getOrdinalDayThatCounts(timestamp):
    newDate = datetime.fromtimestamp(timestamp)
    newHour = newDate.hour
    newDay = newDate.toordinal()
    if newHour < 4:
        newDay = newDay - 1
    return newDay
