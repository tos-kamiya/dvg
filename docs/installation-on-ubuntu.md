## Installation on Ubuntu/macOS

The following steps have been checked on Ubuntu 20.04 and macOS Catalina (+Command Line Developer Tools).

`dvg` is compatible with Python versions from `3.8` to `3.10`.

(1) Install `dvg`.

```sh
python3 -m pip install --user dvg
```

If you want to use the Japanese model, please install it with `[ja]` as follows:

```sh
python3 -m pip install --user dvg[ja]
```

(2) Install pdftotext **(option)**

If you want to search PDF files, install `pdftotext` according to the instructions at https://github.com/jalan/pdftotext.

