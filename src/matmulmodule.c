# include <stdio.h>
# include <stdlib.h>
//s# include <"mpi.h”> 



float *dot(int* indptr, int indptrlen, int* indA, int lenindA, double* A, int lenA, double* B, int size_arr) {
	//MPI_Init(&argc, &argv); // Initialize 
	//MPI_Comm_size(MPI_COMM_WORLD, &np);
	//MPI_Comm_rank(MPI_COMM_WORLD, &pid); 
    
    double * ret;
    int rows = indptrlen - 1;
    //printf("number of rows:  %d \n", rows);
    ret = (double *)malloc(sizeof(double*)* rows);
    int i; 
    int j;

     #pragma omp parallel shared(A, B, ret) private(i,j){
     #pragma omp for schedule (static, chunk)

    int ptr;
    int ptrtemp;
    double sum;
    int numInRow;
   	ptr = 0;

    for(i=1; i < indptrlen; i++){
    	sum = 0;
    	
    	numInRow= indptr[i] - indptr[i-1];
    	//printf("number in each row: %d \n", numInRow);
    	ptrtemp = ptr;
    	ptr += numInRow;
    	

    	for(j = ptrtemp; j < ptr; j++){
    		//printf("value of A here: %f \n", A[j]);
    		//printf("value of B here %f \n \n", B[indA[j]]);
    		sum += A[j]*B[indA[j]];

    	}
    	//printf("sum term here %f \n", sum);
    	ret[i-1] = sum; 
    


    }


	//}
    return ret;
}

double *vecaddn(double* A, double* B, int lenA, double scaleA, double scaleB){
	//MPI_Init(&argc, &argv); // Initialize 
	//MPI_Comm_size(MPI_COMM_WORLD, &np);
	//MPI_Comm_rank(MPI_COMM_WORLD, &pid); 
	
	double *ret;
    ret = (double *)malloc(sizeof(double)* lenA);
    int i; 
	     
    #pragma omp parallel shared(A, B, ret) private(i){
    	#pragma omp for schedule (static, chunk)
	    for (i = 0; i < lenA; i++) {

	        ret[i] = A[i]*scaleA + B[i]*scaleB;

	        printf("%f \n",scaleA);
	    }	
		
	    return ret;

}

void test_trans(double* arr){

		int i = 1;
		int j = 2;
		int len =4;

		printf("item 1: %f", arr[0]);
		*((arr+i*len) + j) = 9;
}