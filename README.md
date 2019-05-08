# CS205-project

To run, do the following commands on Ubuntu 18.04.

On the worker nodes:
```bash
cd src
./setup.sh
cd go
go run server.go
```

Gather all the internal IP addresses of the worker nodes.

On the master node:
```bash
cd src
./setup.sh
cd go
```

Open the GoParallelizer.go file, and modify this line:
```go
var (
	addresses = [2]string{"localhost:8080", "localhost:8081"}
)
```

to
```go
var (
	addresses = [8]string{"<ip_address1>:8080", "<ip_address2>:8081", ...}
)
```

Essentially, we are listing all the IP addresses of the worker nodes. Notice that we need to change `2` to `8` as the size of the array.

Then do
```bash
./gb.sh
cd ..
python3 lightning.py
```
