#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import getopt

testtime = "5s"
testtype = "copy"
testwpara = "S0:2MB:4"  #kB,MB,GB


testlist = []
os.system("rm -rf bench.txt")
os.system("likwid-bench -a > bench.txt")
with open("bench.txt",'r') as file_read:
    while True:
        strline = file_read.readline()
        if not strline:
            break
        testlist.append(strline.split(" ")[0])
os.system("rm -rf bench.txt")
for item in testlist:
    cmd = "likwid-bench -t %s -s %s -w %s"%(item,testtime,testwpara)
    print("test item : %s"%(cmd))
    os.system(cmd)
#os.system("likwid-bench  -t stream -s 5s-w S0:20kB:4")





