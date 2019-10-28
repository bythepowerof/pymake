#T environment: {'FOO': '$(BAZ)'}
#T yamlskip

FOO += $(BAR)
BAR := PASS
BAZ := TEST

all:
	@echo $(subst $(NULL) ,-,$(FOO))
