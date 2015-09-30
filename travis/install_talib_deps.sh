#!/bin/sh
# Thanks to https://github.com/gbeced/pyalgotrade for this script
sudo apt-get install cython
wget http://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure ; make; sudo make install
cd ..
