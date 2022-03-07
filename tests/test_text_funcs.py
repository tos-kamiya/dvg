from typing import *

import unittest

from dvg.text_funcs import *


class TextFuncsTest(unittest.TestCase):
    def test_includes_all_texts(self):
        lines = ["a b", "c", "d e"]

        texts = ["a"]
        self.assertTrue(includes_all_texts(lines, texts))

        texts = ["b"]
        self.assertTrue(includes_all_texts(lines, texts))

        texts = ["d e"]
        self.assertTrue(includes_all_texts(lines, texts))

        texts = ["a", "b"]
        self.assertTrue(includes_all_texts(lines, texts))

        texts = ["x"]
        self.assertFalse(includes_all_texts(lines, texts))

        texts = ["b c"]
        self.assertFalse(includes_all_texts(lines, texts))

        texts = ["a", "x"]
        self.assertFalse(includes_all_texts(lines, texts))

    def test_includes_any_of_texts(self):
        lines = ["a b", "c", "d e"]

        texts = ["a"]
        self.assertTrue(includes_any_of_texts(lines, texts))

        texts = ["b"]
        self.assertTrue(includes_any_of_texts(lines, texts))

        texts = ["d e"]
        self.assertTrue(includes_any_of_texts(lines, texts))

        texts = ["a", "b"]
        self.assertTrue(includes_any_of_texts(lines, texts))

        texts = ["x"]
        self.assertFalse(includes_any_of_texts(lines, texts))

        texts = ["b c"]
        self.assertFalse(includes_any_of_texts(lines, texts))

        texts = ["a", "x"]
        self.assertTrue(includes_any_of_texts(lines, texts))


if __name__ == "__main__":
    unittest.main()
