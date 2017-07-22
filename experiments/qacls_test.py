"""qacls_test
test the connection to the API
test the connection to qsplit
"""

import os
import subprocess


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
                             help='Try using N qsplit buckets instead of ' \
                                  'treewalking ourself.')

connection = None
credentials = None
start_path = None


def find_latest(a, b):
    """take two filenames, return the one that was created most recently"""
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



def main(parsed):
    print "qacls_test.py"
    if parsed.verbose:
        print parsed
    if parsed.with_qsplit:
        print "Running qsplit"
        # qacls_config is added to the namespace by qacls.py
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
