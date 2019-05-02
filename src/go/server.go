package main

import (
	"fmt"
	"log"
	"net"
	"runtime"
	"sync"

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

	procs := runtime.NumCPU() - 1
	resps := make(chan *pb.DotReply)
	finalStatus := make(chan error, 1)
	blockSize := sliceLen / procs
	var wg sync.WaitGroup
	wg.Add(procs)

	go func() {
		for resp := range resps {
			if err := stream.Send(resp); err != nil {
				finalStatus <- err
			}
		}
		finalStatus <- nil
	}()

	for proc := 0; proc < procs; proc++ {
		firstRow := proc * blockSize
		endRow := (proc + 1) * blockSize
		if proc == procs-1 {
			endRow = sliceLen
		}

		go func(firstRow, endRow int) {
			j := sliceIndptr[firstRow] - indptrOffset
			for i := firstRow; i < endRow; i++ {
				if sliceIndptr[i] == sliceIndptr[i+1] {
					resps <- &pb.DotReply{
						LocalRow: int32(i),
						Result:   0,
					}
					continue
				}

				row := sliceData[sliceIndptr[i]-indptrOffset : sliceIndptr[i+1]-indptrOffset]
				var sum float64
				for _, val := range row {
					col := sliceIndices[j]

					sum += val * sliceVec[col]
					j++
				}

				resps <- &pb.DotReply{
					LocalRow: int32(i),
					Result:   sum,
				}
			}

			wg.Done()
		}(firstRow, endRow)
	}

	wg.Wait()
	close(resps)
	return <-finalStatus
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
