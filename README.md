# CS205-project

This branch has both the OMP and Hybrid implementation of the parallelization. In order to run the OMP version you must install the following dependencies: 

-software­properties­common\n
-ppa:ubuntu­toolchain­r/test
-gcc

The following are also needed to run the python scripts:

-numpy
-Anaconda
-scikit
-sckit-sparse
-cython 
-CHOLMOD
-ctypes

Testing was also performed in a py35 enviroment for standarization and to compile and test the code we simply used a c5.xlarge instance with the following commands:
$ gcc - fopenmp omp_sc.c ­o omp_sc
$ export OMP_NUM_THREADS= 8
$ time ./omp_sc



For the hyp
