#T environment: {'FOO': 'TEST'}
#T yamlskip

FOO += $(BAR)
BAR := PASS

all:
	@echo $(subst $(NULL) ,-,$(FOO))
