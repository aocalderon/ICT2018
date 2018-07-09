library(rgl)
library(kohonen)
library(stringr)

rgl_init <- function(new.device = FALSE, bg = "white", width = 800) { 
  if( new.device | rgl.cur() == 0 ) {
    rgl.open()
    par3d(windowRect = 50 + c( 0, 0, width, width ) )
    rgl.bg(color = bg )
  }
  rgl.clear(type = c("shapes", "bboxdeco"))
  rgl.viewpoint(theta = 15, phi = 20, zoom = 0.7)
}

traceNeighborhood <- function(Umatrix, x, y, codes){
  o = Umatrix[x, y]
  coords = c()
  if(x - 1 > 0){
    e = Umatrix[x - 1, y]
    coords = rbind(coords, codes[o,], codes[e,])
  }
  if(y - 1 > 0){
    n = Umatrix[x, y - 1]
    coords = rbind(coords, codes[o,], codes[n,])
  }
  return(coords)
}

plotMap <- function(som_map, x = 1, y = 2, z = 3){
  codes = getCodes(som_map)
  points3d(codes[,x],codes[,y],codes[,z], box = F, col = "red")
  cells = 1:(som_map$grid$xdim * som_map$grid$ydim)
  umatrix = matrix(cells, nrow = som_map$grid$xdim, ncol = som_map$grid$ydim)
  d = c()
  for(i in 1:som_map$grid$xdim){
    for(j in 1:som_map$grid$ydim){
      d = rbind(d, traceNeighborhood(umatrix, i, j, codes))
    }
  }
  segments3d(d, col = "black")
}

SOMRunner <- function(data, rows, cols, iterations){
  som.data <- som(data, alpha = c(0.5, 0.001), rlen = iterations, grid = somgrid(rows, cols, "hexagonal"))
  codes = getCodes(som.data)
  points3d(codes[,1],codes[,2],codes[,3], box = F, col = "red")
  cells = 1:(rows * cols)
  umatrix = matrix(cells, nrow = rows, ncol = cols)
  d = c()
  for(i in 1:nrow(umatrix)){
    for(j in 1:ncol(umatrix)){
      d = rbind(d, traceNeighborhood(umatrix, i, j, codes))
    }
  }
  segments3d(d, col = "black")
  
  return(som.data)
}

data = read.csv("H:/data.csv", sep = ",")
#points3d(data[,3],data[,4],data[,5], box = F, col = "blue")
data = data[,c(3,4,5,6)]
data = as.matrix(data)
set.seed(42)
iterations = 20
rows = 100
cols = 100
ANIMATE = FALSE
#data = scale(data)

if(ANIMATE){
  rgl_init()
  for(i in 1:iterations){
    rgl.clear()
    som = SOMRunner(data, rows, cols, i)
    rgl.snapshot(paste0("H:/Projects/R/figures/som", str_pad(i, 3, pad = "0"),".png"))
  }
  #points3d(data[,1],data[,2],data[,3], box = F, col = "blue")
} else {
  som.data <- som(data, alpha = c(0.5, 0.001), rlen = iterations, grid = somgrid(rows, cols, "hexagonal"))
  plotMap(som.data)
  #points3d(data[,1],data[,2],data[,3], box = F, col = "blue")
}
