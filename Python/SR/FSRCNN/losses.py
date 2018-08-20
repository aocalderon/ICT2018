#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 17:31:58 2018

@author: and
"""
from keras import backend as K
import keras_contrib.backend as KC
import tensorflow as tf

def PSNR(y_true, y_pred):
    return -10. * K.log(K.mean(K.square(y_pred - y_true))) / K.log(10.)

def int_shape(x):
    return KC.int_shape(x) if KC.backend() == 'tensorflow' else KC.shape(x)

def SSIM(y_true, y_pred):
        # There are additional parameters for this function
        # Note: some of the 'modes' for edge behavior do not yet have a gradient definition in the Theano tree
        #   and cannot be used for learning
        kernel_size = 3
        k1 = 0.01
        k2 = 0.03
        max_value = 1.0
        c1 = (k1 * max_value) ** 2
        c2 = (k2 * max_value) ** 2
        dim_ordering = K.image_data_format()
        #backend = KC.backend()
        kernel = [kernel_size, kernel_size]
        y_true = KC.reshape(y_true, [-1] + list(int_shape(y_pred)[1:]))
        y_pred = KC.reshape(y_pred, [-1] + list(int_shape(y_pred)[1:]))

        patches_pred = KC.extract_image_patches(y_pred, kernel, kernel, 'valid', dim_ordering)
        patches_true = KC.extract_image_patches(y_true, kernel, kernel, 'valid', dim_ordering)

        # Reshape to get the var in the cells
        bs, w, h, c1, c2, c3 = int_shape(patches_pred)
        patches_pred = KC.reshape(patches_pred, [-1, w, h, c1 * c2 * c3])
        patches_true = KC.reshape(patches_true, [-1, w, h, c1 * c2 * c3])
        # Get mean
        u_true = KC.mean(patches_true, axis=-1)
        u_pred = KC.mean(patches_pred, axis=-1)
        # Get variance
        var_true = K.var(patches_true, axis=-1)
        var_pred = K.var(patches_pred, axis=-1)
        # Get std dev
        covar_true_pred = K.mean(patches_true * patches_pred, axis=-1) - u_true * u_pred

        ssim = (2 * u_true * u_pred + c1) * (2 * covar_true_pred + c2)
        denom = (K.square(u_true) + K.square(u_pred) + c1) * (var_pred + var_true + c2)
        ssim /= denom  # no need for clipping, c1 and c2 make the denom non-zero
        return ssim#K.mean((1.0 - ssim) / 2.0)
    
def SSIM2(y_true, y_pred):
        """Need tf0.11rc to work"""
        batch_size = 32
        y_true = tf.reshape(y_true, y_true.shape[1:])
        y_pred = tf.reshape(y_pred, y_pred.shape[1:])
        y_true = tf.transpose(y_true, [0, 2, 3, 1])
        y_pred = tf.transpose(y_pred, [0, 2, 3, 1])
        patches_true = tf.extract_image_patches(y_true, [1, 5, 5, 1], [1, 2, 2, 1], [1, 1, 1, 1], "SAME")
        patches_pred = tf.extract_image_patches(y_pred, [1, 5, 5, 1], [1, 2, 2, 1], [1, 1, 1, 1], "SAME")

        u_true = K.mean(patches_true, axis=3)
        u_pred = K.mean(patches_pred, axis=3)
        var_true = K.var(patches_true, axis=3)
        var_pred = K.var(patches_pred, axis=3)
        std_true = K.sqrt(var_true)
        std_pred = K.sqrt(var_pred)
        c1 = 0.01 ** 2
        c2 = 0.03 ** 2
        ssim = (2 * u_true * u_pred + c1) * (2 * std_pred * std_true + c2)
        denom = (u_true ** 2 + u_pred ** 2 + c1) * (var_pred + var_true + c2)
        ssim /= denom
        ssim = tf.select(tf.is_nan(ssim), K.zeros_like(ssim), ssim)
        return ssim
    