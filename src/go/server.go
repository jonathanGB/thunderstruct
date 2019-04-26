package main

import (
	"context"
	"fmt"
	"log"
	"net"

	pb "github.com/jonathanGB/cs205-project/src/go/distributed"
	"google.golang.org/grpc"
)

const port = ":8080"

type server struct{}

func (p *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	fmt.Printf("Received a message from %s", in.Name)

	return &pb.HelloReply{Message: "Got your message, " + in.Name}, nil
}

func main() {
	lis, err := net.Listen("tcp", port)
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterGreeterServer(s, &server{})
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
