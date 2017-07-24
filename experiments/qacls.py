#!/usr/bin/env python
"""qacls can be called with the following subcommands:
create (same as old qacls functionality)
push (push POSIX modes or a defined ACL down a tree)
repair (read top-level POSIX mode or ACL and push it down a tree)
"""

import sys
import argparse
import imp

SUBMODULES = ['qacls_create',
              'qacls_push',
              'qacls_repair',
              'qacls_test',
              ]

# import everything in SUBMODULES and give it the right name
for modname in SUBMODULES:
    mod = imp.load_source(modname, modname + '.py')
    globals()[modname] = mod


def create_parsers():
    parser = argparse.ArgumentParser(prog='qacls')
    parser.add_argument('-c', '--config_filename',
                        help='name of config file',
                        # nargs='?',
                        required=False,
                        default='qacls_config.py',
                        action='store',
                        dest='qacls_config')
    parser.add_argument('-v', '--verbose',
                        help='increase verbosity of output',
                        action='store_true')
    parser.add_argument('--ip', '--host',
                        # default=qacls_config.API['host'],
                        dest='host',
                        required=False,
                        help='specify target cluster address')
    parser.add_argument('-P', '--port', type=int, dest='port',
                        # default=qacls_config.API['port'],
                        required=False,
                        help='specify port on target cluster')
    parser.add_argument('-u', '--user',
                        # default=qacls_config.API['user'],
                        dest='user',
                        required=False,
                        help='specify user credentials for API login')
    parser.add_argument('--pass',
                        # default=qacls_config.API['pass'],
                        dest='passwd',
                        required=False,
                        help='specify user pwd for API login')
    parser.add_argument('--no-ssl-verify',
                        action='store_true',
                        required=False,
                        help='disable strict SSL certificate check')
    subparsers = parser.add_subparsers(help='sub-command help',
                                       dest='subparser_name')

    # so all the subparsers are named correctly in this namespace
    for m in SUBMODULES:
        getattr(globals()[m], 'create_subparser')(subparsers)

    return parser


def validate_args(parser_namespace):
    # Bail if we're trying to create a skeleton on anything but win32
    if parser_namespace.subparser_name == 'create':
        from sys import platform
        if platform != 'win32':
            print "Sorry, 'qacls.py create' is currently win32 only. Please " \
                  "use 'qacls.py push' or 'qacls.py repair' instead."
            sys.exit(1)
        # if we made it here, we're win32 so import more pyad stuff
        import pyad.adquery
        from pyad import aduser
        from pyad import adgroup

    # Try to import the specified or default config
    global qacls_config
    qacls_config = imp.load_source('qacls_config', parser_namespace.qacls_config)

    # Attach the config in all the submodule namespaces
    for modname in SUBMODULES:
        globals()[modname].qacls_config = qacls_config

    # Set defaults based on the imported config if they haven't been set already
    if not parser_namespace.host:
        parser_namespace.host = qacls_config.API['host']
    if not parser_namespace.port:
        parser_namespace.port = qacls_config.API['port']
    if not parser_namespace.user:
        parser_namespace.user = qacls_config.API['user']
    if not parser_namespace.passwd:
        parser_namespace.passwd = qacls_config.API['pass']

    # Disable strict ssl verification if requested
    if parser_namespace.no_ssl_verify:
        import ssl

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context


def run_it(parsed):
    validate_args(parsed)
    if parsed.verbose:
        print parsed
        print globals()
    cmd_name = 'qacls_' + parsed.subparser_name
    cmd = globals()[cmd_name]
    cmd.main(parsed)


def main(argv):
    parser = create_parsers()
    parsed = parser.parse_args(argv)
    run_it(parsed)


if __name__ == '__main__':
    main(sys.argv[1:])
