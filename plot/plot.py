#!/usr/bin/python3
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.ticker import FuncFormatter as ff

def plotFirstMorningPerDay(firstMorningPerDay, saveas):
    days = [int(day) for day in firstMorningPerDay.keys()]
    minutes = [timestamp2minuteOfDay(day) for day in firstMorningPerDay.values()]
    plotMinutesVsDay(days, minutes, saveas)

def plotMinutesVsDay(days, minutes, saveas, annotate=False):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.xaxis_date()
    ax.yaxis.set_major_formatter(ff(m2hm))

    ax.plot_date(days, minutes)

    if annotate:
        for xy in zip(days, minutes):
            ax.annotate(m2hm(xy[1], 0), xy=xy, textcoords='data')

    fig.autofmt_xdate()
    plt.savefig(saveas, bbox_inches='tight')
 
def m2hm(minutes, i):
    h = int(minutes / 60)
    m = int(minutes % 60)
    return '%(h)02d:%(m)02d' % {'h':h,'m':m}

def timestamp2minuteOfDay(timestamp):
    datetime = dt.datetime.fromtimestamp(timestamp)
    hours = datetime.time().hour
    minutes = datetime.time().minute
    return hours * 60 + minutes
