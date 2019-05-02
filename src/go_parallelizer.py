import ctypes
import numpy as np
import numpy.ctypeslib as npct
from sys import stderr

class GoParallelizer:
  def __init__(self):
    self.array_1d_int = npct.ndpointer(dtype=np.int32, ndim=1, flags='C')
    self.array_1d_float = npct.ndpointer(dtype=np.float, ndim=1, flags='C')
    self.lib = ctypes.cdll.LoadLibrary("./go/GoParallelizer.so")
    self.lib.Dot.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int,
      self.array_1d_float
    ]
    self.lib.DistributedDot.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int, 
      self.array_1d_float, ctypes.c_int,
      self.array_1d_float
    ]
    self.lib.Add.argtypes = [
      self.array_1d_float,
      self.array_1d_float,
      ctypes.c_double,
      self.array_1d_float,
      ctypes.c_int,
    ]
    self.lib.Sub.argtypes = [
      self.array_1d_float,
      self.array_1d_float,
      ctypes.c_double,
      self.array_1d_float,
      ctypes.c_int
    ]

  def distributed_dot(self, A, B):
    result = np.empty(B.shape, dtype=np.float)
    self.lib.DistributedDot(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B), result)
    return result

  def dot(self, A, B):
    result = np.empty(B.shape, dtype=np.float)
    self.lib.Dot(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B), result)
    return result

  def datadd(self, A, B, scalar, result):
    self.lib.Add(A, B, scalar, result, len(A))

  def datsub(self, A, B, scalar, result):
    self.lib.Sub(A, B, scalar, result, len(A))

if __name__ == "__main__":
  gp = GoParallelizer()
