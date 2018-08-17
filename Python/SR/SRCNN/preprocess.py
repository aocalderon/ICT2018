from os import listdir, makedirs
from os.path import isfile, join, exists
import platform

import imageio as misc
from skimage.transform import rescale

scale = 3.0
input_size = 33
label_size = 21
pad = 6
stride = 14

if 'Windows' in platform.platform():
    input_dir = "H:\data\EuroSAT\River"
    output_dir = "H:\data\EuroSAT\Test\H"
else:
    input_dir = "/opt/EuroSAT/Test/"
    output_dir = "/opt/EuroSAT/Test/H"
    
if not exists(output_dir):
    makedirs(output_dir)
if not exists(join(output_dir, "input")):
    makedirs(join(output_dir, "input"))
if not exists(join(output_dir, "label")):
    makedirs(join(output_dir, "label"))

count = 1
for f in listdir(input_dir):
    f = join(input_dir, f)
    if not isfile(f):
        continue

    image = misc.imread(f)
    w, h, c = image.shape
    w -= w % 3
    h -= h % 3
    image = image[0:w, 0:h]

    scaled = rescale(image, 1.0/scale, multichannel=True, mode='reflect', anti_aliasing=True)
    scaled = rescale(scaled, scale/1.0, multichannel=True, mode='reflect', anti_aliasing=True)

    for i in range(0, h - input_size + 1, stride):
        for j in range(0, w - input_size + 1, stride):
            sub_img = scaled[j : j + input_size, i : i + input_size]
            sub_img_label = image[j + pad : j + pad + label_size, i + pad : i + pad + label_size]
            misc.imsave(join(output_dir, "input", str(count) + '.png'), sub_img)
            misc.imsave(join(output_dir, "label", str(count) + '.png'), sub_img_label)
            count += 1
