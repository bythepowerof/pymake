pymake + python 3 patches + YAML support
=========================

Fork of [https://github.com/mozilla/pymake](https://github.com/mozilla/pymake) with additional patches for Python 3, breaking Python 2 support.
This builds on [https://github.com/fcostin/pymake](https://github.com/fcostin/pymake) where the python 3 patching was done
This repo adds support to export and import to YAML
```
-y: generate yaml from the makefile and includes (you also need -s as it dumps to SDTOUT)
-z <file|->: read make configuration from file or - to read from STDIN
```
You can do 
```
pymake -s -y | pymake -z -
```
to test your makefile works as YAML

Which is exactly what the test suite does. Not all the tests pass so some are skipped, so it's not a full implementation. I think this is mainly from double handling of escape characters.

### Docker

This is available as an alpine docker image [bythepowerof/pymake:latest](https://cloud.docker.com/u/bythepowerof/repository/docker/bythepowerof/pymake) where pymake is the `ENTRYPOINT`

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
