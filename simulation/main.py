import numpy as np
from numpy.lib.function_base import copy
import numpy.random as rd
import random
import math
import time
from matplotlib import pyplot as plt
import cv2
from scipy import interpolate
import csv
from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from panda3d.core import Quat, Vec3
from panda3d.core import NodePath
from panda3d.core import TextNode
import pickle
import sys
import os
from multiprocessing import Process
from direct.gui.OnscreenText import OnscreenText
from functools import lru_cache
from multiprocessing import Pool
import pprint
from ctypes import *
import joblib
import json
# Call peakDetection.py
import peakDetectionFromMax
import copy
import pandas as pd
import concatFileFromDate
import simpleParse
import shutil


global imageSettingList
imageSettingList = []

# Receiver Class
class Receiver:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.id = 0

        # Antenna Direction
        self.receiveDirection = 0

        self.peopleArriveTimeDict = {}

    def setPosition(self, x, y):
        self.x = x
        self.y = y
    
    def getPosition(self):
        return self.x,self.y
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def setId(self, id):
        self.id = id
    
    def getId(self):
        return self.id
    
    def getReceiveDirection(self):
        return self.receiveDirection

    def setReceiveDirection(self, direction):
        self.receiveDirection = direction
    
    def setPeopleArriveTimeDict(self, peopleId, arriveTime):
        self.peopleArriveTimeDict[peopleId] = arriveTime
    
    def getPeopleArriveTimeDict(self):
        return self.peopleArriveTimeDict
    
    def getPeopleArriveTimeFromPersonId(self, personId):
        if personId in self.peopleArriveTimeDict:
            return self.peopleArriveTimeDict[personId]
        else:
            return - 2

    def getPeopleIdListFromTime(self, targetTime, experimentType):
        peopleIdList = []

        term = 0
        if experimentType == 2:
            term = 120
        else:
            term = 20

        peopleArriveTimeDict = self.getPeopleArriveTimeDict()

        for k, v in peopleArriveTimeDict.items():
            if abs(targetTime - v) < term:
                peopleIdList.append(k)
        
        return peopleIdList
        
# People Class
class People:
    def __init__(self):
        self.initialPositionX = 0
        self.initialPositionY = 0
        self.x = 0
        self.y = 0
        self.v = 0
        self.movingVector = 0
        self.rpi = 0
        self.id = 0
        # Time when RPI is sent for the first time
        self.firstRpiSendTime = 0
        self.tPeriod = 0
        self.tInterval = 0
        self.rpiSendGain = 0
        self.rpiSendFrequency = 0
        self.occurTime = 0
        # List to store linking results
        self.linkedResultList = []
        self.finalLinkedResultList = []
        self.gapTime = 0
        self.groupNumber = 0
        self.signalStrengthDict = {}
        self.oneTimeA = 0
        self.oneTimeB = 0
        self.reSend = 0
        self.senderType = ""
    
    def setReSend(self,reSend):
        self.reSend = reSend
    
    def getReSend(self):
        return self.reSend
    
    def setSignalStrength(self, receiverId, targetTimePinpoint, signalStrength):
        keyTuple = (receiverId,targetTimePinpoint)
        self.signalStrengthDict[keyTuple] = signalStrength
    
    def getSignalStrength(self, receiverId, targetTimePinpoint):
        keyTuple = (receiverId,targetTimePinpoint)
        signalStrength = self.signalStrengthDict.get(keyTuple)

        return signalStrength

    def getOccurTime(self):
        return self.occurTime
    
    def setOccurTime(self,occurTime):
        self.occurTime = occurTime
    
    def getId(self):
        return self.id
    
    def setId(self, myId):
        self.id = myId

    def getRpi(self):
        return self.rpi

    def setRpi(self, rpi):
        self.rpi = rpi
    
    def getInitialPositionX(self):
        return self.initialPositionX
    
    def getInitialPositionY(self):
        return self.initialPositionY
    
    def setInitialPositionX(self, x):
        self.initialPositionX = x
    
    def setInitialPositionY(self, y):
        self.initialPositionY = y
    
    def setInitialPosition(self, x, y):
        self.initialPositionX = x
        self.initialPositionY = y
    
    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self,x):
        self.x = x

    def setY(self, y):
        self.y = y

    def getV(self):
        return self.v

    def setV(self, v):
        self.v = v

    def getSenderType(self):
            return self.senderType
    
    def setSenderType(self, senderType):
        self.senderType = senderType
    
    def setSenderTypeRandom(self,senderTypeList):
        self.senderType = random.choice(senderTypeList)

    def setFirstRpiSendTime(self, firstRpiSendTime):
        self.firstRpiSendTime = firstRpiSendTime
    
    def getFirstRpiSendTime(self):
        return self.firstRpiSendTime

    def setTPeriod(self, tPeriod):
        self.tPeriod = tPeriod
    
    def getTPeriod(self):
        return self.tPeriod
    
    def setTInterval(self, tInterval):
        self.tInterval = tInterval
    
    def getTInterval(self):
        return self.tInterval
    
    def getRpiSendGain(self):
        return self.rpiSendGain
    
    def setRpiSendGain(self, rpiSendGain):
        self.rpiSendGain = rpiSendGain
    
    def getRpiSendFrequency(self):
        return self.rpiSendFrequency
    
    def setRpiSendFrequency(self, rpiSendFrequency):
        self.rpiSendFrequency = rpiSendFrequency
    
    def setMovingVector(self, movingVector):
        self.movingVector = movingVector
    
    def getMovingVector(self):
        return self.movingVector

    def positionToTime(self, targetPositionX, targetPositionY,receiveDirection):
        resultDiffTime = 0

        if receiveDirection == math.pi / 2 * 1:
            resultDiffTimeX = (targetPositionX - self.getInitialPositionX()) / (self.getV() * math.cos(self.getMovingVector()))
            x, y = self.timeToPositionFromTimeDiff(resultDiffTimeX)
            if round(x,1) == targetPositionX and round(y,1) >= targetPositionY:
                resultDiffTime = resultDiffTimeX
            else:
                print("error")
                input("")
                return -1
        else:
            # Difference between the y-coordinate of the receiver and the single line along which the pedestrian walks
            p = self.getInitialPositionY() - targetPositionY

            # Angle at which the receiver is facing
            theta = receiveDirection

            # Misalignment in x-axis direction
            q = p / math.tan(theta)

            targetPositionX = targetPositionX + q

            resultDiffTimeX = (targetPositionX - self.getInitialPositionX()) / (self.getV() * math.cos(self.getMovingVector()))
            x, y = self.timeToPositionFromTimeDiff(resultDiffTimeX)

            if round(x,1) == round(targetPositionX,1) and round(y,1) >= targetPositionY:
                resultDiffTime = resultDiffTimeX

            else:
                print("error")
                input("")
                return -1

        return (resultDiffTime + self.getOccurTime())

    def timeToPositionFromTimeDiff(self, targetDiff):
        initialPositionX = self.getInitialPositionX()
        initialPositionY = self.getInitialPositionY()

        x = initialPositionX + self.getV() * math.cos(self.getMovingVector()) * targetDiff
        y = initialPositionY + self.getV() * math.sin(self.getMovingVector()) * targetDiff

        return x,y

    def timeToPositionTargetTime(self, targetTime):
        diffTime = targetTime - self.getOccurTime()
        x,y  = self.timeToPositionFromTimeDiff(diffTime)
        
        return x, y
    
    # Function to calculate when RPI is sent
    def getRPISendTimeAll(self):
        # Time of first RPI transmission
        tFirst = self.getFirstRpiSendTime()

        oneTerm = 60 + self.getTInterval()
        
        # List of times when RPIs are sent from the first time of one term
        sendTimeInOneTermList = []

        for i in range(10000000):
            sendTimeInOneTerm = self.getRpiSendFrequency() * i
            if sendTimeInOneTerm > self.getTPeriod():
                break
            sendTimeInOneTermList.append(sendTimeInOneTerm)            

        sendTimeList = []

        for i in range(10):
            tStart = tFirst + i * oneTerm
            for sendTimeInOneTerm in sendTimeInOneTermList:
                sendTimeList.append(tStart + sendTimeInOneTerm)
        
        return sendTimeList
    
    def getRPISendTimeFromTargetTime(self, targetTime):
        adjustedTargetTime = targetTime - self.getFirstRpiSendTime()

        oneTerm = 60 + self.getTInterval()

        term = int(round(adjustedTargetTime / oneTerm))
        termPlus = adjustedTargetTime % oneTerm

        sendTimeInOneTermList = []

        for i in range(10000000):
            sendTimeInOneTerm = self.getRpiSendFrequency() * i
            if sendTimeInOneTerm >= self.getTPeriod():
                break
            sendTimeInOneTermList.append(sendTimeInOneTerm)
        
        sendTimeList = []
        for targetCount in range(term - 1, term + 1):
            tStart = self.getFirstRpiSendTime() + targetCount * oneTerm
            for sendTimeInOneTerm in sendTimeInOneTermList:
                sendTimeList.append(tStart + sendTimeInOneTerm)
            
        sendTimeListWithReSend = []
        reSendTime = 0.1
        if self.getReSend() > 0 and self.getRpiSendFrequency() != 0.27:
            reSendCounter = self.getReSend()
            for sendTime in sendTimeList:
                sendTimeListWithReSend.append(sendTime)
                for i in range(reSendCounter):
                    sendTimeListWithReSend.append(sendTime + reSendTime * (i+1))
            return sendTimeListWithReSend
        else:
            return sendTimeList

    def setLinkedResultList(self, linkedResult):
        self.linkedResultList.append(linkedResult)
    
    def replaceLinkedResultList(self, linkedResult):
        self.linkedResultList = linkedResult

    def getLinkedResultList(self):
        return self.linkedResultList
    
    def setGapTime(self,gapTime):
        self.gapTime = gapTime
    
    def getGapTime(self):
        return self.gapTime

    def getFinalLinkedResultList(self):
        return self.finalLinkedResultList
    
    def setFinalLinkedResultList(self,finalLinkeResultList):
        self.finalLinkedResultList = finalLinkeResultList
    
    def combineResult(self):
        resultList = []

        linkedResultList = self.getLinkedResultList()


        pprint.pprint(linkedResultList)
        resultItemList = list(set(linkedResultList))
        resultCounterList = []

        for resultItem in resultItemList:
            count = linkedResultList.count(resultItem)
            resultCounterList.append(count)
        
        print("Before MAX ")
        print(resultCounterList)

        if len(resultCounterList) > 0:
            maxCount = max(resultCounterList)
        else:
            maxCount = -1


        for i,resultItem in enumerate(resultItemList):
            if resultCounterList[i] == maxCount:
                resultList.append(resultItem)
        
        self.setFinalLinkedResultList(resultList)
    
    def removeFinalLinkedResultList(self,targetRpi):
        self.finalLinkedResultList.remove(targetRpi)
    
    def getGroupNumber(self):
        return self.groupNumber
    
    def setGroupNubmer(self, groupNumber):
        self.groupNumber = groupNumber

class imagePerson():
    def __init__(self):
        self.myId = 0
        self.positionX = 0
        self.positionY = 0
        self.v = 0
    
    def getId(self):
        return self.myId
    
    def setId(self, myId):
        self.myId = myId
    
    def getPosition(self):
        return self.positionX, self.positionY
    
    def setPosition(self, positionX, positionY):
        self.positionX = positionX
        self.positionY = positionY

    def getPositionX(self):
        return self.positionX
    
    def getPositionY(self):
        return self.positionY
    
    def setPositionX(self, positionX):
        self.positionX = positionX
    
    def setPositionY(self, positionY):
        self.positionY = positionY
    
    def setV(self, v):
        self.v = v
    
    def getV(self):
        return self.v


class OneImage():
    def __init__(self):
        self.peopleList = []
        self.targetId = -1
        self.capturedTime = -1

    def appendPeopleList(self, people):
        self.peopleList.append(people)
    
    def getPeopleList(self):
        return self.peopleList

    def getCapturedTime(self):
        return self.capturedTime
    
    def setCapturedTime(self, capturedTime):
        self.capturedTime = capturedTime
    
    def setTargetId(self, targetId):
        self.targetId = targetId
    
    def getTargetId(self):
        return self.targetId

class MyApp(ShowBase):    
    def __init__(self,receiverDirection):
        ShowBase.__init__(self)
        self.experimentNumber = 0
        self.receiverDirection = receiverDirection

        self.scene = self.loader.loadModel("./model/panda3d/samples/carousel/models/env")
        self.scene.reparentTo(self.render)
        self.scene.setScale(20)
        self.scene.setPos(0,0, 0)

        self.drawPeople = []
        self.drawMojiList = []
        base.cam.setPos(0, 0, 0.4)
        if receiverDirection == math.pi / 2:
            base.cam.setHpr( 0, 0, 0 )
        elif receiverDirection == math.pi*3 / 4:
            base.cam.setHpr( 45, 0, 0 )
        elif receiverDirection == math.pi / 4:
            base.cam.setHpr( 360-45, 0, 0 )
        base.camLens.setFov(90, 50)
        base.cam.setP(18)

        self.textObject = OnscreenText(text='Start', pos=(-0.5, -2), scale=0.2)


        base.movie(namePrefix='fileName', duration=10000, fps=1, format='png')
        self.taskMgr.add(self.moveTask, "moveTask")

        self.i = 1
    
    def moveTask(self, task):
        counter = task.frame
        print(counter)
        global imageSettingList
        self.textList = []

        if self.i >= len(imageSettingList):
            sys.exit(1)
            return Task.done

        imageSetting = imageSettingList[self.i]

        peopleList = imageSetting.getPeopleList()
        targetId = imageSetting.getTargetId()

        text3dList = []

        for i,person in enumerate(peopleList):
            x, y = person.getPosition()
            drawPerson = self.loader.loadModel("./model/MyHuman/with_cloth.dae")
            drawPerson.reparentTo(self.render)
            drawPerson.setScale(0.6,0.6,1)
            drawPerson.setPos(100, 100, 0)
            quat = None
            print(person.getV())
            if person.getV() > 0:
                quat = Quat( 1, 1, 1, 1 )
            else:
                quat = Quat( -1, -1, 1, 1 )
            drawPerson.setQuat(quat)
            drawPerson.setPos(x, y, 0)
            
            t=str(" " + str(person.getId()))
            text= TextNode('text')
            text.setText(t)
            text.setTextColor(1, 0.8, 0, 1)

            text3d = NodePath(text)
            text3d.reparentTo(drawPerson)
            text3d.setScale(0.3,0.3,0.3)
            if person.getV() > 0:
                text3d.setPos(-0.5,1,0)
                text3d.setHpr(-90,0,-90)
            else:
                if self.receiverDirection == math.pi / 2:
                    text3d.setPos(-0.2,1.0,0.6)
                else:
                    text3d.setPos(0.2,1.0,0.6)
                text3d.setHpr(-90,-180,-90)                
            text3d.setTwoSided(True)
            

            self.drawPeople.append(drawPerson)

        self.textObject.destroy()
        self.textObject = OnscreenText(text='TargetID = ' + str(targetId), pos=(-0.5, 0.8), scale=0.1)

        with open("./" + str(self.experimentNumber) + "/" + "correspoTable.csv", "a") as f:
            f.write(str(targetId) + "," + str(self.i) + "\n")
            f.close()
        

        if counter % 2 ==0:
            for a in self.drawPeople:
                a.setPos(-100,-100,0)
        else:
            self.i = self.i + 1

        return Task.cont

def generateGroupLamList(perTime, groupRatioList):
    groupLamList = []

    for i,groupRatio in enumerate(groupRatioList):
        if not groupRatio == groupRatioList[0]:
            perTimeRatio = ( perTime * ( groupRatio / 100 ) ) / ( i + 1 )
            theLam = perTimeRatio / 3600
            groupLamList.append(theLam)

    return groupLamList



# Function to modify the ratio of groups according to the ratio of the number of people in each group.
# Example.)
# groupRation = [8,6,2]
# normalizedGroupRation = [8/1, 6/2, 2/3]

def reviseGroupRationList(groupRationList):
    groupRationListRevised = []

    for i,groupRation in enumerate(groupRationList):
        theNumberOfBatch = i + 1
        groupRationListRevised.append(groupRation / theNumberOfBatch)
    
    pprint.pprint(groupRationListRevised)

    return groupRationListRevised

def revisePerTime(perTime, groupRationList):
    revisedGroupRationList = reviseGroupRationList(groupRationList)

    normalizedGroupRatioList = normalizeGroupRatioList(revisedGroupRationList)

    sumNumber = 0
    for i,normalizedGroupRatio in enumerate(normalizedGroupRatioList):
        theNumberOfPeole = i + 1
        sumNumber = sumNumber + normalizedGroupRatio * theNumberOfPeole
    
    return perTime / sumNumber

def normalizeGroupRatioList(groupRationListRevised):
    sumOfGroupRation = sum(groupRationListRevised)

    normalizedGroupRatioList = []
    for groupRation in groupRationListRevised:
        normalizedGroupRatioList.append(groupRation / sumOfGroupRation)
    
    return normalizedGroupRatioList



def generateOccurTimeList(lam, simulationPeriodTime, groupRationList):
    n = int(2 * simulationPeriodTime * lam)
    diffList = rd.exponential(1./lam, size=n)

    timeList = []
    occurTime = 0

    groupRationListRevised = reviseGroupRationList(groupRationList)

    normalizedGroupRatioList = normalizeGroupRatioList(groupRationListRevised)

    for x in diffList:
        occurTime = occurTime + x
        # Until the time of occurrence exceeds the simulation time
        if occurTime > simulationPeriodTime:
            break

        randomNumber = random.random()
        sumRandom = 0

        for i,normalizedGroupRatio in enumerate(normalizedGroupRatioList):
            theNumberOfBatch = i + 1

            if randomNumber > sumRandom:
                timeList.append(occurTime)

            sumRandom = sumRandom + normalizedGroupRatio

    return timeList

def makeBlankTime(simulationPeriodTime, baseReceiverSettings):
    maxDistance = 0
    baseReceiverSettings[-1][0]

    return simulationPeriodTime + baseReceiverSettings[-1][0] / 1
        
def generateGroupIdListNew(peopleOccurTimeList):
    groupIdList = []
    personId = -1

    uniqueOccurTimeList = list(set(peopleOccurTimeList))

    for uniqueOccurTime in uniqueOccurTimeList:
        batchSize = peopleOccurTimeList.count(uniqueOccurTime)

         # If we formed a group
        if batchSize > 1:
            groupId = searchKeyAll(peopleOccurTimeList,uniqueOccurTime)
            groupIdList.append(groupId)

    return groupIdList

def searchKeyAll(targetList,targetKey):
    result = []
    for i,target in enumerate(targetList):
        if target == targetKey:
            result.append(i)
    
    return result

def generateGroupOccurTimeListList(groupLamList, simulationPeriodTime):
    groupOccurTimeListList = []

    for groupLam in groupLamList:
        groupOccurTimeList = []
        groupOccurTimeList = generateOccurTimeList(groupLam, simulationPeriodTime)

        print(groupOccurTimeList)
        print(groupLam)

        groupOccurTimeListList.append(groupOccurTimeList)
    
    return groupOccurTimeListList


def appendGroup(peopleOccurTimeList, groupOccurTimeListList):
    removalTimeList = []
    appendedTimeListList = []
    for groupNumber,groupOccurTimeList in enumerate(groupOccurTimeListList):
        appendedTimeList = []
        for groupOccurTime in groupOccurTimeList:
            targetOccurTime, targetIndex = searchNearestFromList(groupOccurTime, peopleOccurTimeList, removalTimeList)
            removalTimeList.append(targetOccurTime)
            appendedTimeList.append(targetOccurTime)
            for i in range(groupNumber+1):
                peopleOccurTimeList.insert(targetIndex, targetOccurTime)
        appendedTimeListList.append(appendedTimeList)
    
    return peopleOccurTimeList, appendedTimeListList

def searchIndexItemInList(targetItem, targetList):
    result = []
    for i, target in enumerate(targetList):
        if target == targetItem:
            result.append(i)
    
    return result

def generateGroupIdList(peopleOccurTimeList, groupRealOccurTimeListList):
    groupdIdListList = []
    for i,groupRealOccurTimeList in enumerate(groupRealOccurTimeListList):
        theNumberOfGroup = i + 2

        for groupRealOccurTime in groupRealOccurTimeList:
            groupIdList = searchIndexItemInList(groupRealOccurTime, peopleOccurTimeList)
            groupdIdListList.append(groupIdList)
    
    return groupdIdListList


def searchNearestFromList(targetTime, timeList, removalTargetTimeList):
    diff = 100000000000
    resultTime = 0
    thisDiff = 100000000000000
    targetIndex = -1


    for i,aTime in enumerate(timeList):
        if not aTime in removalTargetTimeList:
            if abs(targetTime - aTime) > thisDiff:
                break
            else:
                thisDiff = abs(targetTime - aTime)
                if thisDiff < diff:
                    resultTime = aTime
                    diff = thisDiff
                    targetIndex = i

    return resultTime, targetIndex


# Create a list of pedestrian walking speeds
def allPed(count, peopleOccurTimeList):
    mean = 78.09
    sd = 13.17
    walkingSpeedListPerMinute = np.random.normal(loc=mean, scale=sd, size=(count))
    print(count)
    print(len(walkingSpeedListPerMinute))

    # Converting to Seconds.
    walkingSpeedListPerSecond = []

    for walkingSpeed in walkingSpeedListPerMinute:
        walkingSpeedListPerSecond.append(float(walkingSpeed / 60))
    
    walkingSpeedIndex = -1

    resultWalkingSpeedList = []
    lastOccurTime = -1

    for peopleOccurTime in peopleOccurTimeList:
        if not lastOccurTime == peopleOccurTime:
            walkingSpeedIndex = walkingSpeedIndex + 1
            print(walkingSpeedIndex)
            resultWalkingSpeedList.append(walkingSpeedListPerSecond[walkingSpeedIndex])
            lastOccurTime = peopleOccurTime
        else:
            resultWalkingSpeedList.append(walkingSpeedListPerSecond[walkingSpeedIndex])

    return resultWalkingSpeedList


def allPedNoGroupDoubleSide(count, peopleOccurTimeList):
    mean = 78.09
    sd = 13.17
    walkingSpeedListPerMinute = np.random.normal(loc=mean, scale=sd, size=(count))
    print(count)
    print(len(walkingSpeedListPerMinute))

    # Converting to Seconds.
    walkingSpeedListPerSecond = []

    for walkingSpeed in walkingSpeedListPerMinute:
        walkingSpeedListPerSecond.append(float(walkingSpeed / 60))
    
    walkingSpeedIndex = -1

    resultWalkingSpeedList = []
    lastOccurTime = -1

    for peopleOccurTime in peopleOccurTimeList:
        if not lastOccurTime == peopleOccurTime:
            walkingSpeedIndex = walkingSpeedIndex + 1
            print(walkingSpeedIndex)
            resultWalkingSpeedList.append(walkingSpeedListPerSecond[walkingSpeedIndex])
            lastOccurTime = peopleOccurTime
        else:
            resultWalkingSpeedList.append(walkingSpeedListPerSecond[walkingSpeedIndex])
    
    for i in range(len(peopleOccurTimeList)):
        if i % 2 == 0:
            resultWalkingSpeedList[i] = resultWalkingSpeedList[i]
        else:
            resultWalkingSpeedList[i] = resultWalkingSpeedList[i] * (-1)


    return resultWalkingSpeedList

def allPedGroupDoubleSide(count, peopleOccurTimeList):

    mean = 78.09
    sd = 13.17
    walkingSpeedListPerMinute = np.random.normal(loc=mean, scale=sd, size=(count))
    print(count)
    print(len(walkingSpeedListPerMinute))

    # Converting to Seconds.
    walkingSpeedListPerSecond = []

    for walkingSpeed in walkingSpeedListPerMinute:
        walkingSpeedListPerSecond.append(float(walkingSpeed / 60))
    
    walkingSpeedIndex = -1

    resultWalkingSpeedList = []
    lastOccurTime = -1

        
    for i in range(len(walkingSpeedListPerSecond)):
        if i % 2 == 0:
            walkingSpeedListPerSecond[i] = walkingSpeedListPerSecond[i]
        else:
            walkingSpeedListPerSecond[i] = walkingSpeedListPerSecond[i] * (-1)

    for peopleOccurTime in peopleOccurTimeList:
        if not lastOccurTime == peopleOccurTime:
            walkingSpeedIndex = walkingSpeedIndex + 1
            print(walkingSpeedIndex)
            resultWalkingSpeedList.append(walkingSpeedListPerSecond[walkingSpeedIndex])
            lastOccurTime = peopleOccurTime
        else:
            resultWalkingSpeedList.append(walkingSpeedListPerSecond[walkingSpeedIndex])

    return resultWalkingSpeedList


def searchTheNumberOfGroupFromPeopleOccurTime(peopleOccurTime, groupRealOccurTimeListList):
    theNumberOfGroup = -1

    for i, groupRealOccurTimeList in enumerate(groupRealOccurTimeListList):
        if peopleOccurTime in groupRealOccurTimeList:
            theNumberOfGroup = i + 2
            break

    return theNumberOfGroup


def makeRandomListForFirstRpiSendTimeList(theNumberOfPeople):
    resultList = []

    for i in range(theNumberOfPeople):
        resultList.append(random.random())
    
    return resultList

# Make people list
def makingPeopleList(theNumberOfPeople, peopleOccurTimeList, walkingSpeedOfPeopleList, tPeriodList, rpiSendGainList, rpiSendFrequencyList, tIntervalList, gapTimeList, randomListForFirstRpiSendTimeList, initialPositionList, reSend, senderTypeList):
    peopleList = []
    for i in range(theNumberOfPeople):
        initialPositionX =  initialPositionList[i][0]
        initialPositionY =  initialPositionList[i][1]
        people = People()
        people.setOccurTime(peopleOccurTimeList[i])
        people.setId(i)
        people.setRpi(i)
        people.setInitialPosition(initialPositionX, initialPositionY)
        people.setV(walkingSpeedOfPeopleList[i])
        people.setGapTime(gapTimeList[i])
        occurTime = people.getOccurTime()
        sendTime = occurTime + randomListForFirstRpiSendTimeList[i] * rpiSendFrequencyList[i]
        people.setFirstRpiSendTime(sendTime)
        # Set of transmission times per 60 seconds of RPI
        people.setTPeriod(tPeriodList[i])
        # Time of interval between the end of a 60-second transmission of RPI and the next transmission
        people.setTInterval(tIntervalList[i])
        # Setting the transmit gain for RPI transmission
        people.setRpiSendGain(rpiSendGainList[i])
        # RPI transmission frequency setting
        people.setRpiSendFrequency(rpiSendFrequencyList[i])
        people.setReSend(reSend)
        people.setSenderTypeRandom(senderTypeList)
        with open("sender.csv","a",encoding="utf-8") as f:
            f.write(str(i) + "," + str(people.getSenderType() + ",\n"))
        peopleList.append(people)
    
    return peopleList

# Function to generate a list of signal transmission strengths
def generateRpiSendGainList(theNumberOfPeople, rpiSendGain):
    rpiSendGainList = []
    for i in range(theNumberOfPeople):
        rpiSendGainList.append(rpiSendGain)
    return rpiSendGainList


# Function to generate a list of signal transmission cycles [s].
def generateRpiSendFrequencyList(theNumberOfPeople, rpiSendFrequency):
    rpiSendFrequencyList = []
    for i in range(theNumberOfPeople):
        # rpiSendFrequency = 0.3
        rpiSendFrequencyList.append(rpiSendFrequency)
    return rpiSendFrequencyList

# Make lists of receivers
def generateReceiverList(receiverSettings):
    receiverList = []

    for i,receiverSetting in enumerate(receiverSettings):
        x = receiverSetting[0]
        y = receiverSetting[1]
        direction = receiverSetting[2]
        receiver = Receiver()
        receiver.setPosition(x, y)
        receiver.setId(i)
        receiver.setReceiveDirection(direction)
        receiverList.append(receiver)
    
    return receiverList

def generateTIntervalList(theNumberOfPeople,tInterval):
    tIntervalList = []
    
    for i in range(theNumberOfPeople):
        tIntervalList.append(tInterval)
    
    return tIntervalList

def generateTPeriodList(theNumberOfPeople, tPeriod):
    tPeriodList = []

    for i in range(theNumberOfPeople):
        tPeriodList.append(tPeriod)

    return tPeriodList

def calculateInitialPositionYFromReceiverAndWidthOfRoad(receiver, margin, widthOfRoad):
    receiverPositionX, receiverPositionY = receiver.getPosition()
    positionY = random.uniform(receiverPositionY + margin, receiverPositionY + margin + widthOfRoad)

    return positionY


def makeInitialPositionList(peopleOccurTimeList, overlapIsNecessary, receiverList, margin, widthOfRoad):
    mean = widthOfRoad / 2
    sd = widthOfRoad / 2 / 2
    initialPositionYListRaw = np.random.normal(loc=mean, scale=sd, size=(len(peopleOccurTimeList)))

    initialPositionYList = []
    # After correction over the width of the road
    for initialPositionYRaw in initialPositionYListRaw:
        res = initialPositionYRaw
        if initialPositionYRaw < 0:
            res = 0
        elif initialPositionYRaw > widthOfRoad:
            res = widthOfRoad
        initialPositionYList.append(res)

    initialPositionList = []
    lastOccurTime = -1
    lastInitialPositionList = [0,100]
    counter = 0
    groupYMinPosition = 100
    for peopleOccurTime in peopleOccurTimeList:
        x = -1
        y = -1
        if lastOccurTime == peopleOccurTime:
            x = 0
            y = lastInitialPositionList[1] + 0.5
            if groupReverseFlag == 1:
                y = groupYMinPosition - 0.5
            elif y > margin + widthOfRoad:
                y = groupYMinPosition - 0.5
                groupReverseFlag = 1
                

            lastInitialPositionList = [x,y]
            lastOccurTime = peopleOccurTime
            groupYMinPosition = min(groupYMinPosition,y)
        else:
            if overlapIsNecessary == 0:
                x = 0
                y = 100
            else:
                x = 0
                y = margin + initialPositionYList[counter]
            lastInitialPositionList = [x,y]
            lastOccurTime = peopleOccurTime
            groupYMinPosition = y
            groupReverseFlag = 0
        
        counter = counter + 1
        initialPositionList.append([x,y])
    
    return initialPositionList

def makeInitialPositionListNoGroupDoubleSide(peopleOccurTimeList,baseReceiverSettings,walkingSpeedOfPeopleList, overlapIsNecessary, receiverList, margin, widthOfRoad):

    mean = widthOfRoad / 2
    sd = widthOfRoad / 2 / 2
    initialPositionYListRaw = np.random.normal(loc=mean, scale=sd, size=(len(peopleOccurTimeList)))

    initialPositionYList = []
    for initialPositionYRaw in initialPositionYListRaw:
        res = initialPositionYRaw
        if initialPositionYRaw < 0:
            res = 0
        elif initialPositionYRaw > widthOfRoad:
            res = widthOfRoad
        initialPositionYList.append(res)


    maxDistance = baseReceiverSettings[-1][0]

    makeInitialPositionList = []
    defaultX = 0
    defaultY = 100

    defalutRightX = maxDistance + 100
    defalutRightY = 100

    if overlapIsNecessary == 0:
        defaultY = 100
    else:
        defaultY = margin
        defalutRightY = margin 

    counter = 0
    for i in range(len(peopleOccurTimeList)):
        if i % 2 == 0:
            if walkingSpeedOfPeopleList[i] < 0:
                print("ERROR")
                time.sleep(1999)
            makeInitialPositionList.append([defaultX, defaultY + initialPositionYList[counter]])
        else:
            if walkingSpeedOfPeopleList[i] > 0:
                print("ERROR")
                time.sleep(1999)
            makeInitialPositionList.append([defalutRightX, defalutRightY + initialPositionYList[counter]])
        counter = counter + 1
    
    return makeInitialPositionList

def makeInitialPositionListGroupDoubleSide(peopleOccurTimeList,baseReceiverSettings,walkingSpeedOfPeopleList, overlapIsNecessary, receiverList, margin, widthOfRoad):

    mean = widthOfRoad / 2
    sd = widthOfRoad / 2 / 2
    initialPositionYListRaw = np.random.normal(loc=mean, scale=sd, size=(len(peopleOccurTimeList)))

    initialPositionYList = []

    maxDistance = baseReceiverSettings[-1][0]

    defaultX = 0
    defaultY = 100

    defalutRightX = maxDistance + 100
    defalutRightY = 100


    # After correction over the width of the road
    for initialPositionYRaw in initialPositionYListRaw:
        res = initialPositionYRaw
        if initialPositionYRaw < 0:
            res = 0
        elif initialPositionYRaw > widthOfRoad:
            res = widthOfRoad
        initialPositionYList.append(res)

    initialPositionList = []
    lastOccurTime = -1
    lastInitialPositionList = [0,100]
    counter = 0
    groupYMinPosition = 100
    for i,peopleOccurTime in enumerate(peopleOccurTimeList):
        x = -1
        y = -1
        if lastOccurTime == peopleOccurTime:
            if walkingSpeedOfPeopleList[i] >= 0:
                x = defaultX
            else:
                x = defalutRightX
            y = lastInitialPositionList[1] + 0.5
            if groupReverseFlag == 1:
                y = groupYMinPosition - 0.5
            elif y > margin + widthOfRoad:
                y = groupYMinPosition - 0.5
                groupReverseFlag = 1
                

            lastInitialPositionList = [x,y]
            lastOccurTime = peopleOccurTime
            groupYMinPosition = min(groupYMinPosition,y)
        else:
            if overlapIsNecessary == 0:
                if walkingSpeedOfPeopleList[i] >= 0:
                    x = defaultX
                else:
                    x = defalutRightX
                y = 100
            else:
                if walkingSpeedOfPeopleList[i] >= 0:
                    x = defaultX
                else:
                    x = defalutRightX
                y = margin + initialPositionYList[counter]
            lastInitialPositionList = [x,y]
            lastOccurTime = peopleOccurTime
            groupYMinPosition = y
            groupReverseFlag = 0
        
        counter = counter + 1
        initialPositionList.append([x,y])
    
    return initialPositionList



# Record the time each person arrives at each receiver.
def recordTime(peopleList, receiverList):
    for receiver in receiverList:
        receiverPositionX = receiver.getX()
        receiverPositionY = receiver.getY()
        receiveDirection = receiver.getReceiveDirection()
        for person in peopleList:
            personId = person.getId()
            occurTime = person.getOccurTime()
            v = person.getV()
            arriveTime = person.positionToTime(receiverPositionX, receiverPositionY, receiveDirection)
            receiver.setPeopleArriveTimeDict(personId, arriveTime)

def decideTheNumberOfPeople(theNumberOfPeople):
    resultN = 0
    for i in range(1000):
        resultN = resultN + 100
        if resultN >= theNumberOfPeople:
            break
    
    return resultN

def extractGapTimeList(theNumberOfPeople, experimentNumber):
    strTheNumberOfPeople = str(decideTheNumberOfPeople(theNumberOfPeople))

    fileName = "data" + strTheNumberOfPeople + ".csv"
    filePath = "." + "/ " + str(experimentNumber) + "/peopleTimeDiff/" + fileName

    gapTimeList = []
    with open(filePath) as f:
        reader = csv.reader(f)
        for row in reader:
            gapTimeList.append(0)
    
    return gapTimeList

def calculateGapTimeList(theNumberOfPeople):
    mean = 0.1622
    sd = 0.1314
    count = theNumberOfPeople
    gapTimeList = list(np.random.normal(loc=mean, scale=sd, size=(count)))

    return gapTimeList

def calculateDummySignalStrength(n):
    resultList = []

    for i in range(n):
        resultList.append(10)
    
    return resultList

def drawGraph(peopleList, receiverList, globalId, randSeed, Gr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary):
    longFlag = False
    if experimentType == 2:
        longFlag = True

    if graphFlag == 1:
        plt.rcParams['font.sans-serif'] = 'Helvetica'
        plt.rcParams["font.size"] = 30
        os.mkdir("./" + str(experimentNumber) + "/myPickle/")

    np.random.seed(seed=randSeed)

    goodDataList= []
    goodDataTable = None

    for receiver in receiverList:
        receiverId = receiver.getId()
        toFilePacketTimeList = []
        toFileRPIList = []
        toFileSignalStrengthList = []
        toFilePeopleCenterTimeList = []
        toFilePeopleIdList = []

        for person in peopleList:
            fig = None
            ax = None
            if graphFlag == 1:
                fig, ax = plt.subplots()
                ax.set_xlabel('Time : t [s]', fontsize=40)
                ax.set_ylabel('RSSI [dBm]', fontsize=40)
                ax.grid()
                ax.get_xaxis().get_major_formatter().set_useOffset(False)

            
            # When focusing on a specific person, the time at which that person passes in front of the receiver
            arriveTime = receiver.getPeopleArriveTimeFromPersonId(person.getId())

            toFilePeopleIdList.append(person.getId())
            toFilePeopleCenterTimeList.append(arriveTime)


            # For that time, I want to get a list of people who pass by at a similar time
            nearPeopleIdList = receiver.getPeopleIdListFromTime(arriveTime, experimentType)
            nearPeopleList = getPeoleListFromPeopleIdList(peopleList, nearPeopleIdList)

            for nearPeople in nearPeopleList:

                # The process of writing out to memory is bumped up here.
                if person.getId() == nearPeople.getId():
                    print(str(person.getId()) + "/" + str(len(peopleList)))
                    rpiSendTimeList = nearPeople.getRPISendTimeFromTargetTime(arriveTime)
                    filteredRpiSendTimeList = filterRpiSendTimeList(rpiSendTimeList, arriveTime, longFlag)
                    signalStrengthList = calculateSignalStrength(nearPeople, receiver, filteredRpiSendTimeList, Gr, antennaType, experimentType, nearPeopleList, overlapIsNecessary)

                    # Additional time offset
                    for i in range(len(filteredRpiSendTimeList)):
                        gapTime = nearPeople.getGapTime()
                        filteredRpiSendTimeList[i] = filteredRpiSendTimeList[i] + gapTime

                    toFilePacketTimeList.append(filteredRpiSendTimeList)
                    toFileRPIList.append(person.getId())
                    toFileSignalStrengthList.append(signalStrengthList)

                rpiSendTimeList = nearPeople.getRPISendTimeFromTargetTime(arriveTime)
                filteredRpiSendTimeList = filterRpiSendTimeList(rpiSendTimeList, arriveTime, longFlag)
                signalStrengthList = calculateSignalStrength(nearPeople, receiver, filteredRpiSendTimeList, Gr, antennaType, experimentType, nearPeopleList, overlapIsNecessary)

                # Additional time offset
                for i in range(len(filteredRpiSendTimeList)):
                    gapTime = nearPeople.getGapTime()
                    filteredRpiSendTimeList[i] = filteredRpiSendTimeList[i] + gapTime

                if graphFlag == 1:
                    maxSignalStrength = max(signalStrengthList)
                    maxIndex = signalStrengthList.index(maxSignalStrength)

                    # When you want to thin out the signal display results
                    # if abs(filteredRpiSendTimeList[maxIndex] - arriveTime) <15:
                    if True:
                        ax.plot(filteredRpiSendTimeList, signalStrengthList, label="RPI" + str(nearPeople.getId()), marker="o")
                        if person.getId() == nearPeople.getId():
                            ax.plot(filteredRpiSendTimeList[maxIndex], maxSignalStrength, 'b*', markersize=28)
                    ax.set_xlim(arriveTime-10, arriveTime+10)
                    
                    ax.axvline(arriveTime, c='red', linestyle='dashed', linewidth=4)
                    # plt.plot(arriveTime,0, marker="o")

                    print(str(nearPeople.getId()))
                    print("filteredRpiSendTimeList")
                    print(filteredRpiSendTimeList)
                    print("signalStrengthList")
                    print(signalStrengthList)                    


            if graphFlag == 1:
                ax.legend(loc=0, fontsize=28,ncol=2)
                ax.set_ylim(-85,5)
                
                filename = open("./" + str(experimentNumber) + "/myPickle/" +str(person.getId()) + str('.pickle'), 'wb')
                pickle.dump(fig, filename)
                filename.close()
    
        for i in range(len(toFileRPIList)):
            filteredRpiSendTimeList = toFilePacketTimeList[i]
            rpi = toFileRPIList[i]
            signalStrengthList = toFileSignalStrengthList[i]

            for j in range(len(filteredRpiSendTimeList)):
                data = []
                packetTime = filteredRpiSendTimeList[j]
                rpi = rpi
                packetsignaldbm = signalStrengthList[j]
                data = [receiverId, packetTime,rpi, packetsignaldbm]
                goodDataList.append(data)
        
    goodDataTable = pd.DataFrame(goodDataList,columns = ["receiverId","packetTime","rpi","packetsignaldbm"])

    return goodDataTable

def filterRpiSendTimeList(rpiSendTimeList, arriveTime, longFlag):
    if longFlag == True:
        diff = 60
    else:
        diff = 10

    resultRpiSendTimeList = []

    for rpiSendTime in rpiSendTimeList:
        if abs(rpiSendTime - arriveTime) < diff:
            resultRpiSendTimeList.append(rpiSendTime)
    
    return resultRpiSendTimeList     

def getPeoleListFromPeopleIdList(peopleList, peopleIdList):
    resultPeopleList = []

    for people in peopleList:
        if people.getId() in peopleIdList:
            resultPeopleList.append(people)

    return resultPeopleList

@lru_cache(maxsize=100000)
def calculateReceiverCenterPosition(receiver):
    receiverPositionX, receiverPositionY = receiver.getPosition()
    receiverDirection = receiver.getReceiveDirection()

    receiverCenterPositionX = 0
    receiverCenterPositionY = 0

    appndSize = 100

    
    receiverCenterPositionX = receiverPositionX + appndSize * math.cos(receiverDirection)
    receiverCenterPositionY = receiverPositionY + appndSize * math.sin(receiverDirection)

    return receiverCenterPositionX, receiverCenterPositionY

def collisionRayDetection(thetaSR, theta01, theta02, theta03, theta04):
    if theta01 < thetaSR and thetaSR < theta04:
        return True
    elif theta04 < thetaSR and thetaSR < theta01:
        return True
    elif theta03 < thetaSR and thetaSR < theta04:
        return True
    elif theta04 < thetaSR and thetaSR < theta03:
        return True
    elif theta02 < thetaSR and thetaSR < theta03:
        return True
    elif theta03 < thetaSR and thetaSR < theta02:
        return True
    
    return False

def calculateDistance(receiveX, receiveY, peopleCenterPositionX, peopleCenterPositionY):
    distance = 0

    distance = math.sqrt( pow((receiveX - peopleCenterPositionX),2) + pow((receiveY - peopleCenterPositionY),2))

    return distance

def collisionAndDistance(sendX, sendY, receiveX, receiveY, peopleCenterPositionX, peopleCenterPositionY):

    distanceBetweenDistanceAndReceiver = 0

    katahaba = 0.4328
    atsusa = 0.1792

    p01X = peopleCenterPositionX + atsusa / 2
    p01Y = peopleCenterPositionY + katahaba / 2

    p02X = peopleCenterPositionX - atsusa / 2
    p02Y = peopleCenterPositionY + katahaba / 2

    p03X = peopleCenterPositionX - atsusa / 2
    p03Y = peopleCenterPositionY - katahaba / 2

    p04X = peopleCenterPositionX + atsusa / 2
    p04Y = peopleCenterPositionY - katahaba / 2

    thetaSR = math.atan2(sendY-receiveY, sendX - receiveX)

    theta01 = math.atan2(p01Y-receiveY, p01X - receiveX)

    theta02 = math.atan2(p02Y-receiveY, p02X - receiveX)

    theta03 = math.atan2(p03Y-receiveY, p03X - receiveX)

    theta04 = math.atan2(p04Y-receiveY, p04X - receiveX)

    collisionResult = None
    collisionResult = collisionRayDetection(thetaSR, theta01, theta02, theta03, theta04)

    if collisionResult:
        distanceBetweenDistanceAndReceiver = calculateDistance(receiveX, receiveY, peopleCenterPositionX, peopleCenterPositionY)


    return collisionResult, distanceBetweenDistanceAndReceiver

# Check for overlap with others.
# True : Overlap、 False : Not Overlap
def checkOverlap(senderPerson, receiver, nearPeopleList):
    overlapResult = False
    for nearPerson in nearPeopleList:
        sendX= senderPerson.getX()
        sendY= senderPerson.getY()
        receiverPositionX, receiverPositionY = receiver.getPosition()
        for nearPerson in nearPeopleList:
            personX = nearPerson.getX()
            personY = nearPerson.getY()
            collisionResult, distanceBetweenDistanceAndReceiver = collisionAndDistance(sendX, sendY, receiverPositionX, receiverPositionY, personX, personY)
            if collisionResult == True:
                break
    
    return collisionResult


@lru_cache(maxsize=10000000)
def calculateSignalStrengthFromTargetTime(person, receiver, targetTime, Gr, antennaType, experimentType, nearPeopleList, overlapIsNecessary):
    signalStrength = person.getSignalStrength(receiver.getId(), targetTime)
    if signalStrength == None:
        None
    else:
        if signalStrength < 10000000:
            return signalStrength

    # Shadowing Effects by the Human Body
    humanBodyshadowing = -15


    personPositionX, personPositionY = person.timeToPositionTargetTime(targetTime)
    receiverPositionX, receiverPositionY = receiver.getPosition()

    receiverPositionCenterX, receiverPositionCenterY = calculateReceiverCenterPosition(receiver)


    # Ref https://qiita.com/hacchi_/items/7e6f433d465df9378d7a
    a = np.array([personPositionX, personPositionY])
    b = np.array([receiverPositionX, receiverPositionY])
    c = np.array([receiverPositionCenterX, receiverPositionCenterY])

    vec_a = a - b
    vec_c = c - b


    length_vec_a = np.linalg.norm(vec_a)
    length_vec_c = np.linalg.norm(vec_c)
    inner_product = np.inner(vec_a, vec_c)
    cos = inner_product / (length_vec_a * length_vec_c)

    rad = np.arccos(cos)
    deg = np.rad2deg(rad)

    distance = calculateDistance(personPositionX, personPositionY, receiverPositionX, receiverPositionY)
    Pt = 0
    Gt = 0

    senderType = person.getSenderType()
    if senderType == "iphone":
        Pt = 16
        Gt = -4.9
    elif senderType == "nexus6":
        Pt = 6.57
        Gt = -3.00
    else:
        print("error")
        input("sender type error")

    Frequency = 2400000000

    dbm = frisFormulaDbm(Pt, Gr, Gt, distance, Frequency, deg, antennaType)

    noise = np.random.normal(0, 3, 1)[0]

    loss = -12
    dbm = dbm + noise + loss

    if overlapIsNecessary == 1:
        overlapFlag = checkOverlap(person, receiver, nearPeopleList)

        if overlapFlag:
            dbm = dbm + humanBodyshadowing

    person.setSignalStrength(receiver.getId(), targetTime, dbm)


    return dbm


def calculateSignalStrength(person, receiver, targetTimeList, Gr, antennaType, experimentType, nearPeopleList, overlapIsNecessary):
    resultSignalStrengthList = []
    # In order to cache, it is necessary to use tuple instead of list, so I did so.
    tupleNearPeopleList = tuple(nearPeopleList)
    for targetTime in targetTimeList:
        resultSignalStrengthList.append(calculateSignalStrengthFromTargetTime(person,receiver,targetTime, Gr, antennaType, experimentType, tupleNearPeopleList, overlapIsNecessary))
    
    return resultSignalStrengthList

def drawImage(nearPeopleList, receiver, targetTime, targetId):
    receiverPositionX, receiverPositionY = receiver.getPosition()
    receiverDirection = receiver.getReceiveDirection()

    peoplePositionList = []

    global imageSettingList
    oneImage = OneImage()

    for nearPeople in nearPeopleList:
        peoplePositionX, peoplePositionY = nearPeople.timeToPositionTargetTime(targetTime)
        v = nearPeople.getV()

        drawPositionX = peoplePositionX - receiverPositionX
        drawPositionY = peoplePositionY - receiverPositionY

        person = imagePerson()
        person.setPosition(drawPositionX, drawPositionY)
        person.setId(nearPeople.getId())
        person.setV(v)
        
        oneImage.appendPeopleList(person)

    imageSettingList.append(oneImage)

def calculateLookedH(Rd):
    return 100 * 2 / Rd

def calculateLookedS(d, s):
    return s * 2 / d

def calculateLookedSDirection(lookedS, peoplePositionX, peoplePositionY, receiverPositionX, receiverPositionY, receiverDirection):

    if receiverDirection == math.pi / 2 * 0:
        if peoplePositionY - receiverPositionY > 0:
            return lookedS
        else:
            return (-1) * lookedS
            
    elif receiverDirection == math.pi / 2 * 1:
        if peoplePositionX - receiverPositionX > 0:
            return lookedS
        else:
            return (-1)*lookedS

    elif receiverDirection == math.pi / 2 * 2:
        if peoplePositionY - receiverPositionY > 0:
            return (-1)*lookedS
        else:
            return lookedS
    
    elif receiverDirection == math.pi / 2 * 3:
        if peoplePositionX - receiverPositionX > 0:
            return (-1)*lookedS
        else:
            return lookedS

def calculateMagnification(Rd):
    return 1 * 2 / Rd


def calculateDistance(target1X, target1Y, target2X, target2Y):
    dX = (target1X - target2X)** 2
    dY = (target1Y - target2Y)** 2
    kyo = dX + dY
    return math.sqrt(kyo)
    
# Frequency : frequency， Distance : r, Transmission power : pt, Antenna Gain (Transmit): gt, Antenna Gain (Receive) : gr
def firsEquation(frequency, r, pt, gt, gr):
    None

def frisSimple(d):
    return 100 - 20 * math.log10(d)


# Ref : https://qiita.com/ground0state/items/5fa0743837f1bcb374ca
# Ref : https://qiita.com/maskot1977/items/913ef108ff1e2ba5b63f
def splineCurve2D(x, y):
    return interpolate.interp1d(x, y, kind="quadratic")

def gainCalculator(degree):
    x = [0.376855602, 1.316698291, 1.914296029, 2.641017333, 3.170693183, 3.687034686, 4.217979565, 4.660008151, 5.058019223, 5.583011076, 5.897041426, 6.211801074, 6.581212154, 7.034597891, 7.359089718, 7.609527749, 7.9723984, 8.219286805, 8.556976144, 8.989120186, 9.308504052, 9.689802524, 10.04118907, 10.41872775, 10.71959091, 10.96197501, 11.17695595, 11.60396802, 12.07181011, 12.4366599, 12.64720264, 12.94366284, 13.29337602, 13.66446047, 14.26712838, 14.70992928, 14.95046326, 15.27600971, 15.51934301, 15.9128248, 16.36441904, 17.13549671, 17.98728432, 19.15447833, 20.07241208, 21.63781021, 23.43533856, 28.0436142, 34.49030041, 41.86610699, 48.18133428, 60.56869222, 86.60151024]
    y = [-0.840136948, -0.997213021, -1.508970783, -2.03718602, -2.588648673, -3.155777853, -3.714473735, -4.271397282, -4.851920697, -5.408760596, -5.991462414, -6.544213721, -7.116095692, -7.690680225, -8.260488919, -8.833929639, -9.386232458, -9.950570167, -10.58448734, -11.09673934, -11.67084333, -12.25433028, -12.82580905, -13.39664447, -13.97738047, -14.57510975, -15.1606956, -15.69069967, -16.28400501, -16.85201458, -17.44056165, -18.02871094, -18.61320519, -19.20560653, -19.7452457, -20.33798812, -20.91879134, -21.53557414, -22.12577957, -22.71046326, -23.30429581, -23.88236089, -24.46051786, -25.03957726, -25.64319694, -26.08142259, -26.47746601, -27.14039412, -27.72944509, -26.39669117, -26.95876408, -27.43536085, -27.79269213]

    splineCurve2DFun = splineCurve2D(x, y)

    if degree >86.60151024:
        return min(y)
    elif degree < 0.376855602:
        return max(y)
    else:
        res = splineCurve2DFun(degree)
        if res >= 0:
            return res
        else:
            return res

# Antennas and Antenna Kits
def gainCalculatorLogperi(degree):
    x = [0.165904067,2.858611339,4.412897609,5.95273867,7.46220107,9.66196096,11.7515873,13.78101971,15.6317952,17.76320553,19.74501287,21.70196806,24.02973098,26.41122396,28.60961438,30.75461527,32.91289577,34.71845348,36.39347441,38.10761463,39.60468147,40.94489033,42.27617912,43.47862094,44.71076106,45.92873923,46.70058437,48.01431359,48.51204768,49.90666773,50.15971718,51.51390744,51.88878384,52.09978149,53.63551294,54.78916317,55.54049189,56.32780307,57.22265767,59.46155136,60.37646523,62.55361784,64.74843324,67.00988745,69.43795121,72.19448872,74.76195632,76.89829764,79.04894909,79.3811514,80.45090012,80.97137712,82.23303213,82.80742046,83.10477981,83.25987165,88.84069964,89.90083986,90]
    y = [0,0,0,0,0,0,0,-0.072553751,-0.16297931,-0.392894053,-0.60117773,-1.11791469,-1.579008452,-1.985638768,-2.461951317,-2.98265147,-3.476409012,-4.081047225,-4.731837331,-5.36899871,-6.099979992,-6.909502178,-7.7405653,-8.648306845,-9.567956897,-10.52163027,-11.70009334,-12.67877989,-14.0390961,-15.06583442,-16.59188719,-17.64763808,-18.98570247,-19.46772798,-19.60472681,-19.55828306,-18.84387714,-17.77473931,-16.22380237,-15.03893268,-14.2796487,-14.00336224,-14.32770831,-15.10578871,-15.86261205,-16.45061009,-17.40667923,-18.75128745,-20.17225989,-21.50697682,-22.30269725,-23.68302366,-25.01448029,-26.4790474,-27.67761648,-29.89871401,-31.35505269,-30.19490747,-32.24496687]

    splineCurve2DFun = splineCurve2D(x, y)

    if degree >90:
        return 0
    else:
        print("Degree")
        print(degree)
        try:
            res = splineCurve2DFun(degree)
        except:
            res = 0
        if res >= 0:
            return res
        else:
            return res
        
# Monopole antenna
def gainCalculatorMono(degree):
    return 0

def originalFriis(Gt,Gr,Pt,lam,d,deg, antennaType):

    antennaGain = -1
    if antennaType == "mono":
        antennaGain = gainCalculatorMono(deg)
    elif antennaType == "logPeri":
        antennaGain = gainCalculatorLogperi(deg)
    elif antennaType == "parabora":
        antennaGain = gainCalculator(deg)
    else:
        print("antenne Type ERROR")
        sys.exit(-1)

    Gr = Gr + antennaGain
    Pr = 10 * math.log10( (lam / ( 4 * math.pi * d ) )**2 )  + Gt + Gr + Pt

    return Pr

# Ref：https://www.ibsjapan.co.jp/tech/details/elementary-electric-wave/eewave-04-07.html
def frisFormulaDbm(Pt, Gr, Gt, d, frequency, deg, antennaType):

    PtDbm = Pt
    lam =  299792458 / frequency

    
    calculatedDbm = originalFriis(Gt,Gr,PtDbm,lam,d,deg,antennaType)

    return calculatedDbm

def generateImages(peopleList, receiverList, simulationPeriodTime, experimentType):
    for receiver in receiverList:
        for timestamp in range(0, simulationPeriodTime):
            nearPeopleIdList = receiver.getPeopleIdListFromTime(timestamp*1, experimentType)
            nearPeopleList = getPeoleListFromPeopleIdList(peopleList, nearPeopleIdList)

            drawImageAll(nearPeopleList, receiver, timestamp * 1)
            
            print(timestamp)

def drawImageAll(nearPeopleList, receiver, targetTime, targetId):
    receiverPositionX, receiverPositionY = receiver.getPosition()
    receiverDirection = receiver.getReceiveDirection()

    peoplePositionList = []

    global imageSettingList
    oneImage = OneImage()
    oneImage.setCapturedTime(targetTime)


    for nearPeople in nearPeopleList:
        peoplePositionX, peoplePositionY = nearPeople.timeToPositionTargetTime(targetTime)

        drawPositionX = peoplePositionX - receiverPositionX
        drawPositionY = peoplePositionY - receiverPositionY

        person = imagePerson()
        person.setPosition(drawPositionX, drawPositionY)
        person.setId(nearPeople.getId())
        person.setV(nearPeople.getV())
        
        oneImage.appendPeopleList(person)
        oneImage.setTargetId(targetId)

    imageSettingList.append(oneImage)

def makePeakTimeList(receiverId, globalId, experimentNumber, peakTimeTable):
    peakTimeList = []
    peakIdList = []

    newDb = peakTimeTable.query("receiverId==" + str(receiverId))
    peakIdList = newDb["rpi"].to_numpy().tolist()
    peakTimeList = newDb["time"].to_numpy().tolist()

    return peakTimeList, peakIdList

def generateImagesFromPeakTimeList(peopleList, receiver, peakTimeList, peakIdList, experimentType):
    for i,timestamp in enumerate(peakTimeList):
        nearPeopleIdList = receiver.getPeopleIdListFromTime(timestamp*1, experimentType)
        nearPeopleList = getPeoleListFromPeopleIdList(peopleList, nearPeopleIdList)
        drawImageAll(nearPeopleList, receiver, timestamp * 1, peakIdList[i])
        
        print("ReceiverID" + str(receiver.getId()) +"PeakId : " + str(peakIdList[i]) + " peakTime : " + str(timestamp) )

def linkRPIToPersonFromPeakTime(peopleList, targetReceiver, peakTimeList, peakIdList, experimentType):
    for i,timestamp in enumerate(peakTimeList):
        nearPeopleIdList = targetReceiver.getPeopleIdListFromTime(timestamp, experimentType)
        nearPeopleList = getPeoleListFromPeopleIdList(peopleList, nearPeopleIdList)
        mostNearPerson = getMostNearPersonDirection(nearPeopleList, targetReceiver, timestamp, peopleList)
        mostNearPerson.setLinkedResultList(peakIdList[i])

# Function to return the nearest person at a given time
def getMostNearPerson(nearPeopleList, targetReceiver, timestamp):

    targetReceiverPositionX = targetReceiver.getX()

    mostNearDistance = 10000000000000000
    mostNearPerson = nearPeopleList[0]

    for person in nearPeopleList:
        personPositionX, personPositionY = person.timeToPositionTargetTime(timestamp)

        distanceBetweenReceiverAndPerson = abs(targetReceiverPositionX - personPositionX)

        if distanceBetweenReceiverAndPerson < mostNearDistance:
            mostNearDistance = distanceBetweenReceiverAndPerson
            mostNearPerson = person
    
    return mostNearPerson

# Function to find the nearest person on an angle basis, not on a distance basis.
def getMostNearPersonDirection(nearPeopleList, targetReceiver, timestamp, peopleList):
    mostNearPerson = peopleList[0]
    maxCos = -1

    for person in nearPeopleList:
        personPositionX, personPositionY = person.timeToPositionTargetTime(timestamp)
        receiverPositionX, receiverPositionY = targetReceiver.getPosition()
        receiverPositionCenterX, receiverPositionCenterY = calculateReceiverCenterPosition(targetReceiver)

        # Ref https://qiita.com/hacchi_/items/7e6f433d465df9378d7a
        a = np.array([personPositionX, personPositionY])
        b = np.array([receiverPositionX, receiverPositionY])
        c = np.array([receiverPositionCenterX, receiverPositionCenterY])

        vec_a = a - b
        vec_c = c - b

        # Calculate cos
        length_vec_a = np.linalg.norm(vec_a)
        length_vec_c = np.linalg.norm(vec_c)
        inner_product = np.inner(vec_a, vec_c)
        cos = inner_product / (length_vec_a * length_vec_c)

        if maxCos < cos:
            mostNearPerson = person
            maxCos = cos
    
    return mostNearPerson

    None


def showResult(peopleList):
    print("Display linked result.")
    for people in peopleList:
        print(str(people.getId()) + " : " + str(people.getFinalLinkedResultList()))

def combineResultAll(peopleList):
    for people in peopleList:
        people.combineResult()

def combineResultAllWithGroup(peopleList, groupIdList):
    for people in peopleList:
        if groupOrNot(people.getId(), groupIdList):
            people.combineResult()
            None
        else:
            people.combineResult()


def removeAlreadyLikedRPI(peopleList):

    while True:
        uniqueRpiList = getUniqueRPIList(peopleList)

        print("Unique RPI List")
        pprint.pprint(uniqueRpiList)

        flag = 0
        for people in peopleList:
            finalLinkedResultList = people.getFinalLinkedResultList()
            if len(finalLinkedResultList) > 1:
                for finalLinkedResult in finalLinkedResultList:
                    print("finalLinkedResult")
                    print(finalLinkedResult)
                    if finalLinkedResult in uniqueRpiList:
                        print("対象あり")
                        people.removeFinalLinkedResultList(finalLinkedResult)
                        flag = 1
                        print("Remove " + str(finalLinkedResult) + " from " + str(people.getId()))
        
        if flag == 0:
            break


def getUniqueRPIList(peopleList):
    uniqueRpiList = []

    for people in peopleList:
        finalLinkedResultList = people.getFinalLinkedResultList()
        if len(finalLinkedResultList) == 1:
            uniqueRpiList.append(finalLinkedResultList[0])
    
    return uniqueRpiList


# Calculate accuracy
def calculateAccuracy(peopleList, globalId, experimentNumber):
    sumCountOfPeople = len(peopleList)
    uniqueLinkedCount = 0
    linkedCountList = []
    print("Sum of pedestrians: " + str(sumCountOfPeople))

    for linkedCount in range(1,6):
        if not linkedCount == 5:
            uniqueLinkedCount = 0
            for people in peopleList:
                if len(people.getFinalLinkedResultList()) == linkedCount:
                    if people.getId() in people.getFinalLinkedResultList():
                        # print("True")
                        uniqueLinkedCount = uniqueLinkedCount + 1
                else:
                    # print("Not One")
                    None

            linkedCountList.append(uniqueLinkedCount)

            print("m = " + str(linkedCount)+" : " + str(uniqueLinkedCount))
            print("m = " + str(linkedCount)+" : " + str( 100 * uniqueLinkedCount / sumCountOfPeople) + " [%] ")
            print("Sum of all : "+ str(sumCountOfPeople))

            with open("./" + str(experimentNumber) + "/" + "result.csv","a") as f:
                f.write(str(globalId) + "," + str(linkedCount) + "," + str( 100 * uniqueLinkedCount / sumCountOfPeople) + "\n")
                f.close()
        else:
            uniqueLinkedCount = 0
            for people in peopleList:
                if len(people.getFinalLinkedResultList()) >= linkedCount:
                    if people.getId() in people.getFinalLinkedResultList():
                        # print("True")
                        uniqueLinkedCount = uniqueLinkedCount + 1
                else:
                    # print("Not One")
                    None

            linkedCountList.append(uniqueLinkedCount)

            print("m = " + str(linkedCount)+" : " + str(uniqueLinkedCount))
            print("m = " +str(linkedCount)+" : " + str( 100 * uniqueLinkedCount / sumCountOfPeople)  + " [%] ")
            print("Sum of all : "+ str(sumCountOfPeople))

            with open("./" + str(experimentNumber) + "/" + "result.csv","a") as f:
                f.write(str(globalId) + "," + str(linkedCount) + "," + str( 100 * uniqueLinkedCount / sumCountOfPeople) + "\n")
                f.close()


    print(sum(linkedCountList))


        

def groupOrNot(targetPeopleId, groupIdList):
    if len(getPeopleIdFromPeopleIdAndGroupIdList(targetPeopleId, groupIdList)) == 0:
        return False
    else:
        return True

# Summarize results in the same group
# Take all results "AND"
def makeSameResultInSameGroup(peopleList,groupIdList):
    for groupId in groupIdList:
        compiledList = []
        
        for people in peopleList:
            if people.getId() in groupId:
                compiledList.extend(people.getLinkedResultList())

                print(" compiledList ")
                print(compiledList)

        for people in peopleList:
            if people.getId() in groupId:
                people.replaceLinkedResultList(compiledList)



def getPeopleIdFromPeopleIdAndGroupIdList(targetId, groupIdList):
    resultList = []
    for groupId in groupIdList:
        if targetId in groupId:
            resultList = groupId
    
    return resultList

def checkAllFinalLinkedResultListinSameGroupId(finalLinkedResultList, groupIdList):
    if len(finalLinkedResultList) == 0:
        return False
    else:
        targetGroupIdList = getPeopleIdFromPeopleIdAndGroupIdList(finalLinkedResultList[0],groupIdList)
        for finalLinkedResult in finalLinkedResultList:
            if finalLinkedResult in targetGroupIdList:
                None
            else:
                return False
        return True

def calculateAccuracyGroup(peopleList, groupIdList, globalId, experimentNumber):
    sumCountOfPeople = len(peopleList)
    uniqueLinkedCount = 0

    for people in peopleList:
        print(str(people.getId()) + " : ", end="")
        if len(people.getFinalLinkedResultList()) == 1:
            if people.getId() == people.getFinalLinkedResultList()[0]:
                uniqueLinkedCount = uniqueLinkedCount + 1
            
            else:
                if people.getFinalLinkedResultList()[0] in getPeopleIdFromPeopleIdAndGroupIdList(people.getFinalLinkedResultList()[0], groupIdList):
                    uniqueLinkedCount = uniqueLinkedCount + 1

        else:
            if checkAllFinalLinkedResultListinSameGroupId(people.getFinalLinkedResultList(), groupIdList):
                print("True")
                uniqueLinkedCount = uniqueLinkedCount + 1
            else:
                print("False")
            
            
    print("Number of people Linked Uniquely : " + str(uniqueLinkedCount))
    print("Percentage of Unique Linked % : " + str( 100 * uniqueLinkedCount / sumCountOfPeople))
    print("Number of people : "+ str(sumCountOfPeople))

    with open("./" + str(experimentNumber) + "/" + "result_group.csv","a") as f:
        f.write(str(globalId) + "," + str( 100 * uniqueLinkedCount / sumCountOfPeople) + "\n")
        f.close()

def throwToPeakDetection(theNumberOfReceiver, globalId, experimentNumber, goodDataTable):
    timeSignalStrengthFileName = str(experimentNumber) + "/" + str(globalId)+"_0_GoodData.csv"
    picturedFileName = str(experimentNumber)+ "/" + str(globalId) + "_0_timeList"
    dirName = "./"
    deviceNumber = 0
    allRPIList = peakDetectionFromMax.makeAllRpiList(goodDataTable)
    print("All RPI List")
    print(allRPIList)
    # time.sleep(3)
    peakTimeTable = peakDetectionFromMax.makeGraphSimulation(allRPIList, goodDataTable, dirName + picturedFileName, dirName, experimentNumber, deviceNumber, theNumberOfReceiver, globalId)

    return peakTimeTable

def exportAllCondition(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency,tPeriod,tInterval,rpiSendGain, peopleOccurTimeList, walkingSpeedOfPeopleList,gapTimeList,randomListForFirstRpiSendTimeList, seed, initialPositionList,groupRationList, groupLamList, groupdIdList, Gr, antennaType, experimentNumber):

    globalId
    simulationPeriodTime
    perTime
    rpiSendFrequency
    tPeriod
    tInterval
    rpiSendGain
    seed


    jsonData = {
        "globalId" : str(globalId),
        "simulationPeriodTime" : str(simulationPeriodTime),
        "perTime" : str(perTime),
        "rpiSendFrequency" : str(rpiSendFrequency),
        "tPeriod" : str(tPeriod),
        "tInterval" : str(tInterval),
        "rpiSendGain" : str(rpiSendGain),
        "seed" : str(seed),
        "Gr" : str(Gr),
        "antennaType" : str(antennaType)
    }

    jsonFilePath = "./" + str(experimentNumber) + "/" + str(globalId) + "_para.json"
    with open(jsonFilePath, "w") as f:
        json.dump(jsonData, f,ensure_ascii=-False)

    receiverSettings
    peopleOccurTimeList
    walkingSpeedOfPeopleList
    gapTimeList
    randomListForFirstRpiSendTimeList
    initialPositionList
    groupRationList
    groupLamList
    groupdIdList

    parameters = []
    parameters.append(receiverSettings)
    parameters.append(peopleOccurTimeList)
    parameters.append(walkingSpeedOfPeopleList)
    parameters.append(gapTimeList)
    parameters.append(randomListForFirstRpiSendTimeList)
    parameters.append(initialPositionList)
    parameters.append(groupRationList)
    parameters.append(groupLamList)
    parameters.append(groupdIdList)
    

    jobFilePath = "./" + str(experimentNumber) + "/" + str(globalId) + "_para.job"
    joblib.dump(parameters,jobFilePath,compress=3)

    a = joblib.load(jobFilePath)
    pprint.pprint(a)

def loadAllCondition(globalId, experimentNumber):
    jsonFilePath = "./" + str(experimentNumber) + "/" + str(globalId) + "_para.json"
    jobFilePath = "./" + str(experimentNumber) + "/" + str(globalId) + "_para.job"

    # Reading json files
    with open(jsonFilePath) as f:
        loaded = json.load(f)
        f.close()
    
    # Read parameters stored in joblib
    loadedParameters = joblib.load(jobFilePath)

    loadedGlobalId = int(loaded["globalId"])
    simulationPeriodTime = int(loaded["simulationPeriodTime"])
    perTime = int(loaded["perTime"])
    rpiSendFrequency = float(loaded["rpiSendFrequency"])
    tPeriod = int(loaded["tPeriod"])
    tInterval = int(loaded["tInterval"])
    rpiSendGain = int(loaded["rpiSendGain"])
    seed = int(loaded["seed"])
    Gr = int(loaded["Gr"])
    antennaType = str(loaded["antennaType"])

    receiverSettings = loadedParameters[0]
    peopleOccurTimeList = loadedParameters[1]
    walkingSpeedOfPeopleList = loadedParameters[2]
    gapTimeList= loadedParameters[3]
    randomListForFirstRpiSendTimeList = loadedParameters[4]
    initialPositionList = loadedParameters[5]
    groupRationList = loadedParameters[6]
    groupLamList = loadedParameters[7]
    groupIdList = loadedParameters[8]

    return globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency,tPeriod,tInterval,rpiSendGain, peopleOccurTimeList, walkingSpeedOfPeopleList,gapTimeList,randomListForFirstRpiSendTimeList, seed, initialPositionList, groupRationList, groupLamList, groupIdList, Gr, antennaType

def setParameterFromOpendataset(targetOpendatasetFilePath):
    initialPositionList = []
    peopleOccurTimeList = []
    walkingSpeedOfPeopleList = []
    openDatasetSimulationPeriodTime = 0

    # Instance list of persons
    realPersonInstanceList = simpleParse.creatRealPersonInstanceListWithoutSpeed0(targetOpendatasetFilePath)

    # Data set start time
    startTimeDatetime, startTimeUnixtime = simpleParse.calculateMeasureStartTime(realPersonInstanceList)

    firstTimeDatetime, firstTimeUnixtime, firstPositionX, firstPositionY = realPersonInstanceList[0].getFirstPositionAndTime()
    lastTimeDatetime, lastTimeUnixtime, lastPositionX, lastPositionY = realPersonInstanceList[-1].getLastPositionAndTime()

    openDatasetSimulationPeriodTime = lastTimeUnixtime - firstTimeUnixtime

    for realPersonInstance in realPersonInstanceList:
        firstTimeDatetime, firstTimeUnixtime, firstPositionX, firstPositionY = realPersonInstance.getFirstPositionAndTime()
        walkingSpeedM = realPersonInstance.calculateWalkingSpeed()
        ## mm to m unit conversion required
        initialPositionList.append([float(firstPositionX) / 1000, float(firstPositionY) / 1000])
        peopleOccurTimeList.append(firstTimeUnixtime - startTimeUnixtime)
        walkingSpeedOfPeopleList.append(walkingSpeedM)
    
    return initialPositionList, peopleOccurTimeList, walkingSpeedOfPeopleList, openDatasetSimulationPeriodTime
    

def do(allSettingList):

    baseGlobalId = allSettingList[0]
    baseSimulationPeriodTime = allSettingList[1]
    basePerTime = allSettingList[2]
    baseReceiverSettings = allSettingList[3]
    baseRpiSendFrequency = allSettingList[4]
    baseloadOrNot = allSettingList[5]
    baseGroupRationList = allSettingList[6]
    baseAntennaGr = allSettingList[7]
    baseAntennaType = allSettingList[8]
    experimentType = allSettingList[9]
    experimentNumber = allSettingList[10]
    graphFlag = allSettingList[11]
    overlapIsNecessary = allSettingList[12]
    margin = allSettingList[13]
    widthOfRoad = allSettingList[14]
    modelFlag = allSettingList[15]
    useOpendataset = allSettingList[16]
    targetOpendatasetFilePath = allSettingList[17]
    directionFlag = allSettingList[18]
    groupFlag = allSettingList[19]
    reSend = allSettingList[20]
    mixFlag = allSettingList[21]
    

    startTime = time.time()

    openDatasetinitialPositionList = None
    openDatasetpeopleOccurTimeList = None
    openDatasetwalkingSpeedOfPeopleList = None

    # Open Data Utilization
    if useOpendataset == 1:
        openDatasetinitialPositionList, openDatasetpeopleOccurTimeList, openDatasetwalkingSpeedOfPeopleList, openDatasetSimulationPeriodTime = setParameterFromOpendataset(targetOpendatasetFilePath)
    
    # Index number for this experiment
    globalId = baseGlobalId


    simulationPeriodTime = baseSimulationPeriodTime
    if useOpendataset == 1:
        simulationPeriodTime = openDatasetSimulationPeriodTime

    # List of ratios by group
    groupRationList = baseGroupRationList

    # Number of pedestrians generated per hour
    perTime = basePerTime

    # Normalize according to group proportions
    revisedPerTime = revisePerTime(perTime, groupRationList)
    
    # Interval of occurrence per second
    lam = revisedPerTime / 3600


    groupLamList = generateGroupLamList(perTime ,groupRationList)

    # List of receivers
    receiverList = []

    # Parameters of antenna
    Gr = baseAntennaGr
    antennaType = baseAntennaType

    # List of people
    peopleList = []

    # List of times when people occur
    peopleOccurTimeList = generateOccurTimeList(lam, simulationPeriodTime, groupRationList)

    # Utilization of Open Data
    if useOpendataset == 1:
        peopleOccurTimeList = openDatasetpeopleOccurTimeList
    
    # Add time when people do not occur.
    simulationPeriodTime = makeBlankTime(simulationPeriodTime, baseReceiverSettings)

    print("Real Simulation PeriodTime")
    print(simulationPeriodTime)

    pprint.pprint(peopleOccurTimeList)

    groupIdList = []
    if useOpendataset != 1:
        groupIdList = generateGroupIdListNew(peopleOccurTimeList)
    else:
        groupIdList = []


    print("GroupId List")
    pprint.pprint(groupIdList)

    # The number of people
    theNumberOfPeople = len(peopleOccurTimeList)

    # List of random numbers to determine the initial PRI transmission start time
    randomListForFirstRpiSendTimeList = makeRandomListForFirstRpiSendTimeList(theNumberOfPeople)

    walkingSpeedOfPeopleList = None

    if useOpendataset == 1:
        walkingSpeedOfPeopleList = openDatasetwalkingSpeedOfPeopleList
    else:
        if directionFlag == 1:
            if groupFlag == 1:
                walkingSpeedOfPeopleList = allPedGroupDoubleSide(theNumberOfPeople, peopleOccurTimeList)
            else:
                walkingSpeedOfPeopleList = allPedNoGroupDoubleSide(theNumberOfPeople, peopleOccurTimeList)
        else:
            walkingSpeedOfPeopleList = allPed(theNumberOfPeople, peopleOccurTimeList)

    #  Transmission duration per minute
    tPeriod = 60
    tPeriodList = generateTPeriodList(theNumberOfPeople, tPeriod)
    
  
    tInterval = 0
    tIntervalList = generateTIntervalList(theNumberOfPeople,tInterval)
    
    # This parameter is a dummy in the development process and is not used.
    #########################################################################
    rpiSendGain = -50
    rpiSendGainList = generateRpiSendGainList(theNumberOfPeople, rpiSendGain)
    #########################################################################

    rpiSendFrequency = baseRpiSendFrequency
    rpiSendFrequencyList = generateRpiSendFrequencyList(theNumberOfPeople, rpiSendFrequency)

    
    gapTimeList = calculateGapTimeList(theNumberOfPeople)

    receiverSettings = baseReceiverSettings
    
    receiverList = generateReceiverList(receiverSettings)

    seed = 10000

    initialPositionList = None

    if useOpendataset == 1:
        initialPositionList = openDatasetinitialPositionList
    else:
        if directionFlag == 1:
            if groupFlag == 1:
                initialPositionList = makeInitialPositionListGroupDoubleSide(peopleOccurTimeList, baseReceiverSettings, walkingSpeedOfPeopleList, overlapIsNecessary, receiverList, margin, widthOfRoad)
            else:
                initialPositionList = makeInitialPositionListNoGroupDoubleSide(peopleOccurTimeList, baseReceiverSettings, walkingSpeedOfPeopleList, overlapIsNecessary, receiverList, margin, widthOfRoad)
        else:
            initialPositionList = makeInitialPositionList(peopleOccurTimeList, overlapIsNecessary, receiverList, margin, widthOfRoad)
    
    if useOpendataset == 1:
        initialPositionList = openDatasetinitialPositionList
    
    for initialPosition in initialPositionList:
        print(initialPosition[1])

    with open("./" + str(experimentNumber) + "/" + str(globalId) + "_initialPositon.txt","a") as f:
        for i,initialPosition in enumerate(initialPositionList):
            f.writelines(str(peopleOccurTimeList[i]) + "," + str(initialPosition[0]) + "," + str(initialPosition[1]) + "," + str(walkingSpeedOfPeopleList[i]) + "\n")
            print(str(peopleOccurTimeList[i]) + "," + str(initialPosition[0]) + "," + str(initialPosition[1]) + "," + str(walkingSpeedOfPeopleList[i]))
    
    time.sleep(2)

    if baseloadOrNot == 2:
        exportAllCondition(globalId,simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, tPeriod, tInterval, rpiSendGain, peopleOccurTimeList, walkingSpeedOfPeopleList, gapTimeList,randomListForFirstRpiSendTimeList, seed, initialPositionList, groupRationList, groupLamList, groupIdList, Gr, antennaType, experimentNumber)

    if baseloadOrNot == 1:
        _globalId, _simulationPeriodTime, _perTime, _receiverSettings, _rpiSendFrequency,_tPeriod,_tInterval,_rpiSendGain, _peopleOccurTimeList, _walkingSpeedOfPeopleList,_gapTimeList,_randomListForFirstRpiSendTimeList, _seed, _initialPositionList, _groupRationList, _groupLamList, _groupIdList, _Gr, _antennaType = loadAllCondition(globalId, experimentNumber)

        globalId = _globalId
        simulationPeriodTime = _simulationPeriodTime
        perTime = _perTime
        lam =perTime/3600
        receiverList = []
        peopleList = []
        peopleOccurTimeList = _peopleOccurTimeList
        theNumberOfPeople = len(peopleOccurTimeList)
        randomListForFirstRpiSendTimeList = _randomListForFirstRpiSendTimeList
        walkingSpeedOfPeopleList = _walkingSpeedOfPeopleList
        tPeriod = _tPeriod
        tPeriodList = generateTPeriodList(theNumberOfPeople, tPeriod)
        tInterval = _tInterval
        tIntervalList = generateTIntervalList(theNumberOfPeople, tInterval)
        rpiSendGain = _rpiSendGain
        rpiSendGainList = generateRpiSendGainList(theNumberOfPeople, rpiSendGain)
        rpiSendFrequency = _rpiSendFrequency
        rpiSendFrequencyList = generateRpiSendFrequencyList(theNumberOfPeople, rpiSendFrequency)
        gapTimeList = _gapTimeList
        receiverSettings = _receiverSettings
        receiverList = generateReceiverList(receiverSettings)
        seed = _seed
        initialPositionList = _initialPositionList
        groupRationList = _groupRationList
        groupLamList = _groupLamList
        groupIdList = _groupIdList
        Gr = _Gr
        antennaType = _antennaType
    
    senderTypeList = []
    if mixFlag == 0:
        senderTypeList = ["iphone","iphone"]
    else:
        senderTypeList = ["iphone","nexus6"]


    peopleList = makingPeopleList(theNumberOfPeople, peopleOccurTimeList, walkingSpeedOfPeopleList, tPeriodList, rpiSendGainList, rpiSendFrequencyList, tIntervalList, gapTimeList, randomListForFirstRpiSendTimeList, initialPositionList, reSend, senderTypeList)

    # Record the time each person passes in front of each receiver
    recordTime(peopleList, receiverList)

    for receiver in receiverList:
        None
    
    a = peopleList[0].getRPISendTimeAll()
    b = peopleList[0].getRPISendTimeFromTargetTime(1000)

    goodDataTable = drawGraph(peopleList, receiverList, globalId, seed, Gr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary)
    endTime = time.time()
    print(endTime - startTime)
    
    peakTimeTable = throwToPeakDetection(len(receiverList), globalId, experimentNumber, goodDataTable)


    for receiver in receiverList:
        peakTimeList, peakIdList = makePeakTimeList(receiver.getId(), globalId, experimentNumber, peakTimeTable)

        targetReceiver = receiver
        linkRPIToPersonFromPeakTime(peopleList, targetReceiver,peakTimeList, peakIdList, experimentType)

        for person in peopleList:
            print(person.getLinkedResultList())
        
        generateImagesFromPeakTimeList(peopleList, targetReceiver, peakTimeList, peakIdList, experimentType)

    
    peopleListForAccuracyGroup = copy.deepcopy(peopleList)

    makeSameResultInSameGroup(peopleListForAccuracyGroup, groupIdList)


    for i,people in enumerate(peopleList):
        print(str(i) + " : " + str(people.getLinkedResultList()))

    combineResultAllWithGroup(peopleList, groupIdList)
    combineResultAllWithGroup(peopleListForAccuracyGroup, groupIdList)


    for i,people in enumerate(peopleList):
        print(str(i) + " : " + str(people.getFinalLinkedResultList()))
    
    for i,people in enumerate(peopleListForAccuracyGroup):
        print(str(i) + " : " + str(people.getFinalLinkedResultList()))

    showResult(peopleList)

    calculateAccuracy(peopleList, globalId, experimentNumber)

    if graphFlag == 1:
        calculateAccuracyGroup(peopleListForAccuracyGroup, groupIdList, globalId, experimentNumber)


    if modelFlag == 1:
        app = MyApp(receiverList[0].getReceiveDirection())
        app.experimentNumber = experimentNumber
        app.run()
    elif modelFlag == 2:
        app = MyView(peopleList, receiverList)
        app.experimentNumber = experimentNumber
        app.run()
    elif modelFlag == 3:
        drawPeopleMap(peopleList, receiverList)


def drawPeopleMap(peopleList, receiverList):
    colorDict = {}
    for i in range(1000, 2000):
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.set_xlim(0,14)
        ax.set_ylim(-2,5)
        ax.axhspan(0, 4.8, color="gray", alpha=0.3)
        ax.axhspan(-1, 0, color="white", alpha=0.3)
        t = i*0.5
        targetPeopleList = []
        for people in peopleList:
            x,y = people.timeToPositionTargetTime(t)
            if 0 <= x and x <= 14:
                targetPeopleList.append(people)
            
        for people in targetPeopleList:
            color = colorDict.get(people.getId())
            if color == None:
                color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            x,y = people.timeToPositionTargetTime(t)
            colorDict[people.getId()] = color
            ax.scatter(x,y,c=color)
            rX, rY = receiverList[0].getPosition()
            ax.scatter(rX, rY, c = "red", label ="Receiver", s = 6)
            ax.set_title("t = " + str(t) + " [s]")
        
        plt.pause(0.1)
        plt.cla()

# Function to generate a settingList from parameters
def generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag):
    settingList = []

    settingList.append(globalId)
    settingList.append(simulationPeriodTime)
    settingList.append(perTime)
    settingList.append(receiverSettings)
    settingList.append(rpiSendFrequency)
    settingList.append(loadOrNot)
    settingList.append(groupRatioList)
    settingList.append(antennaGr)
    settingList.append(antennaType)
    settingList.append(experimentType)
    settingList.append(experimentNumber)
    settingList.append(graphFlag)
    settingList.append(overlapIsNecessary)
    settingList.append(margin)
    settingList.append(widthOfRoad)
    settingList.append(modelFlag)
    settingList.append(useOpendataset)
    settingList.append(targetOpendatasetFilePath)
    settingList.append(directionFlag)
    settingList.append(groupFlag)
    settingList.append(reSend)
    settingList.append(mixFlag)


    return settingList


def prepareHokousya(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    globalId = 0

    # for test
    if targetFlag == 1:
        perTimeList = [1000]
    # for paper simulation
    else:
        perTimeList = [200,400,600,800,1000,2000,3000,4000,5000]
    rpiSendFrequencyList = [0.270]
    groupRatioListList = [[100,0,0,0,0]]
    overlapIsNecessary = 1
    margin = 1
    widthOfRoad = 3.0
    useOpendataset = 0
    targetOpendatasetFilePath = ""
    reSend = 0
    if groupFlag == 1:
        groupRatioListList = [[66,25,6,2,1]]

    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    return allSettingList



def prepareDaisu(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    globalId = 0

    # for test
    if targetFlag == 1:
        perTimeList = [1000]
    # for paper simulation
    else:
        perTimeList = [5000]
    rpiSendFrequencyList = [0.270]
    groupRatioListList = [[100,0,0,0,0]]
    overlapIsNecessary = 1
    margin = 1
    widthOfRoad = 3.0
    useOpendataset = 0
    targetOpendatasetFilePath = ""
    reSend = 0

    if groupFlag == 1:
        groupRatioListList = [[66,25,6,2,1]]


    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2],[500, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2],[500, 0, math.pi/2],[600, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    return allSettingList

def prepareSyuuki(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    globalId = 0

    perTimeList = [800]
    if targetFlag == 1:
        rpiSendFrequencyList = [15]
    else:
        rpiSendFrequencyList = [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
    groupRatioListList = [[100,0,0,0,0]]
    overlapIsNecessary = 1
    margin = 1
    widthOfRoad = 3.0
    useOpendataset = 0
    targetOpendatasetFilePath = ""
    reSend = 29

    if groupFlag == 1:
        groupRatioListList = [[66,25,6,2,1]]

    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    return allSettingList

def prepareGroup(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    if targetFlag == 1:
        perTimeList = [1000]
    else:
        perTimeList = [5000]
    rpiSendFrequencyList = [0.270]
    groupRatioListList = [[66,25,6,2,1]]
    globalId = 0
    overlapIsNecessary = 1
    margin = 1
    widthOfRoad = 3.0
    useOpendataset = 0
    targetOpendatasetFilePath = ""
    groupFlag = 1
    reSend = 0


    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2],[500, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2],[500, 0, math.pi/2],[600, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    return allSettingList

def prepareDouble(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    globalId = 0
    if targetFlag == 1:
        perTimeList = [1000]
    else:
        perTimeList = [5000]

    rpiSendFrequencyList = [0.270]
    groupRatioListList = [[100,0,0,0,0]]
    overlapIsNecessary = 1
    margin = 1
    widthOfRoad = 3.0
    useOpendataset = 0
    targetOpendatasetFilePath = ""
    reSend = 0

    if groupFlag == 1:
        groupRatioListList = [[66,25,6,2,1]]

    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1

    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2],[500, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)
                globalId = globalId + 1
    
    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 1200
                receiverSettings = [[100, 0, math.pi/2],[200, 0, math.pi/2],[300, 0, math.pi/2],[400, 0, math.pi/2],[500, 0, math.pi/2],[600, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)
                globalId = globalId + 1
    
    return allSettingList

def prepareDoubleWithOpendata(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    globalId = 0
    perTimeList = [1236]
    groupFlag = 1
    rpiSendFrequencyList = [0.270]
    groupRatioListList = [[66,25,6,2,1]]
    overlapIsNecessary = 1
    margin = 1
    widthOfRoad = 4.8
    useOpendataset = 0
    targetOpendatasetFilePath = ""
    reSend = 0

    if groupFlag == 1:
        groupRatioListList = [[66,25,6,2,1]]

    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 3600
                receiverSettings = [[100, 0, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"

                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1
    
    return allSettingList

def prepareHaba(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    globalId = 0
    if targetFlag == 1:
        perTimeList = [1000]
    else:
        perTimeList = [200,400,600,800,1000,2000,3000,4000,5000]
    rpiSendFrequencyList = [0.270]
    groupRatioListList = [[100,0,0,0,0]]
    withOfRoadList = [3,6,9]
    overlapIsNecessary = 1
    margin = 1
    useOpendataset = 0
    targetOpendatasetFilePath = ""
    reSend = 0

    if groupFlag == 1:
        groupRatioListList = [[66,25,6,2,1]]

    for w in withOfRoadList:
        for i, aTime in enumerate(perTimeList):
            for groupRatioList in groupRatioListList:
                for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                    settingList = []
                    perTime = aTime
                    simulationPeriodTime = 1200
                    receiverSettings = [[100, 0, math.pi/2]]
                    rpiSendFrequency = aRpiSendFrequency
                    antennaGr = 23
                    antennaType = "parabora"
                    widthOfRoad = w

                    loadOrNot = 2
                    settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                    allSettingList.append(settingList)

                    globalId = globalId + 1

    
    return allSettingList


def prepareOpendataset(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag):
    allSettingList = []
    globalId = 0
    perTimeList = [10]
    rpiSendFrequencyList = [0.270]
    groupRatioListList = [[100,0,0,0,0]]
    overlapIsNecessary = 1
    margin = 1
    widthOfRoad = 4.8
    useOpendataset = 1


    rangeOrNot = 1
    
    targetOpendatasetFilePath = ""

    upOrDown = 0
    upOrDown = 1
    basePath = "0"
    groupFlag = 0
    reSend = 0


    if upOrDown == 0:
        basePath = "./personpositioncoord/up/data/person_location_out_0000_"
    else:
        basePath = "./personpositioncoord/down/data/person_location_out_0001_"

    if rangeOrNot == 0:
        daytime = ""
        print("ex.) 2021011520")
        print("Range.) 2021")
        daytime = input("day time (ymdt) : ")

        targetOpendatasetFilePath = basePath + daytime + ".csv"
    else:
        f_year = 2021
        f_month = 2
        f_day = 12
        f_hour = 12
        l_year = 2021
        l_month = 2
        l_day = 12
        l_hour = 13
        

        targetOpendatasetFilePath = concatFileFromDate.allDate(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, basePath)

    for i, aTime in enumerate(perTimeList):
        for groupRatioList in groupRatioListList:
            for j,aRpiSendFrequency in enumerate(rpiSendFrequencyList):
                settingList = []
                perTime = aTime
                simulationPeriodTime = 3600
                receiverSettings = None
                if upOrDown == 0:
                    receiverSettings = [[-5, -1, math.pi/2]]
                else:
                    receiverSettings = [[7, -1, math.pi/2]]
                rpiSendFrequency = aRpiSendFrequency
                antennaGr = 23
                antennaType = "parabora"
                loadOrNot = 2
                settingList = generateSettingList(globalId, simulationPeriodTime, perTime, receiverSettings, rpiSendFrequency, loadOrNot, groupRatioList, antennaGr, antennaType, experimentType, experimentNumber, graphFlag, overlapIsNecessary, margin, widthOfRoad, modelFlag, useOpendataset, targetOpendatasetFilePath, directionFlag, groupFlag, reSend, mixFlag)
                allSettingList.append(settingList)

                globalId = globalId + 1

    return allSettingList

def makeFolder(experimentNumber):

    if os.path.exists("./" + str(experimentNumber)):
        shutil.rmtree("./" + str(experimentNumber))

    os.mkdir("./" + str(experimentNumber))
    os.mkdir("./" + str(experimentNumber) + "/" + "image" + "/")

    return experimentNumber


def main():
    experimentType = -1

    # Do you want to draw a graph?
    # No : 0, Yes : 1
    graphFlag = 0

    # Do you output 3D modeling?
    # No : 0, Yes : 1
    # When 3D modeling, experiment only with the first parameter in the list of parameters.
    modelFlag = 0

    # Mix signal strength of two different devices?
    # No : 0, Yes : 1
    mixFlag = 0

    # Walking direction of pedestrians
    # One-way : 0, Two-way :  1
    directionFlag = 1
    
    # Do pedestrians walk in groups?
    # No : 0, Yes : 1
    groupFlag = 0

    # target
    # paper : 0, test : 1
    targetFlag = 0

    print("Please input experiment type.")
    print("0 : Number of pedestrians")
    print("1 : Number of attacking devices")
    print("2 : Signal transmission frequency")
    print("3 : Pedestrians walk in groups")

    print("5 : Use of Open Data")
    print("6 : Same conditions as Open Data")
    print("7 : Various road widths")
    experimentType = int(input("experiment type : "))
    cores = int(input("How many threads to run in parallel? : "))
    

    allSettingList = []


    if experimentType == 0:
        experimentNumber = 0
        allSettingList = prepareHokousya(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)
    elif experimentType == 1:
        experimentNumber = 1
        allSettingList = prepareDaisu(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)
    elif experimentType == 2:
        experimentNumber = 2
        allSettingList = prepareSyuuki(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)
    elif experimentType == 3:
        experimentNumber = 3
        allSettingList = prepareGroup(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)
    elif experimentType == 4:
        experimentNumber = 4
        allSettingList = prepareDouble(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)
    elif experimentType == 5:
        experimentNumber = 5
        allSettingList = prepareOpendataset(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)
    elif experimentType == 6:
        experimentNumber = 6
        allSettingList = prepareDoubleWithOpendata(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)
    if experimentType == 7:
        experimentNumber = 7
        allSettingList = prepareHaba(experimentType, experimentNumber, graphFlag, modelFlag, directionFlag, groupFlag, mixFlag, targetFlag)

    print("experiment number : " + str(experimentNumber))
    makeFolder(experimentNumber)
    for settingList in allSettingList:
        print(settingList)
        with open("./" + str(experimentNumber) + "/" + "setting.csv", "a") as f:
            f.write(str(settingList) + "\n")

    shutil.copy("./main.py","./" + str(experimentNumber) + "/" + "main.py")

    if modelFlag == 0 and graphFlag == 0:
        try:
            with Pool(processes=cores) as pool:
                pool.map(do,allSettingList)
        
        except Exception as e:
            print(e)
            print(e.args)
    
    # When 3D modeling, experiment only with the first parameter in the list of parameters.
    else:
        do(allSettingList[0])

if __name__ == "__main__":
    main()