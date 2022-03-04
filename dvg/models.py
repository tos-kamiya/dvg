from typing import Callable, List, Iterable, Optional, Tuple

from glob import glob
import itertools
import os
import sys

import numpy as np
import toml

from .scdv_embedding import Vec, SCDVEmbedding, read_scdv_embedding
from .scdv_embedding import inner_product_n  # DO NOT remove this. re-exporting it


_script_dir = os.path.dirname(os.path.realpath(__file__))


def find_model_specs(model_name: str, model_dir: Optional[str] = None) -> Optional[Tuple[str, str]]:
    if model_dir is None:
        model_dir = os.path.join(_script_dir, 'models')
    files = glob(os.path.join(model_dir, '**', model_name + ".model.toml"))
    if len(files) == 1:
        toml_file = files[0]
        with open(toml_file, 'r') as inp:
            text = inp.read()
        data = toml.loads(text)
        assert data['type'] == 'scdv'
        tokenizer_name = data['tokenizer']
        dir = os.path.dirname(toml_file)
        file_path = os.path.join(dir, data['file'])
        return tokenizer_name, file_path
    else:
        return None


def load_tokenize_func(lang: Optional[str]) -> Callable[[str], Iterable[str]]:
    if lang == "ja":
        import transformers
        
        tokenizer = transformers.MecabTokenizer(do_lower_case=True)
        return tokenizer.tokenize
    elif lang == 'en':
        import unicodedata

        import nltk
        try:
            nltk.word_tokenize('hello, world.')
        except LookupError:
            nltk.download('punkt')

        # ref: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
        def strip_accents(s):
            return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

        def tokenize(text: str):
            tokens = nltk.word_tokenize(text)
            return [strip_accents(t).lower() for t in tokens]
        return tokenize
    else:
        assert lang in ["en", "ja"]


class Model:
    def lines_to_vec(self, lines: List[str]) -> Vec:
        raise NotImplementedError

    def find_oov_tokens(self, line: str) -> List[str]:
        raise NotImplementedError
    
    def optimize_for_query_lines(self, query_lines: List[str]):
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

    def optimize_for_query_lines(self, query_lines: List[str]):
        for m in self.models:
            m.optimize_for_query_lines(query_lines)


class SCDVModel(Model):
    def __init__(self, tokenizer_name: str, model_file: str):
        self.tokenizer_name = tokenizer_name
        self.tokenizer = None
        try:
            self.embedder = read_scdv_embedding(model_file)
        except:
            # build the model file and re-try to read
            build_model_file(model_file)
            self.embedder = read_scdv_embedding(model_file)

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

    def optimize_for_query_lines(self, query_lines: List[str]):
        query_vec = self.lines_to_vec(query_lines)
        self.embedder.optimize_for_query_vec(query_vec)


def build_model_file(model_file: str):
    files = glob(model_file + ".part-*")
    for k, g in itertools.groupby(files, lambda f: os.path.splitext(f)[0]):
        assert k.endswith('.pkl')

        print("> Build model files as a post installation hook.", file=sys.stderr)

        split_files = sorted(g)
        with open(k, 'wb') as outp:
            for f in split_files:
                with open(f, 'rb') as inp:
                    outp.write(inp.read())
