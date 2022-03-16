#!/usr/bin/python3

import json
import os
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='Plot network specs graphs.')
parser.add_argument('filepath', metavar='F', type=str, nargs='+',
                    help='filename to the result json file.')
parser.add_argument('--show', help='plot the graphs in the process.', action='store_true')
args = parser.parse_args()

def openFile(filename):
    with open(filename, "r") as file:
        return json.loads(file.read())

def getDataDict(datas, path, factor=1000):
    dataDict = {}
    for key, value in datas.items():
        currentDataDict = []
        for test in value:
            if len(path) == 2:
                currentDataDict.append(float(test[path[0]][path[1]])/factor)
            else:
                currentDataDict.append(float(test[path[0]])/factor)
        dataDict[key] = currentDataDict
    return dataDict

def getAvailableQualities(qualityList):
    return pd.DataFrame(qualityList).sort_values(by="bitrate")

def getMinQuality(qualityList):
    return pd.DataFrame(qualityList)["bitrate"].idxmin()

def getMaxQuality(qualityList):
    return pd.DataFrame(qualityList)["bitrate"].idxmax()

def plotQualityBar(ax, index, title, x, x_title, y, y_title, ylim, yticks, mean):
    ax[index[0], index[1]].bar(x, y, label='Data')
    if mean:
        ax[index[0], index[1]].axhline(y=np.mean(y), label='Mean', linestyle='--', color="red")
        ax[index[0], index[1]].legend(loc='upper right')
    ax[index[0], index[1]].set_ylabel(y_title)
    ax[index[0], index[1]].set_xlabel(x_title)
    ax[index[0], index[1]].set_ylim(ylim)
    ax[index[0], index[1]].set_xticks(x)
    ax[index[0], index[1]].set_yscale("log")
    ax[index[0], index[1]].set_yticks(yticks["value"])
    ax[index[0], index[1]].set_yticklabels(yticks["label"])
    ax[index[0], index[1]].set_title(title, fontsize=10)
    ax[index[0], index[1]].tick_params(axis='y', which='major', labelsize=9)
    ax[index[0], index[1]].grid(True, axis="y")
    ax[index[0], index[1]].minorticks_off()

def plotTimingBar(ax, index, title, x, x_title, y, y_title, ylim, mean):
    ax[index[0], index[1]].bar(x, y, label='Data')
    if mean:
        ax[index[0], index[1]].axhline(y=np.mean(y), label='Mean', linestyle='--', color="red")
        ax[index[0], index[1]].legend(loc='upper right')
    if len(ylim) > 0:
        ax[index[0], index[1]].set_ylim(ylim)
    ax[index[0], index[1]].set_ylabel(y_title)
    ax[index[0], index[1]].set_xlabel(x_title)
    ax[index[0], index[1]].set_xticks(x)
    ax[index[0], index[1]].set_title(title, fontsize=10)
    ax[index[0], index[1]].tick_params(axis='y', which='major', labelsize=9)
    ax[index[0], index[1]].grid(True, axis="y")


def qualityBarPlotsAndSave(dataDict, dest, title, x_title, y_title, qualityList, mean=False, show=False):
    SAMPLES = len(list(dataDict.values())[0])
    x = 1 + np.arange(SAMPLES)

    qualityMatrix = getAvailableQualities(qualityList)
    minQuality = (qualityMatrix["bitrate"]/1000)[getMinQuality(qualityList)]
    maxQuality = (qualityMatrix["bitrate"]/1000)[getMaxQuality(qualityList)]
    ylim = [minQuality, maxQuality]
    yticks = {"value":qualityMatrix["bitrate"]/1000, "label":qualityMatrix["id"]}

    yslow3g = np.array(dataDict["SLOW_3G"])
    ygood3g = np.array(dataDict["GOOD_3G"])
    y4g = np.array(dataDict["REGULAR_4G"])
    ywifi = np.array(dataDict["WIFI"])

    fig, ax = plt.subplots(2, 2)

    plotQualityBar(ax, [0, 0], "Slow 3G stream", x, x_title, yslow3g, y_title, ylim, yticks, mean)
    plotQualityBar(ax, [0, 1], "Good 3G stream", x, x_title, ygood3g, y_title, ylim, yticks, mean)
    plotQualityBar(ax, [1, 0], "Regular 4G stream", x, x_title, y4g, y_title, ylim, yticks, mean)
    plotQualityBar(ax, [1, 1], "Wifi stream", x, x_title, ywifi, y_title, ylim, yticks, mean)

    fig.suptitle(title, fontsize=12)
    fig.set_size_inches(10.5, 10.5, forward=True)

    path = f'plots/{dest}/'
    os.makedirs(path, exist_ok=True)
    plt.savefig(f'{path}{title.lower().replace(" ", "_")}_plot.png', dpi=300)

    if show:
        plt.show()

def timingBarPlotsAndSave(dataDict, dest, title, x_title, y_title, ylim, mean=True, show=False):
    SAMPLES = len(list(dataDict.values())[0])
    x = 1 + np.arange(SAMPLES)

    yslow3g = np.array(dataDict["SLOW_3G"])
    ygood3g = np.array(dataDict["GOOD_3G"])
    y4g = np.array(dataDict["REGULAR_4G"])
    ywifi = np.array(dataDict["WIFI"])

    fig, ax = plt.subplots(2, 2)

    plotTimingBar(ax, [0, 0], "Slow 3G stream", x, x_title, yslow3g, y_title, ylim[0], mean)
    plotTimingBar(ax, [0, 1], "Good 3G stream", x, x_title, ygood3g, y_title, ylim[1], mean)
    plotTimingBar(ax, [1, 0], "Regular 4G stream", x, x_title, y4g, y_title, ylim[2], mean)
    plotTimingBar(ax, [1, 1], "Wifi stream", x, x_title, ywifi, y_title, ylim[3], mean)

    fig.suptitle(title, fontsize=12)
    fig.set_size_inches(10.5, 10.5, forward=True)

    path = f'plots/{dest}/'
    os.makedirs(path, exist_ok=True)
    plt.savefig(f'{path}{title.lower().replace(" ", "_")}_plot.png', dpi=300)

    if show:
        plt.show()

def plotGraphs(filename, dest, show):
    results = openFile(filename)["message"]
    availableQualities = results["available_qualities"]
    datas = results["datas"]

    joinTimes = getDataDict(datas, ["joinTime"], factor=1)
    bitrate02s = getDataDict(datas, ["states02s", "currentBitrate"])
    bitrate2s = getDataDict(datas, ["states2s", "currentBitrate"])
    bitrate12s = getDataDict(datas, ["states12s", "currentBitrate"])
    bitrate22s = getDataDict(datas, ["states22s", "currentBitrate"])

    buffer02s = getDataDict(datas, ["states02s", "videoBufferLength"], factor=0.001)
    buffer2s = getDataDict(datas, ["states2s", "videoBufferLength"], factor=0.001)
    buffer12s = getDataDict(datas, ["states12s", "videoBufferLength"], factor=0.001)
    buffer22s = getDataDict(datas, ["states22s", "videoBufferLength"], factor=0.001)

    timingBarPlotsAndSave(joinTimes, dest, "Join times", "Test number", "Join time (s)", [[], [], [], []], mean=True, show=show)

    qualityBarPlotsAndSave(bitrate02s, dest, "Starting bitrate", "Test number", "Bitrate (kbps)", availableQualities, show=show)
    qualityBarPlotsAndSave(bitrate2s, dest, "Bitrates after 2s playback", "Test number", "Bitrate (kbps)", availableQualities, show=show)
    qualityBarPlotsAndSave(bitrate12s, dest, "Bitrates after 12s playback", "Test number", "Bitrate (kbps)", availableQualities, show=show)
    qualityBarPlotsAndSave(bitrate22s, dest, "Bitrates after 22s playback", "Test number", "Bitrate (kbps)", availableQualities, show=show)

    timingBarPlotsAndSave(buffer02s, dest, "Starting buffer level", "Test number", "Buffer filled quantity (ms)", [[0, 10000], [0, 10000], [0, 10000], [0, 10000]], mean=True, show=show)
    timingBarPlotsAndSave(buffer2s, dest, "Buffer level after 2s playback", "Test number", "Buffer filled quantity (ms)", [[0, 10000], [0, 10000], [0, 10000], [0, 10000]], mean=True, show=show)
    timingBarPlotsAndSave(buffer12s, dest, "Buffer level after 12s playback", "Test number", "Buffer filled quantity (ms)", [[0, 10000], [0, 10000], [0, 10000], [0, 10000]], mean=True, show=show)
    timingBarPlotsAndSave(buffer22s, dest, "Buffer level after 22s playback", "Test number", "Buffer filled quantity (ms)", [[0, 10000], [0, 10000], [0, 10000], [0, 10000]], mean=True, show=show)

for filepath in args.filepath:
    dest = filepath.split("/")[-1].split(".")[0]
    plotGraphs(filepath, dest, args.show)