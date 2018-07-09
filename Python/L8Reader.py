# -*- coding: utf-8 -*-
"""
Created on Thu Jul  5 14:19:01 2018

@author: acalderon
"""

#%%
import numpy as np
from osgeo import gdal
band2 = r'C:\Users\acalderon\opt\bda\Bulk Order 921204\Landsat 8 OLI_TIRS C1 Level-1\LC08_L1TP_040036_20180621_20180622_01_RT_B2.tif'
ds = gdal.Open(band2)
gdal.Translate("H:/B2.csv", ds, format = "XYZ")
band3 = r'C:\Users\acalderon\opt\bda\Bulk Order 921204\Landsat 8 OLI_TIRS C1 Level-1\LC08_L1TP_040036_20180621_20180622_01_RT_B3.tif'
ds = gdal.Open(band3)
gdal.Translate("H:/B3.csv", ds, format = "XYZ")
band4 = r'C:\Users\acalderon\opt\bda\Bulk Order 921204\Landsat 8 OLI_TIRS C1 Level-1\LC08_L1TP_040036_20180621_20180622_01_RT_B4.tif'
ds = gdal.Open(band4)
gdal.Translate("H:/B4.csv", ds, format = "XYZ")
band5 = r'C:\Users\acalderon\opt\bda\Bulk Order 921204\Landsat 8 OLI_TIRS C1 Level-1\LC08_L1TP_040036_20180621_20180622_01_RT_B5.tif'
ds = gdal.Open(band5)
gdal.Translate("H:/B5.csv", ds, format = "XYZ")

#%%
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, IntegerType, StructType

spark = SparkSession.builder.appName("SimpleApp").config("spark.executor.memory", "6g").config("spark.driver.memory", "6g").getOrCreate()
schemaString = "x y v"

fields = [StructField(field_name, IntegerType(), True) for field_name in schemaString.split()]
schema = StructType(fields)

band2 = "H:/B2.csv"  
pixels2 = spark.read.option("delimiter", " ").option("header", "false").schema(schema).csv(band2).filter("v > 0").cache()

#%%
psize = 30
gap = 100
xs = pixels2.select("x").orderBy("x").distinct().collect()
midx = xs[0].x + (xs[len(xs) - 1].x - xs[0].x) / 2 
ys = pixels2.select("y").orderBy("y").distinct().collect()
midy = ys[0].y + (ys[len(ys) - 1].y - ys[0].y) / 2 
extend = psize * gap
minx = midx - extend
maxx = midx + extend
miny = midy - extend
maxy = midy + extend

#%%
p2 = pixels2.filter(pixels2["y"] >= miny).filter(pixels2["y"] <= maxy).filter(pixels2["x"] >= minx).filter(pixels2["x"] <= maxx)
p2 = p2.selectExpr("x AS x2" , "y AS y2", "v AS v2")
p2.count()

band3 = "H:/B3.csv"  
pixels3 = spark.read.option("delimiter", " ").option("header", "false").schema(schema).csv(band3).filter("v > 0").cache()
p3 = pixels3.filter(pixels3["y"] >= miny).filter(pixels3["y"] <= maxy).filter(pixels3["x"] >= minx).filter(pixels3["x"] <= maxx)
p3 = p3.selectExpr("x AS x3" , "y AS y3", "v AS v3")
p2.count()

p = p2.join(p3, (p2["x2"] == p3["x3"]) & (p2["y2"] == p3["y3"]), "inner").selectExpr("x3 AS x" , "y3 AS y", "v2", "v3")

band4 = "H:/B4.csv"  
pixels4 = spark.read.option("delimiter", " ").option("header", "false").schema(schema).csv(band4).filter("v > 0").cache()
p4 = pixels4.filter(pixels4["y"] >= miny).filter(pixels4["y"] <= maxy).filter(pixels4["x"] >= minx).filter(pixels4["x"] <= maxx)
p4 = p4.selectExpr("x AS x4" , "y AS y4", "v AS v4")
p4.count()

p = p.join(p4, (p["x"] == p4["x4"]) & (p["y"] == p4["y4"]), "inner").select("x" , "y", "v2", "v3", "v4")

band5 = "H:/B5.csv"  
pixels5 = spark.read.option("delimiter", " ").option("header", "false").schema(schema).csv(band5).filter("v > 0").cache()
p5 = pixels5.filter(pixels5["y"] >= miny).filter(pixels5["y"] <= maxy).filter(pixels5["x"] >= minx).filter(pixels5["x"] <= maxx)
p5 = p5.selectExpr("x AS x5" , "y AS y5", "v AS v5")
p5.count()

data = p.join(p5, (p["x"] == p5["x5"]) & (p["y"] == p5["y5"]), "inner").select("x" , "y", "v2", "v3", "v4", "v5")
data.show()
data.count()

#%%
data.toPandas().to_csv('H:/data.csv', index = False)

#%%
spark.stop()
