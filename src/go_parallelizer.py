import ctypes
import numpy as np
import numpy.ctypeslib as npct
from sys import stderr
import go.distributed.distributed_pb2 as pb
import go.distributed.distributed_pb2_grpc as pb_grpc
import grpc

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
    self.stub = pb_grpc.GreeterStub(grpc.insecure_channel("localhost:8080"))
    print(self.stub.SayHello(pb.HelloRequest(name="Jonathan")))

  def dot(self, A, B):
    #print("{} {}".format(min(A.data), max(A.data)), file=stderr)
    #self.lib.Dot.restype = npct.ndpointer(dtype=ctypes.c_double, shape=B.shape)
    result = np.zeros(B.shape, dtype=np.float)
    self.lib.Dot(A.indptr, len(A.indptr), A.indices, len(A.indices), A.data, len(A.data), B, len(B), result)
    return result

  def datadd(self, A, B, scalar, result):
    self.lib.Add(A, B, scalar, result, len(A))

  def datsub(self, A, B, scalar, result):
    self.lib.Sub(A, B, scalar, result, len(A))
