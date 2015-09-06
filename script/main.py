from lambdaimage import preprocess as prep
from lambdaimage import registration as reg
from lambdaimage import fusion as fus
from lambdaimage import segmentation as seg
from lambdaimage import lambdaimageContext
from lambdaimage.utils.tool import exeTime, log
from pyspark import SparkContext, SparkConf
from parseXML import load_xml_file, get_function
import numpy as np
import time

conf = SparkConf().setAppName('test').setMaster('local[1]').set('spark.executor.memory','2g').set('spark.driver.maxResultSize','6g').set('spark.driver.memory','8g').set('spark.local.dir','/dev/shm').set('spark.storage.memoryFraction','0.2').set('spark.default.parallelism','10')
tsc=lambdaimageContext.start(conf=conf)

result = load_xml_file("./lambdaimage.xml")
count = 0

log('info')('load tiff ...')
rddA = tsc.loadImages('/home/wb/data/1-L/*.tif', inputFormat='tif-stack')
rddB = tsc.loadImages('/home/wb/data/1-R/*.tif', inputFormat='tif-stack')

log('info')('preprocess ...')
fun, para = get_function(count, result)
_rddA = eval(fun)(rddA,int(para[0]))
print fun
_rddB = eval(fun)(rddB,int(para[0]))
print fun
count += 1
fun, para = get_function(count, result)
_rddB = eval(fun)(_rddB)
print fun
rddB = eval(fun)(rddB)
print fun

count += 1
fun, para = get_function(count, result)
log('info')('registration ...')
rddB = eval(fun)(rddB)(_rddA.get(int(para[0])), _rddB.get(int(para[0])))
print fun

count += 1
fun, para = get_function(count, result)
log('info')('fusion ...')
L_img = rddA.collectValuesAsArray()
R_img = rddB.collectValuesAsArray()
img = zip(L_img, R_img)
rdd = tsc.loadImagesFromArray(img)
#rdd = rddA.zip(rddB)
fused_img = eval(fun)(rdd)
print fun

count += 1
fun, para = get_function(count, result)
log('info')('preprocess ...')
rdd = tsc.loadImagesFromArray(fused_img)
rdd = eval(fun)(rdd)
print fun

count += 1
fun, para = get_function(count, result)

rdd = eval(fun)(rdd)
print fun

sub_img = rdd.collectValuesAsArray()
log('info')('segmentation ... ')

count += 1
fun, para = get_function(count, result)

rdd = eval(fun)(rdd, int(para[0]))
print fun

count += 1
fun, para = get_function(count, result)

rdd = eval(fun)(rdd, int(para[0]))
print fun
smooth = rdd.collectValuesAsArray()
img = zip(sub_img, smooth)
rdd = tsc.loadImagesFromArray(img)

count += 1
fun, para = get_function(count, result)

rdd = eval(fun)(rdd, int(para[0]))
print fun
binary = rdd.collectValuesAsArray()

count += 1
fun, para = get_function(count, result)

prop = eval(fun)(binary, sub_img, int(para[0]), int(para[1]))
print fun
prop.to_csv("prop.csv")
