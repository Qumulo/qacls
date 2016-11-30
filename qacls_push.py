#!/usr/bin/env python
"""Examples:
        qacls_push.py ROOT -a ACE_NAME -a ACE_NAME...
        qacls_push.py ROOT -U 500 -G 80 -M 0770

The first usage pushes the ACL defined by all ACEs specified with the -a flag
down the tree whose root is at ROOT. ROOT gets the original, uninherited version
of this ACL. All directories get object and container inherit flags, plus the
inherited flag. All files just get the inherited flag, because you can't inherit
from a file.

The second usage pushes the mode specified with -M, the uid specified with -U,
and the gid specified with -G starting at the root.

The two uses are mutually exclusive, and using -a and (-U, -G, -M) options
together may lead to unpredictable results.
"""

__author__ = 'mbott'

import sys
import os
import argparse
import json

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest.fs as fs
import qacls_config

# Disable SSL Verification
# TODO: fix this by providing expected certificate from Qumulo API server
# perhaps on install?
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

QID_UID_BASE = 3 << 32
QID_GID_BASE = 4 << 32


def uid_to_qid(uid):
    return QID_UID_BASE + int(uid)


def gid_to_qid(gid):
    return QID_GID_BASE + int(gid)


class QaclsCommand(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
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
        parser.add_argument("-U", "--uid", dest="uid", required=False,
                            help="specify user id to be included in the push.")
        parser.add_argument("-G", "--gid", dest="gid", required=False,
                            help="specify group id to be included in the push.")
        parser.add_argument("-M", "--mode", dest="mode", required=False,
                            help="specify mode bits (octal) to be included in the push.")

        self.args = parser.parse_args()

        self.connection = None
        self.credentials = None
        self.start_path = self.args.start_path

        self.login(self.args)

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
        try:
            self.fs_set_acl(path, is_directory=True, is_root=True)
        except qumulo.lib.request.RequestError:
            # most likely we have a borked token, try to login again
            self.login(self.args)
            self.fs_set_acl(path, is_directory=True, is_root=True)

        # process the rest
        self.process_directory(path)

    def fs_set_acl(self, path,
                   is_file=False, is_directory=False, is_root=False):
        """wrapper for fs.set_acl() OR fs.set_attr() depending on options"""
        if not (self.args.uid and self.args.gid and self.args.mode):
            return fs.set_acl(self.connection,
                              self.credentials,
                              path=path,
                              control=qacls_config.CONTROL_DEFAULT,
                              aces=[process_ace(getattr(qacls_config, ace_name),
                                                is_directory=is_directory,
                                                is_root=is_root,
                                                is_file=is_file)
                                    for ace_name in self.args.ace])
        else:
            return self.fs_set_attr(path)

    def fs_set_attr(self, path):
        """wrapper for fs.set_attr(), since PATCH doesn't work right we need to
        read the attributes and replace the ones we care about, then write them
        back to the cluster"""
        response = fs.get_attr(self.connection, self.credentials, path=path)
        attrs = json.loads(str(response))
        if self.args.uid:
            attrs['uid'] = uid_to_qid(self.args.uid)
        if self.args.gid:
            attrs['gid'] = gid_to_qid(self.args.gid)
        if self.args.mode:
            attrs['mode'] = self.args.mode
        fs.set_attr(self.connection, self.credentials,
                    mode=attrs['mode'],
                    owner=attrs['uid'],
                    group=attrs['gid'],
                    size=attrs['size'],
                    modification_time=attrs['modification_time'],
                    change_time=attrs['change_time'],
                    path=path)

    def fs_read_dir(self, path):
        """wrapper for fs.read_entire_directory()"""
        return fs.read_entire_directory(self.connection,
                                        self.credentials,
                                        page_size=5000,
                                        path=path)

    def process_directory(self, path):
        """read directory contents, kick off processing of same"""
        try:
            response = self.fs_read_dir(path)
        except qumulo.lib.request.RequestError:
            # most likely our token has timed out, try to login again
            self.login(self.args)
            response = self.fs_read_dir(path)
        try:
            for r in response:
                self.process_directory_contents(r.data['files'], path)
        except qumulo.lib.request.RequestError:
            self.login(self.args)
            for r in response:
                self.process_directory_contents(r.data['files'], path)

    def process_directory_contents(self, directory_contents, path):
        """do the right thing for files and directories"""
        for entry in directory_contents:
            # if this is a folder, set the ACL then process its contents
            if entry['type'] == 'FS_FILE_TYPE_DIRECTORY':
                try:
                    self.fs_set_acl(os.path.join(path, entry['name']),
                                    is_directory=True)
                except qumulo.lib.request.RequestError:
                    self.login(self.args)
                    self.fs_set_acl(os.path.join(path, entry['name']),
                                    is_directory=True)

                # Since this is a directory, process it anew
                new_path = path + entry['name'] + '/'
                self.process_directory(new_path)
            # if it is a file, set the ACL appropriately
            elif entry['type'] == 'FS_FILE_TYPE_FILE':
                try:
                    self.fs_set_acl(os.path.join(path, entry['name']),
                                    is_file=True)
                except qumulo.lib.request.RequestError:
                    # login again since we most likely are not authed
                    self.login(self.args)
                    self.fs_set_acl(os.path.join(path, entry['name']),
                                    is_file=True)


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
    Q = QaclsCommand()
    Q.directory_set_acl(Q.start_path)


if __name__ == '__main__':
    main()