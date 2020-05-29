"""
qacls_config.py

Edit this file to define ACLs, your directory skeleton, and your API parameters.
"""

# Qumulo cluster address/port/admin credentials
QHOST = '192.168.11.155'
QPORT = 8000
QUSER = 'admin'
QPASS = 'Admin123'

################################################################################

CONTROL_DEFAULT = [
    "PRESENT",
    "AUTO_INHERIT"
]

# Repeatable sets of rights
# Use these to set up common sets of access rights. The usual (Full control,
# read/write, read) have been defined sanely based on basic Windows ACEs

# Full Control
FC = [
    "READ",
    "READ_EA",
    "READ_ATTR",
    "READ_ACL",
    "WRITE_EA",
    "WRITE_ATTR",
    "WRITE_ACL",
    "CHANGE_OWNER",
    "WRITE_GROUP",
    "DELETE",
    "EXECUTE",
    "MODIFY",
    "EXTEND",
    "ADD_FILE",
    "ADD_SUBDIR",
    "DELETE_CHILD",
    "SYNCHRONIZE"
]

# Read-write
RW = [
    "READ",
    "READ_EA",
    "READ_ATTR",
    "READ_ACL",
    "WRITE_EA",
    "WRITE_ATTR",
    "DELETE",
    "EXECUTE",
    "MODIFY",
    "EXTEND",
    "ADD_FILE",
    "ADD_SUBDIR",
    "DELETE_CHILD",
    "SYNCHRONIZE"
]

# Read-only
RO = [
    "READ",
    "READ_EA",
    "READ_ATTR",
    "READ_ACL",
    "EXECUTE",
    "SYNCHRONIZE"
]

# For a directory where admins can move/rename things but users can't
PARENT_MOVE_RENAME = [
    "READ",
    "READ_EA",
    "READ_ATTR",
    "READ_ACL",
    "WRITE_EA",
    "WRITE_ATTR",
    "WRITE_ACL",
    "CHANGE_OWNER",
    "WRITE_GROUP",
    "DELETE",
    "EXECUTE",
    "MODIFY",
    "EXTEND",
    "DELETE_CHILD",
    "SYNCHRONIZE"
]

# Read and execute
RE = [
    "READ",
    "READ_EA",
    "READ_ATTR",
    "READ_ACL",
    "EXECUTE",
    "SYNCHRONIZE"
]

# Inheritance. Can define multiples and reference them in individual ACLs below
INHERIT_ALL = [
    "OBJECT_INHERIT",
    "CONTAINER_INHERIT"
]

INHERIT_ALL_INHERITED = [
    "OBJECT_INHERIT",
    "CONTAINER_INHERIT",
    "INHERITED"
]

INHERITED = [
    "INHERITED"
]

EMPTY_FLAGS = []

# ACEs. Can define command-line accessible ACEs from here. Group name must
# resolve in AD
ACE_DOMAIN_ADMINS_FC = {
    "type": "ALLOWED",
    "groupname": "domain admins",
    "flags": INHERIT_ALL,
    "rights": FC
}

ACE_DOMAIN_USERS_RW = {
    "type": "ALLOWED",
    "groupname": "Domain Users",
    "flags": INHERIT_ALL,
    "rights": RW
}

ACE_DOMAIN_UERS_RO = {
    "type": "ALLOWED",
    "groupname": "Domain Users",
    "flags": INHERIT_ALL,
    "rights": RO
}
