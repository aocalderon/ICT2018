# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 16:06:26 2018

@author: acalderon
"""

# (1) Importing dependency
#import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, Flatten, Conv2D, MaxPooling2D
from keras.layers.normalization import BatchNormalization
from keras.callbacks import LearningRateScheduler, Callback
from keras.optimizers import SGD
from math import floor
import numpy as np
np.random.seed(1000)

# (2) Get Data
from pathlib import Path
import scipy.io

path = Path("C:/Users/acalderon/Downloads/SAT-4_and_SAT-6_datasets.tar/SAT-4_and_SAT-6_datasets/sat-6-full.mat")
mat = scipy.io.loadmat(path)
train_x = mat['train_x']
train_x.shape
train_y = mat['train_y']
train_y.shape
annotations = mat['annotations']
a = {}
for k, v in annotations:
    a[k[0]] = v[0] 
for i in range(10):
    k = ''.join(str(x) for x in train_y[:,i])
    print(a[k])
test_x = mat['test_x']
test_y = mat['test_y']
x = np.transpose( train_x, (3,0,1,2))
x = x.astype('float32') / 255
x.shape
y = np.transpose( train_y, (1,0))
y.shape
x_test = np.transpose( test_x, (3,0,1,2))
x_test = x_test.astype('float32') / 255
x_test.shape
y_test = np.transpose( test_y, (1,0))
y_test.shape

# (3) Create a sequential model
model = Sequential()

# 1st Convolutional Layer
model.add(Conv2D(filters=16, input_shape=(28,28,4), kernel_size=(3,3), strides=(1,1), padding='valid'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation before passing it to the next layer
model.add(BatchNormalization())

# 2nd Convolutional Layer
model.add(Conv2D(filters=48, kernel_size=(3,3), strides=(1,1), padding='same'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(3,3), strides=(2,2), padding='valid'))
# Batch Normalisation
model.add(BatchNormalization())

# 3rd Convolutional Layer
model.add(Conv2D(filters=96, kernel_size=(3,3), strides=(1,1), padding='same'))
model.add(Activation('relu'))
# Batch Normalisation
model.add(BatchNormalization())

# 4th Convolutional Layer
model.add(Conv2D(filters=64, kernel_size=(3,3), strides=(1,1), padding='same'))
model.add(Activation('relu'))
# Batch Normalisation
model.add(BatchNormalization())

# 5th Convolutional Layer
model.add(Conv2D(filters=64, kernel_size=(3,3), strides=(1,1), padding='same'))
model.add(Activation('relu'))
# Pooling
model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2), padding='valid'))
# Batch Normalisation
model.add(BatchNormalization())

# Passing it to a dense layer
model.add(Flatten())
# 1st Dense Layer
model.add(Dense(64*3*3, input_shape=(28*28*4,)))
model.add(Activation('relu'))
# Add Dropout to prevent overfitting
model.add(Dropout(0.5))
# Batch Normalisation
model.add(BatchNormalization())

# 2nd Dense Layer
from keras.layers import ThresholdedReLU
#model.add(Dense(200, activation=))
model.add(Dense(200))
model.add(ThresholdedReLU(theta=0.0000001))
# Add Dropout
model.add(Dropout(0.5))
# Batch Normalisation
model.add(BatchNormalization())

# 3rd Dense Layer
model.add(Dense(200))
model.add(ThresholdedReLU(theta=0.0000001))
# Add Dropout
model.add(Dropout(0.5))
# Batch Normalisation
model.add(BatchNormalization())

# Output Layer
model.add(Dense(6))
model.add(Activation('softmax'))

model.summary()

# (4) Compile
def step_decay(epoch):
   initial_lrate = 1
   drop = 0.5
   epochs_drop = 3.0
   lrate = initial_lrate * pow(drop, floor((1 + epoch) / epochs_drop))
   return lrate

class LossHistory(Callback):
    def on_train_begin(self, logs={}):
       self.losses = []
       self.lr = []
 
    def on_epoch_end(self, batch, logs={}):
       self.losses.append(logs.get('loss'))
       self.lr.append(step_decay(len(self.losses)))
       
loss_history = LossHistory()
lrate = LearningRateScheduler(step_decay)
callbacks_list = [loss_history, lrate]

sgd = SGD(lr=0.2, momentum=0.9, decay=0.0005, nesterov=False)

model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# (5) Train
history = model.fit(x, y, epochs=36, batch_size=128, verbose=1, callbacks=callbacks_list, shuffle=True)
test_loss, test_acc = model.evaluate(x_test, y_test)
test_acc
