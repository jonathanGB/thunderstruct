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


Architecture: Master node
$ lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              8
On-line CPU(s) list: 0-7
Thread(s) per core:  1
Core(s) per socket:  8
Socket(s):           1
NUMA node(s):        1
Vendor ID:           GenuineIntel
CPU family:          6
Model:               79
Model name:          Intel(R) Xeon(R) CPU E5-2686 v4 @ 2.30GHz
Stepping:            1
CPU MHz:             2300.062
BogoMIPS:            4600.13
Hypervisor vendor:   Xen
Virtualization type: full
L1d cache:           32K
L1i cache:           32K
L2 cache:            256K
L3 cache:            46080K
NUMA node0 CPU(s):   0-7

Architecture: Worker nodes
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              72
On-line CPU(s) list: 0-71
Thread(s) per core:  2
Core(s) per socket:  18
Socket(s):           2
NUMA node(s):        2
Vendor ID:           GenuineIntel
CPU family:          6
Model:               85
Model name:          Intel(R) Xeon(R) Platinum 8124M CPU @ 3.00GHz
Stepping:            3
CPU MHz:             3042.379
BogoMIPS:            6000.00
Hypervisor vendor:   KVM
Virtualization type: full
L1d cache:           32K
L1i cache:           32K
L2 cache:            1024K
L3 cache:            25344K
NUMA node0 CPU(s):   0-17,36-53
NUMA node1 CPU(s):   18-35,54-71
