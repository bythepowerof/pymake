#T environment: {'MAKEFLAGS': 'OVAR=oval'}
#T yamlskip

all:
	test "$(OVAR)" = "oval"
	test "$$OVAR" = "oval"
	@echo TEST-PASS

