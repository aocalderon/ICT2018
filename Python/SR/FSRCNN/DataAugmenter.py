# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 15:03:59 2018

@author: acalderon
"""
import os, glob
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import platform
import h5py

SCALE_FACTOR = 2
PATCH_SIZE   = 32
ratio = int(PATCH_SIZE / SCALE_FACTOR)

data_input  = "/opt/Datasets/BSDS200/"
data_output = "/opt/Datasets/FSRCNN/"
if platform.system() in ["Windows"]:
    data_input  = r"H:\data\SR\FSRCNN\91-image\\"
    data_output = r"H:\data\SR\FSRCNN\data\\"
train_path = data_output + "train"
if not os.path.exists(train_path):
    os.makedirs(train_path)
data_file = os.path.join(train_path,'train.h5')
if os.path.exists(data_file):
    os.remove(data_file)
train_file = h5py.File(data_file, 'a')
train_X = train_file.create_dataset('X', (1,ratio,ratio,1), 
                                       maxshape=(None,ratio,ratio,1),
                                       dtype='float32', 
                                       chunks=(10**2,ratio,ratio,1))    
train_y = train_file.create_dataset('y', (1,PATCH_SIZE,PATCH_SIZE,1), 
                                       maxshape=(None,PATCH_SIZE,PATCH_SIZE,1),
                                       dtype='float32', 
                                       chunks=(10**2,PATCH_SIZE,PATCH_SIZE,1))    
offset = 0   
    
filenames = glob.glob(os.path.join(data_input,"*.png"))
print(len(filenames))
count = 1
#filenames = filenames[0:2]
for filename in filenames:
    image = Image.open(filename)
    image = image.convert('L')
    raw = np.array(image)
    WIDTH  = raw.shape[0]
    HEIGHT = raw.shape[1]
    raw = raw[0:WIDTH - (WIDTH % PATCH_SIZE), 0:HEIGHT - (HEIGHT % PATCH_SIZE)]
    WIDTH  = raw.shape[0]
    HEIGHT = raw.shape[1]
    rows = int(HEIGHT / PATCH_SIZE)
    cols = int(WIDTH  / PATCH_SIZE)
    augmented = 6
    n = augmented * rows * cols
    stride = PATCH_SIZE
    
    print("ImageNumber={}".format(count))
    print("Filename={}".format(filename))
    print("ImageSize={}x{}".format(WIDTH, HEIGHT))
    print("NumberOfPatches={}".format(n))
    
    i = 0
    batch_X = np.empty((n,ratio,ratio,1))
    batch_y = np.empty((n,PATCH_SIZE,PATCH_SIZE,1))
    for row in range(0, rows):
        for col in range(0, cols):
            x = col * stride
            y = row * stride
            # Save normal pair...
            patch = raw[x:x + stride, y:y + stride]
            scale = Image.fromarray(patch, 'L')
            scale = scale.resize((ratio, ratio), Image.BICUBIC)
            scale = np.array(scale)
            batch_X[i] = np.expand_dims(scale, axis=2)
            batch_y[i] = np.expand_dims(patch, axis=2)
            i = i + 1
            count = count + 1
            # Saving horizontal flip...
            flip1 = Image.fromarray(patch, 'L')
            flip1 = np.array(flip1.transpose(Image.FLIP_LEFT_RIGHT))
            scale = Image.fromarray(flip1, 'L')
            scale = scale.resize((ratio, ratio), Image.BICUBIC)
            batch_X[i] = np.expand_dims(scale, axis=2)
            batch_y[i] = np.expand_dims(flip1, axis=2)
            i = i + 1
            count = count + 1
            # Saving vertical flip...
            flip2 = Image.fromarray(patch, 'L')
            flip2 = np.array(flip2.transpose(Image.FLIP_TOP_BOTTOM))
            scale = Image.fromarray(flip2, 'L')
            scale = scale.resize((ratio, ratio), Image.BICUBIC)
            batch_X[i] = np.expand_dims(scale, axis=2)
            batch_y[i] = np.expand_dims(flip2, axis=2)
            i = i + 1
            count = count + 1            
            # Saving 90 degrees rotation...
            rotat = Image.fromarray(patch, 'L')
            rotat = np.array(rotat.rotate(90))
            scale = Image.fromarray(rotat, 'L')
            scale = scale.resize((ratio, ratio), Image.BICUBIC)
            batch_X[i] = np.expand_dims(scale, axis=2)
            batch_y[i] = np.expand_dims(rotat, axis=2)
            i = i + 1
            count = count + 1
            # Saving 180 degrees rotation...
            rotat = Image.fromarray(patch, 'L')
            rotat = np.array(rotat.rotate(180))
            scale = Image.fromarray(rotat, 'L')
            scale = scale.resize((ratio, ratio), Image.BICUBIC)
            batch_X[i] = np.expand_dims(scale, axis=2)
            batch_y[i] = np.expand_dims(rotat, axis=2)
            i = i + 1
            count = count + 1
            # Saving 270 degrees rotation...
            rotat = Image.fromarray(patch, 'L')
            rotat = np.array(rotat.rotate(270))
            scale = Image.fromarray(rotat, 'L')
            scale = scale.resize((ratio, ratio), Image.BICUBIC)
            batch_X[i] = np.expand_dims(scale, axis=2)
            batch_y[i] = np.expand_dims(rotat, axis=2)
            i = i + 1
            count = count + 1

    train_X.resize(offset + n, axis=0)  
    train_X[offset:offset + n,...] = batch_X / 255.
    train_y.resize(offset + n, axis=0)
    train_y[offset:offset + n,...] = batch_y / 255.
    offset = train_X.shape[0]
    
train_file.close()         