"""
qacls_config.py

Edit this file to define ACLs, your directory skeleton, and your API parameters.
"""

API = {
    'host': '192.168.11.147',
    'port': '8000',
    'user': 'admin',
    'pass': 'a'
}

AD_USER_BASE_DN = "CN=users, DC=demo, DC=int"
AD_GROUP_BASE_DN = "CN=users, DC=demo, DC=int"

CONTROL_DEFAULT = [
    "QFS_ACL_CONTROL_PRESENT",
    "QFS_ACL_CONTROL_AUTO_INHERIT"
]

# Repeatable sets of rights
# Use these to set up common sets of access rights. The usual (Full control,
# read/write, read) have been defined sanely based on basic Windows ACEs

# Full Control
FC = [
    "QFS_ACCESS_READ",
    "QFS_ACCESS_READ_EA",
    "QFS_ACCESS_READ_ATTR",
    "QFS_ACCESS_READ_ACL",
    "QFS_ACCESS_WRITE_EA",
    "QFS_ACCESS_WRITE_ATTR",
    "QFS_ACCESS_WRITE_ACL",
    "QFS_ACCESS_WRITE_OWNER",
    "QFS_ACCESS_WRITE_GROUP",
    "QFS_ACCESS_DELETE",
    "QFS_ACCESS_EXECUTE",
    "QFS_ACCESS_MODIFY",
    "QFS_ACCESS_EXTEND",
    "QFS_ACCESS_ADD_FILE",
    "QFS_ACCESS_ADD_SUBDIR",
    "QFS_ACCESS_DELETE_CHILD",
    "QFS_ACCESS_SYNCHRONIZE"
]

# Read-write
RW = [
    "QFS_ACCESS_READ",
    "QFS_ACCESS_READ_EA",
    "QFS_ACCESS_READ_ATTR",
    "QFS_ACCESS_READ_ACL",
    "QFS_ACCESS_WRITE_EA",
    "QFS_ACCESS_WRITE_ATTR",
    "QFS_ACCESS_DELETE",
    "QFS_ACCESS_EXECUTE",
    "QFS_ACCESS_MODIFY",
    "QFS_ACCESS_EXTEND",
    "QFS_ACCESS_ADD_FILE",
    "QFS_ACCESS_ADD_SUBDIR",
    "QFS_ACCESS_DELETE_CHILD",
    "QFS_ACCESS_SYNCHRONIZE"
]

# Read-only
RO = [
    "QFS_ACCESS_READ",
    "QFS_ACCESS_READ_EA",
    "QFS_ACCESS_READ_ATTR",
    "QFS_ACCESS_READ_ACL",
    "QFS_ACCESS_EXECUTE",
    "QFS_ACCESS_SYNCHRONIZE"
]

# Inheritance. Can define multiples and reference them in individual ACLs below
INHERIT_ALL = [
    "QFS_ACE_FLAG_OBJECT_INHERIT",
    "QFS_ACE_FLAG_CONTAINER_INHERIT"
]

INHERIT_ALL_INHERITED = [
    "QFS_ACE_FLAG_OBJECT_INHERIT",
    "QFS_ACE_FLAG_CONTAINER_INHERIT",
    "QFS_ACE_FLAG_INHERITED"
]

INHERITED = [
    "QFS_ACE_FLAG_INHERITED"
]

# ACEs. Can define as many as desired, as long as "flags" and "rights" are
# defined previously. For identity, may use 'trustee' for QID, 'adgroupname'
# for ad group, and 'adusername' for ad user
# TODO: add 'username' for duplicate ACEs in a mixed environment
ACE_DOMAIN_ADMINS_FC = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "groupname": "domain admins",
    "flags": INHERIT_ALL,
    "rights": FC
}

ACE_ACCOUNTING_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "adgroupname": "accounting",
    "flags": INHERIT_ALL,
    "rights": RW
}

ACE_DATA_RO = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "groupname": "data",
    "flags": INHERIT_ALL,
    "rights": RO
}

ACE_DATA_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "groupname": "data",
    "flags": INHERIT_ALL,
    "rights": RW
}

ACE_PRODUCTION_RO = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "groupname": "production",
    "flags": INHERIT_ALL,
    "rights": RO
}

ACE_PRODUCTION_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "groupname": "production",
    "flags": INHERIT_ALL,
    "rights": RW
}

ACE_DOMAIN_USERS_RO = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "groupname": "domain users",
    "flags": INHERIT_ALL,
    "rights": RO
}

ACE_NFS_XP_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "12884961889",
    "rights": RW
}

ACE_NFS_XP_RO = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "12884961889",
    "rights": RO
}

ACE_ADMINISTRATOR_FC = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "adusername": "administrator",
    "rights": FC
}

ACE_ADMINISTRATOR_FC_NFS = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "nfsusername": "administrator",
    "rights": FC
}

ACE_EVERYONE_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "8589934592",
    "rights": RW
}

ACE_GUEST_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "501",
    "rights": RW
}

ACE_ADMIN_FC = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "500",
    "rights": FC
}

ACE_NFSNOBODY_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "17179934718",
    "rights": RW
}

# Directory prototype. This defines what will get created when qacls.py is run
# from the command-line.
PROTO_SKELETON = {
    '/projects': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_ADMINISTRATOR_FC,
        ACE_ADMINISTRATOR_FC_NFS,
        ACE_DOMAIN_USERS_RO,
        ACE_NFS_XP_RO
    ],
    '/projects/project1': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_DOMAIN_USERS_RO,
        ACE_NFS_XP_RO
    ],
    '/projects/project1/00_ingest': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_PRODUCTION_RO,
        ACE_DATA_RW,
        ACE_NFS_XP_RW
    ],
    '/projects/project1/01_working': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_PRODUCTION_RW
    ],
    '/projects/project1/02_delivery': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_PRODUCTION_RW,
        ACE_DATA_RW
    ],
    '/projects/project1/03_archive': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_PRODUCTION_RO,
        ACE_DATA_RW
    ],
    '/projects/project1/accounting': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_ACCOUNTING_RW
    ]
}

