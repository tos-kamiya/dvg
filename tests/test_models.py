from typing import *

import unittest
import os
import sys
import tempfile
import time

from dvg.models import find_model_specs, build_model_file


def save_file(file_name: str, contents: Union[str, bytes]):
    with open(file_name, "wb") as outp:
        if not isinstance(contents, bytes):
            contents = contents.encode("utf-8")
        outp.write(contents)


class ModelTest(unittest.TestCase):
    def test_find_model_specs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            mdir = os.path.join(tempdir, "models")
            os.mkdir(mdir)
            c = "\n".join(['type = "scdv"', 'tokenizer = "ja"', 'file = "ja.v1.pkl"'])
            save_file(os.path.join(mdir, "ja.model.toml"), c)
            save_file(os.path.join(mdir, "ja.v1.pkl"), b"0")

            s = find_model_specs("ja", model_dir=tempdir)
            self.assertIsNotNone(s)
            tokenizer, model_file = s.tokenizer_name, s.model_file_path
            self.assertTrue(os.path.splitext(model_file)[1] == ".pkl")

    def test_build_model_file(self):
        with tempfile.TemporaryDirectory() as tempdir:
            mdir = os.path.join(tempdir, "models")
            os.mkdir(mdir)
            c = "\n".join(['type = "scdv"', 'tokenizer = "ja"', 'file = "ja.v1.pkl"'])
            save_file(os.path.join(mdir, "ja.model.toml"), c)
            save_file(os.path.join(mdir, "ja.v1.pkl.part-aa"), b"aa")
            save_file(os.path.join(mdir, "ja.v1.pkl.part-ab"), b"ab")

            s = find_model_specs("ja", model_dir=tempdir)
            self.assertIsNotNone(s)
            tokenizer, model_file = s.tokenizer_name, s.model_file_path
            build_model_file(model_file)
            time.sleep(0.1)
            self.assertTrue(os.path.exists(model_file))
