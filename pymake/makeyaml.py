import sys
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString, preserve_literal

# stolen for data.py for variable defs
FLAVOR_RECURSIVE = 0
FLAVOR_SIMPLE = 1
FLAVOR_APPEND = 2

SOURCE_OVERRIDE = 0     # take this
SOURCE_COMMANDLINE = 1  # and this
SOURCE_MAKEFILE = 2     # and this
SOURCE_ENVIRONMENT = 3
SOURCE_AUTOMATIC = 4
SOURCE_IMPLICIT = 5

yaml=YAML()
yaml.default_flow_style = False

import dumper 
dumper.max_depth = 90

def output(makefile):
    # dumper.dump(makefile)
    # code = yaml.load(makefile)
    # yaml.dump(code, sys.stdout)

    output = {'rules': [], 'variables': {}}
    ruleaddr = {}
    ruleempty = {}

    for v in makefile.variables:
        if v[2] in [SOURCE_OVERRIDE,SOURCE_COMMANDLINE, SOURCE_MAKEFILE]:
            # print("{}={}".format(v[0], makefile.variables.get(v[0], False)))
            output['variables'][v[0]] = preserveliteral(makefile.variables.get(v[0], False)[2])

    # targets
    for k,v in makefile._targets.items():
        processed = False

        print(k)

        for r in v.rules:
            if r.commands == []:
                if k in ruleempty.keys():
                    ruleempty[k]['prereqs'].extend(r.prerequisites)
                    # print(ruleempty[k]['prereqs'])
                    continue


            for ra, rr in ruleaddr.items():
                if r is ra:
                    rr['target'].append(k)
                    processed = True
                    break

            if processed:
                break

            rule = {'target': [k], 'doublecolon': r.doublecolon, 'commands': []}

            if r.prerequisites != []:
                rule['prereqs'] =  r.prerequisites

            for c in r.commands:
                rule['commands'].append(preserveliteral(c.to_source()))

            output['rules'].append(rule)

            if r.commands == []:
                ruleempty[k] = rule
            else:
                ruleaddr[r] = rule

    # code = yaml.load(output)
    yaml.dump(output, sys.stdout)
    # dumper.dump(output)

def preserveliteral(val):
    if '\n' in val:
        return preserve_literal(val)
    else:
        return val


