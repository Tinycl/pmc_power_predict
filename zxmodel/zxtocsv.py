#!/usr/bin/python
import os
import sys
import time

outfilename = "zxout.csv"
os.system("rm -rf zxout.csv")
outfilehandle = open("zxout.csv","a+")
loopcount = 0
samplecount = int(sys.argv[1])

sampletime = 200000000
titlelist = []
resultdata = {}
def  GetCSVTitle():
    
    with open("powerout0.txt", 'r') as file_read:
        while True:
            strline = file_read.readline()
            if not strline:
                break
            if strline.strip("\n") != "":
                titlelist.append(strline.strip("\n").split(":")[0])

    with open("pmcout0.txt", 'r') as file_read:
        while True:
            strline = file_read.readline()
            if not strline:
                break
            if strline.strip("\n") != "":
                titlelist.append(strline.strip("\n").split(":")[0])
    strtitle = ""
    for item in titlelist:
        strtitle = strtitle + item + ","
    outfilehandle.write(strtitle[:-1])
    outfilehandle.write("\n")

def WriteDataToCSV():
    loopcount = 0
    while loopcount < samplecount:
        resultdata.clear()
        powerfilename = "powerout%d.txt"%(loopcount)
        pmcfilename = "pmcout%d.txt"%(loopcount)
        with open(powerfilename, "r") as power_read:
            while True:
                strline = power_read.readline()
                if not strline:
                    break
                if strline.strip("\n") != "":
                    resultdata[strline.strip("\n").split(":")[0]] = strline.strip("\n").split(":")[1]
        with open(pmcfilename, "r") as pmc_read:
            while True:
                strline = pmc_read.readline()
                if not strline:
                    break
                if strline.strip("\n") != "":
                    resultdata[strline.strip("\n").split(":")[0]] = str(float(strline.strip("\n").split(":")[1]) / sampletime)   
        strdata = ""
        for item in titlelist:
            strdata = strdata + resultdata[item] + ","
        outfilehandle.write(strdata[:-1])
        outfilehandle.write("\n")
        loopcount = loopcount + 1
      
if __name__ == '__main__':
    GetCSVTitle()
    WriteDataToCSV()
