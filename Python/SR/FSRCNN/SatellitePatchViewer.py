#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 10:26:58 2018

@author: and
"""
import os
import matplotlib.pyplot as plt
import h5py
import platform
import random

data_output = "/opt/Datasets/FSRCNN/"
if platform.system() in ["Windows"]:
    data_output = r"H:\data\SR\FSRCNN\\"
train_path = os.path.join(data_output, "L7")
dataset = h5py.File(os.path.join(train_path,'train.h5'), 'r')
X = dataset.get('X')
y = dataset.get('y')
print(X.shape)
print(y.shape)

def showPatch(i):
    print("Showing patch {} from {} possible...".format(i, X.shape[0]))
    for j in range(0,5):
        plt.subplot(1,5,j+1)
        if j < 4:
            plt.imshow(X[i,:,:,j], cmap='Greys')
        else:
            plt.imshow(y[i,:,:,0], cmap='Greys')

i = random.randrange(X.shape[0])
showPatch(i)