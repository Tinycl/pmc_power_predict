#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import getopt
import os

loopcount= int(sys.argv[1])
sampletime = 1300000000  #ns
index = 0
outfilename = "out.csv"
os.system("rm -rf out.csv")
outfilehandle = open(outfilename, 'a+')

titlelist = []
def processtitle():
    titlelist.append("PKG")
    titlelist.append("PP0")
    titlelist.append("PP1")
    titlelist.append("DRAM")
    with open("perf0.txt", 'r') as file_read:
        while True:
            strline = file_read.readline()
            if not strline:
                break
            strval = filter(None,strline.split(" "))
            if strval[-1][0] == "(":
                titlelist.append(strval[1])
    strtitle= ""
    for item in titlelist:
        strtitle = strtitle + item + ","
    #print(strtitle[:-1])
    outfilehandle.write(strtitle[:-1])
    outfilehandle.write("\n")
    return

datadict = {}
def mkdatadict():
    datadict.clear()
    for item  in titlelist:
        if item not in datadict.keys():
            datadict[item] = ""
    return

def processdata():
    index = 0
    while index < loopcount:
        inpowerfilename = "power%d.txt"%(index)
        powerlineno = 0
        with open(inpowerfilename, 'r') as power_read:
            while True:
                strlinepower = power_read.readline()
                if not strlinepower:
                    break
                powerlineno = powerlineno + 1
                if powerlineno == 11:
                    datadict[titlelist[0]] = strlinepower.split(" ")[2]
                if powerlineno == 14:
                    datadict[titlelist[1]] = strlinepower.split(" ")[2]
                if powerlineno == 17:
                    datadict[titlelist[2]] = strlinepower.split(" ")[2]
                if powerlineno == 20:
                    datadict[titlelist[3]] = strlinepower.split(" ")[2]

        inperffilename = "perf%d.txt"%(index)
        perflineno = 0
        with open(inperffilename, 'r') as perf_read:
            while True:
                strlineperf = perf_read.readline()
                if not strlineperf:
                    break
                perflineno = perflineno + 1
                strval = filter(None,strlineperf.split(" "))
                if strval[-1][0] == "(":
                    datadict[strval[1]] = str(float(strval[0].replace(",","")) / sampletime)
        
        strdata = ""
        for item in titlelist:
            strdata = strdata + datadict[item] + ","
        outfilehandle.write(strdata[:-1])
        outfilehandle.write("\n")
        index = index + 1

if __name__ == "__main__":
    processtitle()
    mkdatadict()
    processdata()

