################################
# Author   : septicmk
# Date     : 2015/07/24 20:08:44
# FileName : test_p_fusion.py
################################

from lambdaimage.fusion.fusion import *
from lambdaimage import ThunderContext
from test_utils import PySparkTestCase
import numpy as np
import os

L_pwd = os.path.abspath('.') + '/test_data/L_side/*.tif'
R_pwd = os.path.abspath('.') + '/test_data/R_side/*.tif'

class PySparkTestFusionCase(PySparkTestCase):
    def setUp(self):
        super(PySparkTestFusionCase, self).setUp()
        self.tsc = ThunderContext(self.sc)
        self.L_imgs = self.tsc.loadImages(L_pwd, inputFormat='tif-stack')
        self.R_imgs = self.tsc.loadImages(R_pwd, inputFormat='tif-stack')
    
    def tearDown(self):
        super(PySparkTestFusionCase, self).tearDown()

class TestParalleledFusion(PySparkTestFusionCase):
    def test_content_fusion(self):
        self.L_imgs = self.L_imgs.collectValuesAsArray()
        self.R_imgs = self.R_imgs.collectValuesAsArray()
        img_stack = zip(self.L_imgs, self.R_imgs)
        rdd = self.tsc.loadImagesFromArray(img_stack)
        fused_img = content_fusion(rdd)
        assert (fused_img.dtype == self.L_imgs.dtype)
        assert (fused_img.shape == self.L_imgs.shape)
    
    def test_wavelet_fusion(self):
        self.L_imgs = self.L_imgs.collectValuesAsArray()
        self.R_imgs = self.R_imgs.collectValuesAsArray()
        img_stack = zip(self.L_imgs, self.R_imgs)
        rdd = self.tsc.loadImagesFromArray(img_stack)
        fused_img = wavelet_fusion(rdd)
        assert (fused_img.dtype == self.L_imgs.dtype)
        assert (fused_img.shape == self.L_imgs.shape)

