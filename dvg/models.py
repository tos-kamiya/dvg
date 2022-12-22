from typing import Callable, Iterable, List, Optional

from glob import glob
import hashlib
import os
import sys
import tarfile
from typing import NamedTuple
import urllib.request

import toml

from .scdv_embedding import Vec, read_scdv_embedding
from .scdv_embedding import inner_product_n  # DO NOT remove this. re-exporting it


_script_dir = os.path.dirname(os.path.realpath(__file__))


class ModelUrl(NamedTuple):
    name: str
    version: str
    file_url: str
    file_sha256_sum: str


def find_model_url(model_name: str, model_dir: Optional[str]) -> Optional[ModelUrl]:
    if model_dir is None:
        model_dir = os.path.join(_script_dir, "models")

    with open(os.path.join(model_dir, 'model-urls.txt')) as inp:
        for L in inp:
            L = L.rstrip()
            fields = L.split(' ')
            if fields[0] == model_name:
                model_version_str = fields[1]
                model_file_sha256_sum = fields[2]
                model_file_url = fields[3]
                return ModelUrl(model_name, model_version_str, model_file_url, model_file_sha256_sum)

    return None


class ModelSpec(NamedTuple):
    name: str
    version: str
    type: str
    tokenizer_name: str
    file_path: str


def find_model_spec(model_name: str, model_dir: Optional[str] = None) -> Optional[ModelSpec]:
    def find_model_files(model_name: str, model_dir: Optional[str] = None):
        if model_dir is None:
            model_dir = os.path.join(_script_dir, "models")

        files = glob(os.path.join(model_dir, "**", model_name + ".model.toml"))
        return files

    files = find_model_files(model_name, model_dir)
    if len(files) == 1:
        toml_file = files[0]
        with open(toml_file, "r") as inp:
            text = inp.read()
        data = toml.loads(text)
        model_version = data.get("version", 'None')
        model_type = data["type"]
        assert model_type == "scdv"
        tokenizer_name = data["tokenizer"]
        dir = os.path.dirname(toml_file)
        model_file_path = os.path.join(dir, data["file"])
        model_spec = ModelSpec(model_name, model_version, model_type, tokenizer_name, model_file_path)
        return model_spec
    elif len(files) >= 2:
        sys.exit('Internal error: found multiple mode files.')
    else:
        return None


def do_find_model_spec(model_name: str, model_dir: Optional[str] = None) -> ModelSpec:
    url = find_model_url(model_name, model_dir)
    if url is None:
        sys.exit('Error: no such model: %s' % model_name)

    spec = find_model_spec(model_name, model_dir)
    if spec is None or spec.version != url.version:
        print("> Model file not installed. Proceed to installation of the model model: %s %s" % (model_name, url.version), file=sys.stderr, flush=True)
        do_download_model(url, model_dir=model_dir)
        spec = find_model_spec(model_name, model_dir)

    if spec is None or spec.version != url.version:
        sys.exit('Error: (internal) model installation corrupted.')

    return spec


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
        assert False, 'lang is not either "en" or "ja"'


class SCDVModel:
    def __init__(self, tokenizer_name: str, model_file: str):
        self.tokenizer_name = tokenizer_name
        self.tokenizer = None
        self.embedder = read_scdv_embedding(model_file)
        self.query_vec = None

    def find_oov_tokens(self, line: str) -> List[str]:
        if self.tokenizer is None:
            self.tokenizer = load_tokenize_func(self.tokenizer_name)
        tokens = self.tokenizer(line)
        oov_tokens = [t for t in tokens if t not in self.embedder.word_to_index]
        return oov_tokens

    def set_query(self, lines: List[str]) -> None:
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

    def _optimize_for_query_lines(self, query_lines: List[str]) -> None:
        query_vec = self._query_to_vec(query_lines)
        self.embedder.optimize_for_query_vec(query_vec)


# ref: https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html

def sha256sum_of_file(file_name: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_name, 'rb') as inp:
        for bb in iter(lambda: inp.read(4096), b''):
            sha256.update(bb)
    return sha256.hexdigest()


def do_download_model(url: ModelUrl, model_dir: Optional[str] = None) -> None:
    if model_dir is None:
        model_dir = os.path.join(_script_dir, "models")

    print("> Downloading model file from: %s" % url.file_url, file=sys.stderr, flush=True)
    fn = os.path.basename(url.file_url)
    fp = os.path.join(model_dir, fn)
    try:
        urllib.request.urlretrieve(url.file_url, filename=fp)
    except:
        sys.exit("Error: failed to download the model file (network error / file IO error).")

    s = sha256sum_of_file(fp)
    if s != url.file_sha256_sum:
        sys.exit("Error: failed to downlad the model file (sha256sum does not match).")

    try:
        with tarfile.open(fp) as tf:
            tf.extractall(model_dir)
    except:
        sys.exit("Error: failed to uncompress model file.")

    print("> Successfully installed the model file.", file=sys.stderr, flush=True)
