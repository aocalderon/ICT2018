library(satellite)
library(raster)
library(rgdal)
library(tidyverse)

PATCH_SIZE = 16
H_RES = 10
NUMBER_OF_PATCHES = 80000
sysinf <- Sys.info()

sentinel_dir = "H:/S2/VIS2NIR/"
output_dir = "H:/S2/VIS2NIR/Patches/"
if(sysinf['sysname'] == "Linux"){
  sentinel_dir = "/opt/GISData/L7/"
  output_dir = "/opt/GISData/L7/Output/"
}

Bands = c("C", "B", "G", "R", "5", "6", "7", "I")
S2 = vector("list", 4)
for(i in c(2,3,4,8)){
  filename = paste0(sentinel_dir,"S2_",i,".jp2")
  print(paste0("Reading ",filename,"..."))
  S2[[Bands[i]]] = raster(filename) 
}

patches = vector("list", NUMBER_OF_PATCHES)
I = readAll(S2["I"][[1]])
xmin = I@extent@xmin
ymin = I@extent@ymin
xmax = I@extent@xmax
ymax = I@extent@ymax
res = H_RES
size = PATCH_SIZE * res
count = 1
while(xmin < xmax - size){
  ymin = I@extent@ymin
  while(ymin < ymax - size){
    patch <- extent(xmin, xmin + size, ymin, ymin + size)
    I_crop = crop(I, patch)
    v = getValues(I_crop)
    if(count <= NUMBER_OF_PATCHES){
      print(paste0(count, ". ", I_crop@extent@xmin," ",I_crop@extent@xmax," ",I_crop@extent@ymin," ",I_crop@extent@ymax))
      patches[[count]] = patch
      count = count + 1
    }
    ymin = ymin + size
  }
  xmin = xmin + size
  if(count > NUMBER_OF_PATCHES){
    break
  }
}

B = readAll(S2["B"][[1]])
G = readAll(S2["G"][[1]])
R = readAll(S2["R"][[1]])
for(i in 1:(count - 1)){
  patch = patches[i][[1]]
  R_crop = crop(R, patch)
  G_crop = crop(G, patch)
  B_crop = crop(B, patch)

  MS = stack(B_crop, G_crop, R_crop)
  writeRaster(MS, filename=paste0(output_dir,"VIS_",i,".tif"), options="INTERLEAVE=BAND", overwrite=TRUE)
  I_crop = crop(I, patch)
  writeRaster(I_crop, filename=paste0(output_dir,"NIR_",i,".tif"), overwrite=TRUE)
  print(paste0("Patch ",i," has been saved!"))
}
