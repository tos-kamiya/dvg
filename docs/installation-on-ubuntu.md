## Installation on Ubuntu

The following steps have been checked on Ubuntu 20.04.

`dvg` is compatible with Python versions `3.8` and `3.9` (cannot be installed with Python `3.10` because dvg requires PyTorch).

(1) Install the dependencies with `apt` and `pip`.

**Important:** Before installation of dvg, install pdftotext according to the instructions at https://github.com/jalan/pdftotext.

(2) Install `dvg`.

```sh
pip3 install dvg
```

or

```sh
pip3 install dvg-xxxxxxxx-py3-none-any.whl
```

If you want to use the Japanese model, please install it with `[ja]`.

```sh
pip3 install dvg[ja]
```
