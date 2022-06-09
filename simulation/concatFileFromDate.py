import datetime
import csv
import os

def datetimeToStr(targetDatetime):
    strDatetime = targetDatetime.strftime("%Y%m%d%H")
    return strDatetime

def makeFileList(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, baseFilePath):
    f_year = int(f_year)
    f_month = int(f_month)
    f_day = int(f_day)
    f_hour = int(f_hour)
    l_year = int(l_year)
    l_month = int(l_month)
    l_day = int(l_day)
    l_hour = int(l_hour)


    fileNameList = []

    startDatetime = datetime.datetime(f_year, f_month, f_day, f_hour)
    endDatetime = datetime.datetime(l_year, l_month, l_day, l_hour)

    targetDatetime = startDatetime

    while targetDatetime < endDatetime:
        strTargetDatetime = datetimeToStr(targetDatetime)
        fileNameList.append(baseFilePath + strTargetDatetime + ".csv")
        targetDatetime += datetime.timedelta(hours=1)
    
    return fileNameList

def concat(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, baseFilePath, filePathList):
    startDatetime = datetime.datetime(f_year, f_month, f_day, f_hour)
    endDatetime = datetime.datetime(l_year, l_month, l_day, l_hour)
    strStartDatetime = datetimeToStr(startDatetime)
    strEndDatetime = datetimeToStr(endDatetime)
    fileName = strStartDatetime + "_" + strEndDatetime + ".csv"
    targetFilePath = baseFilePath + fileName
    if os.path.exists(targetFilePath):
        os.remove(targetFilePath)
    allRowList = []

    for j,filePath in enumerate(filePathList):
        with open(filePath, "r") as f:
            csvReader = csv.reader(f)
            for i,row in enumerate(csvReader):
                if i == 0 and j != 0:
                    continue
                allRowList.append(row)
    
    with open(targetFilePath,"a",newline="") as f:
        writer = csv.writer(f)

        for row in allRowList:
            writer.writerow(row)
        
    return targetFilePath

def allDate(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, baseFilePath):
    f_year = int(f_year)
    f_month = int(f_month)
    f_day = int(f_day)
    f_hour = int(f_hour)
    l_year = int(l_year)
    l_month = int(l_month)
    l_day = int(l_day)
    l_hour = int(l_hour)

    filePathList = makeFileList(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, baseFilePath)
    targetFilePath = concat(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, baseFilePath, filePathList)

    return targetFilePath

    
if __name__ == "__main__":
    baseFilePath = "./personpositioncoord/up/data/person_location_out_0000_"


    f_year = int(2021)
    f_month = int(1)
    f_day = int(16)
    f_hour = int(2)
    l_year = int(2021)
    l_month = int(1)
    l_day = int(21)
    l_hour = int(3)

    filePathList = makeFileList(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, baseFilePath)
    concat(f_year, f_month, f_day, f_hour,l_year, l_month, l_day, l_hour, baseFilePath, filePathList)

    print(filePathList)