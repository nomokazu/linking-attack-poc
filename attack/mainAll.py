import cv2
import os
import datetime
import time
import subprocess
import sys
import signal
import shutil
from scapy.all import *
import pprint
import binascii
import Levenshtein
import numpy as numpy
import matplotlib.pyplot as plt
from multiprocessing import Pool, Process
import hashlib
import csv

def goodToHash(targetFilePath):
    try:
        targetDir = targetFilePath + "/"
        timeStampList = []
        rpiList = []
        rssiList = []

        with open(targetDir + "0_GoodData.csv") as f:
            reader = csv.reader(f)

            for row in reader:
                timeStamp = row[0]
                rpi = row[1]
                rssi = row[2]

                timeStampList.append(timeStamp)
                rpiList.append(rpi)
                rssiList.append(rssi)
            f.close()


        with open(targetDir + "0_GoodData_Hash.csv", "a") as ff:
            for i in range(len(timeStampList)):
                ff.write(str(timeStampList[i]) + "," + str(hashlib.sha224(rpiList[i].encode()).hexdigest()) + "," + str(rssiList[i]) + ",\n")    
    except:
        None



def makeFileList(basePath, timeList ,experimentNumber ,deviceNumber, cameraNumberNotDevice):
    with open( str(basePath) + '/' + str(experimentNumber) + '/' + str(deviceNumber) + '/' + str(deviceNumber) + '_' + 'timeList' + "_" + str(cameraNumberNotDevice), mode='w') as f:
        f.writelines('\n'.join(timeList))
        f.close()

def saveFrameImagesFromCamera(settingList):
    doingTime = settingList[0]
    deviceNumber = settingList[1]
    experimentNumber = settingList[2]
    basePath = settingList[3]
    cameraNumber = settingList[4]
    startTime = settingList[5]
    cameraNumberNotDevice = settingList[6]

    ext = "jpg"
    windowName = "capturedWindow"
    cap = cv2.VideoCapture(cameraNumber)
    timeList = []
    delay = 1

    if not cap.isOpened():
        print("Could not open capture")
        return
    
    while True:
        try:
            ret, frame = cap.read()
            cv2.imshow(windowName, frame)

            if cv2.waitKey(delay) & 0xFF == ord('q'):
                break

            nowTime = time.time()

            if nowTime > startTime + doingTime:
                break
            
            savePath = str(basePath) + '/' + str(experimentNumber) + '/' + str(deviceNumber) + '/' + str(deviceNumber) + '_' + str(cameraNumberNotDevice) + "_"+ str(nowTime) + '.' + str(ext)
            cv2.imwrite( savePath, frame )
            timeList.append(str(nowTime))
    
        except:
            print("Error")
            break

        makeFileList(basePath, timeList, experimentNumber ,deviceNumber,cameraNumberNotDevice )


def captureProcessExec(doingTime, deviceNumber, experimentNumber, basePath, cameraNumber1, cameraNumber2):
    startTime = time.time()

    settingList = [
        [doingTime, deviceNumber, experimentNumber, basePath, cameraNumber1, startTime,0],
        [doingTime, deviceNumber, experimentNumber, basePath, cameraNumber2, startTime,1]
    ]

    with Pool(processes=2) as pool:
        pool.map(saveFrameImagesFromCamera,settingList)


def dirCheck(basePath ,experimentNumber, deviceNumber):
    filePathList = []

    filePathList.append(str(basePath))
    filePathList.append(str(basePath) + '/' + str(experimentNumber))
    filePathList.append(str(basePath) + '/' + str(experimentNumber) + '/' + str(deviceNumber))

    for filePath in filePathList:
        if not os.path.exists(filePath):
            os.makedirs(filePath)


def makeRpiList(filePath):
    RPIList = []

    packets = rdpcap(filePath)

    for packet in packets:
        try:
            packetuuid = packet['EIR_CompleteList16BitServiceUUIDs'].svc_uuids
            packetpayload = binascii.hexlify(packet['Raw'].load)
            packetsignaldbm = packet['BTLE_RF'].signal
            rpi = packetpayload[:32]
            aem = packetpayload[32:]
            PacketType = packet['BTLE_ADV'].PDU_type
            packetTime = packet.time
            if packetuuid == [0xFD6F]:
                checkFlag = 0
                for targetRPI in RPIList:
                    if Levenshtein.distance(rpi.decode(), targetRPI) <= 0:
                        checkFlag = 1
                        break
                
                if checkFlag == 0:
                    RPIList.append(rpi.decode())
                        
        except:
            None
    
    return RPIList

def makeGoodData(allRpiList, filePath, targetFilePath, experimentNumber):
    packets = rdpcap(filePath)

    with open(targetFilePath + "/" + "0_GoodData.csv", "a") as f:

        for packet in packets:
            try:
                packetuuid = packet['EIR_CompleteList16BitServiceUUIDs'].svc_uuids
                packetpayload = binascii.hexlify(packet['Raw'].load)
                packetsignaldbm = packet['BTLE_RF'].signal
                rpi = packetpayload[:32]
                aem = packetpayload[32:]
                PacketType = packet['BTLE_ADV'].PDU_type
                packetTime = packet.time
                if packetuuid == [0xFD6F] or packetuuid == [0xFD7F]:
                    f.write(str(packetTime) + "," + str(rpi.decode()) + "," + str(packetsignaldbm) + ",\n")
            except:
                None
        f.close()

    goodToHash(targetFilePath)

    ## if you want to delete raw data ##
    # os.remove(filePath)
    # os.remove(targetFilePath + "/" + "0_GoodData.csv")


def pcapToMainGoodCSV(pcapFilePath, targetFilePath, experimentNumber):
    filePath = pcapFilePath

    allRpiList = makeRpiList(filePath)

    print(len(allRpiList))

    makeGoodData(allRpiList, filePath, targetFilePath, experimentNumber)


def copyPcap(basePath, experimentNumber, deviceNumber):
    shutil.copy2(str(experimentNumber) + ".pcap", str(basePath) + '/' + str(experimentNumber) + '/' + str(deviceNumber) + '/' + 'result.pcap')

    copyedPcap = str(basePath) + '/' + str(experimentNumber) + '/' + str(deviceNumber) + '/' + 'result.pcap'
    targetFilePath = str(basePath) + '/' + str(experimentNumber) + '/' + str(deviceNumber)
    pcapToMainGoodCSV(copyedPcap, targetFilePath, experimentNumber)

def myExec(doingTime, deviceNumber, experimentNumber, basePath, cameraNumber1, cameraNumber2):
    btleFileName = str(basePath) + '/' + str(experimentNumber) + '/' + str(deviceNumber) + '/' + 'result.pcap'
    captureProcessExec(doingTime, deviceNumber, experimentNumber, basePath, cameraNumber1, cameraNumber2)

    time.sleep(5)

    print("Video capture has been completed.")

    print("Terminate the ubertooth capture by pressing Ctrl +C in the terminal where the ubertooth capture is running")
    finish = input("Enter (y) when you have finished capturing by ubertooth : ")

    copyPcap(basePath,experimentNumber, deviceNumber)


if __name__ == "__main__":
    experimentNumber = int(input("Experiment Number : "))
    print("Execute the following command in the same directory on another terminal before proceeding.")
    print("Command : ubertooth-btle -n -q "+str(experimentNumber)+".pcap")
    deviceNumber = 0
    doingTime = int(input("Run Time : "))
    cameraNumber1 = int(input("Camera Number Side : "))
    cameraNumber2  = int(input("Camera Number Front : "))
    
    basePath = "./data"
    dirCheck(basePath, experimentNumber, deviceNumber)
    myExec(doingTime, deviceNumber, experimentNumber, basePath, cameraNumber1, cameraNumber2)