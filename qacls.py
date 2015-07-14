__author__ = 'mbott'


import os
import collections

import pyad.adquery

from pyad import aduser
from pyad import adgroup

from qumulo.rest_client import RestClient

# Get the configuration bits we need in this namespace
from qacls_config import \
    PROTO_SKELETON, \
    API, \
    AD_GROUP_BASE_DN, \
    AD_USER_BASE_DN, \
    CONTROL_DEFAULT

QID_UID_BASE = 3 << 32
QID_GID_BASE = 4 << 32
QID_AD1_BASE = 5 << 32  # Only works with one domain right now

SKELETON = collections.OrderedDict(sorted(PROTO_SKELETON.items()))

RC = RestClient(address=API['host'], port=API['port'])
RC.login(username=API['user'], password=API['pass'])


def uid_to_qid(uid):
    return QID_UID_BASE + int(uid)


def gid_to_qid(gid):
    return QID_GID_BASE + int(gid)


def qid_to_uid(qid):
    return qid - QID_UID_BASE


def qid_to_gid(qid):
    return qid - QID_GID_BASE


# QID assignment and creation is handled in /src/fs/sdom/sdom.c
# We use internal Qumulo domains to set up QIDs. Each domain is assigned an
# integer.
#
# Some examples
# LOCAL DOMAIN: 0
# NFS UID: 3
# NFS GID: 4
#
# Each new AD domain we encounter, we assign the next domain ID available. So,
# the first domain we see ends up as domain ID 5
#
# As an example, in this demo.int domain I have Administrator.
#
# C:\Users\Administrator>wmic useraccount where name='administrator' get sid
# SID
# S-1-5-21-149254411-2639798758-1566622432-500
# S-1-5-21-4202559609-2341556158-3224923410-500
#
# Look here for a SID breakdown:
#   https://en.wikipedia.org/wiki/Security_Identifier
# but what you are looking for is -500, the last segment, called the RID
# Relative identifier
#
# When left-shifting 5 32 bits, we get
#
# >>> 5 << 32
# 21474836480
# >>> 21474836980 - ( 5 << 32 )  # QID of DEMO\Administrator
# 500
# >>>
#
# Which is the relative identifier related to Administrator.


def sid_to_qid(sid):
    rid = rid_from_sid(sid)
    return QID_AD1_BASE + rid


def rid_from_sid(sid):
    return int(sid.split('-')[-1])


def sid_from_username(username):
    user_dn = dn_from_username(username)
    # pyad search results don't return ad objects
    user = aduser.ADUser.from_dn(user_dn)
    # Slice off the front of the string 'PySID:S-1-5...'
    return str(user.sid).split(":")[-1]


def query_ad(ldap_attribute, where_clause, isuser=True):
    q = pyad.adquery.ADQuery()
    if isuser:
        dn = AD_USER_BASE_DN
    else:
        dn = AD_GROUP_BASE_DN

    q.execute_query(
        attributes=[ldap_attribute],
        where_clause=where_clause,
        base_dn=dn
    )

    result = q.get_results()
    return result.next()[ldap_attribute]


def dn_from_username(username):
    return query_ad('distinguishedName',
                    "sAMAccountName = '%s'" % username,
                    isuser=True)


def sid_from_groupname(groupname):
    group = adgroup.ADGroup.from_dn(dn_from_groupname(groupname))
    return str(group.sid).split(":")[-1]


def dn_from_groupname(groupname):
    return query_ad('distinguishedName',
                    "name = '%s'" % groupname,
                    isuser=False)


def qid_from_groupname(groupname):
    sid = sid_from_groupname(groupname)
    return sid_to_qid(sid)


def qid_from_username(username):
    sid = sid_from_username(username)
    return sid_to_qid(sid)


def qid_from_nfsuser(username):
    uid = uid_from_username(username)
    return uid_to_qid(uid)


def qid_from_nfsgroup(groupname):
    gid = gid_from_groupname(groupname)
    return gid_to_qid(gid)


def uid_from_username(username):
    return query_ad('uidNumber',
                    "sAMAccountName = '%s'" % username,
                    isuser=True)


def gid_from_groupname(groupname):
    return query_ad('gidNumber',
                    "cn = '%s'" % groupname,
                    isuser=False)


def parse_ace(ace):
    # if we find a 'trustee' just return
    if 'trustee' in ace.keys():
        return ace
    elif 'adgroupname' in ace.keys():
        groupname = ace['adgroupname']
        qid = qid_from_groupname(groupname)
        ace['trustee'] = str(qid)
        del ace['adgroupname']
        return ace
    elif 'adusername' in ace.keys():
        username = ace['adusername']
        qid = qid_from_username(username)
        ace['trustee'] = str(qid)
        del ace['adusername']
        return ace
    elif 'nfsusername' in ace.keys():
        username = ace['nfsusername']
        qid = qid_from_nfsuser(username)
        ace['trustee'] = str(qid)
        del ace['nfsusername']
        return ace
    elif 'nfsgroupname' in ace.keys():
        groupname = ace['nfsgroupname']
        qid = qid_from_nfsgroup(groupname)
        ace['trustee'] = str(qid)
        del ace['nfsgroupname']
        return ace


def create_skeleton():
    for key in SKELETON:
        #print key
        path, name = os.path.split(key)
        print path, name
        RC.fs.create_directory(name=name, dir_path=path)


def set_acls():
    for key in SKELETON:
        for ace in SKELETON[key]:
            parse_ace(ace)
        RC.fs.set_acl(path=key, control=CONTROL_DEFAULT, aces=SKELETON[key])


def main():
    create_skeleton()
    set_acls()


if __name__ == '__main__':
    main()
