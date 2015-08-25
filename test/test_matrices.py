import shutil
import tempfile
from numpy import array, array_equal, add
from lambdaimage.rdds.matrices import RowMatrix
from test_utils import PySparkTestCase


class MatrixRDDTestCase(PySparkTestCase):
    def setUp(self):
        super(MatrixRDDTestCase, self).setUp()
        self.outputDir = tempfile.mkdtemp()

    def tearDown(self):
        super(MatrixRDDTestCase, self).tearDown()
        shutil.rmtree(self.outputDir)


class TestElementWise(MatrixRDDTestCase):

    def test_elementwise_rdd(self):
        mat1 = RowMatrix(self.sc.parallelize([(1, array([1, 2, 3])), (2, array([4, 5, 6]))], 2))
        mat2 = RowMatrix(self.sc.parallelize([(1, array([7, 8, 9])), (2, array([10, 11, 12]))], 2))
        result = mat1.elementwise(mat2, add).rows().collect()
        truth = array([[8, 10, 12], [14, 16, 18]])
        assert array_equal(result, truth)

    def test_elementwise_array(self):
        mat = RowMatrix(self.sc.parallelize([(1, array([1, 2, 3]))]))
        assert array_equal(mat.elementwise(2, add).rows().collect()[0], array([3, 4, 5]))


class TestTimes(MatrixRDDTestCase):

    def test_times_rdd(self):
        mat1 = RowMatrix(self.sc.parallelize([(1, array([1, 2, 3])), (2, array([4, 5, 6]))], 2))
        mat2 = RowMatrix(self.sc.parallelize([(1, array([7, 8, 9])), (2, array([10, 11, 12]))], 2))
        truth = array([[47, 52, 57], [64, 71, 78], [81, 90, 99]])
        resultA = mat1.times(mat2)
        assert array_equal(resultA, truth)

    def test_times_array(self):
        mat1 = RowMatrix(self.sc.parallelize([(1, array([1, 2, 3])), (2, array([4, 5, 6]))]))
        mat2 = array([[7, 8], [9, 10], [11, 12]])
        truth = [array([58, 64]), array([139, 154])]
        rdd = mat1.times(mat2)
        result = rdd.rows().collect()
        assert array_equal(result, truth)
        assert array_equal(rdd.index, range(0, 2))


class TestOuter(MatrixRDDTestCase):

    def test_outer(self):
        mat1 = RowMatrix(self.sc.parallelize([(1, array([1, 2, 3])), (2, array([4, 5, 6]))]))
        resultA = mat1.gramian()
        resultB1 = mat1.gramian("accum")
        resultB2 = mat1.gramian("aggregate")
        truth = array([[17, 22, 27], [22, 29, 36], [27, 36, 45]])
        assert array_equal(resultA, truth)
        assert array_equal(resultB1, truth)
        assert array_equal(resultB2, truth)
