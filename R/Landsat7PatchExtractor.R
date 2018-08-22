library(satellite)
library(raster)
library(rgdal)
library(tidyverse)

PATCH_SIZE = 32
H_RES = 15
L_RES = 30
NUMBER_OF_PATCHES = 12000
sysinf <- Sys.info()

landsat_dir = "H:/L7/VIS_IR_Pan/"
output_dir = "H:/L7/Output/"
if(sysinf['sysname'] == "Linux"){
  landsat_dir = "/opt/GISData/L7/"
  output_dir = "/opt/GISData/L7/Output/"
}

metadata = readLines(paste0(landsat_dir, "L7_MTL.txt"))
R_MB = as.numeric(str_split_fixed(metadata[grep("REFLECTANCE_MULT_BAND", str_trim(metadata))], " = ", 2)[,2])
R_AD = as.numeric(str_split_fixed(metadata[grep("REFLECTANCE_ADD_BAND", str_trim(metadata))], " = ", 2)[,2])

Bands = c("B", "G", "R", "I", "S1", "T", "S2", "P")
L7 = vector("list", 5)
for(i in c(1,2,3,4,8)){
  L7[[Bands[i]]] = raster(paste0(landsat_dir,"L7_",i,".tif")) 
}

patches = vector("list", NUMBER_OF_PATCHES)
P = readAll(L7["P"][[1]])
xmin = P@extent@xmin
ymin = P@extent@ymin
xmax = P@extent@xmax
ymax = P@extent@ymax
res = H_RES
size = PATCH_SIZE * res
count = 1
while(xmin < xmax - size){
  ymin = L@extent@ymin
  while(ymin < ymax - size){
    patch <- extent(xmin, xmin + size, ymin, ymin + size)
    P_crop = crop(P, patch)
    v = getValues(P_crop)
    if(min(v) > 0){
      if(count <= NUMBER_OF_PATCHES){
        print(paste(count, ". ", P_crop@extent@xmin," ",P_crop@extent@xmax," ",P_crop@extent@ymin," ",P_crop@extent@ymax))
        patches[[count]] = patch
        count = count + 1
      }
    }
    ymin = ymin + size
  }
  xmin = xmin + size
  if(count > NUMBER_OF_PATCHES){
    break
  }
}

B = readAll(L7["B"][[1]])
G = readAll(L7["G"][[1]])
R = readAll(L7["R"][[1]])
I = readAll(L7["I"][[1]])
j = 1
for(i in 1:(count - 1)){
  print(paste0("Checking patch ", i, "..."))
  patch = patches[i][[1]]
  valid = TRUE
  I_crop = crop(I, patch)
  v = getValues(I_crop)
  if(min(v) == 0){
    valid = FALSE
  }
  if(valid){
    R_crop = crop(R, patch)
    v = getValues(R_crop)
    if(min(v) == 0){
      valid = FALSE
    }
  }
  if(valid){
    G_crop = crop(G, patch)
    v = getValues(G_crop)
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
    print(paste("Patch ",i," is a valid patch: ", patch@xmin," ", patch@xmax," ", patch@ymin," ", patch@ymax))
    B_crop = convRad2Ref(B_crop, R_MB[1], R_AD[1])
    G_crop = convRad2Ref(G_crop, R_MB[2], R_AD[2])
    R_crop = convRad2Ref(R_crop, R_MB[3], R_AD[3])
    I_crop = convRad2Ref(I_crop, R_MB[4], R_AD[4])
    MS = stack(B_crop, G_crop, R_crop, I_crop)
    writeRaster(MS, filename=paste0(output_dir,"MS_", j,".tif"), options="INTERLEAVE=BAND", overwrite=TRUE)
    P_crop = crop(P, patch)
    P_crop = convRad2Ref(P_crop, R_MB[7], R_AD[7])
    writeRaster(P_crop, filename=paste0(output_dir,"PA_", j,".tif"), overwrite=TRUE)
    print("Patch has been saved!")
    j = j + 1
  }
}
