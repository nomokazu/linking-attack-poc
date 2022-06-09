import os
import csv
import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy import signal

from ctypes import *
import cv2
import pandas as pd

def makeAllRpiList(goodDataTable):
    RPIList = []
    UniqueRPIList = []
    ResultRPIList = []

    RpiCount = 1

    maxSignalStrength = -140
    RPIList = goodDataTable["rpi"].to_numpy().tolist()
    UniqueRPIList = list(set(RPIList))
    for RPI in UniqueRPIList:
        if RPIList.count(RPI) > RpiCount:
            newDf = goodDataTable.query("rpi==" + str(RPI))
            RSSI = newDf["packetsignaldbm"].max()
            if RSSI > maxSignalStrength:
                ResultRPIList.append(RPI)
    
    print(ResultRPIList)
    return ResultRPIList

def link(targetTime, targetRpi, picturedDir,experimentNumber, deviceNumber):
    filePath = picturedDir
    capturedTimeList = []

    with open(filePath + "0_timeList") as ff:
        reader = csv.reader(ff)
        for row in reader:
            capturedTimeList.append(float(row[0]))

    minDiff = 999999999999999
    minTime = 0

    for capturedTime in capturedTimeList:
        if abs(targetTime - capturedTime) < minDiff:
            minDiff = abs(targetTime - capturedTime)
            minTime = capturedTime
    
    targetFilePath = filePath + "0_" + str(minTime) + ".jpg"
    img = cv2.imread(targetFilePath, cv2.IMREAD_COLOR)

    
def dirCheck(experimentNumber, deviceNumber):
    filePathList = []

    filePathList.append('./result')
    filePathList.append('./result' + '/' + str(experimentNumber))
    filePathList.append('./result' + '/' + str(experimentNumber) + '/' + str(deviceNumber))

    for filePath in filePathList:
        if not os.path.exists(filePath):
            os.makedirs(filePath)


def makeGraph(allRPIList, goodDataTable, picturedFilePath, picturedDir, experimentNumber, deviceNumber, theNumberOfReceiver, globalId):
    for j in range(theNumberOfReceiver):
        targetRpiList = allRPIList

        dirCheck(experimentNumber, deviceNumber)

        global EXTRACTCSVFILEPATH
        EXTRACTCSVFILEPATH = picturedDir

        timeListAll = []
        rpiListAll = []
        rssiListAll = []

        toFileRPIList = []
        toFileTimeList = []
        toFileRssiList = []

        for targetRpi in allRPIList:
            newDb = goodDataTable.query("receiverId==" + str(j))
            newDb.query("rpi="+targetRpi)

            reader = goodDataTable.to_numpy().tolist()
            for row in reader:
                targetReceiverNumber = int(row[0])
                if targetReceiverNumber == j:
                    print("True")
                    timeStamp = float(row[1])
                    RPI = row[2]
                    RSSI = float(row[3])
                    timeListAll.append(timeStamp)
                    rpiListAll.append(RPI)
                    rssiListAll.append(RSSI)


            if targetRpi in targetRpiList:
                timeList = []
                signalStrengthList = []

                for i in range(len(timeListAll)):
                    timeStamp = timeListAll[i]
                    rpi = rpiListAll[i]
                    rssi = rssiListAll[i]

                    if rpi == targetRpi:
                        timeList.append(timeStamp)
                        signalStrengthList.append(rssi) 

                maxSignalStrength = max(signalStrengthList)
                maxIndex = signalStrengthList.index(maxSignalStrength)

                toFileRPIList.append(targetRpi)
                toFileTimeList.append(timeList[maxIndex])
                toFileRssiList.append(maxSignalStrength)


        with open(str(globalId) + "_peakTime.csv", "a") as f:
            for i in range(len(toFileRPIList)):
                f.write(str(j) + "," + str(toFileRPIList[i]) + "," + str(toFileTimeList[i]) + "," + str(toFileRssiList[i]) + "\n")
        f.close()


def makeGraphSimulation(allRPIList, goodDataTable, picturedFilePath, picturedDir, experimentNumber, deviceNumber, theNumberOfReceiver, globalId):
    peakTimeList = []
    for j in range(theNumberOfReceiver):
        targetRpiList = allRPIList

        global EXTRACTCSVFILEPATH
        EXTRACTCSVFILEPATH = picturedDir

        timeListAll = []
        rpiListAll = []
        rssiListAll = []

        toFileRPIList = []
        toFileTimeList = []
        toFileRssiList = []

        for targetRpi in allRPIList:
            newDb = goodDataTable.query("receiverId ==" + str(j) + "and rpi ==" + str(targetRpi))
            timeList = newDb["packetTime"].to_numpy().tolist()
            signalStrengthList = newDb["packetsignaldbm"].to_numpy().tolist()
            maxSignalStrength = max(signalStrengthList)
            maxIndex = signalStrengthList.index(maxSignalStrength)
            toFileRPIList.append(targetRpi)
            toFileTimeList.append(timeList[maxIndex])
            toFileRssiList.append(maxSignalStrength)

        for i in range(len(toFileRPIList)):
            data = []
            data.append(j)
            data.append(toFileRPIList[i])
            data.append(toFileTimeList[i])
            data.append(toFileRssiList[i])
            peakTimeList.append(data)
    
    peakTimeTable = pd.DataFrame(peakTimeList,columns = ["receiverId","rpi","time","rssi"])

    return peakTimeTable



def onclick(event):
    print("Clicked")
    print("x: " + str(event.xdata) + " y : " + str(event.ydata))

    filePath = EXTRACTCSVFILEPATH

    targetX = float(event.xdata)
    targetY = float(event.ydata)

    capturedTimeList = []

    with open(filePath + "0_timeList") as ff:
        reader = csv.reader(ff)
        for row in reader:
            capturedTimeList.append(float(row[0]))

    minDiff = 999999999999999
    minTime = 0

    for capturedTime in capturedTimeList:
        if abs(targetX - capturedTime) < minDiff:
            minDiff = abs(targetX - capturedTime)
            minTime = capturedTime
    
    print(filePath + "0_" + str(minTime) + ".jpg")
    imgCV = cv2.imread(filePath + "0_" + str(minTime) + ".jpg")
    cv2.imshow("imgWindow", imgCV)
    
global EXTRACTCSVFILEPATH



def main():

    experimentNumber = 0
    deviceNumber = 0

    globalId = int(input('globalId : '))

    dirName = "./data/" + str(experimentNumber) + "/" + str(deviceNumber) + "/"
    timeSignalStrengthFileName = str(globalId)+"_0_GoodData.csv"
    picturedFileName = str(globalId) + "_0_timeList"
    dirName = "./"
    allRPIList = makeAllRpiList(dirName + timeSignalStrengthFileName)

    theNumberOfReceiver = 2

    makeGraph(allRPIList, dirName + timeSignalStrengthFileName, dirName + picturedFileName, dirName, experimentNumber, deviceNumber, theNumberOfReceiver, globalId)


if __name__ == "__main__":
    main()