"""qacls create
creates a directory skeleton with appropriate inheritable permissions based on
the skeleton defined in qacls_config.py or another specified configuration file
"""


def create_subparser(subparsers):
    # Parser for 'qacls create'
    parser_create = subparsers.add_parser('create',
                                          help='create a directory skeleton '
                                               'with fiddly permissions '
                                               'defined in qacls_config.py (or '
                                               'a config you specify)')
    parser_create.add_argument('start_path',
                               help='desired location of directory skeleton',
                               action='store',
                               default='/')


def main(parsed):
    print "qacls_create.py"
    if parsed.verbose:
        print parsed

if __name__ == '__main__':
    print "Don't invoke this directly, use qacls.py create instead"
