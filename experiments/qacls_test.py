"""qacls_test
test the connection to the API
test the connection to qsplit
"""

import os
import sys
import subprocess

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
            if 'qsync_' in f and
            'bucket' in f and
            '.txt' in f
            ]


def process_item(item):
    """Tell me whether item is a directory or a file
    this is the integration point for qacls subcommands to do their thing
    """
    # print item
    result, _ = fs.get_attr(connection, credentials, path=item)
    # print result
    if result['type'] == 'FS_FILE_TYPE_DIRECTORY':
        return "%s is a DIRECTORY" % item
    elif result['type'] == 'FS_FILE_TYPE_FILE':
        return "%s is a FILE" % item
    else:
        return "%s is unknown" % item


def process_bucket(bucket_name):
    output = []
    print bucket_name
    for line in open(bucket_name):
        processed_line = '/' + line.rstrip()
        output.append(process_item(processed_line))
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


def main(parsed):
    login(parsed)
    if parsed.verbose:
        print "qacls_test.py login to API successful"
    if parsed.verbose:
        print parsed
    if parsed.with_qsplit:
        print "Running qsplit"
        # qacls_config is added to the namespace by qacls.py
        if parsed.verbose:
            print qacls_config.QSPLIT
            print parsed.with_qsplit
        cmdlist = [qacls_config.QSPLIT,
                   '--host', qacls_config.API['host'],
                   '--port', qacls_config.API['port'],
                   '--user', qacls_config.API['user'],
                   '--pass', qacls_config.API['pass'],
                   '--buckets', str(parsed.with_qsplit),
                   parsed.start_path,
                   ]
        qsplit_exit_status = subprocess.call(cmdlist)
        print "qsplit exit status " + str(qsplit_exit_status)


if __name__ == '__main__':
    print "Don't invoke this directly, use 'qacls.py test' instead"
