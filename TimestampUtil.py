from datetime import datetime

def getOrdinalDayThatCounts(timestamp):
    newDate = datetime.fromtimestamp(timestamp)
    newHour = newDate.hour
    newDay = newDate.toordinal()
    if newHour < 4:
        newDay -= 1
    return newDay

def getMinuteOfDay(timestamp):
    newDate = datetime.fromtimestamp(timestamp)
    newHour = newDate.hour
    newMinute = newDate.minute
    return newHour * 60 + newMinute
