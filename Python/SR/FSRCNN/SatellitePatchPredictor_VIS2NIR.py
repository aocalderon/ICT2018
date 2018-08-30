# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 10:33:08 2018

@author: acalderon
"""
from keras.models import Model
from keras.layers import Conv2D, Input, Conv2DTranspose
from keras.layers.advanced_activations import PReLU
from keras import optimizers
from skimage.measure import compare_mse   as mse
from skimage.measure import compare_nrmse as rmse
from skimage.measure import compare_psnr  as psnr
from skimage.measure import compare_ssim  as ssim
from losses import PSNR
import numpy as np
import platform
import os
import rasterio

def normalize(image, bands = 1):
    r = np.empty((image.shape[1],image.shape[2],image.shape[0]))
    for j in range(bands):
        b = image[j]
        imin, imax = np.percentile(b, [1,99])
        b[b > imax] = imax
        b[b < imin] = imin
        r[:,:,j] = (b - imin) / (imax - imin)
    return(r)
    
N_PATCHES    = 1000
PATCH_SIZE   = 16
CHANELS      = 3
IMAGE_SHAPE  = (PATCH_SIZE, PATCH_SIZE, CHANELS)
BATCH_SIZE   = 128
EPOCHS       = 1

base_dir = "/opt/ICT2018/Python/SR/FSRCNN"
img_path    = "/opt/"
if platform.system() in ["Windows"]:
    base_dir = r"H:\Projects\git\ICT2018\Python\SR\FSRCNN\\"
    img_path = r"H:\S2\VIS2NIR\Test\\"
model_path = os.path.join(base_dir, "Results")

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
model = Conv2DTranspose(1, (9, 9), strides=(1, 1), padding='same')(model)
output_img = model
model = Model(input_img, output_img)
model.load_weights(os.path.join(model_path,'fsrcnn_L7_Epoch64_VIS2NIR.h5'))
adam = optimizers.Adam(lr=1e-3)
model.compile(optimizer=adam, loss='mse', metrics=[PSNR])
model.summary()

nir_file = os.path.join(img_path, "NIR_Test.TIF")
NIR = rasterio.open(nir_file, 'r+')
profile = NIR.profile
profile.update(blockxsize=PATCH_SIZE, blockysize=PATCH_SIZE, tiled='yes')
dst = rasterio.open('test.tif', 'w', **profile)
y_true = np.empty((N_PATCHES, PATCH_SIZE, PATCH_SIZE, 1))
n = 0
for ij, window in dst.block_windows():
    norm = normalize(NIR.read(window=window))
    y = np.expand_dims(norm, axis=0)
    if y.shape == (1,PATCH_SIZE,PATCH_SIZE,1):
        print("Extracting patch {}...".format(n))
        y_true[n] = y
        n = n + 1
    if n >= N_PATCHES:
        break
dst.close()

vis_file = os.path.join(img_path, "VIS_Test.TIF")
VIS = rasterio.open(vis_file, 'r+')
profile = VIS.profile
profile.update(blockxsize=PATCH_SIZE, blockysize=PATCH_SIZE, tiled='yes')
dst = rasterio.open('test.tif', 'w', **profile)
y_pred = np.empty((N_PATCHES, PATCH_SIZE, PATCH_SIZE, 1))
n = 0
for ij, window in dst.block_windows():
    x = np.expand_dims(normalize(VIS.read(window=window), bands=3), axis=0)
    if x.shape == (1,PATCH_SIZE,PATCH_SIZE,CHANELS):
        print("Predicting patch {}...".format(n))
        y_pred[n] = model.predict(x)
        n = n + 1
    if n >= N_PATCHES:
        break
dst.close()

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