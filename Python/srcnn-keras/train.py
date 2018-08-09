import sys
from os import walk
from os.path import join, exists
from glob import glob
import argparse
from PIL import Image
import numpy as np
import platform

parser = argparse.ArgumentParser()
parser.add_argument("--save", help="Path to save the checkpoints to", default="/opt/EuroSAT/Test/output")
parser.add_argument("--data", help="Training data directory", default="/opt/EuroSAT/Test/H")
args = parser.parse_args()

if 'Windows' in platform.platform():
    save = "H:\data\EuroSAT\Test\output"
    data = "H:\data\EuroSAT\Test\H"
else:
    data = "/opt/EuroSAT/Test/H"
    save = "/opt/EuroSAT/Test/output"
    
input_dir = join(data, "input")
label_dir = join(data, "label")

if not (exists(input_dir) and exists(label_dir)):
    print("Input/label directories not found")
    sys.exit(1)

from keras.models import Model
from keras.layers import Input, Conv2D
from keras.optimizers import Adam

inputs = Input(shape=(33, 33, 1))

x = Conv2D(filters=64, input_shape=(33, 33, 1), kernel_size=(9, 9), activation='relu', kernel_initializer='he_normal')(inputs)
x = Conv2D(filters=32, kernel_size=(1, 1), activation='relu', kernel_initializer='he_normal')(x)
x = Conv2D(filters=1, kernel_size=(5, 5), kernel_initializer='he_normal')(x)

m = Model(inputs=inputs, outputs=x)
m.compile(Adam(lr=0.001), 'mse')

pngs = [f for x in walk(input_dir) for f in glob(join(x[0], '*.png'))]
X = np.array([np.asarray(Image.open(join(input_dir, f)).convert('L'))[None,...] for f in pngs])
X = np.transpose(X,[0,2,3,1])
pngs = [f for x in walk(label_dir) for f in glob(join(x[0], '*.png'))]
y = np.array([np.asarray(Image.open(join(label_dir, f)).convert('L'))[None,...] for f in pngs])
y = np.transpose(y,[0,2,3,1])

m.fit(X, y, batch_size=128, nb_epoch = 10)
if save:
    print("Saving model...")
    m.save(join(save, 'model_SR.h5'))
