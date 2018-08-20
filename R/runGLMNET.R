library(glmnet)

#multivariate gaussian
x=as.matrix(ds[,1:3])
y=as.matrix(ds[,5:8])
fit1m=glmnet(x, y, family="mgaussian")
print(fit1m)
coef(fit1m,s=0.01) # extract coefficients at a single value of lambda
plot(fit1m,type.coef="2norm")
y_prime = predict(fit1m,newx=x,s=c(0.01))[,,1] # make predictions
mmetric(as.vector(y), as.vector(y_prime), "MSE")
mmetric(as.vector(y), as.vector(y_prime), "R2")
