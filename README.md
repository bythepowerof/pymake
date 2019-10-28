pymake + python 3 patches
=========================

Fork of [https://github.com/mozilla/pymake](https://github.com/mozilla/pymake) with additional patches for Python 3, breaking Python 2 support.

### What is pymake?

>	make.py (and the pymake modules that support it) are an implementation of the make tool
>	which are mostly compatible with makefiles written for GNU make.

Please refer to [`ORIGINAL_README`](/ORIGINAL_README) and [`LICENSE`](/LICENSE)

### Build status:

Platform    | Python | CI Status | Coverage
------------|:-------|:------------|:--------
linux       | 3.7.x  | [![Build Status](https://travis-ci.org/bythepowerof/pymake.svg?branch=master)](https://travis-ci.org/bythepowerof/pymake)| [![codecov](https://codecov.io/gh/bythepowerof/pymake/branch/master/graph/badge.svg)](https://codecov.io/gh/bythepowerof/pymake)
osx         | 3.7.3  | as above -- same ci build as linux. 
windows     | todo   | todo | todo


### Development - how to run the test suite:

Prerequisites:

*	default `python` is Python 3
*	[pytest](https://docs.pytest.org) installed (`pip install -r test-requirements.txt`)
*	a dev install of `pymake` package in this repo (`pip install -e .`)
*	GNU Make installed to test against (assumed to be named `gmake`, can be overridden)

With [pytest](https://docs.pytest.org) installed, the test suite can be run from the root directory of this repo as follows:

```
pytest --gmake=make .
```

With the optional `pytest-dist` plugin installed, the tests can be run in parallel. For example, to use 8 CPUs:

```
pytest --gmake=make -n 8 .
```

This gives about a 5x speedup on my machine.
