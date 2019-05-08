import numpy as np
import pycuda.autoinit
import pycuda.driver as drv
import pycuda.gpuarray as gpuarray
from pycuda.sparse.packeted import PacketedSpMV
from pycuda.tools import DeviceMemoryPool
from scipy.sparse import csr_matrix


def spmv_cuda(a_sparse, b):

    dtype = a_sparse.dtype
    m = a_sparse.shape[0]

    spmv = PacketedSpMV(a_sparse, is_symmetric=False, dtype=dtype)

    dev_pool = DeviceMemoryPool()
    d_b = gpuarray.to_gpu(b, dev_pool.allocate)
    d_c = gpuarray.zeros(m, dtype=dtype, allocator=d_b.allocator)

    d_c.fill(0)
    d_c = spmv(d_b, d_c)
    dev_pool.stop_holding()


    return d_c.get()
