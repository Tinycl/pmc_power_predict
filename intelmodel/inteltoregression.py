#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn import datasets,linear_model
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn import metrics


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
DATA_MATRIX = DATA[stritems]
print("DATA dimension",DATA_MATRIX.shape)
#print("DATA is \n", DATA_MATRIX.head())
strdvitems = stritems[0:4]
print(strdvitems)
del stritems[0:4]
print(stritems)
IV_MATRIX =   DATA[stritems]
#print("IV \n",IV_MATRIX)
DV_PKG = DATA[strdvitems[0]]
DV_PP0 = DATA[strdvitems[1]]
print("PP0:\n",DV_PP0.head())
DV_PP1 = DATA[strdvitems[2]]
DV_DRAM = DATA[strdvitems[3]]
IV_train,IV_test,PP0_train,PP0_test = train_test_split(IV_MATRIX,DV_PP0,test_size=0.6,random_state=0)
print("IV train dimension ", IV_train.shape)
print("IV test dimension ", IV_test.shape)
print("PP0 train dimension ", PP0_train.shape)
print("PP0 test dimension ", PP0_test.shape)
print("IV train head\n", IV_train.head())

print("random data training")
linreg = LinearRegression()
linreg.fit(IV_train,PP0_train)
print("intercept:\n",linreg.intercept_)
print("coefficients:\n",linreg.coef_)
PP0_lin_pred = linreg.predict(IV_test)
print("PP0 MSE:\n",metrics.mean_squared_error(PP0_test,PP0_lin_pred))
print("PP0 RMSE:\n",np.sqrt(metrics.mean_squared_error(PP0_test,PP0_lin_pred)))

plt.figure()
plt.plot(range(len(PP0_test)),PP0_test, 'b', label="real value")
plt.plot(range(len(PP0_lin_pred)),PP0_lin_pred, 'r', label="predict value")
plt.legend()
plt.show()


plt.figure()
plt.plot(range(len(PP0_lin_pred-PP0_test)), (PP0_lin_pred-PP0_test),'r', label="error")
plt.legend()
plt.show()

plt.figure()
plt.scatter(PP0_test, PP0_lin_pred)
plt.plot([PP0_test.min(),PP0_test.max()],[PP0_lin_pred.min(),PP0_lin_pred.max()],'k--')
plt.xlabel('real')
plt.ylabel('linepredict')
plt.legend()
plt.show()

print("all data training")
linreg1 = LinearRegression()
linreg1.fit(IV_MATRIX,DV_PP0)
print("intercept1:\n",linreg1.intercept_)
print("coefficients1:\n",linreg1.coef_)
lin_pred1 = linreg1.predict(IV_MATRIX)
print("PP0 MSE1:\n",metrics.mean_squared_error(DV_PP0,lin_pred1))
print("PP0 RMSE1:\n",np.sqrt(metrics.mean_squared_error(DV_PP0,lin_pred1)))
plt.figure()
plt.plot(range(len(DV_PP0)),DV_PP0, 'b', label="real value")
plt.plot(range(len(lin_pred1)),lin_pred1, 'r', label="predict value")
plt.legend()
plt.show()

"""
poly = PolynomialFeatures(degree = 3)
IV_poly_train = poly.fit_transform(IV_train)
polyreg = LinearRegression()
polyreg.fit(IV_poly_train,PP0_train)

IV_poly_test = poly.fit_transform(IV_test)
PP0_poly_pred = polyreg.predict(IV_poly_test)

plt.scatter(PP0_test,PP0_poly_pred)
plt.plot([PP0_test.min(),PP0_test.max()],[PP0_poly_pred.min(),PP0_poly_pred.max()],'k--')
plt.xlabel('real')
plt.ylabel('polypredict')
plt.show()
"""




 
