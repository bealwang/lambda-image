################################
# Author   : septicmk
# Date     : 2015/07/30 15:15:42
# FileName : test_p_segmentation.py
################################

from MEHI.segmentation.segmentation import *
from MEHI import ThunderContext
from test_utils import PySparkTestCase
import numpy as np
from nose.tools import assert_equals
import os

L_pwd = os.path.abspath('.') + '/test_data/L_side/*.tif'
R_pwd = os.path.abspath('.') + '/test_data/R_side/*.tif'

class PySparkTestSegmentationCase(PySparkTestCase):
    def setUp(self):
        super(PySparkTestSegmentationCase, self).setUp()
        self.tsc = ThunderContext(self.sc)
        self.L_imgs = self.tsc.loadImages(L_pwd, inputFormat='tif-stack')
        self.R_imgs = self.tsc.loadImages(R_pwd, inputFormat='tif-stack')
        self.dtype = self.L_imgs.collectValuesAsArray().dtype
        self.shape = self.L_imgs.collectValuesAsArray().shape

    def tearDown(self):
        super(PySparkTestSegmentationCase, self).tearDown()

class TestParalleledSegmentation(PySparkTestSegmentationCase):

    def test_threshold(self):
        rdd = self.L_imgs
        ret = np.array(threshold(rdd, 'adaptive', 15).collectValuesAsArray())
        assert (ret.shape == self.shape) 
        ret = np.array(threshold(rdd, 'otsu').collectValuesAsArray())
        assert (ret.shape == self.shape)
        ret = np.array(threshold(rdd, 'duel').collectValuesAsArray())
        assert (ret.shape == self.shape)

    #def test_watershed_3d(self):
    #    rdd = self.L_imgs
    #    binary = threshold(rdd, 'adaptive', 15).collectValuesAsArray()
    #    binary = np.array(binary)
    #    labeled_stack = watershed_3d(self.L_imgs.collectValuesAsArray(), binary)
    #    assert (labeled_stack.shape == self.shape)
    #    prop = properties(labeled_stack)
