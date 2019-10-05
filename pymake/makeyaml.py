import sys
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString, preserve_literal
from . import data
from . import parser

# stolen for data.py for Variable defs
# FLAVOR_RECURSIVE = 0
# FLAVOR_SIMPLE = 1
# FLAVOR_APPEND = 2

# SOURCE_OVERRIDE = 0     # take this
# SOURCE_COMMANDLINE = 1  # and this
# SOURCE_MAKEFILE = 2     # and this
# SOURCE_ENVIRONMENT = 3
# SOURCE_AUTOMATIC = 4
# SOURCE_IMPLICIT = 5

yaml=YAML()
yaml.default_flow_style = False

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

        if 'targetpatterns' in v:
            vars.append("{} {} {}: {}".format(' '.join(v['targets']), dc, ' '.join(v['targetpatterns']), ' '.join(v['prereqs'])))
        else:
            vars.append("{} {} {}".format(' '.join(v['targets']), dc, ' '.join(v['prereqs'])))

        for c in v['commands']:
            vars.append('\t{}'.format(c))

    parser.parsestring("\n".join(vars), 'xx').execute(makefile)


def output(makefile):
    output = {'rules': [], 'variables': {}}
    ruleaddr = {}
    ruleempty = {}

    for v in makefile.variables:
        if v[2] in [data.Variables.SOURCE_OVERRIDE, data.Variables.SOURCE_COMMANDLINE, data.Variables.SOURCE_MAKEFILE]:
            output['variables'][v[0]] = preserveliteral(makefile.variables.get(v[0], False)[2])

    # targets
    for k,v in makefile._targets.items():
        processed = False

        for rx in v.rules:
            
            if isinstance(rx, data.PatternRuleInstance):
                thisrule = rx.prule
            else:
                thisrule = rx

            if thisrule.commands == []:
                if k in ruleempty.keys():
                    ruleempty[k]['prereqs'].extend(thisrule.prerequisites)
                    continue

            for ra, rr in ruleaddr.items():
                if thisrule is ra:
                    rr['targets'].append(k)
                    processed = True
                    break

            if processed:
                break

            rule = {'targets': [k], 'doublecolon': thisrule.doublecolon, 'commands': []}

            if thisrule.prerequisites != []:
                rule['prereqs'] =  thisrule.prerequisites

            if hasattr(thisrule, 'targetpatterns'):
                rule['targetpatterns'] = []
                for t in thisrule.targetpatterns:
                    rule['targetpatterns'].append(t.__str__())

            for c in thisrule.commands:
                rule['commands'].append(preserveliteral(c.to_source()))

            output['rules'].append(rule)

            if thisrule.commands == []:
                ruleempty[k] = rule
            else:
                ruleaddr[thisrule] = rule

    yaml.dump(output, sys.stdout)

def preserveliteral(val):
    if '\n' in val:
        return preserve_literal(val)
    else:
        return val
