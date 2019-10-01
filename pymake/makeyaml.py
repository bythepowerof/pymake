import sys
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString, preserve_literal
from . import data
from . import parserdata
from . import functions
from . import parser

#Variables = data.Variables

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

def parsefile(yaml_file, makefile):
    all_config_data = yaml.load(yaml_file)

    vars = []

    for k,v in all_config_data['variables'].items():
        if '\n' in v:
            vars.append("define {}\n{}\nendef".format(k, v))
        else:
            vars.append("{} = {}".format(k, v))
        print("\n".join(vars))

    for v in all_config_data['rules']:
        if 'prereqs' not in v:
            v['prereqs'] = []

        if v['doublecolon']:
            dc = ' :: '
        else:
            dc = ' : '

        vars.append("{} {} {}".format(' '.join(v['target']), dc, ' '.join(v['prereqs'])))

        for c in v['commands']:
            vars.append('\t{}'.format(c))

    parser.parsestring("\n".join(vars), 'xx').execute(makefile)


def output(makefile):
    # dumper.dump(makefile._targets)
    # code = yaml.load(makefile)
    # yaml.dump(code, sys.stdout)

    output = {'rules': [], 'variables': {}}
    ruleaddr = {}
    ruleempty = {}

    for v in makefile.variables:
        if v[2] in [SOURCE_OVERRIDE,SOURCE_COMMANDLINE, SOURCE_MAKEFILE]:
            output['variables'][v[0]] = preserveliteral(makefile.variables.get(v[0], False)[2])

    # targets
    for k,v in makefile._targets.items():
        processed = False

        for r in v.rules:
            if r.commands == []:
                if k in ruleempty.keys():
                    ruleempty[k]['prereqs'].extend(r.prerequisites)
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

            if hasattr(r, 'stem'):
                rule['stem'] = r.stem

            for c in r.commands:
                rule['commands'].append(preserveliteral(c.to_source()))

            output['rules'].append(rule)

            if r.commands == []:
                ruleempty[k] = rule
            else:
                ruleaddr[r] = rule

    yaml.dump(output, sys.stdout)

def preserveliteral(val):
    if '\n' in val:
        return preserve_literal(val)
    else:
        return val


