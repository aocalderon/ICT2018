#from os import listdir
from os.path import join
import argparse

import imageio as misc
from skimage.transform import rescale
import platform
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--model", help="The model to be used for prediction")
parser.add_argument("--input", help="Input image file path")
parser.add_argument("--output", help="Output image file path")
parser.add_argument("--baseline", help="Baseline bicubic interpolated image file path")
parser.add_argument("--scale", help="Scale factor", default=3.0, type=float)
args = parser.parse_args()

from keras.models import load_model

if 'Windows' in platform.platform():
    model = "H:\data\EuroSAT\Test\output\model_SR.h5"
    input  = "H:\data\EuroSAT\River\River_1.jpg"
    output = "H:\data\EuroSAT\Test\output\River_1x3.jpg"
    baseline = "H:\data\EuroSAT\Test\output\River_1_baseline.jpg"
    scale = 3.0
else:
    input_dir = "/opt/EuroSAT/Test/"
    output_dir = "/opt/EuroSAT/Test/H"

m = load_model(model)
input_size = 33
label_size = 21
pad = 6

#X = misc.imread(input, mode='YCbCr')
X = np.asarray(Image.open(join(input)).convert('YCbCr'))
w, h, c = X.shape
w -= int(w % scale)
h -= int(h % scale)
X = X[0:w, 0:h, :]
X.setflags(write=1)
X[:,:,1] = X[:,:,0]
X[:,:,2] = X[:,:,0]

#scaled = misc.imresize(X, 1.0/scale, 'bicubic')
#scaled = misc.imresize(scaled, scale/1.0, 'bicubic')

scaled = rescale(X, 1.0/scale, multichannel=True, mode='reflect', anti_aliasing=True)
scaled = rescale(scaled, scale/1.0, multichannel=True, mode='reflect', anti_aliasing=True)
    
newimg = np.zeros(scaled.shape)

if baseline:
    #misc.imsave(baseline, scaled[pad : w - w % input_size, pad: h - h % input_size, :])
    misc.imsave(baseline, scaled)

for i in range(0, h - input_size + 1, label_size):
    for j in range(0, w - input_size + 1, label_size):
        sub_img = scaled[None, j : j + input_size, i : i + input_size, 0, None]
        prediction = m.predict(sub_img).reshape(label_size, label_size)
        newimg[j + pad : j + pad + label_size, i + pad : i + pad + label_size, 0] = prediction
        sub_img = scaled[None, j : j + input_size, i : i + input_size, 1, None]
        prediction = m.predict(sub_img).reshape(label_size, label_size)
        newimg[j + pad : j + pad + label_size, i + pad : i + pad + label_size, 1] = prediction
        sub_img = scaled[None, j : j + input_size, i : i + input_size, 2, None]
        prediction = m.predict(sub_img).reshape(label_size, label_size)
        newimg[j + pad : j + pad + label_size, i + pad : i + pad + label_size, 2] = prediction

#newimg = newimg[pad : w - w % input_size, pad : h - h % input_size,:]
misc.imsave(output, newimg)
