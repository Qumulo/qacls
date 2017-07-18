"""qacls_test
test the connection to the API
"""


def create_subparser(subparsers):
    # Parser for 'qacls test'
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
                             nargs=1,
                             dest='with_qsplit',
                             default=0,
                             type=int,
                             metavar='N',
                             help='Try using N qsplit buckets instead of ' \
                                  'treewalking ourself.')

connection = None
credentials = None
start_path = None


def main(parsed):
    print "qacls_test.py"
    if parsed.verbose:
        print parsed
    if parsed.with_qsplit:
        print "Running qsplit"


if __name__ == '__main__':
    print "Don't invoke this directly, use qacls.py test instead"
