#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 09:57:42 2018

@author: and
"""
#%%
import os
from img_utils import transform_images, image_generator
import matplotlib.pyplot as plt
from keras import backend as K
from keras.models import Model
from keras.layers import Input, BatchNormalization, Activation, Add
from keras.layers.convolutional import Conv2D, UpSampling2D
import keras.optimizers as optimizers
from losses import PSNRLoss

CREATE_TRAIN_VALID_DATASETS = True

scaling_factor = 4
size = 64
channels = 3
batch_size = 128
base_dataset = "/opt/EuroSAT/Test2/"
train_path = base_dataset + "train/"
valid_path = base_dataset + "valid/"

#%%
if CREATE_TRAIN_VALID_DATASETS:
    init_train_path = base_dataset + "images/train/"
    init_valid_path = base_dataset + "images/valid/"
    
    if not os.path.exists(train_path):
        os.makedirs(train_path)
    if not os.path.exists(valid_path):
        os.makedirs(valid_path)
        
    transform_images(init_train_path, train_path, size, scaling_factor=scaling_factor)
    transform_images(init_valid_path, valid_path, size, scaling_factor=scaling_factor)

#%%

shape = (size, size, channels)

def residual_block(ip, id):
    channel_axis = 1 if K.image_data_format() == 'channels_first' else -1
    init = ip

    x = Conv2D(64, (3, 3), activation='linear', padding='same', name='sr_res_conv_' + str(id) + '_1')(ip)
    x = BatchNormalization(axis=channel_axis, name="sr_res_batchnorm_" + str(id) + "_1")(x, training=False)
    x = Activation('relu', name="sr_res_activation_" + str(id) + "_1")(x)
    x = Conv2D(64, (3, 3), activation='linear', padding='same',name='sr_res_conv_' + str(id) + '_2')(x)
    x = BatchNormalization(axis=channel_axis, name="sr_res_batchnorm_" + str(id) + "_2")(x, training=False)

    m = Add(name="sr_res_merge_" + str(id))([x, init])

    return m

def upscale_block(ip, id):
    init = ip

    x = UpSampling2D()(init)
    x = Conv2D(64, (3, 3), activation="relu", padding='same', name='sr_res_filter1_%d' % id)(x)

    return x

init = Input(shape=shape)
x0 = Conv2D(64, (3, 3), activation='relu', padding='same', name='sr_res_conv1')(init)
x = residual_block(x0, 1)

nb_residual = 5
for i in range(nb_residual):
    x = residual_block(x, i + 2)

x = Add()([x, x0])

#x = upscale_block(x, 1)
x = Conv2D(3, (3, 3), activation="linear", padding='same', name='sr_res_conv_final')(x)

model = Model(init, x)

adam = optimizers.Adam(lr=1e-3)
model.compile(optimizer=adam, loss='mse', metrics=[PSNRLoss])

train_generator = image_generator(train_path,
                                  target_shape=(size, size),
                                  batch_size=40)
valid_generator = image_generator(valid_path,
                                  target_shape=(size, size),
                                  batch_size=40)
for pinput, target in train_generator:
    print(pinput.shape)
    pin = pinput[0]
    print(target.shape)
    pout = target[0]
    break
plt.imshow(pin)
plt.imshow(pout)

print("Training model...")
model.fit_generator(train_generator,
                    steps_per_epoch = 10,
                    epochs = 5, 
                    validation_data = valid_generator,
                    validation_steps = 10)