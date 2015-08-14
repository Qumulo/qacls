import unittest
from qumulo.rest_client import RestClient

API_HOST = '10.120.246.35'
API_PORT = '8000'
API_USER = 'admin'
API_PASS = 'admin'


class TestQumuloRest(unittest.TestCase):
    def test_login(self):
        RC = RestClient(address=API_HOST, port=API_PORT)
        RC.login(username=API_USER, password=API_PASS)
        self.assertTrue(RC)  # If the previous step doesn't throw an exception, pass if RC is instantiated
