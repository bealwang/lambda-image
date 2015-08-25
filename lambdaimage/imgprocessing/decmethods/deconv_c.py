import numpy as np
import numpy.ctypeslib as npct
from ctypes import c_int

array_2d_float=npct.ndpointer(dtype=np.float32, ndim=2, flags='CONTIGUOUS')
array_3d_float=npct.ndpointer(dtype=np.float32, ndim=3, flags='CONTIGUOUS')

libcd=npct.load_library("libdeconv.so", "/home/wb/lambdaimage/lambdaimage/imgprocessing/decmethods/libdeconv.so")

def deconv_func(image, psf, iter):

    h_nx=None
    h_ny=None
    h_nz=1

    y_nx=None
    y_ny=None
    y_nz=1

    if(len(image.shape)==3):
        image=image.T
        image=np.swapaxes(image,1,2)
        tmp=[]
        for i in range(image.shape[0]):
            tmp.append(image[i,:,:])
        image=np.array(tmp)

    if(len(psf.shape)==2):
        h_nx=psf.shape[1]
        h_ny=psf.shape[0]
        y_nx=image.shape[1]
        y_ny=image.shape[0]
    else:
        h_nx=psf.shape[1]
        h_ny=psf.shape[2]
        h_nz=psf.shape[0]

        y_nx=image.shape[1]
        y_ny=image.shape[2]
        y_nz=image.shape[0]

    if(h_nz==1):
        libcd.deconv.restype=None
        libcd.deconv.argtypes=[array_2d_float, c_int, c_int, c_int, array_2d_float, c_int, c_int, c_int, c_int]
    else:
        libcd.deconv.restype=None
        libcd.deconv.argtypes=[array_3d_float, c_int, c_int, c_int, array_3d_float, c_int, c_int, c_int, c_int]
        
    libcd.deconv(image, y_nx, y_ny, y_nz, psf, h_nx, h_ny, h_nz, iter)

    if(len(image.shape)==3):
        image=image.T
        image=np.swapaxes(image,0,1)

    return image
