import unittest
import os
import time

import qacls


class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)

PARSED_NO_QSPLIT = Bunch({'host': '192.168.11.147',
                              'passwd': 'a',
                              'port': '8000',
                              'no_ssl_verify': True,
                              'qacls_config': 'qacls_config.py',
                              'start_path': '/',
                              'subparser_name': 'test',
                              'user': 'admin',
                              'verbose': False,
                              'with_qsplit': 0})

PARSED_WITH_QSPLIT_2 = Bunch({'host': '192.168.11.147',
                              'passwd': 'a',
                              'port': '8000',
                              'no_ssl_verify': True,
                              'qacls_config': 'qacls_config.py',
                              'start_path': '/',
                              'subparser_name': 'test',
                              'user': 'admin',
                              'verbose': False,
                              'with_qsplit': 2})


class TestQacls(unittest.TestCase):
    def tearDown(self):
        """Remove all the bucket files and such"""
        [os.remove(f) for f in os.listdir('.')
         if 'qsync_' in f and
         'bucket' in f and
         '.txt' in f
         ]

    def test_test_qacls(self):
        """Run qacls without qsplit
        """
        parsed = PARSED_NO_QSPLIT
        qacls.run_it(parsed)

    def test_test_qacls_qsplit(self):
        """Run qacls with qsplit
        """
        parsed = PARSED_WITH_QSPLIT_2
        qacls.run_it(parsed)

    def test_test_qacls_find_latest_file(self):
        """Create two files, return the name of the file which was created last
        """
        Fa = open('a', 'w')
        Fa.close()
        Fb = open('b', 'w')
        Fb.close()
        result = qacls.qacls_test.find_latest('a', 'b')
        os.remove('a')
        os.remove('b')
        self.assertEqual(result, 'b')

    def test_test_qacls_find_all_buckets(self):
        """Run qacls with qsplit, verify we identify buckets properly
        """
        parsed = PARSED_WITH_QSPLIT_2
        qacls.run_it(parsed)
        files = [f for f in os.listdir('.')
                 if 'qsync_' in f and
                 'bucket' in f and
                 '.txt' in f
                 ]
        print files
        files_from_qacls = qacls.qacls_test.find_all_buckets('.')
        self.assertEqual(files, files_from_qacls)

    def test_test_qacls_login(self):
        """Issue a login call, make sure connection and credentials are
        populated properly"""
        parsed = PARSED_WITH_QSPLIT_2
        self.assertFalse(qacls.qacls_test.connection)
        self.assertFalse(qacls.qacls_test.credentials)
        qacls.validate_args(parsed)
        qacls.qacls_test.login(parsed)
        self.assertTrue(qacls.qacls_test.connection)
        self.assertTrue(qacls.qacls_test.credentials)

    def test_test_qacls_process_item(self):
        """Try out process item on a file and a directory
        """
        parsed = PARSED_WITH_QSPLIT_2
        qacls.validate_args(parsed)
        qacls.qacls_test.login(parsed)
        result = qacls.qacls_test.process_item('/')
        print result
        self.assertTrue('DIRECTORY' in result)

    def test_test_qacls_process_bucket(self):
        """Eat a bucket file and process all the items in it
        """
        parsed = PARSED_WITH_QSPLIT_2
        qacls.run_it(parsed)
        buckets = qacls.qacls_test.find_all_buckets('.')
        result = qacls.qacls_test.process_bucket(buckets[1])
        print result
        string_result = '\n'.join(result)
        self.assertTrue('DIR' in string_result)
        self.assertTrue('FIL' in string_result)

    def test_test_qacls_process_root(self):
        """Try processing from root without a bucket
        """
        parsed = PARSED_NO_QSPLIT
        qacls.run_it(parsed)
        result = qacls.qacls_test.process_item('/')
        print result
        string_result = '\n'.join(result)
        print string_result
        self.assertTrue('DIR' in string_result)
        self.assertTrue('FIL' in string_result)

    def test_test_qacls_find_latest_buckets(self):
        parsed = PARSED_WITH_QSPLIT_2
        qacls.run_it(parsed)
        bucket_names_before = qacls.qacls_test.find_latest_buckets('.')
        print bucket_names_before
        # make sure we aren't overwriting buckets since timestamp is in minutes
        time.sleep(60)
        qacls.run_it(parsed)
        # this should return a list of the names of the latest generated buckets
        bucket_names_after = qacls.qacls_test.find_latest_buckets('.')
        print bucket_names_after
        self.assertTrue('qsync_' in bucket_names_after[0])
        self.assertNotEqual(bucket_names_before, bucket_names_after)