from typing import *

import unittest
import contextlib
import os
import sys
import tempfile

from dvg.main import prune_overlapped_paragraphs, expand_file_iter


@contextlib.contextmanager
def back_to_curdir():
    curdir = os.getcwd()
    try:
        yield
    finally:
        os.chdir(curdir)


def touch(file_name: str):
    with open(file_name, "w") as outp:
        print("", end="", file=outp)


class DvgUtilFuncsTest(unittest.TestCase):
    def test_prune_overlapped_paragraphs(self):
        lines = ["a b", "c d", "e f", "b a"]
        spps = [
            (0.1, 4, (0, 2), lines),
            (0.3, 4, (1, 3), lines),
            (0.2, 4, (2, 4), lines),
        ]

        actual = prune_overlapped_paragraphs(spps)
        expected = [spps[1]]
        self.assertEqual(actual, expected)

        spps = [
            (0.3, 4, (0, 2), lines),
            (0.2, 4, (1, 3), lines),
            (0.1, 4, (2, 4), lines),
        ]

        actual = prune_overlapped_paragraphs(spps)
        expected = [spps[0]]
        self.assertEqual(actual, expected)

        spps = [
            (0.3, 4, (0, 2), lines),
            (0.1, 4, (1, 3), lines),
            (0.2, 4, (2, 4), lines),
        ]

        actual = prune_overlapped_paragraphs(spps)
        expected = [spps[0], spps[2]]
        self.assertEqual(actual, expected)

    def test_expand_file_iter(self):
        with tempfile.TemporaryDirectory() as tempdir:
            with back_to_curdir():
                os.chdir(tempdir)
                file_a = os.path.join("a")
                touch(file_a)
                file_b = os.path.join("b")
                touch(file_b)

                os.mkdir("D")
                file_Dc = os.path.join("D", "c")
                touch(file_Dc)

                file_list = list(expand_file_iter(["a"]))
                self.assertSequenceEqual(file_list, ["a"])

                file_list = list(expand_file_iter(["a", "b"]))
                self.assertSequenceEqual(file_list, ["a", "b"])

                file_list = list(expand_file_iter(["b", "D/c"]))
                self.assertSequenceEqual(file_list, ["b", "D/c"])

                file_list = list(expand_file_iter(["*"]))
                self.assertSequenceEqual(sorted(file_list), sorted(["a", "b"]))

                file_list = list(expand_file_iter(["**"]))
                self.assertSequenceEqual(sorted(file_list), sorted(["a", "b", os.path.join("D", "c")]))

                sys_stdin = sys.stdin
                try:
                    sys.stdin = ["a", "D/c"]
                    file_list = list(expand_file_iter(["-"]))
                    self.assertSequenceEqual(file_list, ["a", "D/c"])
                finally:
                    sys.stdin = sys_stdin


if __name__ == "__main__":
    unittest.main()
