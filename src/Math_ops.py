import numpy as np
from subprocess import Popen, PIPE
import ctypes
import numpy.ctypeslib as npct

class Math_ops:
	def __init__(self):

		self.math = ctypes.CDLL('./matmulmodule.so')

		#creates pointers to array data types
		self.array_1d_int 	= npct.ndpointer(dtype=np.int32, ndim=1, flags='C')
		self.array_1d_float = npct.ndpointer(dtype=np.double, ndim=1, flags='C')
		self.array_2d_int 	= npct.ndpointer(dtype=np.int32, ndim=2, flags='C')
		self.array_2d_float = npct.ndpointer(dtype=np.double, ndim=2, flags='C')
		
		#initial arguement
		self.math.dot.argtypes = [self.array_1d_float, self.array_1d_int, ctypes.c_int, self.array_1d_int, ctypes.c_int,  self.array_1d_float, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int]
		self.math.vecaddn.argtypes 	= [self.array_1d_float, self.array_1d_float,self.array_1d_float,ctypes.c_int, ctypes.c_double, ctypes.c_double]
		self.math.test_trans.argtypes = None


	def dot(self, A, B):
		#b is just a single vector, not a sparse matrix
		#a is a full sparse matrix 
		#result time
		res = np.zeros(len(A.data),dtype = "float64")
		print(res)
		self.math.dot.restype = None
		#npct.ndpointer(dtype=ctypes.c_double, shape=B.shape)

		#return self.lib.Dot(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B))
		#npct.ndpointer(dtype=ctypes.c_double, shape=B.shape)	
		print("______________C data___________")
		self.math.dot(res, A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B.astype("double"), len(B))
		return res
		
	
	def vecaddn(self, A, B, scaleA, scaleB):
		#simply two vectors
		res = np.zeros(len(A), dtype="float64")
		self.math.vecaddn.restype= npct.ndpointer(dtype=self.array_1d_float, shape=len(A))
		self.math.vecaddn(res, A, B, len(B), scaleA, scaleB)
		return	res


	def test_trans(self):
		arr = np.array([[1.1,2.1,3.1,4.1,5.1,6.1],[1.1,2.1,3.1,4.1,5.1,6.1]])
		self.math.test_trans.restype = None 
		self.math.test_trans(arr)

		print(arr)





