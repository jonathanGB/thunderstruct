package main

import "C"

import (
	"runtime"
	"sync"
	"unsafe"
)

//export Dot
func Dot(indptr *C.int, len_indptr C.int, indices *C.int, len_indices C.int, data *C.double, len_data C.int, vec *C.double, len_vec C.int, result *C.double) {
	sliceIndptr := (*[1 << 30]C.int)(unsafe.Pointer(indptr))[:len_indptr:len_indptr]
	sliceIndices := (*[1 << 30]C.int)(unsafe.Pointer(indices))[:len_indices:len_indices]
	sliceData := (*[1 << 30]C.double)(unsafe.Pointer(data))[:len_data:len_data]
	sliceVec := (*[1 << 30]C.double)(unsafe.Pointer(vec))[:len_vec:len_vec]
	sliceResult := (*[1 << 30]C.double)(unsafe.Pointer(result))[:len_vec:len_vec]

	procs := runtime.NumCPU()
	blockSize := len(sliceVec) / procs
	var wg sync.WaitGroup
	wg.Add(procs)

	for proc := 0; proc < procs; proc++ {
		firstRow := proc * blockSize
		endRow := (proc + 1) * blockSize
		if proc == procs-1 {
			endRow = len(sliceVec)
		}

		go func(firstRow, endRow int) {
			j := sliceIndptr[firstRow]
			for i := firstRow; i < endRow; i++ {
				if sliceIndptr[i] == sliceIndptr[i+1] {
					continue
				}

				row := sliceData[sliceIndptr[i]:sliceIndptr[i+1]]
				var sum C.double = 0.0
				for _, val := range row {
					col := sliceIndices[j]

					sum += val * sliceVec[col]
					j++
				}

				sliceResult[i] = sum
			}

			wg.Done()
		}(firstRow, endRow)
	}

	wg.Wait()
}

func main() {}
