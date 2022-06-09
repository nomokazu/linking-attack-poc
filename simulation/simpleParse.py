import csv
import math
import datetime
import matplotlib.pyplot as plt
import numpy as np

class RealPerson():
    def __init__(self,personId):
        self.personId = personId
        self.rawDataList = []
    
    def getPersonId(self):
        return self.personId

    def getFirstPositionAndTime(self):
        rawData = []
        if len(self.rawDataList) > 0:
            rawData = self.rawDataList[0]
        
        firstTimeStr = rawData[3]
        try:
            firstTimeDatetime = datetime.datetime.strptime(firstTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        except:
            firstTimeDatetime = datetime.datetime.strptime(firstTimeStr, '%Y-%m-%d %H:%M:%S')

        firstTimeUnixtime = firstTimeDatetime.timestamp()
        firstPositionX = rawData[5]
        firstPositionY = rawData[6]

        return firstTimeDatetime, firstTimeUnixtime, int(firstPositionX), int(firstPositionY)

    def getLastPositionAndTime(self):
        
        rawData = []
        if len(self.rawDataList) > 0:
            rawData = self.rawDataList[-1]
        
        lastTimeStr = rawData[3]
        try:
            lastTimeDatetime = datetime.datetime.strptime(lastTimeStr, '%Y-%m-%d %H:%M:%S.%f')
        except:
            lastTimeDatetime = datetime.datetime.strptime(lastTimeStr, '%Y-%m-%d %H:%M:%S')
        lastTimeUnixtime = lastTimeDatetime.timestamp()
        lastPositionX = rawData[5]
        lastPositionY = rawData[6]

        return lastTimeDatetime, lastTimeUnixtime, int(lastPositionX), int(lastPositionY)

    def appendRawDataList(self,row):
        self.rawDataList.append(row)

    def getRawDataList(self):
        return self.rawDataList
    
    def getDirection(self):
        firstTimeDatetime, firstTimeUnixtime, firstPositionX, firstPositionY = self.getFirstPositionAndTime()
        lastTimeDatetime, lastTimeUnixtime, lastPositionX, lastPositionY = self.getLastPositionAndTime()

        if lastPositionX - firstPositionX > 0:
            return "toRight"
        else:
            return "toLeft"
    
    def calculateWalkingSpeed(self):
        speed = 0
        firstTimeDatetime, firstTimeUnixtime, firstPositionX, firstPositionY = self.getFirstPositionAndTime()
        lastTimeDatetime, lastTimeUnixtime, lastPositionX, lastPositionY = self.getLastPositionAndTime()
        absSpeed = 0
        if lastTimeUnixtime-firstTimeUnixtime == 0:
            absSpeed = 0
        else:
            absSpeed = math.sqrt(math.pow(lastPositionX - firstPositionX,2) + math.pow(lastPositionY - firstPositionY,2)) / (lastTimeUnixtime-firstTimeUnixtime)

        direction = self.getDirection()


        if direction == "toLeft":
            speed = absSpeed * (-1)
        elif direction == "toRight":
            speed = absSpeed * 1
        else:
            None
        
        speedM = speed / 1000

        return speedM

def calculateMeasureStartTime(realPersonInstanceList):
    firstTimeDatetime, firstTimeUnixtime, firstPositionX, firstPositionY = realPersonInstanceList[0].getFirstPositionAndTime()
    firstTimeDatetime = firstTimeDatetime.replace(microsecond=0)
    firstTimeDatetime = firstTimeDatetime.replace(second=0)
    startTimeDatetime = firstTimeDatetime.replace(minute=0)
    print(startTimeDatetime)

    startTimeUnixtime = startTimeDatetime.timestamp()

    return startTimeDatetime, startTimeUnixtime


def makePersonList(reader):
    personIdList = []
    for row in reader:
        personId = int(row[1])
        if not personId in personIdList:
            personIdList.append(personId)
        else:
            None
    
    return personIdList

def getTargetInstanceIndex(realPersonInstanceList, targetPersonId):
    for i,realPersonInstance in enumerate(realPersonInstanceList):
        personId = realPersonInstance.getPersonId()
        if targetPersonId == personId:
            return i
    return -1

def debug(realPersonInstanceList):
    counterProblem = 0
    counterAll = 0
    speedList = []
    allXList = []
    allYList = []
    YList = []
    startTimeDatetime, startTimeUnixtime = calculateMeasureStartTime(realPersonInstanceList)
    for realPersonInstance in realPersonInstanceList:
        rawDataList = realPersonInstance.getRawDataList()
        for rawData in rawDataList:
            print(rawData)
        print("-------------")
    
    for realPersonInstance in realPersonInstanceList:
        firstTimeDatetime, firstTimeUnixtime, firstX, firstY = realPersonInstance.getFirstPositionAndTime()
        llastTimeDatetime, lastTimeUnixtime, lastX, lastY = realPersonInstance.getLastPositionAndTime()

        print(realPersonInstance.getPersonId())
        print(str(firstTimeUnixtime - startTimeUnixtime)+ ":" + str(firstX) + ":" + str(firstY))
        print(str(lastTimeUnixtime - startTimeUnixtime)+ ":" + str(lastX) + ":" + str(lastY))
        allXList.append(firstX)
        allXList.append(lastX)
        if realPersonInstance.getDirection() == "toLeft" or realPersonInstance.getDirection() == "toRight":
            YList.append(firstY)
        allYList.append(firstY)
        allYList.append(lastY)
        print("Direction : " +str(realPersonInstance.getDirection()) )
        print("Speed     : " +str(realPersonInstance.calculateWalkingSpeed()))
        speedList.append(realPersonInstance.calculateWalkingSpeed())
        print("-------------")
        counterAll = counterAll + 1
        if firstTimeUnixtime - lastTimeUnixtime == 0:
            counterProblem = counterProblem + 1
    
    print(counterAll)
    print(counterProblem)

    print("minX : " + str(min(allXList)))
    print("minY : " + str(min(allYList)))

    print("maxX : " + str(max(allXList)))
    print("maxY : " + str(max(allYList)))

    calculateMeasureStartTime(realPersonInstanceList)

    plt.hist(speedList, bins=50)
    plt.show()

def creatRealPersonInstanceList(filePath):
    readResultList = []
    realPersonInstanceList = []
    with open(str(filePath), "r") as f:
        spamreader = csv.reader(f)
        for i,row in enumerate(spamreader):
            if i == 0:
                continue
            readResultList.append(row)
    
    personIdList = makePersonList(readResultList)

    for readResult in readResultList:
        personId = int(readResult[1])
        targetIndex = getTargetInstanceIndex(realPersonInstanceList, personId)
        if targetIndex == -1:
            newRealPerson = RealPerson(personId)
            realPersonInstanceList.append(newRealPerson)
        targetIndex = getTargetInstanceIndex(realPersonInstanceList, personId)
        if targetIndex == -1:
            print("ERROR")
        else:
            realPersonInstanceList[targetIndex].appendRawDataList(readResult)
    
    return realPersonInstanceList

def creatRealPersonInstanceListWithoutSpeed0(filePath):
    realPersonInstanceList = creatRealPersonInstanceList(filePath)

    realPersonInstanceListEliminated = []

    for realPersonInstance in realPersonInstanceList:
        lastTimeDatetime, lastTimeUnixtime, lastPositionX, lastPositionY = realPersonInstance.getLastPositionAndTime()
        firstTimeDatetime, firstTimeUnixtime, firstX, firstY = realPersonInstance.getFirstPositionAndTime()
        speed = realPersonInstance.calculateWalkingSpeed()
        if not abs(speed) <= 0.1:
            if not firstTimeUnixtime - lastTimeUnixtime == 0:
                realPersonInstanceListEliminated.append(realPersonInstance)
    
    return realPersonInstanceListEliminated

def creatRealPersonInstanceListWithoutSpeed0FromList(filePathList):
    realPersonInstanceListEliminated = []

    for filePath in filePathList:
        # 除去対象のindex番号
        realPersonInstanceList = creatRealPersonInstanceList(filePath)


        for realPersonInstance in realPersonInstanceList:
            lastTimeDatetime, lastTimeUnixtime, lastPositionX, lastPositionY = realPersonInstance.getLastPositionAndTime()
            firstTimeDatetime, firstTimeUnixtime, firstX, firstY = realPersonInstance.getFirstPositionAndTime()
            speed = realPersonInstance.calculateWalkingSpeed()
            if not abs(speed) <= 0.1:
                if not firstTimeUnixtime - lastTimeUnixtime == 0:
                    realPersonInstanceListEliminated.append(realPersonInstance)
    
    return realPersonInstanceListEliminated

def histgram(realPersonInstanceList):
    
    counterList = []
    limitList = []

    firstTimeDatetime, firstTimeUnixtime, firstPositionX, firstPositionY = realPersonInstanceList[0].getFirstPositionAndTime()
    firstTimeDatetime = firstTimeDatetime.replace(microsecond=0)
    firstTimeDatetime = firstTimeDatetime.replace(second=0)
    startTimeDatetime = firstTimeDatetime.replace(minute=0)

    lowLimit = startTimeDatetime
    highLimit = startTimeDatetime + datetime.timedelta(hours=1)

    for i in range(24):
        counterList.append(0)
        limitList.append(str(lowLimit) + " ~ " + str(highLimit))
        for realPersonInstance in realPersonInstanceList:
            lastTimeDatetime, lastTimeUnixtime, lastPositionX, lastPositionY = realPersonInstance.getLastPositionAndTime()
            firstTimeDatetime, firstTimeUnixtime, firstX, firstY = realPersonInstance.getFirstPositionAndTime()

            if lowLimit <= firstTimeDatetime and firstTimeDatetime < highLimit:
                counterList[i] += 1
        
        lowLimit = lowLimit + datetime.timedelta(hours=1)
        highLimit = lowLimit + datetime.timedelta(hours=1)
    
    for i, counter in enumerate(counterList):
        print(limitList[i] + " : " + str(counter))
    
    print("合計人数 : " + str(sum(counterList)))
    

    plt.rcParams['font.sans-serif'] = 'Helvetica'
    plt.rcParams['axes.axisbelow'] = True
    plt.rcParams["font.size"] = 36

    plt.xlabel('Time')
    plt.ylabel('The number of pedestrians')
    plt.grid()
    plt.bar(range(0,len(counterList)), counterList)
    plt.subplots_adjust(left=0.1, right=0.9, bottom=0.2, top=0.95)
    plt.show()



def main():
    print(datetime.timedelta(hours=1))

    readResultList = []
    realPersonInstanceList = []
    targetOpendatasetFilePath = "/Users/nomotokazuki/Desktop/simulation/everyone/personpositioncoord/down/data/person_location_out_0001_2021021212_2021021213.csv"
    targetOpendatasetFilePathList = []
    basePath = "/Users/nomotokazuki/Desktop/simulation/everyone/personpositioncoord/down/data/"
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021200" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021201" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021202" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021203" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021204" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021205" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021206" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021207" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021208" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021209" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021210" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021211" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021212" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021213" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021214" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021215" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021216" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021217" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021218" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021219" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021220" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021221" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021222" + ".csv")
    targetOpendatasetFilePathList.append(basePath + "person_location_out_0001_2021021223" + ".csv")
    realPersonInstanceList = creatRealPersonInstanceListWithoutSpeed0FromList(targetOpendatasetFilePathList)


    histgram(realPersonInstanceList)


if __name__ == "__main__":
    main()
