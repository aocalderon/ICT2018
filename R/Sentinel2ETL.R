library(raster)
library(rgdal)
library(tidyverse)

options(digits=12)
SAVE_FLAG = T
PLOT_FLAG = T
PREDICT_MODELS = T
H_RES = 5
L_RES = 10

#midx = 467017.5  # Riverside mid x
#midy = 3761452.5 # Riverside mid y
#size = 9000

midx = 499507.5 # Landsat 7 scene mid x
midy = 3757282.5 # Landsat 7 scene mid y
size = 4500

clip <- as(extent(midx - size, midx + size, midy - size, midy + size), 'SpatialPolygons')
B = vector("list", 4)

path = "H:/S2/L1C_T11SMT_A015754_20180628T184014/S2A_MSIL1C_20180628T182921_N0206_R027_T11SMT_20180628T221012.SAFE/GRANULE/L1C_T11SMT_A015754_20180628T184014/IMG_DATA/"
k = 1
for(i in c(2,3,4,8)){
  L = raster(paste0(path, "T11SMT_20180628T182921_B0",i,".jp2"))
  L_Crop = crop(L, clip)
  L_Crop[L_Crop > quantile(L_Crop, 0.99)] = quantile(L_Crop, 0.99)
  B[[k]] = as(L_Crop / 10000.0, 'SpatialGridDataFrame')
  k = k + 1
}

if(PLOT_FLAG){
  for(i in seq(1,4)){
    plot(B[[i]])
  }
}

if(SAVE_FLAG){
  for(i in seq(1,4)){
    writeGDAL(B[[i]], paste0("H:/S2/Refl/B",i,"_Refl.tif"), drivername = "GTiff")
  }
}

B1 = as.tibble(B[[1]])
B2 = as.tibble(B[[2]])
B3 = as.tibble(B[[3]])
B4 = as.tibble(B[[4]])

dsS2 = as.data.frame(cbind(B1[,c(2,3)], B1[,1], B2[,1], B3[,1], B4[,1]))
names(dsS2) = c("x", "y", "B", "G", "R", "I")

if(PREDICT_MODELS){
  newx = as.matrix(dsS2[,3:5])
  y_prime = predict(fit1m,newx=newx,s=c(0.0001))[,,1]
  offset = H_RES / 2.0
  S2 = cbind(dsS2[,1:2], y_prime) %>% 
    mutate(xW = x - offset, xE = x + offset, yN = y + offset, yS = y - offset)
  NW = S2 %>% select(xW, yN, NW) %>% mutate(x = xW, y = yN, v = NW) %>% select(x, y, v)
  NE = S2 %>% select(xE, yN, NE) %>% mutate(x = xE, y = yN, v = NE) %>% select(x, y, v)
  SW = S2 %>% select(xW, yS, SW) %>% mutate(x = xW, y = yS, v = SW) %>% select(x, y, v)
  SE = S2 %>% select(xE, yS, SE) %>% mutate(x = xE, y = yS, v = SE) %>% select(x, y, v)
  S.data = rbind(NW, NE, SW, SE) %>% arrange(desc(y), x) %>% select(v)
  xOffset = B[[1]]@grid@cellcentre.offset[1] - offset
  yOffset = B[[1]]@grid@cellcentre.offset[2] - offset
  xCellsize = B[[1]]@grid@cellsize[1] / 2
  yCellsize = B[[1]]@grid@cellsize[2] / 2
  xDim = B[[1]]@grid@cells.dim[1] * 2
  yDim = B[[1]]@grid@cells.dim[2] * 2
  
  S.grid = GridTopology(c(xOffset, yOffset), c(xCellsize, yCellsize), c(xDim, yDim))
  B5 = SpatialGridDataFrame(S.grid, S.data, proj4string = crs(B[[1]]))
  if(PLOT_FLAG){
    plot(B5)
  }
  if(SAVE_FLAG){
    tag = "L7"
    writeGDAL(B5, paste0("H:/S2/Refl/Pan_",tag,".tif"), drivername = "GTiff")
  }
}
