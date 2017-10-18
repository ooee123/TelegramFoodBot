#!/usr/bin/python3
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot
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
quarterHourLocator = mdates.MinuteLocator(byminute=[15,30,45])

def plotFirstMorningPerDay(firstMorningPerDay, saveas, title, earliestMorning=None):
    #graphBeginning = dt.today() - timedelta
    #firstMorningPerDay = [x in firstMorningPerDay.keys() if dt.fromtimestamp(x) > graphBeginning]
    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax = axSetup(ax)
    plotMinutesVsDay(ax, firstMorningPerDay, saveas, earliestMorning)
    matplotlib.pyplot.title(title)
    fig.autofmt_xdate()
    matplotlib.pyplot.savefig(saveas, bbox_inches='tight')

def axSetup(ax):
    ax.xaxis_date()
    if True: #len(days) < LIMIT:
        ax.xaxis.set_major_locator(everyDayLocator)
    else:
        ax.xaxis.set_major_locator(majorDayLocator)
        ax.xaxis.set_minor_locator(everyDayLocator)

    if True:
        ax.yaxis.set_major_locator(everyHourLocator)
        ax.yaxis.set_minor_locator(quarterHourLocator)
    else:
        ax.yaxis.set_major_locator(majorHourLocator)
        ax.yaxis.set_minor_locator(everyHourLocator)

    ax.xaxis.set_major_formatter(dayFormatter)
    ax.yaxis.set_major_formatter(hourFormatter)
    return ax

def plotMinutesVsDay(ax, firstMorningPerDay, saveas, earliestMorning=None):
    days = [getOrdinalDayThatCounts(day) for day in firstMorningPerDay]
    minutes = [timestamp2minuteOfDay(day) for day in firstMorningPerDay]
    ax.plot_date(days, mpl.dates.date2num(minutes))

    if earliestMorning:
        days = [getOrdinalDayThatCounts(day) for day in earliestMorning]
        minutes = [timestamp2minuteOfDay(day) for day in earliestMorning]
        for day in days:
            print(day)
        for minute in minutes:
            print(minute)
        ax.plot_date(days, mpl.dates.date2num(minutes), 'yo')
        for xy in zip(days, minutes):
            ax.annotate(xy[1].strftime('%I:%M'), xy=xy, textcoords='data', va='top', ha='center')
def timestamp2minuteOfDay(timestamp):
    datetime = dt.datetime.fromtimestamp(timestamp)
    hours = datetime.time().hour
    minutes = datetime.time().minute
    return dt.datetime(dt.MINYEAR, 1, 2, hours, minutes)
