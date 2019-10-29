#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import getopt
import os
import multiprocessing
import time


loopcount =int(sys.argv[1])
infilename = "eventconfig.txt"

def powerworker():
    powerindex = 0
    while powerindex < loopcount:
        powercmd = "likwid-powermeter -s 250ms > power%d.txt "%(powerindex)
        os.system(powercmd)
        powerindex = powerindex + 1

def perfworker():
    perfindex = 0
    while perfindex < loopcount:
        perfcmd = "sudo perf stat -o perf%d.txt -e branch-instructions,branch-misses,bus-cycles,cache-misses,cache-references,cpu-cycles,instructions,ref-cycles,L1-dcache-load-misses,L1-dcache-loads,L1-dcache-stores,L1-icache-load-misses,LLC-load-misses,LLC-loads,LLC-store-misses,LLC-stores,branch-load-misses,branch-loads,dTLB-load-misses,dTLB-loads,dTLB-store-misses,dTLB-stores,iTLB-load-misses,iTLB-loads,node-load-misses,node-loads,node-store-misses,node-stores  -d -d -d -a sleep 0.25 "%(perfindex)
        os.system(perfcmd)
        perfindex = perfindex + 1

def sampleworker():
    strevent = ""
    with open(infilename,'r') as file_read:
        while True:
            strline = file_read.readline()
            if not strline:
                break
            if strline.split(" ")[1].split("\n")[0]:
                strevent = strevent + strline.split(" ")[1].split("\n")[0] + ","       
    index = 0
    while index < loopcount:
        powercmd = "likwid-powermeter -s 1300ms > power%d.txt "%(index)
        perfcmd = "sudo perf stat -e %s -d -d -d  -o perf%d.txt  -a sleep 1.3 "%(strevent[:-1],index)
        os.system(powercmd)
        os.system(perfcmd)
        index = index + 1

if __name__ == "__main__":
    #powerprocess = multiprocessing.Process(target = powerworker,)
    #perfprocess = multiprocessing.Process(target = perfworker,)
    #powerprocess.start()
    #perfprocess.start()
    os.system("sudo modprobe msr")
    sampleworker()
