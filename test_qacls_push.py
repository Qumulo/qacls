__author__ = 'mbott'


import unittest
from copy import deepcopy

import qacls_config
import qacls_push


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
