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

### HOWTO:

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



### MANIFEST:

README.txt
qacls_config.py
test_qacls.py
qacls.py


### DEPENDENCIES:

pyad, which depends on pywin32

### TODO:

* Throw a proper exception when we can't add a trustee to an ACE (malformed ACE)
* Add automatic dual-ACEs using 'username' and 'groupname'
* Add command-line options framework
* Change to a more portable LDAP-only instead of pywin32)

### KNOWN ISSUES:

* Only works under Windows today (depends on pyad/pywin32)
* `runtests` not useful yet, use runtests.bat on Windows
