from calendar import c
import os
import time
import csv
import shutil
import numpy as np
import matplotlib.pyplot as plt
import pickle
import cv2
from scipy import signal

from ctypes import *
import math
import random
import pprint
import cv2
import numpy
import sys
import hashlib

def makeAllRpiList(filePath):
    RPIList = []
    UniqueRPIList = []
    ResultRPIList = []

    # Threshold for the number of received RPIs to be observed
    RpiCount = 1

    # Lower threshold of max signal strength
    maxSignalStrength = -60

    with open(filePath, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            timeStamp = float(row[0])
            RPI = row[1]
            RSSI = float(row[2])
            RPIList.append(RPI)
    
    UniqueRPIList = list(set(RPIList))

    for RPI in UniqueRPIList:
        if RPIList.count(RPI) > RpiCount:
            with open(filePath, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    timeStamp = float(row[0])
                    getRpi = row[1]
                    RSSI = float(row[2])
                    if getRpi == RPI and RSSI > maxSignalStrength:
                        ResultRPIList.append(getRpi)
                        break
        
    print(ResultRPIList)
    return ResultRPIList

def link(targetTime, targetRpi, picturedDir,experimentNumber, deviceNumber):
    filePath = picturedDir
    capturedTimeList = []

    with open(filePath + "0_timeList_0") as ff:
        reader = csv.reader(ff)
        for row in reader:
            capturedTimeList.append(float(row[0]))

    minDiff = 999999999999999
    minTime = 0

    for capturedTime in capturedTimeList:
        if abs(targetTime - capturedTime) < minDiff:
            minDiff = abs(targetTime - capturedTime)
            minTime = capturedTime
    
    targetFilePath = filePath + "0_0_" + str(minTime) + ".jpg"
    img = cv2.imread(targetFilePath, cv2.IMREAD_COLOR)
    cv2.imwrite( './result' + '/' + str(experimentNumber) + '/' + str(deviceNumber)  +"/"+str(targetRpi)+"_"+str(minTime) + "_" + "side"+".jpg", img)
    targetSecondFilePath = targetFilePath

    capturedTimeList = []

    with open(filePath + "0_timeList_1") as ff:
        reader = csv.reader(ff)
        for row in reader:
            capturedTimeList.append(float(row[0]))

    minDiff = 999999999999999
    minTime = 0

    for capturedTime in capturedTimeList:
        if abs(targetTime - capturedTime) < minDiff:
            minDiff = abs(targetTime - capturedTime)
            minTime = capturedTime

    targetFilePath = filePath + "0_1_" + str(minTime) + ".jpg"
    img = cv2.imread(targetFilePath, cv2.IMREAD_COLOR)
    cv2.imwrite( './result' + '/' + str(experimentNumber) + '/' + str(deviceNumber)  +"/"+str(targetRpi)+"_"+str(minTime)+ "_" + "front"+".jpg", img)    


def linkFromTimeList(targetTime, targetRpi, picturedDir, experimentNumber, deviceNumber):
    link(targetTime, targetRpi, picturedDir, experimentNumber, deviceNumber)
    
def dirCheck(experimentNumber, deviceNumber):
    filePathList = []

    filePathList.append('./result')
    filePathList.append('./result' + '/' + str(experimentNumber))
    filePathList.append('./result' + '/' + str(experimentNumber) + '/' + str(deviceNumber))

    for filePath in filePathList:
        if not os.path.exists(filePath):
            os.makedirs(filePath)

def mitigate(timeList, signalStrengthList):

    beforeSignalStrength = -1
    beforeTime = -1.0
    
    alreadyChekcTime = -1

    for j in range(10000000):
        flag = 0
        for i, signalStrengh in enumerate(signalStrengthList):
            if timeList[i] > alreadyChekcTime:
                if len(signalStrengthList) - i > 4:
                    if signalStrengthList[i] == signalStrengthList[i + 1] and signalStrengthList[i + 1] == signalStrengthList[i + 2] and signalStrengthList[i + 2] == signalStrengthList[i + 3]:
                        aveTime = (timeList[i + 1] + timeList[i + 2]) / 2
                        aveSig = (signalStrengthList[i + 1] + signalStrengthList[i + 2]) / 2 + 0.1
                        timeList.insert(i + 2, aveTime)
                        signalStrengthList.insert(i + 2, aveSig)
                        alreadyChekcTime = timeList[i + 3]
                        flag = 1
                        break
                    elif signalStrengthList[i] == signalStrengthList[i + 1] and signalStrengthList[i + 1] == signalStrengthList[i + 2]:
                        aveTime = timeList[i + 1]
                        aveSig = signalStrengthList[i + 1] + 0.1
                        timeList[i + 1] = aveTime
                        signalStrengthList[i + 1] = aveSig
                        alreadyChekcTime = timeList[i + 2]
                        flag = 1
                        break

                    elif signalStrengthList[i] == signalStrengthList[i + 1]:
                        aveTime = (timeList[i] + timeList[i + 1]) / 2
                        aveSig = (signalStrengthList[i] + signalStrengthList[i + 1]) / 2 + 0.1
                        timeList.insert(i+1, aveTime)
                        signalStrengthList.insert(i + 1, aveSig)
                        alreadyChekcTime = timeList[i + 1]
                        flag = 1
                        break
        if flag == 0:
            break

    return timeList, signalStrengthList
        
def removeBeforeData(timeList, signalStrengthList, targetTime):
    resultTimeList = []
    resultSignalStrengthList = []
    for i,aTime in enumerate(timeList):
        if aTime > targetTime:
            resultTimeList.append(aTime)
            resultSignalStrengthList.append(signalStrengthList[i])
    return resultTimeList, resultSignalStrengthList


def makeGraph(allRPIList, timeSignalStrengthFilePath, picturedFilePathSide, picturedFilePathFront, picturedDir, experimentNumber, deviceNumber):
    plt.rcParams["figure.figsize"] = (19, 9.1)
    plt.rcParams['font.sans-serif'] = 'Helvetica'
    plt.rcParams["font.size"] = 44

    dirCheck(experimentNumber, deviceNumber)

    global EXTRACTCSVFILEPATH
    EXTRACTCSVFILEPATH = picturedDir

    fig, ax = plt.subplots()
    ax.set_xlabel('Time : t [s]', fontsize=50)
    ax.set_ylabel('RSSI [dBm]', fontsize=50)
    ax.grid()
    ax.get_xaxis().get_major_formatter().set_useOffset(False)
    

    minTime = getMinTime(picturedDir)

    labelNumber = 1
    print("allRPIList : " + str(allRPIList))
    for count,targetRpi in enumerate(allRPIList):
        print("targetRPI : " + str(targetRpi))

        timeList = []
        signalStrengthList = []

        with open(timeSignalStrengthFilePath, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                timeStamp = float(row[0])
                RPI = row[1]
                RSSI = float(row[2])
                if RPI == targetRpi:
                    timeList.append(timeStamp)
                    signalStrengthList.append(RSSI)

        timeList, signalStrengthList = mitigate(timeList, signalStrengthList)

        zeroStartTimeStart = []

        for aTime in timeList:
            zeroStartTimeStart.append(aTime - minTime)

        maxSignalStrength = max(signalStrengthList)
        print("max")
        print(maxSignalStrength)
        
        maxSignalStrengthThreshold = -60


        if maxSignalStrength >= maxSignalStrengthThreshold:
            maxIndex = signalStrengthList.index(maxSignalStrength)

            print(signalStrengthList[maxIndex])
            print(timeList[maxIndex]-minTime)

            print("MIN")
            print(minTime)

            ax.plot(zeroStartTimeStart, signalStrengthList, label="RPI "+str(labelNumber), marker="o", markersize=12)

            print("peakTime : " + str(zeroStartTimeStart[maxIndex]))
            ax.plot(zeroStartTimeStart[maxIndex], maxSignalStrength, 'b*', markersize=28)

            ax.set_ylim(-85,5)


            print("-----")
            print(zeroStartTimeStart[maxIndex])
            linkFromTimeList(zeroStartTimeStart[maxIndex] + minTime, targetRpi, picturedDir, experimentNumber, deviceNumber)

            labelNumber = labelNumber + 1

    ax.legend(loc=0, fontsize=14)
    fig.tight_layout()
    fig.subplots_adjust(left=0.18, right=0.98, bottom=0.23, top=0.98)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

def getMinTime(filePath):
    timeSignalStrengthFilePath = filePath + "0_GoodData.csv"
    timeList = []
    with open(timeSignalStrengthFilePath, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                timeStamp = float(row[0])
                timeList.append(timeStamp)

    return min(timeList)

def onclick(event):
    print("Clicked")
    print("x: " + str(event.xdata) + " y : " + str(event.ydata))

    filePath = EXTRACTCSVFILEPATH

    minTime = getMinTime(filePath)

    targetX = float(event.xdata) + minTime
    targetY = float(event.ydata)

    capturedTimeListSide = []
    capturedTimeListFront = []

    with open(filePath + "0_timeList_0") as ff:
        reader = csv.reader(ff)
        for row in reader:
            capturedTimeListSide.append(float(row[0]))
    
    with open(filePath + "0_timeList_1") as ff:
        reader = csv.reader(ff)
        for row in reader:
            capturedTimeListFront.append(float(row[0]))

    minDiff = 999999999999999
    minTime = 0

    for capturedTime in capturedTimeListSide:
        if abs(targetX - capturedTime) < minDiff:
            minDiff = abs(targetX - capturedTime)
            minTime = capturedTime
    
    print(filePath + "0_0_" + str(minTime) + ".jpg")
    imgCVSide = cv2.imread(filePath + "0_0_" + str(minTime) + ".jpg")

    minDiff = 999999999999999
    minTime = 0

    for capturedTime in capturedTimeListFront:
        if abs(targetX - capturedTime) < minDiff:
            minDiff = abs(targetX - capturedTime)
            minTime = capturedTime
    
    print(filePath + "0_1_" + str(minTime) + ".jpg")
    imgCVFront = cv2.imread(filePath + "0_1_" + str(minTime) + ".jpg")

    mergeImg = numpy.hstack((imgCVSide, imgCVFront))

    cv2.imshow("imgWindow", mergeImg)
    
global EXTRACTCSVFILEPATH

experimentNumber = int(input("Experiment Number : "))
deviceNumber = 0
targetRpiAllOrTarget = 0
targetRPIList = []


dirName = "./data/" + str(experimentNumber) + "/" + str(deviceNumber) + "/"
timeSignalStrengthFileName = "0_GoodData_Hash.csv"
picturedFileNameSide = "0_timeList_0"
picturedFileNameFront = "0_timeList_1"

allRPIList = []
if targetRpiAllOrTarget == 0:
    allRPIList = makeAllRpiList(dirName + timeSignalStrengthFileName)
    pprint.pprint(allRPIList)
makeGraph(allRPIList, dirName + timeSignalStrengthFileName, dirName + picturedFileNameSide, dirName + picturedFileNameFront, dirName, experimentNumber, deviceNumber)