package main

import "C"

import (
	"reflect"
	"runtime"
	"sync"
	"unsafe"
)

//export DotSerial
func DotSerial(indptr *C.short, len_indptr C.int, indices *C.short, len_indices C.int, data *C.float, len_data C.int, vec *C.float, len_vec C.int) uintptr {
	headerIndptr := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(indptr)),
		Len:  int(len_indptr),
		Cap:  int(len_indptr),
	}
	sliceIndptr := *(*[]int32)(unsafe.Pointer(&headerIndptr))

	headerIndices := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(indices)),
		Len:  int(len_indices),
		Cap:  int(len_indices),
	}
	sliceIndices := *(*[]int32)(unsafe.Pointer(&headerIndices))

	headerData := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(data)),
		Len:  int(len_data),
		Cap:  int(len_data),
	}
	sliceData := *(*[]float64)(unsafe.Pointer(&headerData))

	headerVec := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(vec)),
		Len:  int(len_vec),
		Cap:  int(len_vec),
	}
	sliceVec := *(*[]float64)(unsafe.Pointer(&headerVec))

	result := make([]float64, len_vec, len_vec)
	j := 0
	for i := 0; i < len(sliceVec); i++ {
		if sliceIndptr[i] == sliceIndptr[i+1] {
			continue
		}

		row := sliceData[sliceIndptr[i]:sliceIndptr[i+1]]

		sum := 0.0
		for _, val := range row {
			col := sliceIndices[j]

			sum += val * sliceVec[col]
			j++
		}

		result[i] = sum
	}

	return uintptr(unsafe.Pointer(&result[0]))
}

//export Dot
func Dot(indptr *C.short, len_indptr C.int, indices *C.short, len_indices C.int, data *C.float, len_data C.int, vec *C.float, len_vec C.int) uintptr {
	headerIndptr := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(indptr)),
		Len:  int(len_indptr),
		Cap:  int(len_indptr),
	}
	sliceIndptr := *(*[]int32)(unsafe.Pointer(&headerIndptr))

	headerIndices := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(indices)),
		Len:  int(len_indices),
		Cap:  int(len_indices),
	}
	sliceIndices := *(*[]int32)(unsafe.Pointer(&headerIndices))

	headerData := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(data)),
		Len:  int(len_data),
		Cap:  int(len_data),
	}
	sliceData := *(*[]float64)(unsafe.Pointer(&headerData))

	headerVec := reflect.SliceHeader{
		Data: uintptr(unsafe.Pointer(vec)),
		Len:  int(len_vec),
		Cap:  int(len_vec),
	}
	sliceVec := *(*[]float64)(unsafe.Pointer(&headerVec))

	result := make([]float64, len_vec, len_vec)
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
				sum := 0.0
				for _, val := range row {
					col := sliceIndices[j]

					sum += val * sliceVec[col]
					j++
				}

				result[i] = sum
			}

			wg.Done()
		}(firstRow, endRow)
	}

	wg.Wait()
	return uintptr(unsafe.Pointer(&result[0]))
}

func main() {}
