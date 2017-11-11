#!/usr/bin/python3
import matplotlib as mpl
# matplotlib setup
mpl.use("Agg")
import matplotlib.pyplot
import datetime as dt
import matplotlib.dates as mdates
import seaborn as seaborn
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

def plotFirstMorningPerDayAll(morningEntries, saveas, title):
    ax = setupDateGraph()
    for morningEntry in morningEntries.values():
        plotMinutesVsDay(ax, morningEntry.getFirstMorningPerDay(), label=morningEntry.getName(), linestyle='solid')
    ax.legend()
    saveDateGraph(ax, saveas, title)

def plotFirstMorningPerDay(firstMorningPerDay, saveas, title, earliestMorning=None):
    ax = setupDateGraph()
    plotMinutesVsDay(ax, firstMorningPerDay)
    plotEarliestMornings(ax, earliestMorning)
    saveDateGraph(ax, saveas, title)

def setupDateGraph():
    fig = matplotlib.pyplot.figure()
    seaborn.set()
    ax = fig.add_subplot(1, 1, 1)
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

def saveDateGraph(ax, saveas, title):
    matplotlib.pyplot.title(title)
    ax.get_figure().autofmt_xdate()
    matplotlib.pyplot.savefig(saveas, bbox_inches='tight')

def plotMinutesVsDay(ax, firstMorningPerDay, **kwargs):
    days = [getOrdinalDayThatCounts(day) for day in firstMorningPerDay]
    minutes = [timestampToMinuteOfDay(day) for day in firstMorningPerDay]
    ax.plot_date(days, mpl.dates.date2num(minutes), **kwargs)

def plotEarliestMornings(ax, earliestMorning=None):
    if earliestMorning:
        days = [getOrdinalDayThatCounts(day) for day in earliestMorning]
        minutes = [timestampToMinuteOfDay(day) for day in earliestMorning]
        for day in days:
            print(day)
        for minute in minutes:
            print(minute)
        ax.plot_date(days, mpl.dates.date2num(minutes), 'yo')
        for xy in zip(days, minutes):
            ax.annotate(xy[1].strftime('%I:%M'), xy=xy, textcoords='data', va='top', ha='center')

def timestampToMinuteOfDay(timestamp):
    datetime = dt.datetime.fromtimestamp(timestamp)
    hours = datetime.time().hour
    minutes = datetime.time().minute
    return dt.datetime(dt.MINYEAR, 1, 2, hours, minutes)
