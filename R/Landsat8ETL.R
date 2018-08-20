library(landsat)
library(landsat8)
library(raster)
library(rgdal)
library(tidyverse)

SAVE_FLAG = F
PLOT_FLAG = F
RUN_MODELS = F
H_RES = 15
L_RES = 30
midx = 467017.5  # Riverside mid x
midy = 3761452.5 # Riverside mid y
size = 9000

clip <- as(extent(midx - size, midx + size, midy - size, midy + size), 'SpatialPolygons')
B = vector("list", 5)

L = raster("H:/L8/LC08_L1TP_040036_20180621_20180622_01_RT_B8.TIF")
crs(clip) <- crs(L)
L8_Crop = crop(L, clip)
B[[5]] = reflconv(as(L8_Crop, 'SpatialGridDataFrame'), 2.0000E-05, -0.100000)

for(i in seq(1,4)){
  L = raster(paste0("H:/L8/LC08_L1TP_040036_20180621_20180622_01_RT_B",i+1,".TIF"))
  L_Crop = crop(L, clip)
  L_Resampled = resample(L_Crop, L8_Crop, "ngb")
  B[[i]] = reflconv(as(L_Resampled, 'SpatialGridDataFrame'), 2.0000E-05, -0.100000)
}

if(PLOT_FLAG){
  for(i in seq(1,5)){
    plot(B[[i]])
  }
}

if(SAVE_FLAG){
  for(i in seq(1,5)){
    writeGDAL(B[[i]], paste0("H:/L8/Refl/B",i,"_Refl.tif"), drivername = "GTiff")
  }
}

B1 = as.tibble(B[[1]])
B2 = as.tibble(B[[2]])
B3 = as.tibble(B[[3]])
B4 = as.tibble(B[[4]])
B5 = as.tibble(B[[5]])

grid1 = raster(extent(B[[5]]), resolution=L_RES, crs=crs(B[[5]]))
grid2 = setValues(grid1, 1:ncell(grid1))
grid3 = resample(grid2, L8_Crop, "ngb")
n = as.tibble(as(grid3, 'SpatialGridDataFrame'))

Bands = cbind(n[,1], B1[,c(2,3)], B1[,1], B2[,1], B3[,1], B4[,1], B5[,1])
names(Bands) = c("n", "x", "y", "B", "G", "R", "I", "P")
dataset = Bands %>% arrange(n, y, x) %>% 
  select(n, B, G, R, I, P) %>% 
  group_by(n, B, G, R, I) %>% 
  summarise(Pan = paste(P, collapse = " ")) %>% 
  separate(Pan, c("NW", "NE", "SW", "SE"), sep = " ", convert = T) %>%
  ungroup() 
  
dsL8 = as.data.frame(dataset %>% select(B,G,R,I,NW,NE,SW,SE))

if(RUN_MODELS){
  metric = "R2"
  # models = c("naive", "mars", "cubist", "lm", "randomForest", "xgboost", "mlpe", "ctree", "cv.glmnet", "rpart", "knn", "svm")
  models = c("mars", "cubist")
  targets = c("NW", "NE", "SW", "SE")
  for(model in models){
    for(target in targets){
      f = as.formula(paste0(target, " ~ B + G + R"))
      pan.m = fit(f, dsL8, model = model)
      pan.p = predict(pan.m, dsL8)
      print(paste0(metric," for a ",model," model in ",target,": ", mmetric(dsL8[,target], pan.p, metric)))
    }
  }
}
