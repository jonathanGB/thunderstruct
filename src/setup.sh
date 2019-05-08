#!/usr/bin/env bash

sudo apt-get update

sudo apt-get install python3 python-dev python3-dev build-essential libssl-dev libffi-dev libxml2-dev libxslt1-dev zlib1g-dev python-pip python-scipy libsuitesparse-dev ffmpeg

sudo pip3 install numpy scipy matplotlib IPython pymetis pycuda pyculib
sudo pip3 install scikit-sparse

export PGI=/opt/pgi;
export PATH=/opt/pgi/linux86-64/18.10/bin:$PATH;
export MANPATH=$MANPATH:/opt/pgi/linux86-64/18.10/man;
export LM_LICENSE_FILE=$LM_LICENSE_FILE:/opt/pgi/license.dat;
