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
train_path = os.path.join(data_output, "EIR")
dataset = h5py.File(os.path.join(train_path,'train.h5'), 'r')
X = dataset.get('X')
y = dataset.get('y')
print(X.shape)
print(y.shape)

i = random.randrange(X.shape[0])
print("Showing pair {} from {} possible...".format(i, X.shape[0]))
plt.subplot(121)
plt.imshow(X[i,:,:,0], cmap='Greys')
plt.subplot(122)
plt.imshow(y[i,:,:,0], cmap='Greys')

