#!/usr/bin/env bash

sudo apt-get update

sudo apt-get install ffmpeg
sudo apt-get install python-scipy libsuitesparse-dev

sudo apt-get install python3-pip
sudo pip3 install numpy scipy matplotlib IPython grpcio-tools
sudo pip3 install scikit-sparse

sudo snap install go --classic
sudo snap install protobuf --classic

go get google.golang.org/grpc
go get github.com/golang/protobuf/protoc-gen-go

export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin
mkdir -p "$GOPATH/src/github.com/jonathanGB"
ln -s "$(pwd)/.." "$GOPATH/src/github.com/jonathanGB/project"

./proto.sh
