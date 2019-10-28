#T gmake skip
#T yamlskip
#T returncode: 2
#T grep-for: "Exception: info-exception"

CMD = %pycmd asplode_raise
PYCOMMANDPATH = $(TESTPATH) $(TESTPATH)/subdir

all:
	@$(CMD) info-exception
