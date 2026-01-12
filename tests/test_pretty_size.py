#! /usr/bin/python3

import unittest
import sjutils


class TestPrettySize(unittest.TestCase):
    def setUp(self):
        self.size_37B = 37
        self.size_3MB = 3 * 1024 * 1024 + 23
        self.size_4YB = 4 * 1024**8

    def test_3MB(self):
        self.assertEqual(sjutils.pretty_size(self.size_3MB), "3.0 MB")

    def test_3MB_verbose(self):
        self.assertEqual(
            sjutils.pretty_size(self.size_3MB, verbose=True), "3.0 MegaBytes"
        )

    def test_37B(self):
        self.assertEqual(sjutils.pretty_size(self.size_37B), "37 B")

    def test_37B_verbose(self):
        self.assertEqual(sjutils.pretty_size(self.size_37B, verbose=True), "37 Bytes")

    def test_4YB(self):
        self.assertEqual(sjutils.pretty_size(self.size_4YB), "4 YB")

    def test_4YB_verbose(self):
        self.assertEqual(
            sjutils.pretty_size(self.size_4YB, verbose=True), "4 YottaBytes"
        )


if __name__ == "__main__":
    unittest.main()
