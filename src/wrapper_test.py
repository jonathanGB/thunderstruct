import numpy as np
from subprocess import Popen, PIPE
import ctypes
import os
import sys

import matmul


class Math_ops:
  def __init__(self):
    self.array_1d_int = npct.ndpointer(dtype=np.int32, ndim=1, flags='CONTIGUOUS')
    self.array_1d_float = npct.ndpointer(dtype=np.float, ndim=1, flags='CONTIGUOUS')
     self.array_2d_int = npct.ndpointer(dtype=np.int32, ndim=2, flags='CONTIGUOUS')
    self.array_2d_float = npct.ndpointer(dtype=np.float, ndim=2, flags='CONTIGUOUS')
    self.lib = ctypes.cdll.LoadLibrary("./matmulmodule.so")
    self.lib.matmul.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_double, 
      self.array_1d_float, ctypes.c_double,
      self.array_2d_int, ctypes.c_int, 
      self.array_2d_int, ctypes.c_int, 
      self.array_2d_float, ctypes.c_double, 
      self.array_2d_float, ctypes.c_double

    ]

    self.lib.dot.argtypes = [
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_int, ctypes.c_int, 
      self.array_1d_float, ctypes.c_double, 
      self.array_1d_float, ctypes.c_double,
      self.array_2d_int, ctypes.c_int, 
      self.array_2d_int, ctypes.c_int, 
      self.array_2d_float, ctypes.c_double, 
      self.array_2d_float, ctypes.c_double

    ]

  def dot(self, A, B):
    self.lib.Dot.restype = npct.ndpointer(dtype=ctypes.c_double, shape=B.shape)
    return self.lib.matmul(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B))


