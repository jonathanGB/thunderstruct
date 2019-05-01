from Math_ops import Math_ops 
import numpy as np
from scipy.sparse import csr_matrix

if __name__=="__main__":
	A = np.array([[0,0,3],[4,0,6],[0,8,9]], dtype = "float64")
	B = np.array([3,4], dtype = "float64")
	


	C = np.array([[4,5,6],[6,7,6]], dtype = "float64")
	D = np.array([1,1,1,1,1,1], dtype = "float64")
	E = np.array([4,6,4,3,1,3], dtype = "float64")
	Math = Math_ops()
	
	B = np.array([1.,2.,3.])
	A = csr_matrix(A)
	print("number of nonzero values in each row:")
	print(A.indptr)
	print("length of data: ")
	print(int(len(A.data)))

	#print(len(A.data))
	tmp1 = Math.dot(A,B)
	#print(tmp1)
	#tmp2 = Math.matmul(A,B)
	#tmp3 = Math.vecaddn(D,E,3.,4.)
	#print(tmp3[0].item())
	#Math.test_trans()
	#print(tmp1)
	#print(tmp2)
	#print(tmp3)

