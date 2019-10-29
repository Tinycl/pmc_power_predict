#!/usr/bin/python
# -*- coding: UTF-8 -*-


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

infilename = "out.csv"
stritems = []
lineno = 0
with open(infilename,'r') as file_read:
    while True:
        strline = file_read.readline()
        if not strline:
            break
        lineno = lineno + 1
        stritems = strline[:-1].split(",")
        if lineno == 1:
            break
DATA = pd.read_csv('out.csv')
print(DATA.corr())
DATA.corr().to_csv("corr.csv")
DATASET = DATA[stritems]

#sns.pairplot(DATA)
#plt.show()
#sns.pairplot(DATA,huge='PP0')
sns.distplot(DATA['PP0'])
plt.show()




 
