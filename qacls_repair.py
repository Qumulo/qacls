#!/usr/bin/env python
"""Usage: qacls_repair.py ROOT

Reads the ACL and posix attributes (owner, group, modes) from the ROOT specified
Determines whether to use ACL or POSIX (look for generated:true/false in the ACL)
does a push of the permission set determined, either the ACL or mode bits
"""

__author__ = 'mbott'

import os
import argparse
import json

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest.fs as fs
import qacls_config
import qacls_push


class QaclsRepair(qacls_push.QaclsCommand):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
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
        parser.add_argument("start_path", action="store",
                            help="Directory to start the permissions repair. "
                                 "This directory's contents will get an "
                                 "inherited version of the ACL or owner/modes.")

        self.args = parser.parse_args()

        self.connection = None
        self.credentials = None
        self.start_path = self.args.start_path

        self.login(self.args)
        # these will store trustees aka authids aka qids, NOT real UID/GID
        self.owner=None
        self.group=None

        self.mode=None
        self.acl=None

    def get_attrs(self, path):
        """path=path of dir or file, returns JSON of attrs"""
        result, _ = fs.get_attr(self.connection, self.credentials, path=path)
        return result

    def get_acl(self, path):
        """path=path of dir or file, returns JSON of acl"""
        print path
        result, _ = fs.get_acl(self.connection, self.credentials, path=path)
        return result

    def is_acl(self, path):
        acl = self.get_acl(path)
        return not acl['generated']

    def is_posix(self, path):
        acl = self.get_acl(path)
        return acl['generated']

    def directory_repair_acl(self, path):
        """If the directory is posix-managed, push uid/gid and mode bits
        if the directory is acl-managed, push the acl"""
        attrs = self.get_attrs(path)
        self.owner = attrs['owner']
        self.group = attrs['group']
        self.mode = attrs['mode']
        self.acl = self.get_acl(path)
        if self.is_posix(path):
            self.process_directory_posix(path)
        elif self.is_acl(path):
            self.process_directory_acl(path)

    def process_directory_acl(self, path):
        """read directory contents, kick off acl push under same"""
        try:
            response = self.fs_read_dir(path)
        except qumulo.lib.request.RequestError:
            # most likely our token has timed out, try to login again
            self.login(self.args)
            response = self.fs_read_dir(path)
        try:
            for r in response:
                self.process_directory_contents_acl(r.data['files'], path)
        except qumulo.lib.request.RequestError:
            self.login(self.args)
            for r in response:
                self.process_directory_contents_acl(r.data['files'], path)

    def process_directory_posix(self, path):
        """read directory contents, kick off posix push under same"""
        try:
            response = self.fs_read_dir(path)
        except qumulo.lib.request.RequestError:
            # most likely our token has timed out, try to login again
            self.login(self.args)
            response = self.fs_read_dir(path)
        try:
            for r in response:
                self.process_directory_contents_posix(r.data['files'], path)
        except qumulo.lib.request.RequestError:
            self.login(self.args)
            for r in response:
                self.process_directory_contents_posix(r.data['files'], path)

    def process_directory_contents_acl(self, directory_contents, path):
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

    def process_directory_contents_posix(self, directory_contents, path):
        for entry in directory_contents:
            # if this is a folder, set the owner/modes then process its contents
            if entry['type'] == 'FS_FILE_TYPE_DIRECTORY':
                try:
                    self.fs_set_attr(os.path.join(path, entry['name']))
                except qumulo.lib.request.RequestError:
                    self.login(self.args)
                    self.fs_set_attr(os.path.join(path, entry['name']))

                # Since this is a directory, process it anew
                new_path = path + entry['name'] + '/'
                self.process_directory_posix(new_path)
            # if it is a file, set the owner/modes appropriately
            elif entry['type'] == 'FS_FILE_TYPE_FILE':
                try:
                    self.fs_set_attr(os.path.join(path, entry['name']))
                except qumulo.lib.request.RequestError:
                    # login again since we most likely are not authed
                    self.login(self.args)
                    self.fs_set_attr(os.path.join(path, entry['name']))

    def fs_set_acl(self, path,
                    is_file = False, is_directory = False, is_root = False):
        """We don't ever need to set an ACL on the root in a repair job
        so just take a path and check it for type"""
        attrs = self.get_attrs(path)
        if attrs['type'] == 'FS_FILE_TYPE_FILE':
            is_file = True
        elif attrs['type'] == 'FS_FILE_TYPE_DIRECTORY':
            is_directory = True
        return fs.set_acl(self.connection,
                          self.credentials,
                          path=path,
                          control=qacls_config.CONTROL_DEFAULT,
                          aces=[process_ace(ace_name,
                                            is_directory=is_directory,
                                            is_root=is_root,
                                            is_file=is_file)
                                for ace_name in self.acl['acl']['aces']])

    def fs_set_attr(self, path):
        """wrapper for fs.set_attr(), since PATCH doesn't work right we need to
        read the attributes and replace the ones we care about, then write them
        back to the cluster"""
        response = fs.get_attr(self.connection, self.credentials, path=path)
        attrs = json.loads(str(response))
        fs.set_attr(self.connection, self.credentials,
                    mode=self.mode,
                    owner=self.owner,
                    group=self.group,
                    size=attrs['size'],
                    modification_time=attrs['modification_time'],
                    change_time=attrs['change_time'],
                    path=path)


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
    Q = QaclsRepair()
    Q.directory_repair_acl(Q.args.start_path)


if __name__ == '__main__':
    main()
