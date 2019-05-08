# CS205-project

##OMP
This branch has both the OMP and Hybrid implementation of the parallelization. In order to run the OMP version you must install the following dependencies: 



-software­properties­common

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

Testing was also performed in a py35 enviroment for standarization and to compile and test the code we simply used a c5.xlarge instance with the following commands as per the infrastructure guide:

$ gcc -fopenmp omp_sc.c o omp_sc

$ export OMP_NUM_THREADS= 8

$ time ./omp_sc

Here the -fopenmp flag specifies openmp and the OMP_NUM_THREADS export allows the user to determine the number of threads being used.

##Hybrid
The hybrid implementation requires all of the above in addition to the creation of a cluster of nodes with the following dependencies:

- master: nfs-kernel-server

- worker: nfs-common

- all nodes: mpich

In addition, you must configure the nodes together using sshkeygen and ssh-copy-id to share the keys between the master and node and between all of the nodes themselves. All of the workers must have a shared mounted directory to work. Once this is configured the mpi/omp script can be compiled and run using the following commands:

$ mpicc -fPIC -shared -o matmulmodule.so matmulmodule.c -fopenmp 

$ mpirun -np n -hosts master,node1, node2, node3 python lightning.py
