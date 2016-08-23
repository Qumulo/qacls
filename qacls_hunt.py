#!/usr/bin/env python
"""Examples:
        qacls_hunt.py ROOT

This starts hunting from ROOT for child directories that have ACEs for entities
that do not appear in the ACL of the parent. It logs to stdout.
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
        parser.add_argument("start_path", action="store",
                            help="Directory to start directory hunt.")

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
        # Get the ACL from the parent (path)
        parent_acl, _ = fs.get_acl(self.connection,
                                self.credentials,
                                path=path)

        parent_entities = [ace['trustee'] for ace in parent_acl['acl']['aces']]
        for entry in directory_contents:
            # if it is a folder
            if entry['type'] == 'FS_FILE_TYPE_DIRECTORY':
                # get its ACL
                entry_acl, _ = fs.get_acl(self.connection,
                                       self.credentials,
                                       path=os.path.join(path, entry['name']))
                # for each entry in the ACL
                for entry_ace in entry_acl['acl']['aces']:
                # if the entity from the ACE doesn't exist in parent ACL
                    if not entry_ace['trustee'] in parent_entities:
                        print "More-permissive child found: trustee %s found in %s but not %s" % (entry_ace['trustee'], os.path.join(path, entry['name']), path)
                        print "Trustee %s maps to SID %s" % (entry_ace['trustee'], entry_ace['trustee_details']['id_value'])
                # Finally, process this folder for more permissions fun
                self.process_directory(os.path.join(path, entry['name']))


def main():
    Q = QaclsCommand()
    Q.process_directory(Q.start_path)


if __name__ == '__main__':
    main()