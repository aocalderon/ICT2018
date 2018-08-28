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

data_path = "/opt/GISData/Sentinel/Patches/"
if platform.system() in ["Windows"]:
    data_path = r"H:\data\SR\FSRCNN\\"
dataset = h5py.File(os.path.join(data_path,'sentinel.h5'), 'r')
X = dataset.get('X')
print(X.shape)

def showPatch(i):
    print("Showing patch {} from {} possible...".format(i, X.shape[0]))
    for j in range(0,4):
        plt.subplot(1,4,j+1)
        plt.imshow(X[i,:,:,j], cmap='Greys')

i = random.randrange(X.shape[0])
showPatch(i)