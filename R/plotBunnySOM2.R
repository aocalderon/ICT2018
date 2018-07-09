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

iterations = 10000
interval = 100
rows = 20
cols = 20
rgl_init()

data = read.csv("H:/Projects/R/bunny.txt", sep = " ")
cells = 1:(rows * cols)
umatrix = matrix(cells, nrow = rows, ncol = cols)
for(w in seq(interval, iterations - 1, interval)){
  wts = read.csv(paste0("c:/Users/acalderon/opt/SOM/bunny_",w,".txt"), sep = " ", header = F, skip = 3)
  wts = as.matrix(wts[,c(1,2,3)])
  d = c()
  for(i in 1:nrow(umatrix)){
    for(j in 1:ncol(umatrix)){
      d = rbind(d, traceNeighborhood(umatrix, i, j, wts))
    }
  }
  rgl_init()
  points3d(wts, col = 'red')
  segments3d(d, col = "black")
}
points3d(data, col = 'lightgrey')
