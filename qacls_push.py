#!/usr/bin/env python
"""qacls_push.py
Usage: qacls_push.py ROOT -a ACE_NAME -a ACE_NAME...

Pushes the ACL defined by all ACEs specified with the -a flag down the tree
whose root is at ROOT. ROOT gets the original, uninherited version of this ACL.
All directories get object and container inherit flags, plus the inherited flag.
All files just get the inherited flag, because you can't inherit from a file.
"""

__author__ = 'mbott'

import sys
import os
import argparse

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest.fs as fs
import qacls_config


class QaclsCommand(object):
    def __init__(self, argv=None):
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", "--host", default=qacls_config.API['host'],
                            dest="host", required=False,
                            help="specify target cluster address")
        parser.add_argument("-P", "--port", type=int, dest="port",
                            default=qacls_config.API['port'], required=False,
                            help="specify port on target cluster")
        parser.add_argument("-u", "--user", default=qacls_config.API['user'],
                            dest="user", required=False,
                            help="specify user credentials for API login")
        parser.add_argument("--pass", default=qacls_config.API['pass'],
                            dest="passwd", required=False,
                            help="specify user pwd for API login")
        parser.add_argument("-a", "--ace", action="append",
                            help="ACE name for the ACL to push, defined in "
                                 "config. Can add multiples by specifying -a "
                                 "multiple times.")
        parser.add_argument("start_path", action="store",
                            help="Directory to start perms push. This directory"
                                 " will get an uninherited version of the "
                                 "specified ACL.")

        self.args = parser.parse_args()

        self.connection = None
        self.credentials = None
        self.start_path = self.args.start_path

        self.login(self.args)

        print self.directory_set_acl(self.start_path)

    def login(self, args):
        try:
            self.connection = qumulo.lib.request.Connection(args.host,
                                                            int(args.port))
            login_results, _ = qumulo.rest.auth.login(self.connection, None,
                                                      args.user, args.passwd)

            self.credentials = qumulo.lib.auth.Credentials.from_login_response(
                login_results)
        except Exception, e:
            print "Error connecting to the REST server: %s" % e
            print __doc__
            sys.exit(1)

    def directory_set_acl(self, path):
        """set ACLs properly on all paths"""
        # set it on the root first
        fs.set_acl(self.connection, self.credentials,
                   path=path, control=qacls_config.CONTROL_DEFAULT,
                   aces=[
                       process_ace(getattr(qacls_config, ace_name),
                                   is_directory=True,
                                   is_root=True)
                       for ace_name in self.args.ace])
        # process the rest
        self.process_directory(path)

    def process_directory(self, path):
        response = fs.read_entire_directory(self.connection, self.credentials,
                                            page_size=5000, path=path)
        for r in response:
            self.process_directory_contents(r.data['files'], path)

    def process_directory_contents(self, directory_contents, path):
        for entry in directory_contents:
            ace_list = [getattr(qacls_config, ace_name)
                        for ace_name in self.args.ace]
            # if this is a folder, set the ACL then process its contents
            if entry['type'] == 'FS_FILE_TYPE_DIRECTORY':
                fs.set_acl(self.connection, self.credentials,
                           path=os.path.join(path, entry['name']),
                           control=qacls_config.CONTROL_DEFAULT,
                           aces=[process_ace(ace, is_directory=True)
                                 for ace in ace_list])

                # Since this is a directory, process it anew
                new_path = path + entry['name'] + '/'
                self.process_directory(new_path)
            # if it is a file, set the ACL appropriately
            elif entry['type'] == 'FS_FILE_TYPE_FILE':
                fs.set_acl(self.connection, self.credentials,
                           path=os.path.join(path, entry['name']),
                           control=qacls_config.CONTROL_DEFAULT,
                           aces=[process_ace(ace, is_file=True)
                                 for ace in ace_list])


def process_ace(ace, is_file=False, is_directory=False, is_root=False):
    if is_directory and is_root and not is_file:
        return ace
    elif is_directory and not is_root and not is_file:
        ace['flags'] = qacls_config.INHERIT_ALL_INHERITED
        return ace
    elif is_file and not is_directory and not is_root:
        ace['flags'] = qacls_config.INHERITED
        return ace


def main():
    QaclsCommand(sys.argv)


if __name__ == '__main__':
    main()