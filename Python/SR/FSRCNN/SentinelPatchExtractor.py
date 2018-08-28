#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 11:55:40 2018

@author: and
"""

import os
import numpy as np
import platform
import h5py
from osgeo import gdal
from skimage.util.shape import view_as_windows

PATCH_SIZE   = 32
SCALE_FACTOR = 2
CHANNELS     = 4
RATIO        = PATCH_SIZE / SCALE_FACTOR

data_input  = "/opt/GISData/Sentinel/"
if platform.system() in ["Windows"]:
    data_input  = r"H:\L7\Output\\"
train_path = os.path.join(data_input, "Patches")
if not os.path.exists(train_path):
    os.makedirs(train_path)

def normalize(b):
    imin, imax = np.percentile(b, [1,99])
    b[b > imax] = imax
    b[b < imin] = imin
    b = (b - imin) / (imax - imin)
    return(b)

filename = os.path.join(data_input, "S_1.tif")
s = gdal.Open(filename)
s = np.array(s.GetRasterBand(1).ReadAsArray())
image = np.empty((s.shape[0], s.shape[1], CHANNELS))
image[:,:,0] = normalize(s)
filename = os.path.join(data_input, "S_2.tif")
s = gdal.Open(filename)
s = np.array(s.GetRasterBand(1).ReadAsArray())
image[:,:,1] = normalize(s)
filename = os.path.join(data_input, "S_3.tif")
s = gdal.Open(filename)
s = np.array(s.GetRasterBand(1).ReadAsArray())
image[:,:,2] = normalize(s)
filename = os.path.join(data_input, "S_4.tif")
s = gdal.Open(filename)
s = np.array(s.GetRasterBand(1).ReadAsArray())
image[:,:,3] = normalize(s)

patches = view_as_windows(image, (PATCH_SIZE,PATCH_SIZE, CHANNELS), PATCH_SIZE)
n = patches.shape[0] * patches.shape[1]
patches = np.reshape(patches, (n, PATCH_SIZE, PATCH_SIZE, CHANNELS))

data_file = os.path.join(train_path, 'sentinel.h5')
if os.path.exists(data_file):
    os.remove(data_file)
train_file = h5py.File(data_file, 'w')
X = train_file.create_dataset('X', data=patches)    
train_file.close() 
