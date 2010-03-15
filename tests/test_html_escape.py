#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sjutils

class TestHtmlEscape(unittest.TestCase):

    def setUp(self):
        self.sjtools_desc = """[Errno 13] ("Bad lid: 9758 wasn't found in the db", 'No such file')"""
        self.sjtools_desc_escaped = """[Errno 13] (&quot;Bad lid: 9758 wasn't found in the db&quot;, 'No such file')"""

    def test_desc_from_sjtools(self):
        self.assertEqual(sjutils.html_escape(self.sjtools_desc),
                         self.sjtools_desc_escaped)

    def test_escape_gt_and_lt(self):
        self.assertEqual(sjutils.html_escape('3 is > 2 but < 5'),
                         '3 is &gt; 2 but &lt; 5')

if __name__ == '__main__':
    unittest.main()
