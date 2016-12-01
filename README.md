# qacls.py
## A tool for managing ACEs and ACLs on Qumulo QSFS. Rhymes with 'cackles'

```
Copyright (c) 2015 Qumulo, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
```

### INTRO:

Qacls is a collection of permissions management tools that work via the Qumulo
Core API. Anecdotal evidence suggests it is a bit faster than chmod -R or Windows
Explorer.

There are 3 main tools, all of which depend on qacls_config.py:

* qacls.py - Create directory skeletons with fiddly permission sets
* qacls_push.py - Push a set of ACES or POSIX modes/owner/group down the
specified tree, doing the Right Things with inheritance.
* qacls_repair.py - Reads the ACL and attributes from the specified directory and
repairs all permissions inside said directory accordingly. It will push either
POSIX modes/owner/group or an ACL (if generated is False).

### SETUP:

Install dependencies with pip:

```
pip install -r requirements.txt
```

Edit qacls_config.py to your liking.

Set your admin credentials:

```python
API = {
    'host': '192.168.11.147',
    'port': '8000',
    'user': 'admin',
    'pass': 'a'
}
```

Set your distinguished names for searching:

```python
AD_USER_BASE_DN = "CN=users, DC=demo, DC=int"
AD_GROUP_BASE_DN = "CN=users, DC=demo, DC=int"
```

Create your ACEs as follows.

```python
ACE_DOMAIN_ADMINS_FC_NFS = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "nfsgroupname": "domain admins",
    "flags": INHERIT_ALL,
    "rights": FC
}

ACE_ACCOUNTING_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "adgroupname": "accounting",
    "flags": INHERIT_ALL,
    "rights": RW
}
```

### QACLS.PY HOWTO

Set up your directory skeleton with paths and ACLs:

```python
# Directory prototype. This defines what will get created when qacls.py is run from the command-line.
PROTO_SKELETON = {
    '/projects': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_DOMAIN_ADMINS_FC_NFS,
        ACE_DOMAIN_USERS_RO,
        ACE_DOMAIN_USERS_RO_NFS
    ],
    '/projects/project1': [
        ACE_DOMAIN_ADMINS_FC,
        ACE_DOMAIN_ADMINS_FC_NFS,
        ACE_DOMAIN_USERS_RO,
        ACE_DOMAIN_USERS_RO_NFS,
        ACE_PROJECT1_USERS_RW
    ]
}
```

Run qacls.py to create the desired directory structure and ACLs.

### QACLS_PUSH HOWTO

Run qacls_push.py to push a desired set of ACEs into a directory tree (specify
multiples by repeating -a ACE at the command line:

```
# ./qacls_push.py /path/to/broken/permissions/ -a ACE_EVERYONE_RW -a ACE_GUEST_RW -a ACE_ADMIN_FC -a ACE_NFSNOBODY_RW
```

### QACLS_REPAIR HOWTO

Run qacls_repair.py on a directory that has a tree with sideways permissions,
and it will do its best to make all the permission in the tree match the
chosen directory:

```
# ./qacls_repair.py /path/to/directory
```

### EXAMPLES:

Note that most of the ACL examples result in inheritable ACLs, which will
ultimately behave differently from standard POSIX mode bits.

Some examples to closely mimic behavior of POSIX mode bits:

#### Mode 775 Example

```
Directory name '/foo'
Mode 775
user:   pablo
group:  staff
(-rwxrwxr-x pablo staff)
```

```python
ACE_USER_PABLO_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "adusername": "pablo",
    "flags": INHERIT_ALL,
    "rights": RW
}
ACE_GROUP_STAFF_RW = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "groupname": "domain admins",
    "flags": INHERIT_ALL,
    "rights": RW
}
ACE_EVERYONE_RO = {
    "type": "QFS_ACE_TYPE_ALLOWED",
    "trustee": "8589934592",
    "flags": INHERIT_ALL,
    "rights": RO
}
```

### MANIFEST:

* README.md
* qacls_config.py
* test_qacls.py
* qacls.py
* test_qacls_push.py
* qacls_push.py
* test_qacls_repair.py
* qacls_repair.py


### DEPENDENCIES:

qumulo-api
qacls.py depends on pyad, which depends on pywin32
qacls_push.py and qacls_repair.py do not depend on pywin32

### TODO:

These are not in priority order.

* Throw a proper exception when we can't add a trustee to an ACE (malformed ACE)
* Change to a more portable LDAP-only instead of pywin32)
* Progress meter. Traditionally these were hard for jobs like this, but AGGREGATES!
* Multithreading (really, just better performance)

### KNOWN ISSUES:

* qacls.py only works under Windows today (depends on pyad/pywin32)
* `runtests` not useful yet, use runtests.bat on Windows
