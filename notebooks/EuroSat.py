# coding: utf-8

# In[24]:

import numpy as np
import rasterio
import matplotlib.pyplot as plt
import h5py
import os
from glob import glob

# In[170]:

forest_path = "/opt/Datasets/EuroSat/Forest/"
with rasterio.open(forest_path + 'Forest_1.tif', 'r+') as r:
    image = r.read().astype('float32') 
    for j in np.arange(image.shape[0]):
        image[j] = (image[j] - np.amin(image[j])) / (np.amax(image[j]) - np.amin(image[j]))
print(image.shape)
image[7]

# In[167]:

sample = image[[7,3,2],:,:]
sample = np.transpose(sample, [1,2,0])
plt.imshow(sample)
plt.axis('off')

# In[168]:

sample = image[[3,2,1],:,:] 
sample = np.transpose(sample, [1,2,0])
plt.imshow(sample)
plt.axis('off')

# In[211]:

output_path = "/opt/Datasets/EuroSat/"
n = 500

geotiffs = [y for x in os.walk(forest_path) for y in glob(os.path.join(x[0], '*.tif'))]
len(geotiffs)
batch = np.zeros((4, 64, 64, n))
i = 0
for geotiff in geotiffs[:n]:
    with rasterio.open(geotiff, 'r+') as g:
        image = g.read()
        image = image[[1,2,3,7],...].astype('float32') 
        for j in np.arange(image.shape[0]):
            imin = np.amin(image[j])
            imax = np.amax(image[j])
            image[j] = (image[j] - imin) / (imax - imin)
        batch[:,:,:,i] = image
        i = i + 1
batch.shape
h5f = h5py.File(output_path + 'eurosat.h5', 'w')
h5f.create_dataset('forest', data=batch)
#h5f.close()

# In[213]:

industrial_path = "/opt/Datasets/EuroSat/Industrial/"

geotiffs = [y for x in os.walk(industrial_path) for y in glob(os.path.join(x[0], '*.tif'))]
len(geotiffs)
batch = np.zeros((4, 64, 64, n))
i = 0
for geotiff in geotiffs[:n]:
    with rasterio.open(geotiff, 'r+') as g:
        image = g.read()
        image = image[[1,2,3,7],...].astype('float32') 
        for j in np.arange(image.shape[0]):
            imin = np.amin(image[j])
            imax = np.amax(image[j])
            image[j] = (image[j] - imin) / (imax - imin)
        batch[:,:,:,i] = image
        i = i + 1
batch.shape
#h5f = h5py.File(output_path + 'industrial.h5', 'w')
h5f.create_dataset('industrial', data=batch)
#h5f.close()

# In[ ]:

river_path = "/opt/Datasets/EuroSat/River/"

geotiffs = [y for x in os.walk(river_path) for y in glob(os.path.join(x[0], '*.tif'))]
len(geotiffs)
batch = np.zeros((4, 64, 64, n))
i = 0
for geotiff in geotiffs[:n]:
    with rasterio.open(geotiff, 'r+') as g:
        image = g.read()
        image = image[[1,2,3,7],...].astype('float32') 
        for j in np.arange(image.shape[0]):
            imin = np.amin(image[j])
            imax = np.amax(image[j])
            image[j] = (image[j] - imin) / (imax - imin)
        batch[:,:,:,i] = image
        i = i + 1
batch.shape
#h5f = h5py.File(output_path + 'river.h5', 'w')
h5f.create_dataset('river', data=batch)
h5f.close()

#%%

f = h5py.File(output_path + 'eurosat.h5', 'r')
[v for v in f.values()]


