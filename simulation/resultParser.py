import csv
from curses.ascii import NL
import pprint
import statistics

def idToExperimentNumberList(theId):
    return [theId]

def labelMakerForNumber7():
    nList = [200,400,600,800,1000,2000,3000,4000,5000]
    wList = [3,6,9]
    labelList = []

    for w in wList:
        for n in nList:
            labelList.append("( " + str(w) + " : " + str(n) + " )")
    return labelList

def do(experimentNumber):
    endFlag = 0
    sdList = []
    filePath = str(experimentNumber) + "/result.csv"

    x = []
    labelList = []
    labelType = ""
    if experimentNumber == 0:
        labelList = [200,400,600,800,1000,2000,3000,4000,5000]
        labelType = "N"
        for i in range(len(labelList)):
            x.append(i)
    elif experimentNumber == 1:
        labelList = [1,2,3,4,5,6]
        labelType = "L"
        for i in range(len(labelList)):
            x.append(i)
    elif experimentNumber == 2:
        labelList = [3, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        labelType = "L"
        for i in range(len(labelList)):
            x.append(i)
    elif experimentNumber == 3:
        labelList = [1,2,3,4,5,6]
        labelType = "L"
        for i in range(len(labelList)):
            x.append(i)
    elif experimentNumber == 5:
        labelList = [1]
        labelType = "L"
        for i in range(len(labelList)):
            x.append(i)
    elif experimentNumber == 6:
        labelList = [1]
        labelType = "L"
        for i in range(len(labelList)):
            x.append(i)
    elif experimentNumber == 7:
        labelList = labelMakerForNumber7()
        labelType = "(W,N)"
        for i in range(len(labelList)):
            x.append(i)
    else:
        labelType = "DUMMY"
        for i in range(10):
            x.append(i)
    
    print(str(labelType) + "& m = 1 & m = 2 & m = 3 & m = 4 & m = 5 \\\\", end="")

    linkedCountList = [1,2,3,4,5]
    resultList = []

    for theId in range(len(x)):
        print("\n" +str(labelList[theId]) + " & ",end="")
        experimentNumberList = idToExperimentNumberList(theId)

        for linkedCount in linkedCountList:
            resultList = []
            sumAccuracy = 0
            for experimentNumber in experimentNumberList:
                with open(filePath) as f:
                    reader = csv.reader(f)

                    for row in reader:
                        globalId = int(row[0])
                        linkCount = int(row[1])
                        accuracy = float(row[2])

                        if globalId == experimentNumber and linkCount == linkedCount:
                            resultList.append(accuracy)


            sumAccuracy = sum(resultList)
            
            result = sumAccuracy

            if linkedCount == 1:
                resultList.append(result)
            
            if linkedCount == linkedCountList[0]:
                print("{:.1f}".format(result)  + " & ", end="")
            elif linkedCount != linkedCountList[-1]:
                print("{:.1f}".format(result)  + " & ", end="")
            else:
                print("{:.1f}".format(result)  + " \\\\ ", end="")
    # print(resultList)


if __name__ == "__main__":
    experimentNumber = int(input("Experiment type : "))

    do(experimentNumber)