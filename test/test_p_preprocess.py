################################
# Author   : septicmk
# Date     : 2015/07/24 18:56:01
# FileName : test_p_preprocess.py
################################

from lambdaimage.preprocess.preprocess import *
from lambdaimage import lambdaimageContext
from test_utils import PySparkTestCase
import numpy as np
import os

L_pwd = os.path.abspath('.') + '/test_data/L_side/*.tif'
R_pwd = os.path.abspath('.') + '/test_data/R_side/*.tif'

class PySparkTestPreprocessCase(PySparkTestCase):
    def setUp(self):
        super(PySparkTestPreprocessCase, self).setUp()
        self.tsc = lambdaimageContext(self.sc)
        self.L_imgs = self.tsc.loadImages(L_pwd, inputFormat='tif-stack')
        self.R_imgs = self.tsc.loadImages(R_pwd, inputFormat='tif-stack')
        self.dtype = self.L_imgs.collectValuesAsArray().dtype
        self.shape = self.L_imgs.collectValuesAsArray().shape
    def tearDown(self):
        super(PySparkTestPreprocessCase, self).tearDown()

class TestParalleledPreprocess(PySparkTestPreprocessCase):
    def test_stripe_removal(self):
        rdd = self.L_imgs
        ret = stripe_removal(rdd).collectValuesAsArray()
        assert (ret.shape == self.shape) 
        assert (ret.dtype == self.dtype)
    
    def test_intensity_normalization(self):
        rdd = self.L_imgs
        ret = intensity_normalization(rdd).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == self.dtype)
        ret = intensity_normalization(rdd, 8).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == np.uint8)
        ret = intensity_normalization(rdd, 16).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == np.uint16)
    
    def test_flip(self):
        rdd = self.L_imgs
        ret = flip(rdd).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == self.dtype)
    
    def test_invert(self):
        rdd = self.L_imgs
        ret = invert(rdd).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == self.dtype)
    
    def test_black_tophat(self):
        rdd = self.L_imgs
        ret = black_tophat(rdd).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == self.dtype)
    
    def test_subtract_Background(self):
        rdd = self.L_imgs
        ret = subtract_Background(rdd).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == self.dtype)
    
    def test_shrink(self):
        rdd = self.L_imgs
        ret = shrink(rdd).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.dtype == self.dtype)
        assert (ret.shape == (10, 256, 256))
    
    def test_projection(self):
        self.L_imgs = self.L_imgs.collectValuesAsArray()
        maxp = projection(self.L_imgs, 'max')
        minp = projection(self.L_imgs, 'min')
        meanp = projection(self.L_imgs, 'mean')
        assert (maxp.dtype == self.L_imgs.dtype and maxp.shape == self.L_imgs[0].shape)
        assert (minp.dtype == self.L_imgs.dtype and minp.shape == self.L_imgs[0].shape)
        assert (meanp.shape == self.L_imgs[0].shape)

    def test_smooth(self):
        rdd = self.L_imgs
        ret = np.array(smooth(rdd, 10).collectValuesAsArray())
        assert (ret.dtype == self.dtype)
        assert (ret.shape == self.shape)

