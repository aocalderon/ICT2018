# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 15:02:37 2018

@author: acalderon
"""

import os
import platform
import random
import h5py
import matplotlib.pyplot as plt

data_path  = "/opt/ICT2018/Python/SR/FSRCNN"
if platform.system() in ["Windows"]:
    data_path = r"H:/data/Sat-6"

dataset = h5py.File(os.path.join(data_path, 'sat-6-full.h5'), 'r')
X = dataset.get('X')
Y = dataset.get('Y')
print(X.shape)
print(Y.shape)

def showPatch(i):
    print("Showing patch {} from {} possible...".format(i, X.shape[0]))
    for j in range(0,4):
        plt.subplot(1,4,j+1)
        if j < 3:
            plt.imshow(X[i,:,:,j], cmap='Greys')
        else:
            plt.imshow(Y[i,:,:,0], cmap='Greys')

i = random.randrange(X.shape[0])
showPatch(i)