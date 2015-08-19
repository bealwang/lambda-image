"""Provides ImagesLoader object and helpers, used to read Images data from disk or other filesystems.
"""
from io import BytesIO
import json
from matplotlib.pyplot import imread
from numpy import array, dstack, frombuffer, ndarray, prod, load, swapaxes

from MEHI.rdds.fileio.readers import getParallelReaderForPath, getFileReaderForPath, FileNotFoundError
from MEHI.rdds.images import Images


class ImagesLoader(object):
    """Loader object used to instantiate Images data stored in a variety of formats.
    """
    def __init__(self, sparkContext):
        """Initialize a new ImagesLoader object.

        Parameters
        ----------
        sparkcontext: SparkContext
            The pyspark SparkContext object used by the current MEHI environment.
        """
        from MEHI.utils.aws import AWSCredentials
        self.sc = sparkContext
        self.awsCredentialsOverride = AWSCredentials.fromContext(sparkContext)

    def fromArrays(self, arrays, npartitions=None):
        """Load Images data from passed sequence of numpy arrays.

        Expected usage is mainly in testing - having a full dataset loaded in memory
        on the driver is likely prohibitive in the use cases for which MEHI is intended.
        """
        # if passed a single array, cast it to a sequence of length 1
        if isinstance(arrays, ndarray):
            arrays = [arrays]

        shape = None
        dtype = None
        for ary in arrays:
            if shape is None:
                shape = ary.shape
                dtype = ary.dtype
            if not ary.shape == shape:
                raise ValueError("Arrays must all be of same shape; got both %s and %s" %
                                 (str(shape), str(ary.shape)))
            if not ary.dtype == dtype:
                raise ValueError("Arrays must all be of same data type; got both %s and %s" %
                                 (str(dtype), str(ary.dtype)))
        narrays = len(arrays)
        npartitions = min(narrays, npartitions) if npartitions else narrays
        return Images(self.sc.parallelize(enumerate(arrays), npartitions),
                      dims=shape, dtype=str(dtype), nrecords=narrays)

    def fromStack(self, dataPath, dims=None, dtype=None, ext='stack', startIdx=None, stopIdx=None, recursive=False,
                  nplanes=None, npartitions=None, confFilename='conf.json'):
        """Load an Images object stored in a directory of flat binary files

        The RDD wrapped by the returned Images object will have a number of partitions equal to the number of image data
        files read in by this method.

        Currently all binary data read by this method is assumed to be formatted as signed 16 bit integers in native
        byte order.

        Parameters
        ----------

        dataPath: string
            Path to data files or directory, specified as either a local filesystem path or in a URI-like format,
            including scheme. A dataPath argument may include a single '*' wildcard character in the filename.

        dims: tuple of positive int
            Dimensions of input image data, ordered with fastest-changing dimension first

        ext: string, optional, default "stack"
            Extension required on data files to be loaded.

        startIdx, stopIdx: nonnegative int. optional.
            Indices of the first and last-plus-one data file to load, relative to the sorted filenames matching
            `datapath` and `ext`. Interpreted according to python slice indexing conventions.

        recursive: boolean, default False
            If true, will recursively descend directories rooted at datapath, loading all files in the tree that
            have an extension matching 'ext'. Recursive loading is currently only implemented for local filesystems
            (not S3 or GS).

        nplanes: positive integer, default None
            If passed, will cause a single binary stack file to be subdivided into multiple records. Every
            `nplanes` z-planes in the file will be taken as a new record, with the first nplane planes of the
            first file being record 0, the second nplane planes being record 1, etc, until the first file is
            exhausted and record ordering continues with the first nplane planes of the second file, and so on.
            With nplanes=None (the default), a single file will be considered as representing a single record.

        npartitions: positive int, optional.
            If specified, request a certain number of partitions for the underlying Spark RDD. Default is 1
            partition per image file.
        """
        reader = getFileReaderForPath(dataPath)(awsCredentialsOverride=self.awsCredentialsOverride)
        try:
            jsonBuf = reader.read(dataPath, filename=confFilename)
            params = json.loads(jsonBuf)
        except FileNotFoundError:
            params = {}

        if 'dtype' in params.keys():
            dtype = params['dtype']
        if 'dims' in params.keys():
            dims = params['dims']

        if not dims:
            raise ValueError("Image dimensions must be specified either as argument or in a conf.json file")

        if not dtype:
            dtype = 'int16'

        if nplanes is not None:
            if nplanes <= 0:
                raise ValueError("nplanes must be positive if passed, got %d" % nplanes)
            if dims[-1] % nplanes:
                raise ValueError("Last dimension of stack image '%d' must be divisible by nplanes '%d'" %
                                 (dims[-1], nplanes))

        def toArray(idxAndBuf):
            idx, buf = idxAndBuf
            ary = frombuffer(buf, dtype=dtype, count=int(prod(dims))).reshape(dims, order='F')
            if nplanes is None:
                yield idx, ary
            else:
                # divide array into chunks of nplanes
                npoints = dims[-1] / nplanes  # integer division
                if dims[-1] % nplanes:
                    npoints += 1
                timepoint = 0
                lastPlane = 0
                curPlane = 1
                while curPlane < ary.shape[-1]:
                    if curPlane % nplanes == 0:
                        slices = [slice(None)] * (ary.ndim - 1) + [slice(lastPlane, curPlane)]
                        yield idx*npoints + timepoint, ary[slices]
                        timepoint += 1
                        lastPlane = curPlane
                    curPlane += 1
                # yield remaining planes
                slices = [slice(None)] * (ary.ndim - 1) + [slice(lastPlane, ary.shape[-1])]
                yield idx*npoints + timepoint, ary[slices]

        reader = getParallelReaderForPath(dataPath)(self.sc, awsCredentialsOverride=self.awsCredentialsOverride)
        readerRdd = reader.read(dataPath, ext=ext, startIdx=startIdx, stopIdx=stopIdx, recursive=recursive,
                                npartitions=npartitions)
        nrecords = reader.lastNRecs if nplanes is None else None
        newDims = tuple(list(dims[:-1]) + [nplanes]) if nplanes else dims
        return Images(readerRdd.flatMap(toArray), nrecords=nrecords, dims=newDims, dtype=dtype)

    def fromOCP(self, bucketName, resolution, server='ocp.me', startIdx=None, stopIdx=None,
                minBound=None, maxBound=None):
        """
        Creates up a new Image object with data read from OCP.
      
        Parameters
        ----------
        bucketName: string
            Name of the token/bucket in OCP. You can use the token name you created in OCP here.
            You can also access publicly available data on OCP at this URL "http://ocp.me/ocp/ca/public_tokens/"
        
        resolution: nonnegative int
            Resolution of the data in OCP

        server: string. optional.
            Name of the server in OCP which has the corresponding token.

        startIdx, stopIdx: nonnegative int. optional.
            Indices of the first and last-plus-one data file to load, relative to the sorted filenames matching
            `datapath` and `ext`. Interpreted according to python slice indexing conventions.

        minBound, maxBound: tuple of nonnegative int. optional.
            X,Y,Z bounds of the data you want to fetch from OCP. minBound contains
            the (xMin,yMin,zMin) while maxBound contains (xMax,yMax,zMax)
        """

        # Given a data-path/bucket Query JSON
        # Given bounds get a list of URI's
        import urllib2
        urlList = []
        url = 'http://{}/ocp/ca/{}/info/'.format(server, bucketName)

        try:
            f = urllib2.urlopen(url)
        except urllib2.URLError:
            raise Exception("Failed URL {}".format(url))

        import json
        projInfo = json.loads(f.read())

        # Loading Information from JSON object
        ximageSize, yimageSize = projInfo['dataset']['imagesize']['{}'.format(resolution)]
        zimageStart, zimageStop = projInfo['dataset']['slicerange']
        timageStart, timageStop = projInfo['dataset']['timerange']

        # Checking if dimensions are within bounds
        if startIdx is None:
            startIdx = timageStart
        elif startIdx < timageStart or startIdx > timageStop:
            raise Exception("startIdx out of bounds {},{}".format(timageStart, timageStop))

        if stopIdx is None:
            stopIdx = timageStop
        elif stopIdx < timageStart or stopIdx > timageStop:
            raise Exception("startIdx out of bounds {},{}".format(timageStart, timageStop))

        if minBound is None:
            minBound = (0, 0, zimageStart)
        elif minBound < (0, 0, zimageStart) or minBound > (ximageSize, yimageSize, zimageStop):
            raise Exception("minBound is incorrect {},{}".format((0, 0, zimageStart),
                                                                 (ximageSize, yimageSize, zimageStop)))

        if maxBound is None:
            maxBound = (ximageSize, yimageSize, zimageStop)
        elif maxBound < (0, 0, zimageStart) or maxBound > (ximageSize, yimageSize, zimageStop):
            raise Exception("minBound is incorrect {},{}".format((0, 0, zimageStart), (ximageSize, yimageSize,
                                                                                       zimageStop)))

        for t in range(timageStart, timageStop, 1):
            urlList.append("http://{}/ocp/ca/{}/npz/{},{}/{}/{},{}/{},{}/{},{}/".
                           format(server, bucketName, t, t + 1, resolution, minBound[0],
                                  maxBound[0], minBound[1], maxBound[1], minBound[2], maxBound[2]))

        def read(url):
            """Fetch URL from the server"""

            try:
                npzFile = urllib2.urlopen(url)
            except urllib2.URLError:
                raise Exception("Failed URL {}.".format(url))

            imgData = npzFile.read()
        
            import zlib
            import cStringIO
            pageStr = zlib.decompress(imgData[:])
            pageObj = cStringIO.StringIO(pageStr)
            data = load(pageObj)
            # Data comes in as 4d numpy array in t,z,y,x order. Swapping axes and removing the time dimension
            # to give back a 3d numpy array in x,y,z order
            data = swapaxes(data[0, :, :, :], 0, 2)

            return data
      
        rdd = self.sc.parallelize(enumerate(urlList), len(urlList)).map(lambda (k, v): (k, read(v)))
        return Images(rdd, nrecords=len(urlList))

    def fromTif(self, dataPath, ext='tif', startIdx=None, stopIdx=None, recursive=False, nplanes=None,
                npartitions=None):
        """Sets up a new Images object with data to be read from one or more tif files.

        Multiple pages of a multipage tif file will by default be assumed to represent the z-axis (depth) of a
        single 3-dimensional volume, in which case a single input multipage tif file will be converted into
        a single Images record. If `nplanes` is passed, then every nplanes pages will be interpreted as a single
        3d volume (2d if nplanes==1), allowing a single tif file to contain multiple Images records.

        This method attempts to explicitly import PIL. ImportError may be thrown if 'from PIL import Image' is
        unsuccessful. (PIL/pillow is not an explicit requirement for MEHI.)

        The RDD wrapped by the returned Images object will by default have a number of partitions equal to the
        number of image data files read in by this method; it may have fewer partitions if npartitions is specified.

        Parameters
        ----------

        dataPath: string
            Path to data files or directory, specified as either a local filesystem path or in a URI-like format,
            including scheme. A datapath argument may include a single '*' wildcard character in the filename.

        ext: string, optional, default "tif"
            Extension required on data files to be loaded.

        startIdx, stopIdx: nonnegative int. optional.
            Indices of the first and last-plus-one data file to load, relative to the sorted filenames matching
            `datapath` and `ext`. Interpreted according to python slice indexing conventions.

        recursive: boolean, default False
            If true, will recursively descend directories rooted at datapath, loading all files in the tree that
            have an extension matching 'ext'.

        nplanes: positive integer, default None
            If passed, will cause a single multipage tif file to be subdivided into multiple records. Every
            `nplanes` tif pages in the file will be taken as a new record, with the first nplane pages of the
            first file being record 0, the second nplane pages being record 1, etc, until the first file is
            exhausted and record ordering continues with the first nplane images of the second file, and so on.
            With nplanes=None (the default), a single file will be considered as representing a single record.

        npartitions: positive int, optional.
            If specified, request a certain number of partitions for the underlying Spark RDD. Default is 1
            partition per image file.
        """

        try:
            from PIL import Image
        except ImportError, e:
            Image = None
            raise ImportError("fromMultipageTif requires a successful 'from PIL import Image'; " +
                              "the PIL/pillow library appears to be missing or broken.", e)
        # we know that that array(pilimg) works correctly for pillow == 2.3.0, and that it
        # does not work (at least not with spark) for old PIL == 1.1.7. we believe but have not confirmed
        # that array(pilimg) works correctly for every version of pillow. thus currently we check only whether
        # our PIL library is in fact pillow, and choose our conversion function accordingly
        isPillow = hasattr(Image, "PILLOW_VERSION")
        if isPillow:
            conversionFcn = array  # use numpy's array() function
        else:
            from MEHI.utils.common import pil_to_array
            conversionFcn = pil_to_array  # use our modified version of matplotlib's pil_to_array

        if nplanes is not None and nplanes <= 0:
            raise ValueError("nplanes must be positive if passed, got %d" % nplanes)

        def multitifReader(idxAndBuf):
            idx, buf = idxAndBuf
            pageCount = -1
            values = []
            fbuf = BytesIO(buf)
            multipage = Image.open(fbuf)
            if multipage.mode.startswith('I') and 'S' in multipage.mode:
                # signed integer tiff file; use tifffile module to read
                import MEHI.rdds.fileio.tifffile as tifffile
                fbuf.seek(0)  # reset pointer after read done by PIL
                tfh = tifffile.TiffFile(fbuf)
                ary = tfh.asarray()  # ary comes back with pages as first dimension, will need to transpose
                pageCount = ary.shape[0]
                if nplanes is not None:
                    values = [ary[i:(i+nplanes)] for i in xrange(0, ary.shape[0], nplanes)]
                else:
                    values = [ary]
                tfh.close()
                # transpose Z dimension if any, leave X and Y in same order
                if ary.ndim == 3:
                    values = [val.transpose((1, 2, 0)) for val in values]
                    # squeeze out last dimension if singleton
                    values = [val.squeeze(-1) if val.shape[-1] == 1 else val for val in values]
            else:
                # normal case; use PIL/Pillow for anything but signed ints
                pageIdx = 0
                imgArys = []
                npagesLeft = -1 if nplanes is None else nplanes  # counts number of planes remaining in image if positive
                while True:
                    try:
                        multipage.seek(pageIdx)
                        imgArys.append(conversionFcn(multipage))
                        pageIdx += 1
                        npagesLeft -= 1
                        if npagesLeft == 0:
                            # we have just finished an image from this file
                            retAry = dstack(imgArys) if len(imgArys) > 1 else imgArys[0]
                            values.append(retAry)
                            # reset counters:
                            npagesLeft = nplanes
                            imgArys = []
                    except EOFError:
                        # past last page in tif
                        break
                pageCount = pageIdx
                if imgArys:
                    retAry = dstack(imgArys) if len(imgArys) > 1 else imgArys[0]
                    values.append(retAry)
            # check for inappropriate nplanes that doesn't evenly divide num pages
            if nplanes and (pageCount % nplanes):
                raise ValueError("nplanes '%d' does not evenly divide page count of multipage tif '%d'" %
                                 (nplanes, pageCount))
            nvals = len(values)
            keys = [idx*nvals + timepoint for timepoint in xrange(nvals)]
            return zip(keys, values)

        reader = getParallelReaderForPath(dataPath)(self.sc, awsCredentialsOverride=self.awsCredentialsOverride)
        readerRdd = reader.read(dataPath, ext=ext, startIdx=startIdx, stopIdx=stopIdx, recursive=recursive,
                                npartitions=npartitions)
        nrecords = reader.lastNRecs if nplanes is None else None
        #return Images(readerRdd.flatMap(multitifReader), nrecords=nrecords)
        return Images(readerRdd, nrecords=nrecords)

    def fromPng(self, dataPath, ext='png', startIdx=None, stopIdx=None, recursive=False, npartitions=None):
        """Load an Images object stored in a directory of png files

        The RDD wrapped by the returned Images object will have a number of partitions equal to the number of image data
        files read in by this method.

        Parameters
        ----------

        dataPath: string
            Path to data files or directory, specified as either a local filesystem path or in a URI-like format,
            including scheme. A dataPath argument may include a single '*' wildcard character in the filename.

        ext: string, optional, default "png"
            Extension required on data files to be loaded.

        startIdx, stopIdx: nonnegative int. optional.
            Indices of the first and last-plus-one data file to load, relative to the sorted filenames matching
            `datapath` and `ext`. Interpreted according to python slice indexing conventions.

        recursive: boolean, default False
            If true, will recursively descend directories rooted at datapath, loading all files in the tree that
            have an extension matching 'ext'. Recursive loading is currently only implemented for local filesystems
            (not s3 or Google Storage).

        npartitions: positive int, optional.
            If specified, request a certain number of partitions for the underlying Spark RDD. Default is 1
            partition per image file.
        """
        def readPngFromBuf(buf):
            fbuf = BytesIO(buf)
            return imread(fbuf, format='png')

        reader = getParallelReaderForPath(dataPath)(self.sc, awsCredentialsOverride=self.awsCredentialsOverride)
        readerRdd = reader.read(dataPath, ext=ext, startIdx=startIdx, stopIdx=stopIdx, recursive=recursive,
                                npartitions=npartitions)
        return Images(readerRdd.mapValues(readPngFromBuf), nrecords=reader.lastNRecs)


def writeBinaryImagesConfig(outputDirPath, dims, dtype='int16',
                            confFilename="conf.json", overwrite=True, awsCredentialsOverride=None):
    """
    Helper function to write out a conf.json file with required information to load binary Image data.
    """
    from MEHI.rdds.fileio.writers import getFileWriterForPath

    filewriterClass = getFileWriterForPath(outputDirPath)

    # write configuration file
    conf = {'dims': dims, 'dtype': dtype}
    confWriter = filewriterClass(outputDirPath, confFilename, overwrite=overwrite,
                                 awsCredentialsOverride=awsCredentialsOverride)
    confWriter.writeFile(json.dumps(conf, indent=2))

    # touch "SUCCESS" file as final action
    successWriter = filewriterClass(outputDirPath, "SUCCESS", overwrite=overwrite,
                                    awsCredentialsOverride=awsCredentialsOverride)
    successWriter.writeFile('')
