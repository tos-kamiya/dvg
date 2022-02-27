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

    def test_extract_para_iter(self):
        lines = ["a b", "c", "d e", "", "f g h", "i j"]

        paras = list(extract_para_iter(lines, 1))
        self.assertSequenceEqual(paras, [
            ((0, 1), ["a b"]),
            ((1, 2), ["c"]),
            ((2, 3), ["d e"]),
            ((3, 4), [""]),
            ((4, 5), ["f g h"]),
            ((5, 6), ["i j"]),
        ])

        paras = list(extract_para_iter(lines, 2))
        self.assertSequenceEqual(paras, [
            ((0, 2), ["a b", "c"]),
            ((1, 3), ["c", "d e"]),
            ((2, 4), ["d e", ""]),
            ((3, 5), ["", "f g h"]),
            ((4, 6), ["f g h", "i j"]),
        ])

        paras = list(extract_para_iter(lines, 3))
        self.assertSequenceEqual(paras, [
            ((0, 3), ["a b", "c", "d e"]),
            ((1, 4), ["c", "d e", ""]),
            ((2, 5), ["d e", "", "f g h"]),
            ((3, 6), ["", "f g h", "i j"]),
        ])

        paras = list(extract_para_iter(lines, 4))
        self.assertSequenceEqual(paras, [
            ((0, 4), ["a b", "c", "d e", ""]),
            ((2, 6), ["d e", "", "f g h", "i j"]),
        ])

        paras = list(extract_para_iter(lines, 5))
        self.assertSequenceEqual(paras, [
            ((0, 5), ["a b", "c", "d e", "", "f g h"]),
            ((2, 6), ["d e", "", "f g h", "i j"]),
        ])

        for i in range(6, 13):
            paras = list(extract_para_iter(lines, i))
            self.assertSequenceEqual(paras, [
                ((0, 6), lines),
            ])


if __name__ == "__main__":
    unittest.main()
