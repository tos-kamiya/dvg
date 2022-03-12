from operator import neg
from typing import Iterable, List, NewType, Optional

from collections import Counter
import pickle
import sys

import numpy as np
from numpy.linalg import norm


Vec = NewType("Vec", np.ndarray)


def inner_product_n(dv: Vec, pv: Vec) -> float:
    return float(np.inner(dv, pv))


def sparse(v: Vec) -> Vec:
    v = v.copy()
    threshold = (abs(np.max(v)) + abs(np.min(v))) * 0.5 * 0.02
    v[abs(v) < threshold] = 0.0
    return v


class NPWord:
    nega_posi: int  # +1 or -1
    word: str


class QueryVecError(ValueError):
    pass


class SCDVEmbedding:
    def __init__(self, words: List[str], clusters: np.ndarray, idf_wvs: np.ndarray):
        self.word_to_index = dict((w, i) for i, w in enumerate(words))
        self.cluster_idf_wvs = np.concatenate((clusters, idf_wvs), axis=1)
        self.m_shape = (clusters[0].size, idf_wvs[0].size)

    def embed(self, words: Iterable[str]) -> Vec:
        wf = Counter(words)
        v = np.zeros(self.m_shape, dtype=np.float32)
        cluster_size = self.m_shape[0]
        for word, freq in wf.items():
            i = self.word_to_index.get(word, None)
            if i is not None:
                cv = self.cluster_idf_wvs[i]
                if freq > 1:
                    v += np.outer(freq * cv[:cluster_size], cv[cluster_size:])  # here, `cv[:cluster_size]` is shorter than `cv[cluster_size:]``
                else:
                    v += np.outer(cv[:cluster_size], cv[cluster_size:])

        v = v.reshape(-1)

        n = norm(v)
        if n == 0.0:
            return v

        v *= 1.0 / n
        return v

    def optimize_for_query_vec(self, query_vec: Vec):
        assert query_vec.size == self.m_shape[0] * self.m_shape[1]

        query_vec = sparse(query_vec)
        if query_vec.size == 0:
            raise QueryVecError("query vector does not contain any topics in the model")

        # remove words with zero-weight
        idx_words = sorted((i, w) for w, i in self.word_to_index.items())
        discarded_indices = []
        w2i = dict()
        ci = 0
        for i, w in idx_words:
            vec = self.embed([w])
            sim = inner_product_n(vec, query_vec)
            if abs(sim) < 0.001:
                discarded_indices.append(i)
            else:
                w2i[w] = ci
                ci += 1

        if ci == 0:  # prevent all words being removed
            keep_i_w = idx_words[0]
            discarded_indices = [i for i, w in idx_words[1:]]
            w2i[keep_i_w[1]] = keep_i_w[0]
            ci = 1

        assert ci + len(discarded_indices) == len(idx_words)

        self.word_to_index = w2i
        self.cluster_idf_wvs = np.delete(self.cluster_idf_wvs, discarded_indices, axis=0)
        assert self.cluster_idf_wvs.shape[0] == len(self.word_to_index)

        # remove cluster items with zero-weight
        discarded_cluster_items = []
        len_idf_wvs = self.m_shape[1]
        cluster_size = self.m_shape[0]
        for i in range(cluster_size):
            if norm(query_vec[i * len_idf_wvs : (i + 1) * len_idf_wvs]) < 0.001:
                discarded_cluster_items.append(i)

        if len(discarded_cluster_items) == cluster_size:  # prevent all cluster items being discarded
            discarded_cluster_items.pop()

        self.cluster_idf_wvs = np.delete(self.cluster_idf_wvs, discarded_cluster_items, axis=1)
        self.m_shape = (cluster_size - len(discarded_cluster_items), len_idf_wvs)


def read_scdv_embedding(wordtopicvec_pack_file: str) -> SCDVEmbedding:
    assert wordtopicvec_pack_file.endswith(".pkl")
    with open(wordtopicvec_pack_file, "rb") as inp:
        data = pickle.load(inp)
    words = data["words"]
    clusters = data["clusters"]
    idf_wvs = data["idf_wvs"]
    return SCDVEmbedding(words, clusters, idf_wvs)
