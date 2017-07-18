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
              ]

for modname in SUBMODULES:
    mod = imp.load_source(modname, modname + '.py')
    globals()[modname] = mod


def create_parsers():
    # Top-level parser stuff
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
                        dest='host', required=False,
                        help='specify target cluster address')
    parser.add_argument('-P', '--port', type=int, dest='port',
                        # default=qacls_config.API['port'],
                        required=False,
                        help='specify port on target cluster')
    parser.add_argument('-u', '--user',
                        # default=qacls_config.API['user'],
                        dest='user', required=False,
                        help='specify user credentials for API login')
    parser.add_argument('--pass',
                        # default=qacls_config.API['pass'],
                        dest='passwd', required=False,
                        help='specify user pwd for API login')
    subparsers = parser.add_subparsers(help='sub-command help',
                                       dest='subparser_name')

    for m in SUBMODULES:
        getattr(globals()[m], 'create_subparser')(subparsers)

    return parser


def validate_args(parser_namespace):
    # Bail if we're trying to create a skeleton on anything but win32
    if parser_namespace.subparser_name == 'create':
        from sys import platform
        if platform != 'win32':
            print "Sorry, qacls.py is currently win32 only. Exiting..."
            sys.exit(1)
        # if we made it here, we're win32 so import more pyad stuff
        import pyad.adquery
        from pyad import aduser
        from pyad import adgroup

    # Try to import the specified or default config
    global qacls_config
    qacls_config = imp.load_source('qacls_config', parser_namespace.qacls_config)

    # Set defaults based on the imported config if they haven't been set already
    if not parser_namespace.host:
        parser_namespace.host = qacls_config.API['host']
    if not parser_namespace.port:
        parser_namespace.port = qacls_config.API['port']
    if not parser_namespace.user:
        parser_namespace.user = qacls_config.API['user']
    if not parser_namespace.passwd:
        parser_namespace.passwd = qacls_config.API['pass']


def main(argv):
    parser = create_parsers()
    parsed = parser.parse_args(argv)
    validate_args(parsed)
    print parsed


if __name__ == '__main__':
    print sys.argv
    main(sys.argv[1:])
