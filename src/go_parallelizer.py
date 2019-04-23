import ctypes
import numpy as np
import numpy.ctypeslib as npct

class GoParallelizer:
  def __init__(self):
    self.array_1d_int = npct.ndpointer(dtype=np.int32, ndim=1, flags='CONTIGUOUS')
    self.array_1d_float = npct.ndpointer(dtype=np.float, ndim=1, flags='CONTIGUOUS')

    self.array_2d_int = npct.ndpointer(dtype=np.int32, ndim=2, flags='CONTIGUOUS')
    self.array_2d_float = npct.ndpointer(dtype=np.float, ndim=2, flags='CONTIGUOUS')

    self.lib = ctypes.cdll.LoadLibrary("./GoParallelizer.so")

    self.lib.Dot.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int
    ]

    self.lib.MatMul.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int,
      self.array_2d_int, ctypes.c_int, 
      self.array_2d_int, ctypes.c_int, 
      self.array_2d_float, ctypes.c_int, 
      self.array_2d_float, ctypes.c_int
    ]


  def matmult(self, A, B):
  	#have to change this to 2 dimensions
  	#restype - result type
  	self.lib.Dot.restype = npct.ndpointer(dtype=ctypes.c_double, shape=(A.shape[0],B.shape[1]))
  	return self.lib.MatMul(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B))

  def dot(self, A, B):
    self.lib.Dot.restype = npct.ndpointer(dtype=ctypes.c_double, shape=B.shape)
    return self.lib.Dot(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B))



