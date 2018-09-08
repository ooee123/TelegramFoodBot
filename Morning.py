import time
import datetime
import statistics

from JsonSerializable import JsonSerializable
from TimestampUtil import getOrdinalDayThatCounts
from TimestampUtil import getMinuteOfDay
from plot import plot

MORNING_STICKER = "CAADAgADEQEAAtQ7SgJzg0f_OmyrNQI"

latestRecordedDay = 0

class Morning:

    def __init__(self, token, chatroom, config):
        earliestMornings = {} #None # Change to {} if you want the earliest mornings
        self.chatroom = chatroom
        self.config = self.initConfig(config, earliestMornings)
        self.users = config.get("users")
        self.earliestMornings = self.switchEarliestMorningDimension(earliestMornings)

    def switchEarliestMorningDimension(self, earliestMornings):
        if earliestMornings is not None:
            newDimension = {}
            mornings = earliestMornings.values()
            for morning in mornings:
                for id in morning["ids"]:
                    if id not in newDimension:
                        newDimension[id] = [morning["timestamp"]]
                    else:
                        newDimension[id].append(morning["timestamp"])
            return newDimension
        else:
            return None

    def initConfig(self, config, earliestMornings=None):
        users = config.get("users")
        if users is None:
            config.set("users", {})
        else:
            newUsers = {}
            for user_id in users.keys():
                newUsers[int(user_id)] = MorningEntry(int(user_id), users[user_id]["name"], users[user_id], earliestMornings)
            config.set("users", newUsers)
        return config
            
    def morningSticker(self, bot, update):
        print("Start morning sticker", flush=True)
        global latestRecordedDay
        senderId = update.message.from_user.id 
        senderName = update.message.from_user.first_name
        messageDate = int(update.message.date.timestamp())
        if senderId not in self.users.keys():
            self.users[senderId] = MorningEntry(senderId, senderName)
        self.users[senderId].setLastMorning(messageDate)
        self.config.saveConfig()

        ordinalDay = getOrdinalDayThatCounts(messageDate)
        if self.earliestMornings is not None and ordinalDay > latestRecordedDay:
            if senderId not in self.earliestMornings:
                self.earliestMornings[senderId] = [messageDate]
            else:
                self.earliestMornings[senderId].append(messageDate)
            latestRecordedDay = ordinalDay
        
    def morningStats(self, bot, update, args={}):
        sortedMornings = sorted(self.users.values(), key=lambda entry: entry.getTotalMorningsCount(), reverse=True)
        todayOrdinalDay = getOrdinalDayThatCounts(time.time())
        strings = [morning.statsString(todayOrdinalDay) for morning in sortedMornings]
        text = "\n".join(strings)
        if text:
            bot.send_message(chat_id=self.chatroom, text=text)
        
    def morningStatistics(self, bot, update, args={}):
        days = None
        descriptor = "lifetime"
        if args:
            try:
                days = int(args[0])
                descriptor = "last " + str(days) + " days"
            except TypeError:
                pass 
        senderId = update.message.from_user.id 
        firstMorningPerDay = self.users[senderId].getFirstMorningPerDay(days)
        if firstMorningPerDay:
            print(descriptor)
            minutesOfDay = [getMinuteOfDay(x) for x in firstMorningPerDay]
            mean = int(round(statistics.mean(minutesOfDay)))
            mean = datetime.time(int(mean / 60), int(mean % 60))
            pstdev = round(statistics.pstdev(minutesOfDay), 2)
            earliestMornings = self.earliestMornings[senderId]
            earliestMornings = [x for x in earliestMornings if x in firstMorningPerDay]
            name = self.users[senderId].getName()
            print(descriptor)

            text = "{name}'s {descriptor} stats:\nMean: {mean}\nStdDev: {pstdev}m\nMornings: {mornings}\nEarliest Count: {earliestMornings}".format(name=name, descriptor=descriptor, mean=mean.strftime("%I:%M%p"), pstdev=pstdev, mornings=len(firstMorningPerDay), earliestMornings=len(earliestMornings))
            bot.send_message(chat_id=self.chatroom, text=text)

    def morningGraph(self, bot, update, args={}):
        days = 30
        if args:
            try:
                days = int(args[0])
            except TypeError:
                pass 
        senderId = update.message.from_user.id 
        if senderId in self.users:
            senderName = self.users[senderId].getName()
            saveas = senderName + ".png"
            firstMorningPerDay = self.users[senderId].getFirstMorningPerDay(days)
            if senderId in self.earliestMornings:
                earliestMornings = self.earliestMornings[senderId]
                earliestMornings = [x for x in earliestMornings if x in firstMorningPerDay]
            else:
                earliestMornings = None
            plot.plotFirstMorningPerDay(firstMorningPerDay, saveas, senderName, earliestMornings)
            bot.send_photo(chat_id=self.chatroom, photo=open(saveas, "rb"))

    def morningGraphAll(self, bot, _):
        saveas = "everyone.png"
        plot.plotFirstMorningPerDayAll(self.users, saveas, "Everyone's Mornings")
        bot.send_photo(chat_id=self.chatroom, photo=open(saveas, "rb"))

    def downloadMornings(self, bot, update, args={}):
        senderId = update.message.from_user.id 
        if senderId in self.users:
            senderName = self.users[senderId].getName()
            saveas = senderName + ".txt"
            firstMorningPerDay = self.users[senderId].getFirstMorningPerDay()
            times = "\n".join([str(x) for x in firstMorningPerDay])
            f = open(saveas, "w")
            f.write(times)
            f.close()
            f = open(saveas, "rb")
            
            today = time.strftime("%Y-%m-%d")
            
            bot.send_document(chat_id=self.chatroom, document=f, filename=senderName + "." + today + ".txt")

class MorningEntry(JsonSerializable):
    def __init__(self, id, name, json=None, earliestMornings=None):
        if json is None:
            json = {"firstMorningPerDay": []}
        json["name"] = name
        self.json = json
        self.id = id

        global latestRecordedDay
        highestStreak = 0
        currentStreak = 0
        previousDay = 0
        for timestamp in json["firstMorningPerDay"]:
            currentDay = getOrdinalDayThatCounts(timestamp)
            if currentDay - previousDay == 1:
                currentStreak += 1
            else:
                currentStreak = 1
            if currentStreak > highestStreak:
                highestStreak = currentStreak
            previousDay = currentDay
            if currentDay > latestRecordedDay:
                latestRecordedDay = currentDay

            if earliestMornings is not None:
                if currentDay not in earliestMornings or timestamp < earliestMornings[currentDay]["timestamp"]:
                    earliestMornings[currentDay] = {"timestamp": timestamp, "ids": [id]}
                elif timestamp == earliestMornings[currentDay]["timestamp"]:
                    earliestMornings[currentDay]["ids"].append(id)

        # This is also caught only when displaying, i.e. morningstats
        #today = getOrdinalDayThatCounts(time.time())
        #if today - previousDay > 1:
        #    self.currentStreak = 0
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

    def setLastMorning(self, timestamp):
        if self.countsAsNewDay(timestamp):
            if self.isContinuingStreak(timestamp):
                self.currentStreak += 1
            else:
                self.currentStreak = 1
            if self.currentStreak > self.highestStreak:
                self.highestStreak = self.currentStreak
            self.json["firstMorningPerDay"].append(timestamp)

    def isContinuingStreak(self, timestamp):
        return getOrdinalDayThatCounts(timestamp) - getOrdinalDayThatCounts(self.getLastMorning()) == 1

    def countsAsNewDay(self, timestamp):
        newDay = getOrdinalDayThatCounts(timestamp)
        lastDay = getOrdinalDayThatCounts(self.getLastMorning())
        return newDay > lastDay

    def getFirstMorningPerDay(self, lastNDays=None):
        if lastNDays:
            today = time.time()
            afterTime = today - lastNDays * 24 * 60 * 60
            return [x for x in self.json["firstMorningPerDay"] if x >= afterTime]
        else:
            return self.json["firstMorningPerDay"]

    def __json__(self):
        return self.json

    def __str__(self):
        return self.json

    def statsString(self, todayOrdinalDay):
        lastOrdinalDay = getOrdinalDayThatCounts(self.getLastMorning())
        if todayOrdinalDay - lastOrdinalDay > 1:
            self.currentStreak = 0
        return "{name}: Ttl: {total}, Str: {streak}, Hi: {high}".format(name=self.getName(), total=self.getTotalMorningsCount(), streak=self.getCurrentStreak(), high=self.getHighestStreak())
