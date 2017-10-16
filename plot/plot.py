#!/usr/bin/python3
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import datetime as dt
import matplotlib.dates as mdates
from TimestampUtil import getOrdinalDayThatCounts

LIMIT = 14
#SINCE_HOW_MANY_DAYS = 14

#timedelta = dt.timedelta(SINCE_HOW_MANY_DAYS)

majorDayLocator = mdates.DayLocator(interval=3)
everyDayLocator = mdates.DayLocator(interval=1)
dayFormatter = mdates.DateFormatter('%a %b %d')

majorHourLocator = mdates.HourLocator(interval=2)
everyHourLocator = mdates.HourLocator(interval=1)
hourFormatter = mdates.DateFormatter('%I:%M %p')
halfHourLocator = mdates.MinuteLocator(byminute=30)

def plotFirstMorningPerDay(firstMorningPerDay, saveas, title):
    #graphBeginning = dt.today() - timedelta
    #firstMorningPerDay = [x in firstMorningPerDay.keys() if dt.fromtimestamp(x) > graphBeginning]
    days = [getOrdinalDayThatCounts(day) for day in firstMorningPerDay]
    minutes = [timestamp2minuteOfDay(day) for day in firstMorningPerDay]
    plt = plotMinutesVsDay(days, minutes, saveas)
    plt.title(title)
    plt.savefig(saveas, bbox_inches='tight')

def plotMinutesVsDay(days, minutes, saveas, annotate=False):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.xaxis_date()

    ax.plot_date(days, mpl.dates.date2num(minutes))
    if len(days) < LIMIT:
        ax.xaxis.set_major_locator(everyDayLocator)
    else:
        ax.xaxis.set_major_locator(majorDayLocator)
        ax.xaxis.set_minor_locator(everyDayLocator)
    ax.xaxis.set_major_formatter(dayFormatter)

    ax.yaxis.set_major_locator(everyHourLocator)
    ax.yaxis.set_minor_locator(halfHourLocator)
    ax.yaxis.set_major_formatter(hourFormatter)

    if annotate:
        for xy in zip(days, minutes):
            ax.annotate(m2hm(xy[1], 0), xy=xy, textcoords='data')

    fig.autofmt_xdate()
    return plt

def timestamp2minuteOfDay(timestamp):
    datetime = dt.datetime.fromtimestamp(timestamp)
    hours = datetime.time().hour
    minutes = datetime.time().minute
    return dt.datetime(dt.MINYEAR, 1, 1, hours, minutes)
