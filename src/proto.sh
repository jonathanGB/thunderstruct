#!/usr/bin/env bash

protoc -I. go/distributed/distributed.proto --go_out=plugins=grpc:.
