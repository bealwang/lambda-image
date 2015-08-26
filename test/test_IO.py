################################
# Author   : septicmk
# Date     : 2015/07/24 18:47:16
# FileName : test_IO.py
################################

from lambdaimage.serial.IO import *
from test_utils import LocalTestCase
import os
import numpy as np

class TestSerialIO(LocalTestCase):
    def test_load_tiff(self):
        testDirPath = os.path.dirname(os.path.realpath(__file__))
        L_pwd = os.path.join(testDirPath,'test_data/L_side/')
        R_pwd = os.path.join(testDirPath,'test_data/R_side/')
        img_stack = load_tiff(L_pwd)
        assert (img_stack.shape == (10,512,512))
        assert (img_stack.dtype == np.uint16)

