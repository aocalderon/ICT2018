from os import listdir, makedirs
from os.path import isfile, join, exists
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input_dir", help="Data input directory", default="/opt/EuroSAT/Test/")
parser.add_argument("--output_dir", help="Data output directory", default="/opt/EuroSAT/Test/H")
args = parser.parse_args()

import imageio as misc
from skimage.transform import rescale

scale = 3.0
input_size = 33
label_size = 21
#pad = (input_size - label_size) / 2
pad = 6
stride = 14

if not exists(args.output_dir):
    makedirs(args.output_dir)
if not exists(join(args.output_dir, "input")):
    makedirs(join(args.output_dir, "input"))
if not exists(join(args.output_dir, "label")):
    makedirs(join(args.output_dir, "label"))

count = 1
for f in listdir(args.input_dir):
    f = join(args.input_dir, f)
    if not isfile(f):
        continue

    #image = misc.imread(f, flatten=False, mode='YCbCr')
    #image = Image.open(f).convert("L")
    image = misc.imread(f)
    w, h, c = image.shape
    w -= w % 3
    h -= h % 3
    image = image[0:w, 0:h]

    #scaled = misc.imresize(image, 1.0/scale, 'bicubic')
    scaled = rescale(image, 1.0/scale, multichannel=True, mode='reflect', anti_aliasing=True)
    scaled = rescale(image, scale/1.0, multichannel=True, mode='reflect', anti_aliasing=True)

    for i in range(0, h - input_size + 1, stride):
        for j in range(0, w - input_size + 1, stride):
            sub_img = scaled[j : j + input_size, i : i + input_size]
            sub_img_label = image[j + pad : j + pad + label_size, i + pad : i + pad + label_size]
            misc.imsave(join(args.output_dir, "input", str(count) + '.png'), sub_img)
            misc.imsave(join(args.output_dir, "label", str(count) + '.png'), sub_img_label)

            count += 1
