library(raster)
library(rgdal)

test_dir = "H:/S2/VIS2NIR/Test/"
B = raster(paste0(test_dir,"S2_2.tif"))
G = raster(paste0(test_dir,"S2_3.tif"))
R = raster(paste0(test_dir,"S2_4.tif"))
VIS = stack(B,G,R)
writeRaster(VIS, filename=paste0(test_dir,"VIS.tif"), options="INTERLEAVE=BAND", overwrite=TRUE)
