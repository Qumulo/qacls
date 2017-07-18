def create_subparser(subparsers):
    # Parser for 'qacls repair'
    parser_repair = subparsers.add_parser('repair',
                                          help='read the top-level ACL or '
                                               'POSIX modes of a directory and '
                                               'push that down the tree '
                                               'underneath said directory.')
    parser_repair.add_argument("-r", "--root",
                               help="root of tree to read and repair",
                               nargs=1,
                               default="/")