#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 10:44:35 2018

@author: and
"""
#%%
import os
import numpy as np
import cv2
from img_utils import transform_images, image_generator, make_patches, combine_patches
from scipy.misc import imsave, imread, imresize
from keras.models import Model
from keras.layers import Input
from keras.layers.convolutional import Conv2D
import keras.optimizers as optimizers
from losses import PSNRLoss, SSIM

#%%
scaling_factor = 4
batch_size = 64
suffix = "intermidiate_"

base_dataset = "/opt/EuroSAT/Test/"
init_train_path = base_dataset + "images/train/"
init_valid_path = base_dataset + "images/valid/"
train_path = base_dataset + "train/"
valid_path = base_dataset + "valid/"

if not os.path.exists(train_path):
    os.makedirs(train_path)
if not os.path.exists(valid_path):
    os.makedirs(valid_path)
transform_images(init_train_path, train_path, scaling_factor=scaling_factor)
transform_images(init_valid_path, valid_path, scaling_factor=scaling_factor)

#%%

verbose = True
width    = 128
height   = 128
channels = 3

shape = (width, height, channels)
init = Input(shape=shape)
x = Conv2D(64, (9, 9), activation='relu', padding='same', name='level1')(init)
x = Conv2D(32, (1, 1), activation='relu', padding='same', name='level2')(x)
out = Conv2D(channels, (3, 3), padding='same', name='output')(x)
model = Model(init, out)
adam = optimizers.Adam(lr=1e-3)
model.compile(optimizer=adam, loss='mse', metrics=[PSNRLoss, SSIM])

from keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(rescale=1./255)
valid_datagen = ImageDataGenerator(rescale=1./255)
train_generator = train_datagen.flow_from_directory(train_path,
                                                    target_size=(128, 128),
                                                    batch_size=20)
valid_generator = valid_datagen.flow_from_directory(valid_path,
                                                    target_size=(128, 128),
                                                    batch_size=20)

print("Training model...")
model.fit_generator(train_generator,
                    steps_per_epoch = 10,
                    epochs = 128, 
                    validation_data = valid_generator,
                    validation_steps = 10)

#%%

img_path = "/opt/EuroSAT/Test/output/Highway_47.jpg"
#img_path = "/opt/EuroSAT/Test/output/Highway_58.jpg"
#img_path = "/opt/EuroSAT/Test/output/Highway_63.jpg"
path = os.path.splitext(img_path)
filename = path[0] + "_" + suffix + "(%dx)" % (scaling_factor) + path[1]
true_img = imread(img_path, mode='RGB')
init_dim_1, init_dim_2 = true_img.shape[0], true_img.shape[1]
if verbose: 
    print("Old Size : ", true_img.shape)
    print("New Size : (%d, %d, 3)" % (init_dim_1 * scaling_factor, init_dim_2 * scaling_factor))

inter_img = imresize(true_img, (width, height))
conv_img = inter_img.astype(np.float32) / 255.
conv_img = np.expand_dims(conv_img, axis=0)
result = model.predict(conv_img, batch_size=64, verbose=verbose)

result = cv2.pyrUp(result[0])
result = cv2.medianBlur(result, 3)
result = cv2.pyrDown(result)

import matplotlib.pyplot as plt
plt.imshow(true_img)
plt.imshow(inter_img)
plt.imshow(result)

if verbose: print("De-processing image Completed!!!")
if verbose: print("Saving image...")
imsave(filename, result)

#%%

img_path = "/opt/EuroSAT/Test/output/Highway_47.jpg"
#img_path = "/opt/EuroSAT/Test/output/Highway_58.jpg"
#img_path = "/opt/EuroSAT/Test/output/Highway_63.jpg"
path = os.path.splitext(img_path)
filename = path[0] + "_" + suffix + "(%dx)" % (scaling_factor) + path[1]
true_img = imread(img_path, mode='RGB')
init_dim_1, init_dim_2 = true_img.shape[0], true_img.shape[1]
if verbose: 
    print("Old Size : ", true_img.shape)
    print("New Size : (%d, %d, 3)" % (init_dim_1 * scaling_factor, init_dim_2 * scaling_factor))

images = make_patches(true_img, scaling_factor, patch_size, verbose)

nb_images = images.shape[0]
img_dim_1, img_dim_2 = images.shape[1], images.shape[2]
print("Number of patches = %d, Patch Shape = (%d, %d)" % (nb_images, img_dim_2, img_dim_1))

if verbose: print("Saving intermediate image...")
fn = path[0] + "_intermediate_" + path[1]
intermediate_img = imresize(true_img, (init_dim_1 * scaling_factor, init_dim_2 * scaling_factor))
imsave(fn, intermediate_img)

img_conv = images.astype(np.float32) / 255.

result = model.predict(img_conv, batch_size=64, verbose=verbose)
if verbose: print("De-processing images...")
result = result.astype(np.float32) * 255.

out_shape = (init_dim_1 * scaling_factor, init_dim_2 * scaling_factor, 3)
result = combine_patches(result, out_shape, scaling_factor)

result = np.clip(result, 0, 255).astype('uint8')

result = cv2.pyrUp(result)
result = cv2.medianBlur(result, 3)
result = cv2.pyrDown(result)

if verbose: print("De-processing image Completed!!!")
if verbose: print("Saving image...")
imsave(filename, result)