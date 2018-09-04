# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 14:43:01 2018

@author: acalderon
"""

import scipy.io
import os
import platform
import numpy as np 
import h5py

data_in  = "/opt/ICT2018/Python/SR/FSRCNN"
data_out = "/opt/ICT2018/Python/SR/FSRCNN"
if platform.system() in ["Windows"]:
    data_in  = r"C:/Users/acalderon/Downloads/SAT-4_and_SAT-6_datasets.tar/SAT-4_and_SAT-6_datasets"
    data_out = r"H:/data/Sat-6"

sat6 = scipy.io.loadmat(os.path.join(data_in, 'sat-6-full.mat'))

bands = np.transpose(sat6['train_x'], (3,0,1,2))
print(bands.shape)

data_file = os.path.join(data_out, 'sat-6-full_int.h5')
if os.path.exists(data_file):
    os.remove(data_file)

train_file = h5py.File(data_file, 'w')
X = bands[:,:,:,0:3]
train_file.create_dataset('X', data=X)
Y = np.expand_dims(bands[:,:,:,3], axis = 3)
train_file.create_dataset('Y', data=Y)    
train_file.close() 
