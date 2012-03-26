#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from sjutils.utils import compare_versions


class TestCompareVersions(unittest.TestCase):

    def test_compare_simple(self):
        self.assertTrue(compare_versions('1', '2', '<'))
        self.assertFalse(compare_versions('1', '2', '>'))

    def test_compare_simple_triplet(self):
        self.assertTrue(compare_versions('1.1.0', '1.1.1', '<'))

    def test_compare_uneven_tuples(self):
        self.assertFalse(compare_versions('1.5.3', '1', '<'))
        self.assertTrue(compare_versions('1.5.3', '2', '<'))

    def test_compare_str_vs_num(self):
        self.assertFalse(compare_versions('1.10.0', '1.1.1', '<'))
        self.assertTrue(compare_versions('1.1.1', '1.10.0', '<'))


if __name__ == '__main__':
    unittest.main()
