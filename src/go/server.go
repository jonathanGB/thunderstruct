package main

import (
	"fmt"
	"log"
	"net"
	"runtime"

	pb "github.com/jonathanGB/cs205-project/src/go/distributed"
	"google.golang.org/grpc"
)

const port = ":8080"

type server struct{}

func (p *server) Dot(in *pb.DotRequest, stream pb.Parallelizer_DotServer) error {
	sliceIndptr := in.Indptr
	sliceIndices := in.Indices
	sliceData := in.Data
	sliceVec := in.Vec
	sliceLen := len(sliceIndptr) - 1
	indptrOffset := sliceIndptr[0]

	procs := runtime.NumCPU()
	resps := make(chan *pb.DotReply, procs)
	blockSize := sliceLen / procs

	for proc := 0; proc < procs; proc++ {
		firstRow := proc * blockSize
		endRow := (proc + 1) * blockSize
		if proc == procs-1 {
			endRow = sliceLen
		}

		go func(firstRow, endRow int) {
			lenResults := endRow - firstRow
			results := make([]float64, lenResults, lenResults)
			j := sliceIndptr[firstRow] - indptrOffset
			for i := firstRow; i < endRow; i++ {
				if sliceIndptr[i] == sliceIndptr[i+1] {
					results[i-firstRow] = 0.0
					continue
				}

				row := sliceData[sliceIndptr[i]-indptrOffset : sliceIndptr[i+1]-indptrOffset]
				var sum float64
				for _, val := range row {
					col := sliceIndices[j]

					sum += val * sliceVec[col]
					j++
				}

				results[i-firstRow] = sum
			}

			resps <- &pb.DotReply{Result: results, Offset: int32(firstRow)}
		}(firstRow, endRow)
	}

	for i := 0; i < procs; i++ {
		if err := stream.Send(<-resps); err != nil {
			fmt.Println("err streaming")
			fmt.Println(err)
			return err
		}
	}
	return nil
}

func main() {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}
	fmt.Printf("Listening to port %s", port)

	s := grpc.NewServer(grpc.MaxRecvMsgSize(322942800))
	pb.RegisterParallelizerServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
