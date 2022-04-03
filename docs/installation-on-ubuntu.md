## Installation on Ubuntu / macOS

The following steps have been checked on Ubuntu 20.04 and macOS Catalina (+ Python of Command Line Developer Tools).

`dvg` is compatible with Python versions from `3.8` to `3.10`.

(1) Install `dvg`.

```sh
python3 -m pip install --user dvg
```

(2) Install pdftotext **(option)**

If you want to search PDF files, install `pdftotext` according to the instructions at https://github.com/jalan/pdftotext.

(3) Japanese Model **(option)** 

If you want to use the Japanese model, please install it with `[ja]` as follows:

```sh
python3 -m pip install --user dvg[ja]
```

However, if you run dvg without PyTorch, Tensorflow, or Flax installed, you will get the warning message **"None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ..."** This will not have any harmful effect on execution, but if you are concerned about the warning message, please install PyTorch as follows.

```sh
python3 -m pip install --user torch
```
