import unittest
import os

import qacls


class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)


class TestQacls(unittest.TestCase):
    def tearDown(self):
        """Remove all the bucket files and such"""
        [os.remove(f) for f in os.listdir('.')
         if 'qsync_' in f and
         'bucket' in f and
         '.txt' in f
         ]

    def test_test_qacls(self):
        parsed = Bunch({'host': '192.168.11.147',
                        'passwd': 'a',
                        'port': '8000',
                        'qacls_config': 'qacls_config.py',
                        'start_path': '/',
                        'subparser_name': 'test',
                        'user': 'admin',
                        'verbose': True,
                        'with_qsplit': 0})
        qacls.run_it(parsed)

    def test_test_qacls_qsplit(self):
        parsed = Bunch({'host': '192.168.11.147',
                        'passwd': 'a',
                        'port': '8000',
                        'qacls_config': 'qacls_config.py',
                        'start_path': '/',
                        'subparser_name': 'test',
                        'user': 'admin',
                        'verbose': False,
                        'with_qsplit': 2})
        qacls.run_it(parsed)

    def test_test_qacls_find_latest_file(self):
        Fa = open('a','w')
        Fa.close()
        Fb = open('b','w')
        Fb.close()
        result = qacls.qacls_test.find_latest('a', 'b')
        os.remove('a')
        os.remove('b')
        self.assertEqual(result, 'b')

    def test_test_qacls_find_all_buckets(self):
        parsed = Bunch({'host': '192.168.11.147',
                        'passwd': 'a',
                        'port': '8000',
                        'qacls_config': 'qacls_config.py',
                        'start_path': '/',
                        'subparser_name': 'test',
                        'user': 'admin',
                        'verbose': False,
                        'with_qsplit': 2})
        qacls.run_it(parsed)
        files = [f for f in os.listdir('.')
                 if 'qsync_' in f and
                 'bucket' in f and
                 '.txt' in f
                 ]
        print files
        files_from_qacls = qacls.qacls_test.find_all_buckets('.')
        self.assertEqual(files, files_from_qacls)
