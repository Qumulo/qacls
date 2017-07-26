"""qacls_test
test the connection to the API
test the connection to qsplit
"""

import os
import sys
import subprocess
import re

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


def find_latest_buckets(directory):
    latest = None
    for f in find_all_buckets(directory):
        if not latest:
            latest = f
        else:
            latest = find_latest(latest, f)
    print latest
    # find all the latest bucket file names
    m = re.match(r'qsync_(\d+)_bucket(\d+).txt', latest)
    time_stamp = m.group(1)
    return [f for f in find_all_buckets(directory) if time_stamp in f]


def process_item(item):
    """Tell me whether item is a directory or a file
    this is the integration point for qacls subcommands to do their thing
    """
    # print item
    result, _ = fs.get_attr(connection, credentials, path=item)
    # print result
    if result['type'] == 'FS_FILE_TYPE_DIRECTORY':
        return process_directory(item)
    elif result['type'] == 'FS_FILE_TYPE_FILE':
        return process_file(item)
    else:
        return process_unknown(item)


def process_directory(item):
    """return a list of responses walking the directory and processing dirs and
    files found
    """
    result_list = []
    result_list.append('DIR\t%s' % item)
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
    return ["UNK\t%s" % item]


def process_bucket(bucket_name):
    output = []
    print bucket_name
    for line in open(bucket_name):
        processed_line = '/' + line.rstrip()
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
