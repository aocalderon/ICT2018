# -*- coding: utf-8 -*-
"""
Created on Wed Aug 22 10:43:09 2018

@author: acalderon
"""

import os
import numpy as np
import rasterio
import platform
import h5py
#from PIL import Image

NUMBER_OF_PATCHES = 45072
#NUMBER_OF_PATCHES = 100
AUGMENTORS = 6
PATCH_SIZE = 16

def doFlip(image, direction = 0):
    w = image.shape[0]
    h = image.shape[1]
    c = image.shape[2]
    flip = np.empty((w, h, c))
    for j in range(0, c):
        f = image[:,:,j]
        flip[:,:,j] = np.flip(f, direction)
    return flip

def doRotation(image, times = 1):
    w = image.shape[0]
    h = image.shape[1]
    c = image.shape[2]
    rotation = np.empty((w, h, c))
    for j in range(0, c):
        r = image[:,:,j]
        rotation[:,:,j] = np.rot90(r, times)
    return rotation

data_input  = "/opt/Datasets/BSDS200/"
data_output = "/opt/Datasets/FSRCNN/"
if platform.system() in ["Windows"]:
    data_input  = r"H:\data\SR\FSRCNN\L7\Patches\\"
    data_output = r"H:\data\SR\FSRCNN\L7\\"
train_path = os.path.join(data_output, "VIS2NIR")
if not os.path.exists(train_path):
    os.makedirs(train_path)
data_file = os.path.join(train_path,'VIS2NIR_train.h5')
if os.path.exists(data_file):
    os.remove(data_file)
train_file = h5py.File(data_file, 'w')
X = train_file.create_dataset('X', (NUMBER_OF_PATCHES*AUGMENTORS,PATCH_SIZE,PATCH_SIZE,3), dtype='float32')      
y = train_file.create_dataset('y', (NUMBER_OF_PATCHES*AUGMENTORS,PATCH_SIZE,PATCH_SIZE,1), dtype='float32')                                    
i = 0
n = 1
while i < NUMBER_OF_PATCHES*AUGMENTORS:
    print("Processing patches {} to {} from image {}...".format(i, i + AUGMENTORS - 1, n))
    filename = os.path.join(data_input, "MS_{}.tif".format(n))
    ms = rasterio.open(filename, 'r+')
    image = ms.read().astype('float32')
    for j in [0,1,2]:
        b = image[j]
        imin, imax = np.percentile(b, [1,99])
        b[b > imax] = imax
        b[b < imin] = imin
        b = (b - imin) / (imax - imin)
        X[i,:,:,j] = b
    X[i+1] = doFlip(X[i],0)
    X[i+2] = doFlip(X[i],1)
    X[i+3] = doRotation(X[i],1)
    X[i+4] = doRotation(X[i],2)
    X[i+5] = doRotation(X[i],3)

    b = image[3]
    imin, imax = np.percentile(b, [1,99])
    b[b > imax] = imax
    b[b < imin] = imin
    b = (b - imin) / (imax - imin)
    y[i,:,:,0] = b    
    y[i+1] = doFlip(y[i],0)
    y[i+2] = doFlip(y[i],1)
    y[i+3] = doRotation(y[i],1)
    y[i+4] = doRotation(y[i],2)
    y[i+5] = doRotation(y[i],3)
            
    i = i + AUGMENTORS
    n = n + 1

train_file.close()

