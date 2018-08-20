library(landsat)
library(landsat8)
library(raster)
library(rgdal)
library(tidyverse)

SAVE_FLAG = F
PLOT_FLAG = T


B = vector("list", 5)

metadata = readLines("H:/L7/LE07_L1TP_040036_20180629_20180629_01_RT_MTL.txt")
R_MB = as.numeric(str_split_fixed(metadata[grep("REFLECTANCE_MULT_BAND", str_trim(metadata))], " = ", 2)[,2])
R_AD = as.numeric(str_split_fixed(metadata[grep("REFLECTANCE_ADD_BAND", str_trim(metadata))], " = ", 2)[,2])

Bands = c("B", "G", "R", "I", "S1", "T", "S2", "P")
L7 = vector("list")
i = 8
L = satellite(paste0("H:/L7/LE07_L1TP_040036_20180629_20180629_01_RT_B",i,".TIF"))
L7[[Bands[i]]] = convRad2Ref(L)@layers[2][[1]]
for(i in seq(1,4)){
  L = satellite(paste0("H:/L7/LE07_L1TP_040036_20180629_20180629_01_RT_B",i,".TIF"))
  L7[[Bands[i]]] = resample(convRad2Ref(L)@layers[2][[1]], L7$P)
}

xmin = L7_prime$I@extent@xmin
ymin = L7_prime$I@extent@ymin
Hres = 15
Lres = 30
res = 30
col = 1
row = 1
patch <- as(extent(xmin, xmin + col * res, ymin, ymin + row * res), 'SpatialPolygons')

L = raster("H:/L7/LE07_L1TP_040036_20180629_20180629_01_RT_B8.TIF")
crs(clip) <- crs(L)
L8_Crop = crop(L, clip)
B[[5]] = reflconv(as(L8_Crop, 'SpatialGridDataFrame'), R_MB[7], R_AD[7])

for(i in seq(1,4)){
  L = raster()
  L_Crop = crop(L, clip)
  L_Resampled = resample(L_Crop, L8_Crop, "ngb")
  B[[i]] = reflconv(as(L_Resampled, 'SpatialGridDataFrame'), R_MB[i], R_MB[i])
}

if(PLOT_FLAG){
  for(i in seq(1,5)){
    plot(B[[i]])
  }
}

if(SAVE_FLAG){
  for(i in seq(1,5)){
    writeGDAL(B[[i]], paste0("H:/L7/Refl/B",i,"_Refl.tif"), drivername = "GTiff")
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
  
ds = as.data.frame(dataset %>% select(B,G,R,I,NW,NE,SW,SE))


if(RUN_MODELS){
  metric = "R2"
  # models = c("naive", "mars", "cubist", "lm", "randomForest", "xgboost", "mlpe", "ctree", "cv.glmnet", "rpart", "knn", "svm")
  models = c("mars", "cubist")
  targets = c("NW", "NE", "SW", "SE")
  for(model in models){
    for(target in targets){
      f = as.formula(paste0(target, " ~ B + G + R"))
      pan.m = fit(f, ds, model = model)
      pan.p = predict(pan.m, ds)
      print(paste0(metric," for a ",model," model in ",target,": ", mmetric(ds[,target], pan.p, metric)))
    }
  }
}

