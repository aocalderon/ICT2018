# -*- coding: utf-8 -*-
"""
Created on Fri Aug 17 10:33:08 2018

@author: acalderon
"""
from keras.models import Model
from keras.layers import Conv2D, Input, Conv2DTranspose
from keras.layers.advanced_activations import PReLU
from keras import optimizers
from skimage.measure import compare_ssim as SSIM
from losses import PSNR
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import platform
import os, glob

SCALE_FACTOR = 4
PATCH_SIZE   = 32
PIXEL_SIDE   = PATCH_SIZE / SCALE_FACTOR
IMAGE_SHAPE  = (PIXEL_SIDE, PIXEL_SIDE, 1)
BATCH_SIZE   = 128
EPOCHS       = 1

base_dir    = "/opt/ICT2018/Python/SR/FSRCNN"
if platform.system() in ["Windows"]:
    base_dir   = "H:\Projects\git\ICT2018\Python\SR\FSRCNN\\"
    data_input = "H:\data\SR\FSRCNN\\" 
data_output = os.path.join(base_dir, "Results")

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
model.load_weights(os.path.join(data_output,'fsrcnn_model_{}x.h5'.format(SCALE_FACTOR)))
adam = optimizers.Adam(lr=1e-3)
model.compile(optimizer=adam, loss='mse', metrics=[PSNR])
model.summary()

SCALE_FACTOR = 4
PATCH_SIZE   = 32
ratio = int(PATCH_SIZE / SCALE_FACTOR)

test_dir = "/opt/SR/"
if platform.system() in ["Windows"]:
    test_dir = "H:\data\SR\FSRCNN\91-image\\"
    figu_dir = "H:\data\SR\FSRCNN\Results\\"

filenames = glob.glob(os.path.join(test_dir,"*.bmp"))
print(len(filenames))
count = 1
mses  = []
ssims = []
psnrs = []
#filenames = filenames[0:25]
for filename in filenames:    
    image = Image.open(filename)
    image = image.convert('L')
    raw = np.array(image)
    WIDTH  = raw.shape[0]
    HEIGHT = raw.shape[1]
    out = np.empty((WIDTH, HEIGHT), dtype='uint8')
    raw = raw[0:WIDTH - (WIDTH % PATCH_SIZE), 0:HEIGHT - (HEIGHT % PATCH_SIZE)]
    WIDTH  = raw.shape[0]
    HEIGHT = raw.shape[1]
    rows = int(HEIGHT / PATCH_SIZE)
    cols = int(WIDTH  / PATCH_SIZE)
    n = rows * cols
    stride = PATCH_SIZE
    batch_mse  = []
    batch_ssim = []
    batch_psnr = []
    for row in range(0, rows):
        for col in range(0, cols):
            x = col * stride
            y = row * stride
            # Getting patches...
            patch = raw[x:x + stride, y:y + stride]
            scale = Image.fromarray(patch, 'L')
            scale = scale.resize((ratio, ratio), Image.BICUBIC)
            scale = np.array(scale)
            
            x_true = scale / 255.
            y_true = patch / 255.
            x_prime = np.expand_dims(x_true, axis=2)
            x_prime = np.expand_dims(x_prime, axis=0)
            y_pred = model.predict(x_prime)
            y_pred = y_pred[0,:,:,0]
            mse = np.mean( (y_true - y_pred) ** 2 )
            batch_mse.append(mse)
            psnr = 20 * np.log10(1 / np.sqrt(mse))
            batch_psnr.append(psnr)
            ssim = SSIM(y_true, y_pred)
            batch_ssim.append(ssim)
            #print("Count={} Image={} MSE={} SSIM={} PSNR={}".format(count, filename, mse, ssim, psnr))
            
            out[x:x + stride, y:y + stride] = (y_pred * 255).astype(np.uint8)
            plt.subplot(131)
            plt.imshow(x_true, cmap='Greys')
            plt.subplot(132)
            plt.imshow(y_true, cmap='Greys')
            plt.subplot(133)
            plt.imshow(y_pred, cmap='Greys')
            plt.savefig(os.path.join(figu_dir, "t{}.png".format(count)))
            count = count + 1
    mses.append(np.mean(batch_mse))
    ssims.append(np.mean(batch_ssim))
    psnrs.append(np.mean(batch_psnr))
    #image2 = Image.fromarray(out)
    #image3 = image2.resize((ratio, ratio), Image.BICUBIC)
    #image.save(os.path.join(figu_dir, 'image3.bmp'))
    #image2.save(os.path.join(figu_dir, 'image2.bmp'))
    #image2.save(os.path.join(figu_dir, 'image1.bmp'))
    print("MSE={} SSIM={} PSNR={}".format(np.mean(mses), np.mean(ssims), np.mean(psnrs)))