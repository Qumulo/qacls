"""qacls push
Take the specified ACL or mode bits/ownership supplied
push them down the tree specified with -r
do the Right Thing with inheritance and make everthing look inherited from the
directory specified with -r, and all directories ACLs inheritable
"""


def create_subparser(subparsers):
    # Parser for 'qacls push'
    parser_push = subparsers.add_parser('push',
                                        help='push the requested ')
    parser_push.add_argument('start_path',
                             action='store',
                             help='Directory to start perms push. This '
                                  'directory will get an uninherited version '
                                  'of the specified ACL or owner/modes.')
    parser_push.add_argument('-a', '--ace',
                             action='append',
                             help='ACE name for the ACL to push, defined in '
                             'config. Can add multiples by specifying -a '
                             'multiple times.')
    parser_push.add_argument('-U', '--uid',
                             dest='uid',
                             required=False,
                             help='specify uid to be included in the push.')
    parser_push.add_argument('-G', '--gid',
                             dest='gid',
                             required=False,
                             help='specify gid to be included in the push.')
    parser_push.add_argument('-M', '--mode',
                             dest='mode',
                             required=False,
                             help='specify mode bits (octal) to be included in '
                                  'the push.')


def main(parsed):
    print "qacls_push.py"
    if parsed.verbose:
        print parsed

if __name__ == '__main__':
    print "Don't invoke this directly, use qacls.py create instead"
