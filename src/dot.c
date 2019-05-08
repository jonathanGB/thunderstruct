#include <math.h>
#include <stdio.h>
//export Dot
int main (int argc, char* argv[])
{
  int indptr = argv[0];
  int len_indptr = argv[1];
  int indices = argv[2];
  int len_indices = argv[3];
  double data = argv[4];
  int len_data = argv[5];
  double vec = argv[6];
  int len_vec = argv[7];

  int res[len_vec], number_in_row, k;
  int ptr = 0;
  int sum = 0;

  for(int i=0; i < len_vec; i ++){

    number_in_row = indptr[i] - indptr[i-1];

    int eles[number_in_row];

    k = 0;

    for(int m=ptr; m<(ptr+number_in_row); m ++){

      eles = indices[m];

      k += 1;

    }

    ptr += number_in_row;

    for(int j = 0; j < number_in_row; j ++){

      sum += data[indptr[i-1]+j]*vec[eles[j]];

    }

    res[i-1] = sum;

  }

}
