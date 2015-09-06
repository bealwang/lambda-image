#from lambdaimage.rdds.images import Images
from lambdaimage.imgprocessing.deconvolution import DeconvolutionMethod

class deconvRL(DeconvolutionMethod):
    def __init__(self, *args, **kwargs):
        self.psf=None
        self.iteration=None

    def prepare(self, psf, iter):
        from lambdaimage.rdds.fileio.tifffile import imread
        self.psf=imread(psf)
        self.iteration=iter


class deconvER(DeconvolutionMethod):
    def __init__(self, *args, **kwargs):
        pass

    def prepare(self, images):
        pass

