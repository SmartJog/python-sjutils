#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from sjutils.debversion import DebianVersion, debver_array


class TestDebVersion(unittest.TestCase):
    def test_debver_array(self):
        testcases = [
            ["abcxyz", 6, [ord("a"), ord("b"), ord("c"), ord("x"), ord("y"), ord("z")]],
            ["ab", 4, [ord("a"), ord("b"), 0, 0]],
            ["a~b", 3, [ord("a"), -1, ord("b")]],
            ["a+b", 3, [ord("a"), ord("+") + 256, ord("b")]],
        ]

        for testcase in testcases:
            self.assertEqual(testcase[2], debver_array(testcase[0], testcase[1]))

    def test_init(self):
        testcases = [
            ["1", 0, "1", ""],
            ["1.0.1", 0, "1.0.1", ""],
            ["1.0-1", 0, "1.0", "1"],
            ["1:1.0-1", 1, "1.0", "1"],
            ["2:3.4-5.6-7ubuntu8", 2, "3.4-5.6", "7ubuntu8"],
        ]

        for testcase in testcases:
            debver = DebianVersion(testcase[0])

            self.assertEqual(
                testcase[1], debver.epoch, "Epoch doesn't match for %s" % testcase[0]
            )
            self.assertEqual(
                testcase[2],
                debver.upstream,
                "Upstream version doesn't match for %s" % testcase[0],
            )
            self.assertEqual(
                testcase[3],
                debver.debian,
                "Debian version doesn't match for %s" % testcase[0],
            )

    def test_debian_version(self):
        # In each testcase, we have two version strings, and then the expected
        # result -- -1 if the first is less than the second; 1 if the first
        # is greater than the second, and 0 if they're equivalent.
        testcases = [
            ["1", "2", -1],
            ["1", "1", 0],
            ["2", "1", 1],
            ["1.0", "1.1", -1],
            ["1.2.3", "1.2.1", 1],
            ["1.0.0.1", "1.0.0.1", 0],
            ["1.0", "1.0-0", 0],
            ["1.0-1", "1.0-0", 1],
            ["1.0-1", "1.0-0.1", 1],
            ["1.0", "1:0.1", -1],
            ["1.0beta1", "1.0", 1],
            ["1.0beta1", "1.0-1", 1],
            ["1.0", "1.0-1", -1],
            ["1.0-1bpo1", "1.0-1", 1],
            ["1.0-1bpo1", "1.0-1.1", -1],
            ["1.0-1", "1.0-1~sarge1", 1],
            ["1:1.0-1", "1.0", 1],
            ["1:0.42-11", "2:1.5.0-2", -1],
            ["0.42-11+squeeze", "0.42-11+squeeze2", -1],
            ["0.10.1", "0.10.1~dev", 1],
            ["0.10.1~dev-1", "0.10.1~dev-2", -1],
            ["1.0.25+2+nmu2", "1.0.25+2+nmu1", 1],
            ["3.0pl1-124", "3.0pl1-116", 1],
        ]
        for testcase in testcases:
            val = DebianVersion(testcase[0]).__cmp__(DebianVersion(testcase[1]))
            msg = "%s <=> %s return %s instead of %s" % (
                testcase[0],
                testcase[1],
                val,
                testcase[2],
            )
            self.assertEqual(val, testcase[2], msg)


if __name__ == "__main__":
    unittest.main()
