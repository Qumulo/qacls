import sys
import unittest

import qacls_config
# system under test
import qacls_repair

import qumulo.rest.fs as fs


class TestQaclsRepair(unittest.TestCase):
    def setUp(self):
        sys.argv = ['./qacls_repair.py', '/']
        self.Q = qacls_repair.QaclsRepair()
        fs.create_file(self.Q.connection, self.Q.credentials, "testfile",
                       dir_path="/")
        fs.set_acl(self.Q.connection, self.Q.credentials, path="/testfile",
                   control=qacls_config.CONTROL_DEFAULT,
                   aces=[qacls_config.ACE_ADMIN_FC])

        fs.create_directory(self.Q.connection, self.Q.credentials,
                            'testdir_posix', dir_path='/')
        fs.create_file(self.Q.connection, self.Q.credentials,
                       "testfile_posix", dir_path="/testdir_posix")
        fs.create_directory(self.Q.connection, self.Q.credentials,
                            'nested_testdir_posix', dir_path='/testdir_posix')
        
        fs.create_directory(self.Q.connection, self.Q.credentials,
                            'testdir_acl', dir_path='/')
        fs.create_file(self.Q.connection, self.Q.credentials,
                       "testfile_acl", dir_path="/testdir_acl")
        fs.create_directory(self.Q.connection, self.Q.credentials,
                            'nested_testdir_acl', dir_path='/testdir_acl')
        fs.set_acl(self.Q.connection, self.Q.credentials, path="/testdir_acl",
                   control=qacls_config.CONTROL_DEFAULT,
                   aces=[qacls_config.ACE_ADMIN_FC])

    def tearDown(self):
        FILES = ['/testfile',
                 '/testdir_posix/',
                 '/testdir_posix/testfile_posix',
                 '/testdir_posix/nested_testdir_posix/',
                 '/testdir_acl/',
                 '/testdir_acl/testfile_acl',
                 '/testdir_acl/nested_testdir_acl/',
                 ]
        FILES.reverse()
        for file in FILES:
            #print file
            fs.delete(self.Q.connection, self.Q.credentials, path=file)

    def test_read_attr(self):
        attrs = self.Q.get_attrs(path='/')
        self.assertTrue(attrs)

    def test_read_attr_root(self):
        attrs = self.Q.get_attrs(path='/')
        self.assertEquals('0777', attrs['mode'])

    def test_read_acl(self):
        acl = self.Q.get_acl(path='/')
        self.assertTrue(acl)

    def test_read_acl_root(self):
        """Root on a fresh cluster should be generated ACL (POSIX-managed)"""
        acl = self.Q.get_acl(path='/')
        self.assertTrue(acl['generated'])

    def test_decide_acl_root(self):
        """Root on fresh cluster should be generated and thus is_acl() False"""
        self.assertFalse(self.Q.is_acl('/'))

    def test_decide_posix_root(self):
        """Root on fresh cluster should be generated and thus is_posix() True"""
        self.assertTrue(self.Q.is_posix('/'))

    def test_file_with_acl_decide_acl_root(self):
        self.assertTrue(self.Q.is_acl('/testfile'))

    def test_testdir_acl(self):
        self.assertTrue(self.Q.is_acl('/testdir_acl'))
        self.assertFalse(self.Q.is_posix('/testdir_acl'))

    def test_testdir_posix(self):
        self.assertTrue(self.Q.is_posix('/testdir_posix'))
        self.assertFalse(self.Q.is_acl('/testdir_posix'))

    def test_repair_acl(self):
        self.Q.directory_repair_acl('/testdir_acl')
        # TODO: this test could be more rigorous
        self.assertTrue(self.Q.is_acl('/testdir_acl/nested_testdir_acl'))

    def test_repair_posix(self):
        testdir = '/testdir_posix'
        sampledir = '/testdir_posix/nested_testdir_posix'
        testmode = '0644'
        testgroup = '17179869184'
        testowner = '12884901888'

        attrs, _ = fs.get_attr(self.Q.connection,
                            self.Q.credentials,
                            path=testdir)
        # twiddle the user group and mode on the root posix dir
        fs.set_attr(self.Q.connection,
                    self.Q.credentials,
                    mode='0644',
                    owner='12884901888',
                    group='17179869184',
                    size=attrs['size'],
                    modification_time=attrs['modification_time'],
                    change_time=attrs['change_time'],
                    path=testdir,
                    )
        # set an ACL on a subdirectory
        fs.set_acl(self.Q.connection, self.Q.credentials,
                   path=sampledir,
                   control=qacls_config.CONTROL_DEFAULT,
                   aces=[qacls_config.ACE_ADMIN_FC])
        # run the repair
        self.Q.directory_repair_acl('/testdir_posix')
        sampleattrs, _ = fs.get_attr(self.Q.connection,
                                     self.Q.credentials,
                                     path=sampledir)
        self.assertEqual(testmode, sampleattrs['mode'])
        self.assertEqual(testgroup, sampleattrs['group'])
        self.assertEqual(testowner, sampleattrs['owner'])
