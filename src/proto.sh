#!/usr/bin/env bash

python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. go/distributed/distributed.proto
protoc -I. go/distributed/distributed.proto --go_out=plugins=grpc:.
