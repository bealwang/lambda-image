###############################
# Author   : septicmk
# Date     : 2015/07/25 16:14:09
# FileName : main.py
################################

from lambdaimage import preprocess as prep
from lambdaimage import registration as reg
from lambdaimage import fusion as fus
from pyspark import SparkContext, SparkConf
from lambdaimage import ThunderContext
from lambdaimage.utils.tool import exeTime, log, showsize
import numpy as np

#conf = SparkConf().setAppName('test').setMaster('local[1]').set('spark.executor.memory','2g').set('spark.driver.maxResultSize','6g').set('spark.driver.memory','8g').set('spark.local.dir','/dev/shm').set('spark.storage.memoryFraction','0.2').set('spark.default.parallelism','10')
#tsc=ThunderContext.start(conf=conf)
tsc = ThunderContext.start(master="spark://blade12:7077",appName="lambdaimage")
log('info')('tiff load start...')
rddA = tsc.loadImages('/home/wb/data/1-L/*.tif', inputFormat='tif-stack')
rddB = tsc.loadImages('/home/wb/data/1-R/*.tif', inputFormat='tif-stack')
log('info')('tiff load over...')

log('info')('intensity normalization start ...')
rddA = prep.intensity_normalization(rddA)
rddB = prep.intensity_normalization(rddB)
rddB = prep.flip(rddB)

_rddA = prep.intensity_normalization(rddA,8)
_rddB = prep.intensity_normalization(rddB,8)
log('info')('intensity normalization over ...')

log('info')('registration start ...')
vec0 = [0,0,0,1,1,0,0]
vec = reg.c_powell(_rddA.get(4), _rddB.get(4), vec0)
rddB = reg.execute(rddB, vec)
log('info')('registration over ...')

log('info')('fusion start ...')
L_img_stack = rddA.collectValuesAsArray()
R_img_stack = rddB.collectValuesAsArray()
img_stack = zip(L_img_stack, R_img_stack)
rdd = tsc.loadImagesFromArray(img_stack)
fused_img = fus.wavelet_fusion(rdd)
fused_img = tsc.loadImagesFromArray(fused_img)
log('info')('fusion over ...')

log('info')('saving ...')
fused_img.exportAsTiffs('/home/wb/data/lambdaimage/fusion',overwrite = True)
#fused_img = np.squeeze(np.array(fused_img.values().collect()))

log('info')('subtract background start ...')
sb_img = prep.subtract_Background(fused_img)
log('info')('sbutract background over ... ')

log('info')('saving ...')
sb_img.exportAsTiffs('/home/wb/data/lambdaimage/subtract',overwrite = True)
