#!/usr/bin/env python

import argparse
from pprint import pprint

import qacls_config

parser = argparse.ArgumentParser()

parser.add_argument('--ip', '--host',
                    default=qacls_config.QHOST,
                    dest='host',
                    required=False,
                    help='specify target cluster address')

parser.add_argument('-P', '--port',
                    type=int,
                    dest='port',
                    default=qacls_config.QPORT,
                    required=False,
                    help='specify target cluster port')

parser.add_argument('-u', '--user',
                    default=qacls_config.QUSER,
                    dest='user',
                    required=False,
                    help='specify API username on target cluster')

parser.add_argument('-p', '--password',
                    default=qacls_config.QPASS,
                    dest='passwd',
                    required=False,
                    help='specify API password on target cluster')

subparsers = parser.add_subparsers(dest='command', 
                                   help='commands', 
                                   required=True)

# Creates a directory based on the skeleton defined in the config file
create_parser = subparsers.add_parser('create')

create_parser.add_argument('-r', '--root',
                           help='desired location of directory skeleton',
                           required=True)

create_parser.add_argument('-n', '--name',
                           help='name of directory to create',
                           required=True)


# Set a single ACL on a file or directory
set_parser = subparsers.add_parser('set')

set_parser.add_argument('-p', '--path',
                        help='full path to dir or file',
                        required=True)

set_parser.add_argument('-a', '--ace',
                        action='append',
                        help='ACE name for the ACL to push, defined in the '
                             'configuration file. Can add multiple ACEs by '
                             'using -a multiple times.')

set_parser.add_argument('-U', '--uid',
                        dest='uid',
                        required=False,
                        help='specify user id to be set as owner')

set_parser.add_argument('-G', '--gid',
                        dest='gid',
                        required=False,
                        help='specify group id to be set as group owner')

# Push permissions down a tree, do the right things with inheritance
push_parser = subparsers.add_parser('push')

push_parser.add_argument('-p', '--path',
                        help='full path to dir or file',
                        required=True)

push_parser.add_argument('-a', '--ace',
                        action='append',
                        help='ACE name for the ACL to push, defined in the '
                             'configuration file. Can add multiple ACEs by '
                             'using -a multiple times.')

push_parser.add_argument('-U', '--uid',
                        dest='uid',
                        required=False,
                        help='specify user id to be set as owner')

push_parser.add_argument('-G', '--gid',
                        dest='gid',
                        required=False,
                        help='specify group id to be set as group owner')

# Read top-level ACL, apply it as if it is inherited through the tree
repair_parser = subparsers.add_parser('repair')

repair_parser.add_argument('-p', '--path',
                           help='full path to directory to repair',
                           required=True)


def repair():
    print("REPAIR")


# shadows built-in set, hopefully it won't be necessary
def set():
    print("SET")


def create():
    print("CREATE")


def push():
    print("PUSH")


def main():
    args = parser.parse_args()
    globals()[args.command]()


if __name__ == '__main__':
    main()
