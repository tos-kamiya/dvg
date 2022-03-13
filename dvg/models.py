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


class ModelSpec:
    model_type: str
    tokenizer_name: str
    model_file_path: str

    def __init__(self, model_type: str, tokenizer_name: str, model_file_path: str):
        self.model_type = model_type
        self.tokenizer_name = tokenizer_name
        self.model_file_path = model_file_path


def find_model_specs(model_name: str, model_dir: Optional[str] = None) -> Optional[ModelSpec]:
    if model_dir is None:
        model_dir = os.path.join(_script_dir, "models")
    files = glob(os.path.join(model_dir, "**", model_name + ".model.toml"))
    if len(files) == 1:
        toml_file = files[0]
        with open(toml_file, "r") as inp:
            text = inp.read()
        data = toml.loads(text)
        model_type = data["type"]
        assert model_type == "scdv"
        tokenizer_name = data["tokenizer"]
        dir = os.path.dirname(toml_file)
        model_file_path = os.path.join(dir, data["file"])
        model_spec = ModelSpec(model_type, tokenizer_name, model_file_path)
        return model_spec
    else:
        return None


def load_tokenize_func(lang: Optional[str]) -> Callable[[str], Iterable[str]]:
    if lang == "ja":
        import transformers

        tokenizer = transformers.MecabTokenizer(do_lower_case=True)
        return tokenizer.tokenize
    elif lang == "en":
        import nltk

        try:
            nltk.word_tokenize("hello, world.")
        except LookupError:
            nltk.download("punkt")

        return nltk.word_tokenize
    else:
        assert lang in ["en", "ja"]


class SCDVModel:
    def __init__(self, tokenizer_name: str, model_file: str):
        self.tokenizer_name = tokenizer_name
        self.tokenizer = None
        try:
            self.embedder = read_scdv_embedding(model_file)
        except:
            # build the model file and re-try to read
            build_model_file(model_file)
            self.embedder = read_scdv_embedding(model_file)
        self.query_vec = None

    def find_oov_tokens(self, line: str) -> List[str]:
        if self.tokenizer is None:
            self.tokenizer = load_tokenize_func(self.tokenizer_name)
        tokens = self.tokenizer(line)
        oov_tokens = [t for t in tokens if t not in self.embedder.word_to_index]
        return oov_tokens

    def set_query(self, lines: List[str]):
        self._optimize_for_query_lines(lines)
        self.query_vec = self._query_to_vec(lines)
    
    def get_query_vec(self) -> Vec:
        return self.query_vec

    def similarity_to_lines(self, lines: List[str]) -> float:
        assert self.query_vec is not None, "call set_query() before similarity_to_lines()"
        dv = self._lines_to_vec(lines)
        return inner_product_n(dv, self.query_vec)

    def _query_to_vec(self, lines: List[str]) -> Vec:
        if self.tokenizer is None:
            self.tokenizer = load_tokenize_func(self.tokenizer_name)
        words = self.tokenizer("\n".join(lines))
        vec = self.embedder.embed(words)  # unit vector
        return vec

    def _lines_to_vec(self, lines: List[str]) -> Vec:
        if self.tokenizer is None:
            self.tokenizer = load_tokenize_func(self.tokenizer_name)
        words = self.tokenizer("\n".join(lines))
        vec = self.embedder.embed(words)  # unit vector
        return vec

    def _optimize_for_query_lines(self, query_lines: List[str]):
        query_vec = self._query_to_vec(query_lines)
        self.embedder.optimize_for_query_vec(query_vec)


def build_model_file(model_file: str):
    files = glob(model_file + ".part-*")
    for k, g in itertools.groupby(files, lambda f: os.path.splitext(f)[0]):
        assert k.endswith(".pkl")

        print("> Build model files as a post installation hook.", file=sys.stderr)

        split_files = sorted(g)
        with open(k, "wb") as outp:
            for f in split_files:
                with open(f, "rb") as inp:
                    outp.write(inp.read())
