def create_subparser(subparsers):
    # Parser for 'qacls push'
    parser_push = subparsers.add_parser('push',
                                        help='push the requested ')
    parser_push.add_argument("-r", "--root",
                             help="root of tree to push",
                             nargs=1,
                             default="/")