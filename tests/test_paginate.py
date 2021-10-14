#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from sjutils.utils import paginate


class TestPaginate(unittest.TestCase):
    @staticmethod
    def _list_from_paginated(iterable):
        return [list(page) for page in iterable]

    def test_paginate_simple(self):
        self.assertEqual(
            self._list_from_paginated(paginate(range(10), 3)),
            [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]],
        )

    def test_paginate_even(self):
        self.assertEqual(
            self._list_from_paginated(paginate(range(9), 3)),
            [[0, 1, 2], [3, 4, 5], [6, 7, 8]],
        )

    def test_paginate_by_one(self):
        self.assertEqual(
            self._list_from_paginated(paginate(range(9), 1)),
            [[0], [1], [2], [3], [4], [5], [6], [7], [8]],
        )

    def test_paginate_none(self):
        self.assertEqual(
            self._list_from_paginated(paginate(range(9), 9)), [list(range(9))]
        )


if __name__ == "__main__":
    unittest.main()
