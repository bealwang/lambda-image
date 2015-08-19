################################
# Author   : septicmk
# Date     : 2015/07/24 18:56:05
# FileName : test_p_registration.py
################################

from MEHI.registration.registration import *
from MEHI.serial.preprocess import flip
from MEHI import ThunderContext
from test_utils import PySparkTestCase
import numpy as np
from nose.tools import assert_equals
import os

L_pwd = os.path.abspath('.') + '/test_data/L_side_8/*.tif'
R_pwd = os.path.abspath('.') + '/test_data/R_side_8/*.tif'

class PySparkTestRegistrationCase(PySparkTestCase):
    def setUp(self):
        super(PySparkTestRegistrationCase, self).setUp()
        self.tsc = ThunderContext(self.sc)
        self.L_imgs = self.tsc.loadImages(L_pwd, inputFormat='tif-stack')
        self.R_imgs = self.tsc.loadImages(R_pwd, inputFormat='tif-stack')
        self.dtype = self.L_imgs.collectValuesAsArray().dtype
        self.shape = self.L_imgs.collectValuesAsArray().shape
        self.L_imgs = self.L_imgs.collectValuesAsArray()
        self.R_imgs = self.R_imgs.collectValuesAsArray()
        self.imgA = self.L_imgs[0]
        self.imgB = flip(self.R_imgs)[0]
        self.vec0 = [0,0,0,1,1,0,0]
    
    def tearDown(self):
        super(PySparkTestRegistrationCase, self).tearDown()

class TestParalleledRegistration(PySparkTestRegistrationCase):
    def test_p_powell(self):
        pass
        #vec = p_powell(self.imgA, self.imgB, self.vec0)
        #assert (abs(vec[0]-2) <= 5 and abs(vec[1]-3) <= 5 and abs(vec[2]-0) <= 0.5 and abs(vec[3]-1) <= 0.5 and abs(vec[4]-1) <= 0.5 and abs(vec[5]) < 0.2 and abs(vec[6]) < 0.2)
    
    def test_c_powell(self):
        vec = c_powell(self.imgA, self.imgB, self.vec0)
        assert (abs(vec[0]-2) <= 5 and abs(vec[1]-3) <= 5 and abs(vec[2]-0) <= 0.5 and abs(vec[3]-1) <= 0.5 and abs(vec[4]-1) <= 0.5 and abs(vec[5]) < 0.2 and abs(vec[6]) < 0.2)
    
    def test_execute(self):
        rdd = self.tsc.loadImagesFromArray(self.L_imgs)
        ret = execute(rdd, self.vec0).collectValuesAsArray() 
        ret = np.array(ret)
        assert_equals(sum(self.L_imgs.flatten()), sum(ret.flatten()))

    def test_mutual_information(self):
        rdd = self.tsc.loadImagesFromArray(self.L_imgs)
        ret = mutual_information(rdd, 0, self.vec0, self.imgA, self.imgB).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)
        assert (ret.dtype == self.dtype)

    def test_cross_correlation(self):
        img_stack = zip(self.L_imgs, self.R_imgs)
        rdd = self.tsc.loadImagesFromArray(img_stack)
        ret = cross_correlation(rdd).collectValuesAsArray()
        ret = np.array(ret)
        assert (ret.shape == self.shape)


