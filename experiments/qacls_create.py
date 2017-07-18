def create_subparser(subparsers):
    # Parser for 'qacls create'
    parser_create = subparsers.add_parser('create',
                                          help='create a directory skeleton '
                                               'with fiddly permissions '
                                               'defined in qacls_config.py (or '
                                               'a config you specify)')
    parser_create.add_argument("-r", "--root",
                               help="desired location of skeleton",
                               nargs=1,
                               default="/")
