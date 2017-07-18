"""qacls repair
Read the ACL or mode bits from the start_path.
Take the read ACL or mode bits/ownership and push them down the tree specified
with -r. Do the Right Thing with inheritance and make everthing look inherited
from the directory specified with -r, and all directories ACLs inheritable.
"""


def create_subparser(subparsers):
    # Parser for 'qacls repair'
    parser_repair = subparsers.add_parser('repair',
                                          help='read the top-level ACL or '
                                               'POSIX modes of a directory and '
                                               'push that down the tree '
                                               'underneath said directory.')
    parser_repair.add_argument('start_path',
                               action='store',
                               help='Directory to start the permissions repair. '
                                    'This directory\'s contents will get an '
                                    'inherited version of the ACL or owner/modes.')

def main(parsed):
    print "qacls_repair.py"
    if parsed.verbose:
        print parsed

if __name__ == '__main__':
    print "Don't invoke this directly, use qacls.py create instead"
