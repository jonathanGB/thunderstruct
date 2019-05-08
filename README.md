# CS205-project

### PyCuda
PyCuda implementation is on the `pycuda` branch.
`git checkout pycuda`

### Go: single-node
The implementation is here, on master. To run, you need to do the following commands on Ubuntu 18.04
```bash
cd src
./setup.sh
./gb.sh
python3 lightning.py
```

Architecture: 96-core machine on GCP
$ lscpu
Architecture:            x86_64
CPU op-mode(s):          32-bit, 64-bit
Byte Order:              Little Endian
CPU(s):                  96
On-line CPU(s) list: 0-95
Thread(s) per core:  2
Core(s) per socket:  24
Socket(s):               2
NUMA node(s):            2
Vendor ID:               GenuineIntel
CPU family:              6
Model:                   85
Model name:              Intel(R) Xeon(R) CPU @ 2.00GHz
Stepping:                3
CPU MHz:                 2000.180
BogoMIPS:                4000.36
Hypervisor vendor:   KVM
Virtualization type: full
L1d cache:               32K
L1i cache:               32K
L2 cache:                256K
L3 cache:                56320K
NUMA node0 CPU(s):   0-23,48-71
NUMA node1 CPU(s):   24-47,72-95

### Go: multi-node
The implementation can be found on the `grpc-buffer` branch.
`git checkout grpc-buffer`

### OMP and Hybrid

The implementation can be found on the `MPI-OMP` branch. 
`git checkout MPI-OMP`
