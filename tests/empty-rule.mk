all: obj
	$(MAKE) -f $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST)) obj

obj: header

	# Subtlety: make prints the source code of this shell snippet
	# while executing it. But the test harness looks in the stdout
	# from make for a certain special failure token to decide if
	# the test has passed or failed. So we break the special token
	# into two pieces, so it cannot be found by merely reading the
	# source code without executing the source code.

	# Regard test as failed if make attempts to build obj more than once.
	if [ -e obj ]; then X=FAIL; echo TEST-$$X; fi;
	touch obj

	# Regard test as passed if make attempts to build obj at least once.
	echo TEST-PASS

header: cpp

cpp:
	touch header
	touch cpp
