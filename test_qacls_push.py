__author__ = 'mbott'


import unittest
import sys
from copy import deepcopy

import qacls_config
import qacls_push

import qumulo.rest.fs as fs


class TestQaclsPush(unittest.TestCase):
    def test_process_ace_root_directory(self):
        """The ACL applied to the root directory should not appear inherited"""
        ACE = deepcopy(qacls_config.ACE_EVERYONE_RW)
        result = qacls_push.process_ace(ACE, is_directory=True, is_root=True)
        self.assertEqual(result['flags'], qacls_config.INHERIT_ALL)

    def test_process_ace_directory(self):
        """The ACL applied to all non-root dirs should appear inherited"""
        ACE = deepcopy(qacls_config.ACE_EVERYONE_RW)
        result = qacls_push.process_ace(ACE, is_directory=True, is_root=False)
        self.assertEqual(result['flags'], qacls_config.INHERIT_ALL_INHERITED)

    def test_process_ace_file(self):
        """The ACL applied to files should just show inherited, since you can't
        inherit from files"""
        ACE = deepcopy(qacls_config.ACE_EVERYONE_RW)
        result = qacls_push.process_ace(ACE, is_file=True)
        self.assertEqual(result['flags'], qacls_config.INHERITED)

    def test_process_directory_without_login(self):
        """process_directory() should work if our bearer token is borked"""
        sys.argv = ['./qacls_push.py', '/', '-a', 'ACE_NFSNOBODY_RW']
        Q = qacls_push.QaclsCommand()
        print Q.credentials.bearer_token
        print Q.start_path
        Q.credentials.bearer_token = 'borked'
        Q.process_directory(Q.start_path)

    def test_process_directory_contents_without_login(self):
        # TODO: Fix this test (and others) to create/destroy test trees
        sys.argv = ['./qacls_push.py', '/', '-a', 'ACE_NFSNOBODY_RW']
        #test_file_names = ['a', 'b', 'c', 'd']
        Q = qacls_push.QaclsCommand()
        # fs.create_directory(Q.connection, Q.credentials, 'test_dir', '/')
        # for foo in test_file_names:
        #     fs.create_file(Q.connection, Q.credentials, foo, '/test_dir/')
        response = fs.read_entire_directory(Q.connection,
                                            Q.credentials,
                                            page_size=5000,
                                            path='/test_dir')
        print response
        print Q.credentials.bearer_token
        print Q.start_path
        r_list = []
        for r in response:
            r_list.append(r)
        print r_list
        Q.credentials.bearer_token = 'borked'
        Q.process_directory_contents(r.data['files'], '/test_dir/')

