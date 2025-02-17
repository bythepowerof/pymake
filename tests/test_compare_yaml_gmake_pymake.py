#!/usr/bin/env python
"""
Run the test(s) listed on the command line. If a directory is listed, the script will recursively
walk the directory for files named .mk and run each.

For each test, we run gmake -f test.mk. By default, make must exit with an exit code of 0, and must print 'TEST-PASS'.

Each test is run in an empty directory.

The test file may contain directive lines at the beginning to alter the default behavior. These are all evaluated as python:

#T commandline: ['extra', 'params', 'here']
#T returncode: 2
#T returncode-on: {'win32': 2}
#T environment: {'VAR': 'VALUE}
#T grep-for: "text"
"""


import subprocess
import os
import re
import sys
import pytest

THISDIR = os.path.dirname(os.path.abspath(__file__))

@pytest.fixture
def pymake():
    return [sys.executable, "-m", "pymake.cli.main"]

class ParentDict(dict):
    def __init__(self, parent, **kwargs):
        self.d = dict(kwargs)
        self.parent = parent

    def __setitem__(self, k, v):
        self.d[k] = v

    def __getitem__(self, k):
        if k in self.d:
            return self.d[k]

        return self.parent[k]

def run_test(makefile, make, logfile, options, commandline):
    """
    Given a makefile path, test it with a given `make` and return
    (pass, message).
    """

    stdin = sys.stdin
    stdout = subprocess.PIPE

    i=0

    for c in commandline:
        if i == 0:
            stderr = open('{}.stderr'.format(i), 'w')
            process = subprocess.Popen(make + c, stdout=stdout, stderr=stderr, env=options['env'])
        else:
            stderr = open('{}.stderr'.format(i), 'w')
            process = subprocess.Popen(make + c, stdin=stdin, stdout=stdout, stderr=stderr, env=options['env'])

        i += 1

        stdin = process.stdout
        
    stdout, _ = process.communicate()
    retcode = process.returncode

    stdout = stdout.decode('utf-8')

    if retcode != options['returncode']:
        print(stdout)
        return False, "FAIL (returncode=%i)" % retcode
        
    if stdout.find('TEST-FAIL') != -1:
        print(stdout)
        return False, "FAIL (TEST-FAIL printed)"

    if options['grepfor'] and stdout.find(options['grepfor']) == -1:
        print(stdout)
        return False, "FAIL (%s not in output)" % options['grepfor']

    if options['returncode'] == 0 and stdout.find('TEST-PASS') == -1:
        print(stdout)
        return False, 'FAIL (No TEST-PASS printed)'

    if options['returncode'] != 0:
        return True, 'PASS (retcode=%s)' % retcode

    return True, 'PASS'


def modify_dmap_with_scenario_directives(dmap, makefile):
    tre = re.compile('^#T (gmake |pymake )?([a-z-]+)(?:: (.*))?$')
    with open(makefile) as mdata:
        for line in mdata:
            line = line.strip()
            m = tre.search(line)

            # do each line as some makefiles don't allow a comment on the first line
            if m is None:
                continue
            #    break

            make, key, data = m.group(1, 2, 3)
            d = dmap[make]
            if data is not None:
                data = eval(data)
            if key == 'commandline':
                assert make is None
                d['commandline'].extend(data)
                d['commandline1'].extend(data)
                d['commandline2'].extend(data)
            elif key == 'returncode':
                d['returncode'] = data
            elif key == 'returncode-on':
                if sys.platform in data:
                    d['returncode'] = data[sys.platform]
            elif key == 'environment':
                for k, v in data.items():
                    d['env'][k] = v
            elif key == 'grep-for':
                d['grepfor'] = data
            elif key == 'fail':
                d['pass'] = False
            elif key in ['skip', 'yamlskip']:
                d['skip'] = True
            else:
                raise RuntimeError("%s: Unexpected #T key: %s" % (makefile, key))


def test_scenarios(makefile, tmp_path_factory, gmake, pymake):

    print("%-30s%-28s%-28s" % ("Test:", "gmake:", "pymake:"))

    gmakefails = 0
    pymakefails = 0


    # For some reason, MAKEFILE_LIST uses native paths in GNU make on Windows
    # (even in MSYS!) so we pass both TESTPATH and NATIVE_TESTPATH
    #cline = ['-f', os.path.abspath(makefile), 'TESTPATH=%s' % THISDIR.replace('\\','/'), 'NATIVE_TESTPATH=%s' % THISDIR]
    cline = ['TESTPATH=%s' % THISDIR.replace('\\','/'), 'NATIVE_TESTPATH=%s' % THISDIR]
    if sys.platform == 'win32':
        #XXX: hack so we can specialize the separator character on windows.
        # we really shouldn't need this, but y'know
        cline += ['__WIN32__=1']

    options = {
        'returncode': 0,
        'grepfor': None,
        'env': dict(os.environ),
        'pass': True,
        'skip': False,
        'commandline': cline,
        'commandline1': cline,
        'commandline2': cline
        }

    gmakeoptions = ParentDict(options)
    pymakeoptions = ParentDict(options)

    dmap = {None: options, 'gmake ': gmakeoptions, 'pymake ': pymakeoptions}

    modify_dmap_with_scenario_directives(dmap, makefile)

    # fragile, rework: specialising different temp dirs has to be done after
    # modify_dmap_with_scenario_directives call, as that wants to
    # modify the default options that both makes will inherit and customist
    gmake_temp_dir = str(tmp_path_factory.mktemp("gmake"))
    pymake_temp_dir = str(tmp_path_factory.mktemp("pymake"))

    gmakeoptions['commandline'] = ['-f', os.path.abspath(makefile), '-C', gmake_temp_dir] + gmakeoptions['commandline']
    pymakeoptions['commandline1'] = ['-f', os.path.abspath(makefile), '-y', '-s', '-C', pymake_temp_dir] +   pymakeoptions['commandline1']
    pymakeoptions['commandline2'] = ['-z', '-', '-C', pymake_temp_dir] +  pymakeoptions['commandline2']

    if gmakeoptions['skip']:
        gmakepass, gmakemsg = True, ''
    else:
        gmakepass, gmakemsg = run_test(makefile, [gmake],
                                      makefile + '.gmakelog', gmakeoptions, [gmakeoptions['commandline']])

    if gmakeoptions['pass']:
        if not gmakepass:
            gmakefails += 1
    else:
        if gmakepass:
            gmakefails += 1
            gmakemsg = "UNEXPECTED PASS"
        else:
            gmakemsg = "KNOWN FAIL"

    if pymakeoptions['skip']:
        pymakepass, pymakemsg = True, ''
    else:
        pymakepass, pymakemsg = run_test(makefile, pymake,
                                        makefile + '.pymakelog', pymakeoptions, [pymakeoptions['commandline1'], pymakeoptions['commandline2']])

    if pymakeoptions['pass']:
        if not pymakepass:
            pymakefails += 1
    else:
        if pymakepass:
            pymakefails += 1
            pymakemsg = "UNEXPECTED PASS"
        else:
            pymakemsg = "OK (known fail)"

    print("%-30.30s%-28.28s%-28.28s" % (os.path.basename(makefile),
                                        gmakemsg, pymakemsg))
    
    # x = open('yamlout.txt', 'a')
    # if pymakefails:
    #     x.write("%-30.30s%-28.28s%-28.28s\n" % (os.path.basename(makefile),
    #                                     gmakemsg, pymakemsg))
    # x.close()
    assert not pymakefails
