## Installation on Ubuntu

The following steps have been checked on Ubuntu 20.04.

`dvg` is compatible with Python versions `3.8` and `3.9` (cannot be installed with Python `3.10` because dvg requires PyTorch).

(1) Install `dvg`.

Download the file `dvg-xxxxxxxx-py3-none-any.whl` from the github release page and install it with pip.

```sh
pip3 install dvg-xxxxxxxx-py3-none-any.whl
```

If you want to use the Japanese model, please install it with `[ja]`.

```sh
pip3 install dvg-xxxxxxxx-py3-none-any.whl[ja]
```

(2) Install pdftotext **(option)**

If you want to search PDF files, install `pdftotext` according to the instructions at https://github.com/jalan/pdftotext.

