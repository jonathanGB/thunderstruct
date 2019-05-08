import numpy as np
import pycuda.autoinit
import pycuda.driver as drv
import pycuda.gpuarray as gpuarray
from pycuda.sparse.packeted import PacketedSpMV
from pycuda.tools import DeviceMemoryPool
from scipy.sparse import csr_matrix
from time import time


def spmv_cuda(a_sparse, b, count):
    print(a_sparse.data.nbytes + a_sparse.indptr.nbytes + a_sparse.indices.nbyt$
    print(a_sparse.shape, b.shape)
    print(a_sparse.dtype, b.dtype)
    dtype = a_sparse.dtype
    m = a_sparse.shape[0]
    start = time()
    print('moving objects to GPU...')

    spmv = PacketedSpMV(a_sparse, is_symmetric=False, dtype=dtype)
    spmv = PacketedSpMV(a_sparse, is_symmetric=False, dtype=dtype)

    dev_pool = DeviceMemoryPool()
    d_b = gpuarray.to_gpu(b, dev_pool.allocate)
    d_c = gpuarray.zeros(m, dtype=dtype, allocator=d_b.allocator)
    print(time()-start)
    print('executing spmv operation...\n')

    tic = time()
    d_c.fill(0)
    d_c = spmv(d_b, d_c)
    toc = time()
    dev_pool.stop_holding()
    return d_c.get(), toc - tic


# run benchmark
COUNT = 100
N = 90000
P = 0.00004
DTYPE = np.float32

print('Constructing objects...\n\n')

np.random.seed(0)
a_dense = np.random.rand(N, N).astype(DTYPE)
a_dense[np.random.rand(N, N) >= P] = 0
a_sparse = csr_matrix(a_dense)

b = np.random.rand(N, 1).astype(DTYPE)

# pycuda sparse
c, t = spmv_cuda(a_sparse, b, COUNT)
print('pycuda sparse matrix multiplication took {} seconds\n'.format(t))
print('c = {}\n'.format(c[:5]))
