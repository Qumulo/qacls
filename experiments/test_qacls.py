import unittest
import os
import posixpath

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest
import qumulo.rest.fs as fs

import qacls
import qacls_config


class Bunch(object):
    def __init__(self, adict):
        self.__dict__.update(adict)

TEST_PATH = '/test_qsplit_' + str(os.getpid()) + '/'

QC = qacls_config

PARSED_NO_QSPLIT = Bunch({'host': QC.API['host'],
                          'user': QC.API['user'],
                          'passwd': QC.API['pass'],
                          'port': QC.API['port'],
                          'no_ssl_verify': True,
                          'qacls_config': 'qacls_config.py',
                          'start_path': TEST_PATH,
                          'subparser_name': 'test',
                          'verbose': False,
                          'with_qsplit': 0})

PARSED_WITH_QSPLIT_2 = Bunch({'host': QC.API['host'],
                              'user': QC.API['user'],
                              'passwd': QC.API['pass'],
                              'port': QC.API['port'],
                              'no_ssl_verify': True,
                              'qacls_config': 'qacls_config.py',
                              'start_path': TEST_PATH,
                              'subparser_name': 'test',
                              'verbose': True,
                              'with_qsplit': 2})

# Make sure this list of files is in order so that tree creation doesn't fail
TEST_TREE = ['foo/',
             'foo/afile',
             'bar/',
             'bar/adir/',
             'bar/afile2',
             'bar/adir/another_file',
             'baz/',
             'baz/another_dir/',
             'baz/another_dir2/',
             'baz/foo',
             'baz/bar',
             'baz/baz',
             'baz/another_dir/afile',
             'baz/another_dir/afile2',
             'baz/another_dir/afile3',
             ]

DATA = 'foo' * 10


def login(parsed_args):
    # Disable strict ssl verification if requested
    if parsed_args.no_ssl_verify:
        import ssl

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

    try:
        connection = qumulo.lib.request.Connection(parsed_args.host,
                                                   int(parsed_args.port))
        # login() returns a two-tuple, the second member of which we don't need
        login_results, _ = qumulo.rest.auth.login(connection,
                                                  None,
                                                  parsed_args.user,
                                                  parsed_args.passwd)

        credentials = qumulo.lib.auth.Credentials.from_login_response(
            login_results)
    except Exception, e:
        print "Error connecting to the REST server: %s" % e
        # print __doc__
        sys.exit(1)
    return connection, credentials


def create_skeleton(start_path, skeleton):
    # login
    connection, credentials = login(PARSED_NO_QSPLIT)
    # make the temporary testing directory
    print fs.create_directory(connection,
                              credentials,
                              name=start_path.strip('/'),
                              dir_path='/')
    for path in skeleton:
        # if the last character is a trailing slash, make a directory
        if path[-1] == '/':
            # remove the trailing slash and split the dir path from the dir name
            dir_path, dir_name = posixpath.split(path[0:-1])
            # add the start_path directory name
            dir_path = posixpath.join(start_path, dir_path)
            print "path, name: " + str((dir_path, dir_name))
            print fs.create_directory(connection, credentials, dir_path=dir_path, name=dir_name)
        # else if the last character is NOT a trailing slash, make a file
        else:
            file_path, file_name = posixpath.split(path)
            # add the start_path directory name
            file_path = posixpath.join(start_path, file_path)
            print file_path
            fs.create_file(connection, credentials, file_name, file_path)
            # TODO: also fill that file with some data
            # fs.write_file(connection, credentials, DATA, path)


class TestQacls(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        create_skeleton(TEST_PATH, TEST_TREE)

    @classmethod
    def tearDownClass(self):
        connection, credentials = login(PARSED_NO_QSPLIT)
        fs.delete_tree(connection, credentials, TEST_PATH)

    def tearDown(self):
        """Remove all the bucket files and such"""
        [os.remove(f) for f in os.listdir('.')
         if 'split_' in f and
         'bucket_' in f and
         '.txt' in f
         ]

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
        qacls.validate_args(parsed)
        qacls.qacls_test.login(parsed)
        qacls.qacls_test.run_qsplit(parsed)
        files = [f for f in os.listdir('.')
                 if 'split_' in f and
                 'bucket_' in f and
                 '.txt' in f
                 ]
        print files
        files_from_qacls = qacls.qacls_test.find_all_buckets('.')
        self.assertEqual(files, files_from_qacls)

    def test_test_qacls_login(self):
        """Issue a login call, make sure connection and credentials are
        populated properly"""
        parsed = PARSED_WITH_QSPLIT_2
        qacls.validate_args(parsed)
        qacls.qacls_test.login(parsed)
        self.assertTrue(qacls.qacls_test.connection)
        self.assertTrue(qacls.qacls_test.credentials)

    def test_test_qacls_process_item(self):
        """Try out process item on TEST_PATH with no bucket
        """
        parsed = PARSED_WITH_QSPLIT_2
        qacls.validate_args(parsed)
        qacls.qacls_test.login(parsed)
        result = qacls.qacls_test.process_item(TEST_PATH)
        print result
        string_result = '\n'.join(result)
        self.assertTrue('DIR' in string_result)

    def test_test_qacls_process_bucket(self):
        """Eat a bucket file and process all the items in it
        """
        parsed = PARSED_WITH_QSPLIT_2
        qacls.validate_args(parsed)
        qacls.qacls_test.login(parsed)
        qacls.qacls_test.run_qsplit(parsed)
        buckets = qacls.qacls_test.find_all_buckets('.')
        print buckets
        for b in buckets:
            print b
            print str(open(b).readlines())
        result = qacls.qacls_test.process_bucket(buckets[0], TEST_PATH)
        result.extend(qacls.qacls_test.process_bucket(buckets[1], TEST_PATH))
        print result
        string_result = '\n'.join(result)
        self.assertTrue('DIR' in string_result)
        self.assertTrue('FIL' in string_result)

    def test_test_qacls_process_root(self):
        """Try processing from root of TEST_PATH without a bucket
        """
        parsed = PARSED_NO_QSPLIT
        qacls.validate_args(parsed)
        qacls.qacls_test.login(parsed)
        result = qacls.qacls_test.process_item(TEST_PATH)
        print result
        string_result = '\n'.join(result)
        print string_result
        self.assertTrue('DIR' in string_result)
        self.assertTrue('FIL' in string_result)


