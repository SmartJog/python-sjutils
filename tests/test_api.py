#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sjutils


class TestAPI(unittest.TestCase):
    def test_compat(self):
        """Backward compatibility test."""

        api = (
            # from defaultdict
            "DefaultDict",
            # from logger2
            "Logger2",
            # from loggeradapter
            "LoggerAdapter",
            # from pgconnmanager
            "PgConnManager",
            "PgConnProxy",
            "manage_pgconn",
            "manage_pgconn_conf",
            # from threadpool
            "threadpool",
            # from utils
            "all",
            "any",
            "flatten_dict",
            "flatten_list",
            "html_entity_fixer",
            "html_escape",
            "pretty_size",
        )

        self.assertTrue(set(dir(sjutils)).issuperset(api))


if __name__ == "__main__":
    unittest.main()
