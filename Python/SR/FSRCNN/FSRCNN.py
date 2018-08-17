#!/usr/bin/env python

from __future__ import print_function
from keras import backend as K
from keras.models import Model
from keras.layers import Conv2D, Input, Conv2DTranspose
from keras.layers.advanced_activations import PReLU
import tensorflow as tf
from keras import optimizers
from keras.callbacks import ModelCheckpoint

import platform
import h5py
import os

SCALE_FACTOR = 2
PIXEL_SIDE   = 16
IMAGE_SHAPE  = (PIXEL_SIDE, PIXEL_SIDE, 1)
BATCH_SIZE   = 128
EPOCHS       = 32

data_output = "/opt/Datasets/FSRCNN/"
if platform.system() in ["Windows"]:
    data_output = r"H:\data\SR\FSRCNN\data\\"
train_path = data_output + "train"
dataset = h5py.File(os.path.join(train_path,'train.h5'), 'a')
X = dataset.get('X')
y = dataset.get('y')

def tf_log10(x):
  numerator = tf.log(x)
  denominator = tf.log(tf.constant(10, dtype=numerator.dtype))
  return numerator / denominator

def PSNR(y_true, y_pred):
	max_pixel = 1.0
	return 10.0 * tf_log10((max_pixel ** 2) / (K.mean(K.square(y_pred - y_true)))) 
    
input_img = Input(shape=IMAGE_SHAPE)

model = Conv2D(56, (5, 5), padding='same', kernel_initializer='he_normal')(input_img)
model = PReLU()(model)

model = Conv2D(16, (1, 1), padding='same', kernel_initializer='he_normal')(model)
model = PReLU()(model)

model = Conv2D(12, (3, 3), padding='same', kernel_initializer='he_normal')(model)
model = PReLU()(model)
model = Conv2D(12, (3, 3), padding='same', kernel_initializer='he_normal')(model)
model = PReLU()(model)
model = Conv2D(12, (3, 3), padding='same', kernel_initializer='he_normal')(model)
model = PReLU()(model)
model = Conv2D(12, (3, 3), padding='same', kernel_initializer='he_normal')(model)
model = PReLU()(model)

model = Conv2D(56, (1, 1), padding='same', kernel_initializer='he_normal')(model)
model = PReLU()(model)

model = Conv2DTranspose(1, (9, 9), strides=(SCALE_FACTOR, SCALE_FACTOR), padding='same')(model)

output_img = model

model = Model(input_img, output_img)

# model.load_weights('./checkpoints/weights-improvement-20-26.93.hdf5')

adam = optimizers.Adam(lr=1e-3)
model.compile(optimizer=adam, loss='mse', metrics=[PSNR])

#model.compile(optimizer='adam', lr=0.0001, loss='mse', metrics=[PSNR, "accuracy"])

model.summary()

filepath = os.path.join(data_output, "checkpoints",
                        "weights-improvement-{epoch:02d}-{PSNR:.2f}.hdf5")
checkpoint = ModelCheckpoint(filepath, monitor=PSNR, verbose=1, mode='max')
callbacks_list = [checkpoint]

model.fit(X, y, epochs=EPOCHS, 
          validation_split=0.2,
          batch_size=BATCH_SIZE, callbacks=callbacks_list, shuffle="batch")

print("Done training!!!")
print("Saving the final model ...")

model.save(os.path.join(data_output,'fsrcnn_model.h5'))  # creates a HDF5 file 
