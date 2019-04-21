#!/usr/bin/env bash

sudo apt-get update

sudo apt-get install ffmpeg
sudo apt-get install python-scipy libsuitesparse-dev

sudo apt-get install python3-pip
sudo pip3 install numpy scipy matplotlib IPython
sudo pip3 install scikit-sparse

sudo snap install go --classic
go build -o GoParallelizer.so -buildmode=c-shared GoParallelizer.go