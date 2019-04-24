import ctypes
import numpy as np
import numpy.ctypeslib as npct
from sys import stderr

class GoParallelizer:
  def __init__(self):
    self.array_1d_int = npct.ndpointer(dtype=np.int32, ndim=1, flags='C')
    self.array_1d_float = npct.ndpointer(dtype=np.float, ndim=1, flags='C')
    self.lib = ctypes.cdll.LoadLibrary("./GoParallelizer.so")
    self.lib.Dot.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int,
      self.array_1d_float
    ]

  def dot(self, A, B):
    #print("{} {}".format(min(A.data), max(A.data)), file=stderr)
    #self.lib.Dot.restype = npct.ndpointer(dtype=ctypes.c_double, shape=B.shape)
    result = np.zeros(B.shape, dtype=np.float)
    self.lib.Dot(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B), result)
    return result



