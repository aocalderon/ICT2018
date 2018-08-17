#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 14:43:31 2018

@author: and
"""

import os
from shutil import copyfile

folders = ['PermanentCrop', 'Highway', 'Residential', 'Pasture', 'HerbaceousVegetation', 'AnnualCrop', 'Industrial', 'Forest', 'SeaLake', 'River']
folders = ['PermanentCrop', 'HerbaceousVegetation', 'AnnualCrop', 'Forest']
base_dir = "/opt/EuroSAT/Test2/"
split = 0.8

for folder in folders:
    nfiles = len(os.listdir(base_dir + folder))
    print("{}: {}".format(folder, nfiles))
    for n in range(1, nfiles + 1):
        src_dir = base_dir + folder + "/"
        filename = "{1}_{2}.jpg".format(base_dir, folder, n)
        ntrain = int(nfiles * split) + 1
        if n <= ntrain:
            dst_dir = base_dir + "images/train/"
        else:
            dst_dir = base_dir + "images/valid/"
        print("{} copied to {}".format(filename, dst_dir))
        copyfile(src_dir + filename, dst_dir + filename)
print("Files in {}: {}".format(base_dir + "Test/images/train/", len(os.listdir(base_dir + "Test/images/train/"))))
print("Files in {}: {}".format(base_dir + "Test/images/valid/", len(os.listdir(base_dir + "Test/images/valid/"))))
