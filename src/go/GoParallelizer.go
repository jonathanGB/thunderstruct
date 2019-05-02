package main

import "C"

import (
	"context"
	"fmt"
	"io"
	"runtime"
	"sync"
	"unsafe"

	pb "github.com/jonathanGB/cs205-project/src/go/distributed"
	"google.golang.org/grpc"
)

var (
	addresses = [2]string{"localhost:8080", "localhost:8081"}
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
				sliceResult[i] = sliceA[i] + sliceB[i]*scalar
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
				sliceResult[i] = sliceA[i] - sliceB[i]*scalar
			}

			wg.Done()
		}(firstCol, endCol)
	}

	wg.Wait()
}

//export DistributedDot
func DistributedDot(indptr *C.int, len_indptr C.int, indices *C.int, len_indices C.int, data *C.double, len_data C.int, vec *C.double, len_vec C.int, result *C.double) {
	sliceIndptr := (*[1 << 30]int32)(unsafe.Pointer(indptr))[:len_indptr:len_indptr]
	sliceIndices := (*[1 << 30]int32)(unsafe.Pointer(indices))[:len_indices:len_indices]
	sliceData := (*[1 << 30]float64)(unsafe.Pointer(data))[:len_data:len_data]
	sliceVec := (*[1 << 30]float64)(unsafe.Pointer(vec))[:len_vec:len_vec]
	sliceResult := (*[1 << 30]float64)(unsafe.Pointer(result))[:len_vec:len_vec]

	servers := len(addresses)
	blockSize := len(sliceVec) / servers
	var wg sync.WaitGroup
	wg.Add(servers)

	for server := 0; server < servers; server++ {
		firstRow := server * blockSize
		endRow := (server + 1) * blockSize
		if server == servers-1 {
			endRow = len(sliceVec)
		}

		go func(firstRow, endRow, server int) {
			conn, err := grpc.Dial(addresses[server], grpc.WithInsecure())
			if err != nil {
				panic(err)
			}
			defer conn.Close()

			subIndptr := sliceIndptr[firstRow : endRow+1]
			subStart, subEnd := subIndptr[0], subIndptr[len(subIndptr)-1]
			req := &pb.DotRequest{
				Indptr:  subIndptr,
				Indices: sliceIndices[subStart:subEnd],
				Data:    sliceData[subStart:subEnd],
				Vec:     sliceVec,
			}
			stream, err := pb.NewParallelizerClient(conn).Dot(context.Background(), req)
			if err != nil {
				panic(err)
			}

			for {
				resp, err := stream.Recv()
				if err == io.EOF {
					break
				}
				if err != nil {
					fmt.Println("Err receiving...")
					panic(err)
				}

				resultFirstRow := firstRow + int(resp.Offset)
				copy(sliceResult[resultFirstRow:resultFirstRow+len(resp.Result)], resp.Result)
			}

			wg.Done()
		}(firstRow, endRow, server)
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
					sliceResult[i] = 0.0
					continue
				}

				row := sliceData[sliceIndptr[i]:sliceIndptr[i+1]]
				var sum C.double
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
