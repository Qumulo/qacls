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

# ACEs. Can define as many as desired, as long as "flags" and "rights" are
# defined previously. For identity, may use 'trustee' for QID, 'adgroupname'
# for ad group, and 'adusername' for ad user
# TODO: add 'username' for duplicate ACEs in a mixed environment
ACE_DOMAIN_ADMINS_FC = {
    "type": "ALLOWED",
    "groupname": "domain admins",
    "flags": INHERIT_ALL,
    "rights": FC
}

ACE_ACCOUNTING_RW = {
    "type": "ALLOWED",
    "adgroupname": "accounting",
    "flags": INHERIT_ALL,
    "rights": RW
}

ACE_DATA_RO = {
    "type": "ALLOWED",
    "groupname": "data",
    "flags": INHERIT_ALL,
    "rights": RO
}

ACE_DATA_RW = {
    "type": "ALLOWED",
    "groupname": "data",
    "flags": INHERIT_ALL,
    "rights": RW
}

ACE_PRODUCTION_RO = {
    "type": "ALLOWED",
    "groupname": "production",
    "flags": INHERIT_ALL,
    "rights": RO
}

ACE_PRODUCTION_RW = {
    "type": "ALLOWED",
    "groupname": "production",
    "flags": INHERIT_ALL,
    "rights": RW
}

ACE_DOMAIN_USERS_RO = {
    "type": "ALLOWED",
    "groupname": "domain users",
    "flags": INHERIT_ALL,
    "rights": RO
}

ACE_NFS_XP_RW = {
    "type": "ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "12884961889",
    "rights": RW
}

ACE_NFS_XP_RO = {
    "type": "ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "12884961889",
    "rights": RO
}

ACE_ADMINISTRATOR_FC = {
    "type": "ALLOWED",
    "flags": INHERIT_ALL,
    "adusername": "administrator",
    "rights": FC
}

ACE_ADMINISTRATOR_FC_NFS = {
    "type": "ALLOWED",
    "flags": INHERIT_ALL,
    "nfsusername": "administrator",
    "rights": FC
}

ACE_EVERYONE_RW = {
    "type": "ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "8589934592",
    "rights": RW
}

ACE_GUEST_RW = {
    "type": "ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "501",
    "rights": RW
}

ACE_ADMIN_FC = {
    "type": "ALLOWED",
    "flags": INHERIT_ALL,
    "trustee": "500",
    "rights": FC
}

ACE_NFSNOBODY_RW = {
    "type": "ALLOWED",
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

