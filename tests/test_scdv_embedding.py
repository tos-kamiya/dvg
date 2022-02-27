from typing import *

import unittest

import numpy as np
from numpy.linalg import norm

from dvg.scdv_embedding import *


def unit_vector(vec: np.ndarray) -> np.ndarray:
    return vec / norm(vec)


class SCDVEmgeddingTest(unittest.TestCase):
    def test_constructor(self):
        words = ['a', 'b', 'c', 'd']
        clusters = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.5, 0.5, 0.0],
        ], dtype=np.float32)
        idf_wvs = np.array([
            [0.00, 1.00],
            [0.25, 0.75],
            [0.50, 0.50],
            [0.75, 0.25],
        ], dtype=np.float32)

        emb = SCDVEmbedding(words, clusters, idf_wvs)

        vec = emb.embed(['a'], sparse=False)
        v = unit_vector(np.array([0, 1, 0, 0, 0, 0], dtype=np.float32))
        self.assertTrue(norm(vec - v) < 0.01)

        vec = emb.embed(['b'], sparse=False)
        v = unit_vector(np.array([0, 0, 0.25, 0.75, 0, 0], dtype=np.float32))
        self.assertTrue(norm(vec - v) < 0.01)

        vec = emb.embed(['c'], sparse=False)
        v = unit_vector(np.array([0, 0, 0, 0, 0.5, 0.5], dtype=np.float32))
        self.assertTrue(norm(vec - v) < 0.01)

    def test_otpimization(self):
        words = ['a', 'b', 'c', 'd']
        clusters = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.5, 0.5, 0.0],
        ], dtype=np.float32)
        idf_wvs = np.array([
            [0.00, 1.00],
            [0.25, 0.75],
            [0.50, 0.50],
            [0.75, 0.25],
        ], dtype=np.float32)

        emb = SCDVEmbedding(words, clusters, idf_wvs)

        query_vec = emb.embed(['a'])
        emb.optimize_for_query_vec(query_vec)

        self.assertEqual(emb.word_to_index, {'a': 0, 'd': 1})
        d = emb.clusters - np.array([
            [1.0], 
            [0.5],
        ], dtype=np.float32)
        self.assertTrue(norm(d.flatten()) < 0.01)
        d = emb.idf_wvs - np.array([
            [0.00, 1.00], 
            [0.75, 0.25],
        ], dtype=np.float32)
        self.assertTrue(norm(d.flatten()) < 0.01)

    def test_otpimization_zerovec(self):
        words = ['a', 'b', 'c', 'd']
        clusters = np.array([
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.5, 0.5, 0.0],
        ], dtype=np.float32)
        idf_wvs = np.array([
            [0.00, 1.00],
            [0.25, 0.75],
            [0.50, 0.50],
            [0.75, 0.25],
        ], dtype=np.float32)

        emb = SCDVEmbedding(words, clusters, idf_wvs)
        query_vec = np.zeros(6, dtype=np.float32)
        emb.optimize_for_query_vec(query_vec)

        self.assertTrue(len(emb.word_to_index) > 0)
        self.assertEqual(len(emb.word_to_index), emb.clusters.shape[0])
        self.assertTrue(emb.clusters.shape[1] > 0)
        self.assertEqual(len(emb.word_to_index), emb.idf_wvs.shape[0])
        self.assertTrue(emb.idf_wvs.shape[1] > 0)


if __name__ == "__main__":
    unittest.main()
