"""qacls_test
test the connection to the API
test the connection to qsplit
"""

import os
import sys
import subprocess
import posixpath

from multiprocessing import Pool

import qumulo.lib.auth
import qumulo.lib.request
import qumulo.rest
import qumulo.rest.fs as fs


def create_subparser(subparsers):
    """Parser for 'qacls test"""
    parser_test = subparsers.add_parser('test',
                                        help='test qumulo_api and qsplit '
                                             'availability, and connection to'
                                             'the API of the chosen cluster.')
    parser_test.add_argument('start_path',
                             action='store',
                             help='Directory for existence test. This '
                                  'directory will have its metadata read, if '
                                  'you can login')
    parser_test.add_argument('-s', '--with-qsplit',
                             action='store',
                             dest='with_qsplit',
                             default=0,
                             type=int,
                             metavar='N',
                             help='Try using N qsplit buckets instead of '
                                  'treewalking ourself.')

connection = None
credentials = None
start_path = None


def find_latest(a, b):
    """take two (local) filenames, return the one that was created most recently
    """
    a_mtime = os.path.getmtime(a)
    b_mtime = os.path.getmtime(b)
    return a if a_mtime > b_mtime else b


def find_all_buckets(directory):
    """return a list of qsplit buckets found in the specified directory"""
    return [f for f in os.listdir(directory)
            if 'split_' in f and
            'bucket_' in f and
            '.txt' in f
            ]


def process_item(item):
    """Determine whether item is a directory or a file and hand it to the
    correct function.
    this is the integration point for qacls subcommands to do their thing and
    should not normally need to be modified.
    """
    # TODO: we are currently issuing two metadata requests with directories, could reduce to one
    result, _ = fs.get_attr(connection, credentials, path=item)
    if result['type'] == 'FS_FILE_TYPE_DIRECTORY':
        return process_directory(item)
    elif result['type'] == 'FS_FILE_TYPE_FILE':
        return process_file(item)
    else:
        return process_unknown(item)


def process_directory(item):
    """return a list of responses walking the directory and processing dirs and
    files found -- handle directories in this function
    """
    result_list = ['DIR\t%s' % item]
    # result_list.append('DIR\t%s' % item)
    for new_item in fs.read_entire_directory(connection,
                                             credentials,
                                             path=item):
        directory_list = new_item[0]['files']
        # print directory_list
        for f in directory_list:
            # print file['path']
            result_list.extend(process_item(f['path']))
    return result_list


def process_file(item):
    """return list containing file status - do whatever you need to to a file in
    this function
    """
    return ["FIL\t%s" % item]


def process_unknown(item):
    """Anything that isn't a directory or a file ends up here. We can increase
    the file types we support by enhancing process_item() and adding functions
    """
    return ["UNK\t%s" % item]


def process_bucket(bucket_name, start_dir='/'):
    """Open a bucket file, iterate through each entry and process everything"""
    output = []
    # print bucket_name
    for line in open(bucket_name):
        processed_line = posixpath.join(start_dir, line.rstrip())
        print processed_line
        output.extend(process_item(processed_line))
    return output


def login(parsed_args):
    global connection, credentials
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


def run_qsplit(parsed):
    cmdlist = [qacls_config.QSPLIT,
               '--host', qacls_config.API['host'],
               '--port', qacls_config.API['port'],
               '--user', qacls_config.API['user'],
               '--pass', qacls_config.API['pass'],
               '--buckets', str(parsed.with_qsplit),
               '--aggregate_type', 'files',
               parsed.start_path,
               ]
    if parsed.verbose:
        print "running qsplit: " + str(cmdlist)
    try:
        output = subprocess.check_call(cmdlist)
        if parsed.verbose:
            print output
        return 0
    except subprocess.CalledProcessError as e:
        print e.output
        print "qsplit exited with status %s" % str(e.returncode)


def main(parsed):
    login(parsed)
    if parsed.verbose:
        print "qacls_test.py login to API successful"
        print parsed
    if parsed.with_qsplit:
        print "Starting process pool"
        P = Pool(parsed.with_qsplit)
        print "Running qsplit"
        # qacls_config is added to the namespace by qacls.py
        if parsed.verbose:
            print qacls_config.QSPLIT
            print parsed.with_qsplit
        qsplit_exit_status = run_qsplit(parsed)
        if parsed.verbose:
            print "qsplit exit status " + str(qsplit_exit_status)
        results = P.map(process_bucket, find_latest_buckets('.'))
        for r in results:
            print '\n'.join(r)

    else:
        print "Running qacls test"
        print '\n'.join(process_item(parsed.start_path))


if __name__ == '__main__':
    print "Don't invoke this directly, use 'qacls.py test' instead"
