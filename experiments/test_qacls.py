import unittest

import qacls


class Bunch(object):
  def __init__(self, adict):
    self.__dict__.update(adict)


class TestQacls(unittest.TestCase):
    def test_test_qacls(self):
        parsed = Bunch({'host': '192.168.11.147',
                        'passwd': 'a',
                        'port': '8000',
                        'qacls_config': 'qacls_config.py',
                        'start_path': '/',
                        'subparser_name': 'test',
                        'user': 'admin',
                        'verbose': True,
                        'with_qsplit': 0})
        qacls.run_it(parsed)

    def test_test_qacls_qsplit(self):
        parsed = Bunch({'host': '192.168.11.147',
                        'passwd': 'a',
                        'port': '8000',
                        'qacls_config': 'qacls_config.py',
                        'start_path': '/',
                        'subparser_name': 'test',
                        'user': 'admin',
                        'verbose': False,
                        'with_qsplit': 2})
        qacls.run_it(parsed)