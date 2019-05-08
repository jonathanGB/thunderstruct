#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install python3 python-dev python3-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev python-pip python-scipy libsuitesparse-dev ffmpeg
sudo apt-get install libcr-dev mpich mpich-doc
sudo pip3 install numpy scipy matplotlib IPython pymetis pycuda pyculib cython ctypes
sudo pip3 install scikit-sparse
sudo apt-get install nfs-common
sudo apt-get install nfs-kernel-server

export MPICH_PORT_RANGE=10000:10100
export MPIR_CVAR_CH3_PORT_RANGE=10000:10100
export LM_LICENSE_FILE=$LM_LICENSE_FILE:/opt/pgi/license.dat;
