package main

import "C"

import (
	"runtime"
	"sync"
	"unsafe"
)

//export Add
func Add(A *C.double, B *C.double, scalar C.double, result *C.double, lenVec C.int) {
	sliceA := (*[1 << 30]C.double)(unsafe.Pointer(A))[:lenVec:lenVec]
	sliceB := (*[1 << 30]C.double)(unsafe.Pointer(B))[:lenVec:lenVec]
	sliceResult := (*[1 << 30]C.double)(unsafe.Pointer(result))[:lenVec:lenVec]

        procs := runtime.NumCPU()
        blockSize := len(sliceA) / procs
        var wg sync.WaitGroup
        wg.Add(procs)

        for proc := 0; proc < procs; proc++ {
		firstCol := proc * blockSize
                endCol := (proc + 1) * blockSize
                if proc == procs-1 {
                        endCol = len(sliceA)
                }

		go func(firstCol, endCol int) {
			for i := firstCol; i < endCol; i++ {
				sliceResult[i] = sliceA[i] + sliceB[i] * scalar
			}

			wg.Done()
		}(firstCol, endCol)
	}

	wg.Wait()
}

// Logic is the same as `Add` except for the - vs + sign in the loop.
// We keep them separate because it was slightly faster that way.
//export Sub
func Sub(A *C.double, B *C.double, scalar C.double, result *C.double, lenVec C.int) {
        sliceA := (*[1 << 30]C.double)(unsafe.Pointer(A))[:lenVec:lenVec]
        sliceB := (*[1 << 30]C.double)(unsafe.Pointer(B))[:lenVec:lenVec]
        sliceResult := (*[1 << 30]C.double)(unsafe.Pointer(result))[:lenVec:lenVec]

        procs := runtime.NumCPU()
        blockSize := len(sliceA) / procs
        var wg sync.WaitGroup
        wg.Add(procs)

        for proc := 0; proc < procs; proc++ {
                firstCol := proc * blockSize
                endCol := (proc + 1) * blockSize
                if proc == procs-1 {
                        endCol = len(sliceA)
                }

                go func(firstCol, endCol int) {
                        for i := firstCol; i < endCol; i++ {
                                sliceResult[i] = sliceA[i] - sliceB[i] * scalar
                        }

                        wg.Done()
                }(firstCol, endCol)
        }

        wg.Wait()
}

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
