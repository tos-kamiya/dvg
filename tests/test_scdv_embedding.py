from typing import *

import unittest

import numpy as np
from numpy.linalg import norm

from dvg.scdv_embedding import *


def unit_vector(vec: np.ndarray) -> np.ndarray:
    return vec / norm(vec)


class SCDVEmgeddingTest(unittest.TestCase):
    def test_constructor(self):
        words = ["a", "b", "c", "d"]
        clusters = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.5, 0.5, 0.0],
            ],
            dtype=np.float32,
        )
        idf_wvs = np.array(
            [
                [0.00, 1.00],
                [0.25, 0.75],
                [0.50, 0.50],
                [0.75, 0.25],
            ],
            dtype=np.float32,
        )

        emb = SCDVEmbedding(words, clusters, idf_wvs)

        vec = emb.embed(["a"])
        v = unit_vector(np.array([0, 1, 0, 0, 0, 0], dtype=np.float32))
        self.assertTrue(np.allclose(vec, v))

        vec = emb.embed(["b"])
        v = unit_vector(np.array([0, 0, 0.25, 0.75, 0, 0], dtype=np.float32))
        self.assertTrue(np.allclose(vec, v))

        vec = emb.embed(["c"])
        v = unit_vector(np.array([0, 0, 0, 0, 0.5, 0.5], dtype=np.float32))
        self.assertTrue(np.allclose(vec, v))

    def test_otpimization(self):
        words = ["a", "b", "c", "d"]
        clusters = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.5, 0.5, 0.0],
            ],
            dtype=np.float32,
        )
        idf_wvs = np.array(
            [
                [0.00, 1.00],
                [0.25, 0.75],
                [0.50, 0.50],
                [0.75, 0.25],
            ],
            dtype=np.float32,
        )

        emb = SCDVEmbedding(words, clusters, idf_wvs)

        query_vec = emb.embed(["a"])
        emb.optimize_for_query_vec(query_vec)

        self.assertEqual(emb.word_to_index, {"a": 0, "d": 1})
        c = np.array(
            [
                [1.0],
                [0.5],
            ],
            dtype=np.float32,
        )
        iv = np.array(
            [
                [0.00, 1.00],
                [0.75, 0.25],
            ],
            dtype=np.float32,
        )
        self.assertTrue(np.allclose(emb.cluster_idf_wvs, np.concatenate((c, iv), axis=1)))

    def test_otpimization_zerovec(self):
        words = ["a", "b", "c", "d"]
        clusters = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.5, 0.5, 0.0],
            ],
            dtype=np.float32,
        )
        idf_wvs = np.array(
            [
                [0.00, 1.00],
                [0.25, 0.75],
                [0.50, 0.50],
                [0.75, 0.25],
            ],
            dtype=np.float32,
        )

        emb = SCDVEmbedding(words, clusters, idf_wvs)
        query_vec = np.zeros(6, dtype=np.float32)
        emb.optimize_for_query_vec(query_vec)

        self.assertTrue(len(emb.word_to_index) > 0)
        self.assertEqual(len(emb.word_to_index), emb.cluster_idf_wvs.shape[0])
        self.assertTrue(emb.cluster_idf_wvs.shape[1] > 0)


if __name__ == "__main__":
    unittest.main()
