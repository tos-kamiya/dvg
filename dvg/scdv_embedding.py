from typing import Iterable, NewType

from collections import Counter
import pickle
import sys

import numpy as np
from numpy.linalg import norm


Vec = NewType("Vec", np.ndarray)


def inner_product_n(dv: Vec, pv: Vec) -> float:
    return float(np.inner(dv, pv))  # debug


class SCDVEmbedding:
    def __init__(self, wordtopicvec_pack_file: str):
        assert wordtopicvec_pack_file.endswith('.pkl')
        with open(wordtopicvec_pack_file, 'rb') as inp:
            data = pickle.load(inp)
        words = data['words']
        self.word_to_index = dict((w, i) for i, w in enumerate(words))
        self.clusters = data['clusters']
        self.idf_wvs = data['idf_wvs']
        self.m_shape = (self.clusters[0].size, self.idf_wvs[0].size)

    def embed(self, text: Iterable[str], sparse: bool = True) -> Vec:
        wf = Counter(text)
        m = np.zeros(self.m_shape, dtype=np.float32)
        for word, freq in wf.items():
            i = self.word_to_index.get(word, None)
            if i is not None:
                c = self.clusters[i]
                idf_wv = self.idf_wvs[i]
                if freq > 1:
                    m += freq * np.outer(c, idf_wv)
                else:
                    m += np.outer(c, idf_wv)
        vec = m.flatten()

        n = norm(vec)
        if n == 0.0:
            return vec

        if sparse:
            # (Note that this sparsification is different from the Mekara et al.'s original 
            # https://arxiv.org/abs/1612.06778 . The original uses a threshold of 4% of max in all vectors 
            # from the document set. In this process, the threshold is 8% of max in each vector.)
            threshold = (abs(vec.max()) + abs(vec.min())) * 0.5 * 0.08  # 8%
            vec[abs(vec) < threshold] = 0.0
        
        return vec * (1.0 / n)

    def optimize_for_query_vec(self, query_vec: Vec):
        # remove words with zero-weight
        idx_words = sorted((i, w) for w, i in self.word_to_index.items())
        discarded_indices = []
        w2i = dict()
        ci = 0
        for i, w in idx_words:
            vec = self.embed([w], sparse=False)
            ip = inner_product_n(vec, query_vec)
            if ip == 0.0:
                discarded_indices.append(i)
            else:
                w2i[w] = ci
                ci += 1
        assert ci + len(discarded_indices) == len(idx_words)

        self.word_to_index = w2i
        self.clusters = np.delete(self.clusters, discarded_indices, axis=0)
        self.idf_wvs = np.delete(self.idf_wvs, discarded_indices, axis=0)
        assert self.clusters.shape[0] == self.idf_wvs.shape[0] == len(self.word_to_index)

        # remove cluster items with zero-weight        
        assert query_vec.size == self.m_shape[0] * self.m_shape[1]
        discarded_cluster_items = []
        len_idf_wvs = self.m_shape[1]
        for i in range(self.clusters[0].size):
            if norm(query_vec[i * len_idf_wvs : (i + 1) * len_idf_wvs]) == 0.0:
                discarded_cluster_items.append(i)

        # prevent all cluster items being discarded
        if len(discarded_cluster_items) == self.m_shape[0]:
            discarded_cluster_items.pop()
        
        self.clusters = np.delete(self.clusters, discarded_cluster_items, axis=1)
        self.m_shape = (self.clusters[0].size, self.idf_wvs[0].size)
