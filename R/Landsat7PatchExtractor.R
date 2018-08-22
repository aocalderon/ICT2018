library(satellite)
library(raster)
library(rgdal)
library(tidyverse)

SAVE_FLAG = F
PLOT_FLAG = F
PATCH_SIZE = 32
H_RES = 15
L_RES = 30
sysinf <- Sys.info()

landsat_dir = "H:/L7/"
if(sysinf['sysname'] == "Linux")
  landsat_dir = "/opt/GISData/L7/"

B = vector("list", 5)

metadata = readLines(paste0(landsat_dir, "L7_MTL.txt"))
R_MB = as.numeric(str_split_fixed(metadata[grep("REFLECTANCE_MULT_BAND", str_trim(metadata))], " = ", 2)[,2])
R_AD = as.numeric(str_split_fixed(metadata[grep("REFLECTANCE_ADD_BAND", str_trim(metadata))], " = ", 2)[,2])

Bands = c("B", "G", "R", "I", "S1", "T", "S2", "P")
L7 = vector("list", 5)
for(i in c(1,2,3,4,8)){
  L7[[Bands[i]]] = raster(paste0(landsat_dir,"L7_",i,".tif")) 
}

# resample(convRad2Ref(L)@layers[2][[1]], L7$P)

patches = vector("list", 200)
band = "P"
L = readAll(L7[band][[1]])
xmin = L@extent@xmin
ymin = L@extent@ymin
xmax = L@extent@xmax
ymax = L@extent@ymax
res = L_RES
if(band == "P")
  res = H_RES
size = PATCH_SIZE * res
count = 1
while(xmin < xmax - size){
  ymin = L@extent@ymin
  while(ymin < ymax - size){
    patch <- extent(xmin, xmin + size, ymin, ymin + size)
    L_crop = crop(L, patch)
    print(paste(L_crop@extent@xmin," ",L_crop@extent@xmax," ",L_crop@extent@ymin," ",L_crop@extent@ymax))
    v = getValues(L_crop)
    if(min(v) > 0){
      plot(L_crop)
      patches[[count]] = patch
      count = count + 1
    }
    ymin = ymin + size
  }
  xmin = xmin + size
  if(count > 100){
    break
  }
}

B = readAll(L7["B"][[1]])
G = readAll(L7["G"][[1]])
R = readAll(L7["R"][[1]])
I = readAll(L7["I"][[1]])
for(i in 1:(count - 1)){
  patch = patches[i][[1]]
  valid = TRUE
  B_crop = crop(I, patch)
  v = getValues(B_crop)
  if(min(v) == 0){
    valid = FALSE
  }
  if(valid){
    B_crop = crop(R, patch)
    v = getValues(B_crop)
    if(min(v) == 0){
      valid = FALSE
    }
  }
  if(valid){
    B_crop = crop(G, patch)
    v = getValues(B_crop)
    if(min(v) == 0){
      valid = FALSE
    }
  }
  if(valid){
    B_crop = crop(B, patch)
    v = getValues(B_crop)
    if(min(v) == 0){
      valid = FALSE
    }
  }
  if(valid){
    print(paste("It is a valid patch: ", patch@xmin," ", patch@xmax," ", patch@ymin," ", patch@ymax))
  }
}

if(PLOT_FLAG){
  for(i in seq(1,5)){
    plot(patch)
  }
}

if(SAVE_FLAG){
  for(i in seq(1,5)){
    writeGDAL(B[[i]], paste0("H:/L7/Refl/B",i,"_Refl.tif"), drivername = "GTiff")
  }
}


