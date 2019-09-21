import sys
from ruamel.yaml import YAML

yaml=YAML()
yaml.default_flow_style = False

from io import StringIO

import dumper 
dumper.max_depth = 90

def output(makefile):
    # dumper.dump(makefile)
    # code = yaml.load(makefile)
    # yaml.dump(code, sys.stdout)

    output = {}

    for k,v in makefile._targets.items():
        # print(k)
        output[k] = {'rules': []}
        for r in v.rules:
            # print(r)

            rule = {'prereqs': r.prerequisites, 'doublecolon': r.doublecolon, 'commands': []}

            #rule['commands'] = r.commands
            for c in r.commands:
                # sio = StringIO()

                # c.resolve(makefile, makefile.variables, sio)
                # sio.seek(0)
                # print(sio.getvalue())
                rule['commands'].append(c.to_source())

                # print(c.s)
            output[k]['rules'].append(rule)

    # code = yaml.load(output)
    yaml.dump(output, sys.stdout)
    # dumper.dump(output)


