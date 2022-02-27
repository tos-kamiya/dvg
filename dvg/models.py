from typing import Callable, List, Iterable, Optional

from glob import glob
import itertools
import os
import sys

import numpy as np

from .scdv_embedding import Vec, SCDVEmbedding
from .scdv_embedding import inner_product_n  # DO NOT remove this. re-exporting it


_script_dir = os.path.dirname(os.path.realpath(__file__))


def find_file_in_model_dir(file_name: str) -> Optional[str]:
    files = glob(os.path.join(_script_dir, 'models', '**', file_name))
    if len(files) == 1:
        return files[0]
    else:
        return None


def load_tokenize_func(lang: Optional[str]) -> Callable[[str], Iterable[str]]:
    if lang == "ja":
        try:
            import transformers
        except ModuleNotFoundError as e:
            sys.exit("Error: transformers not installed.")
        tokenizer = transformers.MecabTokenizer(do_lower_case=True)
        return tokenizer.tokenize
    else:
        import nltk
        try:
            nltk.word_tokenize('hello, world.')
        except LookupError:
            nltk.download('punkt')

        return nltk.word_tokenize


class Model:
    def lines_to_vec(self, lines: List[str]) -> Vec:
        raise NotImplementedError

    def find_oov_tokens(self, line: str) -> List[str]:
        raise NotImplementedError
    
    def optimize_for_query_vec(self, pattern_vec: Vec):
        raise NotImplementedError


class CombinedModel(Model):  # todo !! TEST !!
    def __init__(self, models: List[Model]):
        self.models = models
        self.vec_widths = None
    
    def lines_to_vec(self, lines: List[str]) -> Vec:
        vecs = [model.lines_to_vec(lines) for model in self.models]
        if self.vec_widths is None:
            self.vec_widths = [vec.size for vec in vecs]
        return np.concatenate(vecs)

    def find_oov_tokens(self, line: str) -> List[str]:
        oov_set = set(self.models[0].find_oov_tokens(line))
        for m in self.models[1:]:
            oov_set.intersection_update(m.find_oov_tokens(line))
        return sorted(oov_set)

    def optimize_for_query_vec(self, pattern_vec: Vec):
        assert self.vec_widths is not None
        for i, (m, w) in enumerate(zip(self.models, self.vec_widths)):
            sub_pattern_vec = pattern_vec[i * w : (i + 1) * w]
            m.optimize_for_query_vec(sub_pattern_vec)


class SCDVModel(Model):
    def __init__(self, tokenizer_name: str, model_file: str):
        self.tokenizer_name = tokenizer_name
        self.tokenizer = None
        self.embedder = SCDVEmbedding(model_file)

    def lines_to_vec(self, lines: List[str]) -> Vec:
        if self.tokenizer is None:
            self.tokenizer = load_tokenize_func(self.tokenizer_name)
        tokens = self.tokenizer('\n'.join(lines))
        vec = self.embedder.embed(tokens)  # unit vector
        return vec

    def find_oov_tokens(self, line: str) -> List[str]:
        if self.tokenizer is None:
            self.tokenizer = load_tokenize_func(self.tokenizer_name)
        tokens = self.tokenizer(line)
        oov_tokens = [t for t in tokens if t not in self.embedder.word_to_index]
        return oov_tokens

    def optimize_for_query_vec(self, pattern_vec: Vec):
        self.embedder.optimize_for_query_vec(pattern_vec)


def build_model_files():
    files = glob(os.path.join(_script_dir, 'models', '**', '*.pkl.part-*'))
    if files:
        print("> Build model files as a post installation hook.", file=sys.stderr)
        for k, g in itertools.groupby(files, lambda f: os.path.splitext(f)[0]):
            assert k.endswith('.pkl')
            if os.path.exists(k):
                continue  # for k, g
            split_files = sorted(g)
            with open(k, 'wb') as outp:
                for f in split_files:
                    with open(f, 'rb') as inp:
                        outp.write(inp.read())
            for f in split_files:
                os.remove(f)
