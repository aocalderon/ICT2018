#!/usr/bin/env python

from keras.models import Model
from keras.layers import Conv2D, Input, Conv2DTranspose
from keras.layers.advanced_activations import PReLU
from keras import optimizers
from keras.callbacks import ModelCheckpoint
from losses import PSNR
from skimage.measure import compare_mse   as mse
from skimage.measure import compare_nrmse as rmse
from skimage.measure import compare_psnr  as psnr
from skimage.measure import compare_ssim  as ssim
import platform
import h5py
import os

PATCH_SIZE   = 32
SCALE_FACTOR = 2
CHANNELS     = 4
PIXEL_SIDE   = PATCH_SIZE / SCALE_FACTOR
IMAGE_SHAPE  = (PIXEL_SIDE, PIXEL_SIDE, CHANNELS)
BATCH_SIZE   = 128
EPOCHS       = 32

base_dir    = "/opt/ICT2018/Python/SR/FSRCNN"
data_input  = "/opt/Datasets/FSRCNN"
if platform.system() in ["Windows"]:
    base_dir   = "H:\Projects\git\ICT2018\Python\SR\FSRCNN\\"
    data_input = "H:\data\SR\FSRCNN\\" 
data_output = os.path.join(base_dir, "Results")
train_path  = os.path.join(data_input, "L7")
dataset = h5py.File(os.path.join(train_path,'trainL7.h5'), 'r')
X = dataset.get('X')
y = dataset.get('y')

n = X.shape[0]
t = int(n * 0.8)
x_true = X[t:n, ...]
y_true = y[t:n, ...]
X = X[0:t, ...]
y = y[0:t, ...]

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

model.save(os.path.join(data_output,"fsrcnn_L7_Epoch{}_{}x.h5".format(EPOCHS, SCALE_FACTOR)))  # creates a HDF5 file

y_pred = model.predict(x_true)
n = y_true.shape[0]
mses  = 0
rmses = 0
psnrs = 0
ssims = 0
for i in range(0,n):
    print("Testing {}/{}...".format(i,n))
    y = y_true[i,:,:,0]
    y_prime = y_pred[i,:,:,0]
    mses  = mses  +  mse(y, y_prime)
    rmses = rmses + rmse(y, y_prime)
    psnrs = psnrs + psnr(y, y_prime, data_range=y_prime.max() - y_prime.min())
    ssims = ssims + ssim(y, y_prime, data_range=y_prime.max() - y_prime.min())
mses  =  mses / n
rmses = rmses / n
psnrs = psnrs / n
ssims = ssims / n
print("MSE={} RMSE={} SSIM={} PSNR={}".format(mses, rmses, ssims, psnrs))
