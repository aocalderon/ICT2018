#!/usr/bin/env python

from keras.models import Model
from keras.layers import Conv2D, Input, Conv2DTranspose
from keras.layers.advanced_activations import PReLU
from keras import optimizers
from keras.callbacks import ModelCheckpoint
from losses import PSNR, SSIM
import platform
import h5py
import os

PATCH_SIZE   = 32
SCALE_FACTOR = 4
PIXEL_SIDE   = PATCH_SIZE / SCALE_FACTOR
IMAGE_SHAPE  = (PIXEL_SIDE, PIXEL_SIDE, 1)
BATCH_SIZE   = 128
EPOCHS       = 32

base_dir    = "/opt/ICT2018/Python/SR/FSRCNN"
if platform.system() in ["Windows"]:
    base_dir   = "H:\Projects\git\ICT2018\Python\SR\FSRCNN\\"
    data_input = "H:\data\SR\FSRCNN\\" 
data_output = os.path.join(base_dir, "Results")
train_path  = os.path.join(data_input, "BSDS200")
dataset = h5py.File(os.path.join(train_path,'train.h5'), 'r')
X = dataset.get('X')
y = dataset.get('y')

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

# model.load_weights('/checkpoints/weights-improvement-20-26.93.hdf5')
# model.load_weights(os.path.join(data_output,'fsrcnn_model.h5'))

adam = optimizers.Adam(lr=1e-3)
model.compile(optimizer=adam, loss='mse', metrics=[PSNR])

model.summary()

filepath = os.path.join(data_output, "checkpoints",
                        "weights-improvement-{epoch:02d}-{PSNR:.2f}.hdf5")
checkpoint = ModelCheckpoint(filepath, monitor=PSNR, verbose=1, mode='max')
callbacks_list = [checkpoint]

model.fit(X, y, epochs=EPOCHS,
          validation_split=0.25,
          batch_size=BATCH_SIZE, callbacks=callbacks_list, shuffle="batch")

print("Done training!!!")
print("Saving the final model ...")

model.save(os.path.join(data_output,"fsrcnn_model_{}x.h5".format(SCALE_FACTOR)))  # creates a HDF5 file
