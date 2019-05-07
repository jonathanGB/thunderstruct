# include <stdio.h>
# include <stdlib.h>
# include "mpi.h"



void dot(double* ret, int* indptr, int indptrlen, int* indA, int lenindA, double* A, int lenA, double* B, int size_arr$
    int rows = indptrlen - 1;
    int i; 
    int j;
    int provided = 0;
    int ptr;
    int ptrtemp;
    double sum;
    int numInRow;
    ptr = 0;
    
    MPI_Init_thread(NULL,NULL,  MPI_THREAD_MULTIPLE, &provided); // Initialize 
    #pragma omp parallel shared(A, B, ret) private(i,j)
    {
    for(i=1; i < indptrlen; i++){
        sum = 0;
        numInRow= indptr[i] - indptr[i-1];
        ptrtemp = ptr;
        ptr += numInRow;


        for(j = ptrtemp; j < ptr; j++){
                sum += A[j]*B[indA[j]];

        }
    
        ret[i-1] = sum; 

    }
    }
    MPI_Finalize();
}

void vecaddn(double* ret, double* A, double* B, int lenA, double scaleA, double scaleB){
    int i; 

    #pragma omp parallel shared(A, B, ret) private(i)
    {
    for (i = 0; i < lenA; i++) {

                ret[i] = A[i]*scaleA + B[i]*scaleB;

                printf("%f \n",scaleA);
            }   

}
