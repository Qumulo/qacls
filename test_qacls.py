__author__ = 'mbott'


import unittest
import qacls


from qacls import QID_UID_BASE, QID_GID_BASE

# Some global defaults for testing
INHERIT_ALL = [
    "QFS_ACE_FLAG_OBJECT_INHERIT",
    "QFS_ACE_FLAG_CONTAINER_INHERIT"
]
RO = [
    "QFS_ACCESS_READ",
    "QFS_ACCESS_READ_EA",
    "QFS_ACCESS_READ_ATTR",
    "QFS_ACCESS_READ_ACL",
    "QFS_ACCESS_EXECUTE",
    "QFS_ACCESS_SYNCHRONIZE"
]

class TestQacls(unittest.TestCase):
    def test_uid_to_qid_root(self):
        qid_target = QID_UID_BASE
        uid = 0
        self.assertEqual(qid_target, qacls.uid_to_qid(uid))

    def test_uid_to_qid_20(self):
        uid = 20
        qid_target = QID_UID_BASE + uid
        self.assertEqual(qid_target, qacls.uid_to_qid(uid))

    def test_gid_to_qid_wheel(self):
        gid = 0
        qid_target = QID_GID_BASE + gid
        self.assertEqual(qid_target, qacls.gid_to_qid(gid))

    def test_uid_to_qid_root_string(self):
        uid = '0'
        qid_target = QID_UID_BASE + int(uid)
        self.assertEqual(qid_target, qacls.uid_to_qid(uid))

    def test_gid_to_qid_wheel_string(self):
        gid = '0'
        qid_target = QID_GID_BASE + int(gid)
        self.assertEqual(qid_target, qacls.gid_to_qid(gid))

    def test_qid_to_uid_root(self):
        uid_target = 0
        qid = QID_UID_BASE
        self.assertEqual(uid_target, qacls.qid_to_uid(qid))

    def test_qid_to_gid_wheel(self):
        gid_target = 0
        qid = QID_GID_BASE
        self.assertEqual(gid_target, qacls.qid_to_gid(qid))

    def test_sid_to_qid(self):
        qid_target = 21474836980
        sid = 'S-1-5-21-4202559609-2341556158-3224923410-500'
        self.assertEqual(qid_target, qacls.sid_to_qid(sid))

    def test_rid_from_sid(self):
        rid_target = 500
        sid = 'S-1-5-21-4202559609-2341556158-3224923410-500'
        self.assertEqual(rid_target, qacls.rid_from_sid(sid))


class TestADQacls(unittest.TestCase):
    def test_sid_from_username(self):
        """
        C:\>wmic useraccount where name='dan' get sid
        SID
        S-1-5-21-4202559609-2341556158-3224923410-1117
        """
        username = 'dan'
        sid_target = 'S-1-5-21-4202559609-2341556158-3224923410-1117'
        self.assertEqual(sid_target, qacls.sid_from_username(username))

    def test_sid_from_groupname_data(self):
        """
        C:\>wmic group where name='data' get sid
        SID
        S-1-5-21-4202559609-2341556158-3224923410-1109
        """
        groupname = 'data'
        sid_target = 'S-1-5-21-4202559609-2341556158-3224923410-1109'
        self.assertEqual(sid_target, qacls.sid_from_groupname(groupname))

    def test_sid_from_groupname_accounting(self):
        """
        C:\>wmic group where name='accounting' get sid
        SID
        S-1-5-21-4202559609-2341556158-3224923410-1111
        """
        groupname = 'accounting'
        sid_target = 'S-1-5-21-4202559609-2341556158-3224923410-1111'
        self.assertEqual(sid_target, qacls.sid_from_groupname(groupname))

    def test_qid_from_groupname_data(self):
        groupname = 'data'
        qid_target = 21474837589
        self.assertEqual(qid_target, qacls.qid_from_groupname(groupname))

    def test_uid_from_username_dan(self):
        username = 'dan'
        uid_target = 10000
        self.assertEqual(uid_target, qacls.uid_from_username(username))

    def test_gid_from_groupname_production(self):
        groupname = 'accounting'
        gid_target = 10003
        self.assertEqual(gid_target, qacls.gid_from_groupname(groupname))

    def test_parse_ace_group_to_trustee(self):
        """
        ACE_DATA_RO = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "adgroupname": "data",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        should become
        ACE_DATA_RO = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "trustee": "21474837589",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        before being applied by set_acls()
        """
        ace_data_ro_with_groupname = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "adgroupname": "data",
            "flags": INHERIT_ALL,
            "rights": RO
        }

        ace_data_ro_target = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "trustee": "21474837589",
            "flags": INHERIT_ALL,
            "rights": RO
        }

        self.assertEqual(ace_data_ro_target,
                         qacls.parse_ace(ace_data_ro_with_groupname))

    def test_parse_ace_user_to_trustee(self):
        ace_data_ro_with_username = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "adusername": "administrator",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        ace_data_ro_target = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "trustee": "21474836980",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        self.assertEqual(ace_data_ro_target,
                         qacls.parse_ace(ace_data_ro_with_username))

    def test_parse_ace_nfsuser_to_trustee(self):
        ace_data_ro_with_username = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "nfsusername": "dan",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        ace_data_ro_target = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "trustee": "12884911888",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        self.assertEqual(ace_data_ro_target,
                         qacls.parse_ace(ace_data_ro_with_username))

    def test_parse_ace_nfsgroup_to_trustee(self):
        ace_data_ro_with_username = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "nfsgroupname": "production",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        ace_data_ro_target = {
            "type": "QFS_ACE_TYPE_ALLOWED",
            "trustee": "17179879186",
            "flags": INHERIT_ALL,
            "rights": RO
        }
        self.assertEqual(ace_data_ro_target,
                         qacls.parse_ace(ace_data_ro_with_username))
