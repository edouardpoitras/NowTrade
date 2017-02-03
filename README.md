# NowTrade

[![Build Status](https://travis-ci.org/edouardpoitras/NowTrade.svg?branch=master)](https://travis-ci.org/edouardpoitras/NowTrade)
[![Coverage Status](https://coveralls.io/repos/edouardpoitras/NowTrade/badge.svg?branch=master&service=github)](https://coveralls.io/github/edouardpoitras/NowTrade?branch=master)

NowTrade is an algorithmic trading library with a focus on creating powerful strategies using easily-readable and simple Python code.
With the help of NowTrade, full blown stock/currency trading strategies, harnessing the power of machine learning, can be implemented with few lines of code.

NowTrade strategies are not event driven like most other algorithmic trading libraries available.
The strategies are implemented in a sequential manner (one line at a time) without worrying about events, callbacks, or object overloading.

### The Basics

All strategies follow this basic pattern:

* Load the required data for your strategy
* Train your machine learning algorithm (optional)
* Add your technical indicators (example: moving average, relative strength index, neural network, random forest, etc)
* Add criteria based on your technical indicators (example: neural network prediction is higher than current price)
* Associate actions to those criteria (example: go long when a certain criteria is true)
* Create a trading profile (includes information such as your capital, trading amount rules, trading fee rules, slippage rules, etc)
* Send all of this information to a strategy simulator and wait for results


Check out some example strategies in the [examples](examples) directory.

### Features
Here is a list of reasons you may want to use NowTrade over alternatives:

* Implement strategies easily
* Flexible data connections (store data locally from any remote data connection)
* Easily implement machine learning into strategies (neural networks, random forest, etc)
* Simple, small, and clean code base (build failure on pylint warning)

### Cons
List of reasons you may not want to choose NowTrade over alternatives:

* Not mature yet
* Performance sacrificed for simple abstraction and code base
* Still lacking many features (contributions welcome!)

### Installation

NowTrade has only been tested on Ubuntu 14.04 and 16.04.  It will most likely run just fine on any UNIX-based operating system provided all dependencies have been met.

##### Dependencies

    apt-get install python-pip python-numpy python-pandas python-scipy cython
    pip install pandas-datareader

##### TaLib for Technical Indicators
    wget -O ta-lib-0.4.0-src.tar.gz http://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz/download
    tar xvzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib/
    ./configure --prefix=/usr
    make
    make install
    pip install Ta-Lib

##### Matplotlib for pretty charts

    apt-get install python-matplotlib

##### For MySQL Support

    apt-get install python-mysqldb

##### For MongoDB Local Storage Support

    apt-get install mongodb python-pymongo

Note: You may need to un-comment the line '#port 27017' in /etc/mongodb.conf for NowTrade to communicate with mongo

##### For ensemble (random forest) support

    apt-get install python-sklearn

##### For neural network support

    pip install pybrain

##### Finally, install nowtrade
    python setup.py install

##### Tests
To run the tests you'll need nose:

    apt-get install python-nose

Then you can run the tests by running the following command in the root of the repository:

    sh tests/test_all.sh

### Give it a Spin

You can try out some strategies in the [examples](examples) directory.

I recommend taking a look at the following examples:

* [Learn how to pull from remote data sources and storing stock data locally for backtesting purposes](examples/data_connection.md)
* [A simple moving average crossover strategy](examples/crossover.md)
* [A simple strategy utilizing the random forest machine learning technique](examples/random_forest.md)
* [A simple strategy utilizing the neural network machine learning technique](examples/neural_network.md)
* [Display some pretty charts of your strategies](examples/figures.md)

## See Also

You may also be interested in these other python-based backtesting systems:

* zipline - [https://github.com/quantopian/zipline](https://github.com/quantopian/zipline)
* PyAlgoTrade - [http://gbeced.github.io/pyalgotrade/](http://gbeced.github.io/pyalgotrade/)

## Author
Edouard Poitras <edouardpoitras@gmail.com>
