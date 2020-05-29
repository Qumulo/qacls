#!/usr/bin/env python

import argparse
import copy


from pprint import pprint

import qtreewalk

from qumulo.rest_client import RestClient
from qumulo.lib.request import RequestError

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
                        dest='aces',
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

set_parser.add_argument('-i', '--inheritance',
                        dest='inheritance',
                        default='INHERIT_ALL')

# Push permissions down a tree, do the right things with inheritance
push_parser = subparsers.add_parser('push')

push_parser.add_argument('-p', '--path',
                        help='full path to dir or file',
                        required=True)

push_parser.add_argument('-a', '--ace',
                         dest='aces',
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

RC = RestClient(address=qacls_config.QHOST, port=qacls_config.QPORT)
RC.login(username=qacls_config.QUSER, password=qacls_config.QPASS)


class QaclsError(Exception):
    pass


def empty_acl():
    acl = {'aces': [],
           'control': [],
           'posix_special_permissions': []}
    return acl


# For do_per_file()
FILE_ACL = empty_acl()
DIR_ACL = empty_acl()


def build_ace(flags, rights, trustee, type_):
    ace = {'flags': flags,
           'rights': rights,
           'trustee': trustee,
           'type': type_}
    return ace


def get_trustee_from_name(name):
    response = RC.auth.find_identity(name=name)
    return response


def build_ace_list(args):
    ace_list = []
    for ace in args.aces:
        ace_list.append(get_ace_from_config_name(ace))
    return ace_list


def get_ace_from_config_name(ace_name):
    ace = get_config(ace_name)
    flags = ace['flags']
    rights = ace['rights']
    trustee = get_trustee_from_name(ace['groupname'])
    type_ = ace['type']
    return build_ace(flags, rights, trustee, type_)


# Take the ACL on the chosen directory and make it inherited if it's not already
# type is 'f' or 'd'
# Be very careful about how inheritance is handled, if we don't know, bail
def process_repair_acl(acl, type):
    local_acl = copy.deepcopy(acl)
    for ace in local_acl['aces']:
        if ace['flags'] in (qacls_config.INHERIT_ALL, qacls_config.INHERIT_ALL_INHERITED):
            if type == 'f':
                ace['flags'] = qacls_config.INHERITED
            elif type == 'd':
                ace['flags'] = qacls_config.INHERIT_ALL_INHERITED
        # Should we be propagating an ACE that isn't inherited?? I say NO.
        elif ace['flags'] == qacls_config.EMPTY_FLAGS:
            # remove it
            local_acl['aces'].remove(ace)
        else:
            raise QaclsError("I don't know how to deal with the ace %s" %
                             str(ace))
    return local_acl


def repair_do_per_file(ent, d, out_file=None, rc=RC):
    if ent['type'] == 'FS_FILE_TYPE_FILE':
        rc.fs.set_acl_v2(path=ent['path'], acl=FILE_ACL)
    elif ent['type'] == 'FS_FILE_TYPE_DIRECTORY':
        rc.fs.set_acl_v2(path=ent['path'], acl=DIR_ACL)
    else:
        raise QaclsError("I don't know how to deal with the ent type %s" %
                         ent['type'])


def push_create_acl(args):
    ACL = empty_acl()
    ACL['aces'] = build_ace_list(args)
    return ACL


def repair(args):
    print("REPAIR")
    parent_acl = RC.fs.get_acl_v2(path=args.path)
    pprint(parent_acl)
    global FILE_ACL
    FILE_ACL = process_repair_acl(parent_acl, 'f')
    global DIR_ACL
    DIR_ACL = process_repair_acl(parent_acl, 'd')
    qtreewalk.do_per_file = repair_do_per_file
    qtreewalk.walk_tree(qacls_config.QHOST,
                        qacls_config.QUSER,
                        qacls_config.QPASS,
                        args.path)


# shadows built-in set, hopefully it won't be necessary
def set(args):
    acl = empty_acl()
    acl['aces'] = build_ace_list(args)
    acl['control'] = qacls_config.CONTROL_DEFAULT
    RC.fs.set_acl_v2(acl, args.path)


def create(args):
    print("CREATE NOT IMPLEMENTED")


def push(args):
    print("PUSH")
    pprint(args)
    ACL = push_create_acl(args)
    pprint(ACL)
    ACL['control'] = qacls_config.CONTROL_DEFAULT
    RC.fs.set_acl_v2(ACL, args.path)
    repair(args)


def get_config(e_name):
    return getattr(qacls_config, e_name)


def main():
    args = parser.parse_args()
    globals()[args.command](args)


if __name__ == '__main__':
    main()
