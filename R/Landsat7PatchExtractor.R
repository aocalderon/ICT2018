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
L7 = vector("list")
for(i in c(1,2,3,4,8)){
  L7[[Bands[i]]] = raster(paste0(landsat_dir,"L7_",i,".tif")) 
}

# resample(convRad2Ref(L)@layers[2][[1]], L7$P)

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
ncols = (L@ncols - (L@ncols %% PATCH_SIZE)) / PATCH_SIZE
nrows = (L@nrows - (L@nrows %% PATCH_SIZE)) / PATCH_SIZE
while(xmin < xmax - size){
  ymin = L@extent@ymin
  while(ymin < ymax - size){
    patch <- extent(xmin, xmin + size, ymin, ymin + size)
    L_crop = crop(L, patch)
    print(paste(L_crop@extent@xmin," ",L_crop@extent@xmax," ",L_crop@extent@ymin," ",L_crop@extent@ymax))
    v = getValues(L_crop)
    if(min(v) > 0){
      plot(L_crop)
    }
    ymin = ymin + size
  }
  xmin = xmin + size
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


