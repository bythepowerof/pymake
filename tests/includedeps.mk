#T gmake skip
#T yamlskip

all: file1
	@echo TEST-PASS

includedeps $(TESTPATH)/includedeps.deps

file1:
	touch $@
