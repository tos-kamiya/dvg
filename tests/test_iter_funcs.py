from typing import *

import random
import unittest
import itertools

from dvg.iter_funcs import *


class IterFuncsTest(unittest.TestCase):
    def test_remove_non_first_appearances(self):
        lst = [1, 2, 3, 4, 2, 3, 2, 1]
        actual = remove_non_first_appearances(lst)
        expected = [1, 2, 3, 4]
        self.assertSequenceEqual(actual, expected)

    def test_ranges_overwrapping(self):
        rand = random.Random(123)
        tc = fc = 0
        for i in range(1000):
            x = rand.randrange(20)
            range1 = (
                x,
                x + rand.randrange(1, 10),
            )  # prevent from generating an empty range
            y = rand.randrange(20)
            range2 = (
                y,
                y + rand.randrange(1, 10),
            )  # prevent from generating an empty range
            act = ranges_overwrapping(range1, range2)
            s1 = set(range(range1[0], range1[1]))
            s2 = set(range(range2[0], range2[1]))
            expected = len(s1.intersection(s2)) > 0
            if expected:
                tc += 1
            else:
                fc += 1
            self.assertEqual(act, expected)
        assert tc >= 100
        assert fc >= 100

    def test_chunked_iter(self):
        it = range(1000)
        last_chunk_size = 0
        r = []
        for c in chunked_iter(it, 100):
            self.assertTrue(len(c) >= last_chunk_size)
            self.assertTrue(len(c) <= 100)
            r.extend(c)
        self.assertSequenceEqual(r, list(range(1000)))

        it = range(1001)
        last_chunk_size = 0
        r = []
        for c in chunked_iter(it, 100):
            self.assertTrue(len(c) >= last_chunk_size)
            self.assertTrue(len(c) <= 100)
            r.extend(c)
        self.assertSequenceEqual(r, list(range(1001)))

    def test_sliding_window_iter(self):
        range_length = 6
        poss = list(sliding_window_iter(range_length, 1))
        self.assertSequenceEqual(
            poss,
            [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)],
        )

        poss = list(sliding_window_iter(range_length, 2))
        self.assertSequenceEqual(
            poss,
            [(0, 2), (1, 3), (2, 4), (3, 5), (4, 6)],
        )

        poss = list(sliding_window_iter(range_length, 3))
        self.assertSequenceEqual(
            poss,
            [(0, 3), (1, 4), (2, 5), (3, 6)],
        )

        poss = list(sliding_window_iter(range_length, 4))
        self.assertSequenceEqual(
            poss,
            [(0, 4), (2, 6)],
        )

        poss = list(sliding_window_iter(range_length, 5))
        self.assertSequenceEqual(
            poss,
            [(0, 5), (2, 6)],
        )

        for i in range(6, 13):
            poss = list(sliding_window_iter(range_length, i))
            self.assertSequenceEqual(
                poss,
                [(0, 6)],
            )

if __name__ == "__main__":
    unittest.main()
