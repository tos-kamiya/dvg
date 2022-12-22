from typing import *

import unittest
import os
import tempfile

from dvg.models import ModelSpec, find_model_spec
from dvg.models import ModelUrl, find_model_url


def save_file(file_name: str, contents: Union[str, bytes]):
    with open(file_name, "wb") as outp:
        if not isinstance(contents, bytes):
            contents = contents.encode("utf-8")
        outp.write(contents)


class ModelTest(unittest.TestCase):
    def test_find_model_specs(self):
        with tempfile.TemporaryDirectory() as tempdir:
            mdir = os.path.join(tempdir, 'models')
            os.mkdir(mdir)
            jadir = os.path.join(mdir, 'ja')
            os.mkdir(jadir)

            c = "\n".join(['type = "scdv"', 'tokenizer = "ja"', 'file = "ja.v1.pkl"', 'version = "v1"'])
            save_file(os.path.join(jadir, "ja.model.toml"), c)
            save_file(os.path.join(jadir, "ja.v1.pkl"), b"0")

            model_spec = find_model_spec("ja", model_dir=mdir)
            self.assertIsNotNone(model_spec)

            self.assertEqual(model_spec, ModelSpec('ja', 'v1', 'scdv', 'ja', os.path.join(jadir, 'ja.v1.pkl')))

    def test_find_model_url(self):
        with tempfile.TemporaryDirectory() as tempdir:
            mdir = os.path.join(tempdir, 'models')
            os.mkdir(mdir)

            c = "ja v4 d2e3e7a318991460328ae3745fef79be99e49a5eae8b43a74535af530a750349 https://www.toshihirokamiya.com/dvg/jawiki-scdv-v4.tar.gz\n"
            save_file(os.path.join(mdir, "model-urls.txt"), c)

            model_url = find_model_url('ja', model_dir=mdir)
            self.assertIsNotNone(model_url)

            self.assertEqual(model_url, ModelUrl('ja', 'v4', 'https://www.toshihirokamiya.com/dvg/jawiki-scdv-v4.tar.gz', 'd2e3e7a318991460328ae3745fef79be99e49a5eae8b43a74535af530a750349'))
