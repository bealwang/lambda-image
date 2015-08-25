from lambdaimage.rdds.images import Images
from lambdaimage.utils.common import checkParams
from lambdaimage.imgprocessing.decmethods.deconv_c import deconv_func

class Deconvolution(object):
    """
    """
    def __new__(cls, method, **kwargs):
        from lambdaimage.imgprocessing.decmethods.deconv import deconvRL, deconvER
    
        DECMETHODS={
            'rl': deconvRL,
            'er': deconvER
        }

        checkParams(method, DECMETHODS.keys())
        return DECMETHODS[method](kwargs)

class DeconvolutionMethod(object):
    def __init__(self, *args, **kwargs):
        pass

    #def run(self, nfile):
    def run(self, images):
        """
        """
        from lambdaimage.rdds.fileio.tifffile import imread
        from lambdaimage.rdds.fileio.tifffile import imsave
        import numpy as np

        #images=imread(nfile)

        #print 'apple before: '
        #print images
        psf=images.rdd.context.broadcast(self.psf)
        iteration=images.rdd.context.broadcast(self.iteration)

        newrdd=images.rdd.map(lambda (k, v):(k, deconv_func(np.float32(v), np.float32(psf.value), iteration.value)))
        #newrdd=images.rdd.map(lambda (k, v):(k, v+10))
        #result=deconv_func(images, self.psf, self.iteration)
        #return Images(newrdd).__finalize__(images)
        #print 'apple newrdd apple count' , newrdd.count()
        #print 'apple after: '
        return Images(newrdd)
        #print result
        #if(len(result.shape)==3):
        #    result=image.T
        #    result=np.swapaxes(image,1,2)
        #imsave("/home/jph/test/g3/w_g3.tif", result)
        
