#! /usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import sjutils


class TestFlattenDict(unittest.TestCase):
    def setUp(self):
        self.simple_dictionary = {"first": "value", "second": {"nested": "hello"}}

        self.nested_dictionary = {
            "first": {"1": {"2": "3"}, "a": {"b": {"c": "d", "e": "f"}}}
        }

    def test_flatten_dict_simple(self):
        self.assertEqual(
            sjutils.flatten_dict(self.simple_dictionary),
            {"first": "value", "second/nested": "hello"},
        )

    def test_flatten_dict_simple_with_sep(self):
        self.assertEqual(
            sjutils.flatten_dict(self.simple_dictionary, sep=":"),
            {"first": "value", "second:nested": "hello"},
        )

    def test_flatten_dict_medium(self):
        self.assertEqual(
            sjutils.flatten_dict(self.nested_dictionary),
            {"first/1/2": "3", "first/a/b/c": "d", "first/a/b/e": "f"},
        )

    def test_flatten_dict_medium_with_sep(self):
        self.assertEqual(
            sjutils.flatten_dict(self.nested_dictionary, sep=":"),
            {"first:1:2": "3", "first:a:b:c": "d", "first:a:b:e": "f"},
        )

    def test_flatten_dict_no_original_modification(self):
        sjutils.flatten_dict(self.simple_dictionary)
        self.assertEqual(
            self.simple_dictionary, {"first": "value", "second": {"nested": "hello"}}
        )


class TestFlattenList(unittest.TestCase):
    def setUp(self):
        self.simple_list = ["first", ["second", "nested"], "third"]
        self.nested_list = [
            "first",
            ["second", ["nested", ["deep", 3], "more"], [["another", 5], 4]],
        ]
        self.with_empty_list = [3, [4, [], 5], 6]

    def test_flatten_list_simple(self):
        self.assertEqual(
            sjutils.flatten_list(self.simple_list),
            ["first", "second", "nested", "third"],
        )

    def test_flatten_list_no_original_modification(self):
        sjutils.flatten_list(self.simple_list)
        self.assertEqual(self.simple_list, ["first", ["second", "nested"], "third"])

    def test_flatten_list_nested(self):
        self.assertEqual(
            sjutils.flatten_list(self.nested_list),
            ["first", "second", "nested", "deep", 3, "more", "another", 5, 4],
        )

    def test_flatten_list_with_empty(self):
        self.assertEqual(sjutils.flatten_list(self.with_empty_list), [3, 4, 5, 6])


if __name__ == "__main__":
    unittest.main()
