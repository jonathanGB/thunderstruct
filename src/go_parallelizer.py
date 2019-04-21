import ctypes
import numpy as np
import numpy.ctypeslib as npct

class GoParallelizer:
  def __init__(self):
    self.array_1d_int = npct.ndpointer(dtype=np.int32, ndim=1, flags='CONTIGUOUS')
    self.array_1d_float = npct.ndpointer(dtype=np.float, ndim=1, flags='CONTIGUOUS')
    self.lib = ctypes.cdll.LoadLibrary("./GoParallelizer.so")
    self.lib.Dot.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int
    ]

  def dot(self, A, B):
    self.lib.Dot.restype = npct.ndpointer(dtype=ctypes.c_double, shape=B.shape)
    return self.lib.Dot(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B))



