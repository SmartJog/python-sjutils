#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sjutils

class TestFactory(unittest.TestCase):

    def test_factory(self):
        """ Factory object unicity test. """

        inst1 = sjutils.pgconnmanager.PgConnManager({'host':'toto', 'port':3128, 'user':'toto', 'password':'toto', 'dbname':'toto'})
        inst2 = sjutils.pgconnmanager.PgConnManager({'host':'toto', 'port':3128, 'user':'toto', 'password':'toto', 'dbname':'toto'})
        inst3 = sjutils.pgconnmanager.PgConnManager({'host':'toto', 'port':3128, 'user':'toto', 'password':'toto', 'dbname':'tata'})

        self.assertEqual(id(inst1), id(inst2))
        self.assertNotEqual(id(inst1), id(inst3))

if __name__ == '__main__':
    unittest.main()
