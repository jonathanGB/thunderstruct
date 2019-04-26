#!/usr/bin/env /bin/bash

# Compile GoParallelizer.go to C shared library
go build -o GoParallelizer.so -buildmode=c-shared GoParallelizer.go
