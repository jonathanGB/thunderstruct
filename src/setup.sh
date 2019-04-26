#!/usr/bin/env bash

sudo apt-get update

sudo apt-get install ffmpeg
sudo apt-get install python-scipy libsuitesparse-dev

sudo apt-get install python3-pip
sudo pip3 install numpy scipy matplotlib IPython grpcio-tools
sudo pip3 install scikit-sparse

sudo snap install go --classic
go build -o GoParallelizer.so -buildmode=c-shared GoParallelizer.go

go get google.golang.org/grpc
go get github.com/golang/protobuf/protoc-gen-go

export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
ln -s "$(pwd)/.." "$GOPATH/src/github.com/jonathanGB/project"

python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. go/distributed/distributed.proto
protoc -I. go/distributed/distributed.proto --go_out=plugins=grpc:.