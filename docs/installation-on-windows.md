## Installation on Windows

The following steps have been checked on Windows 10 (+ Python distributed on the [official Python website](https://www.python.org)).

`dvg` is compatible with Python versions from `3.8` to `3.10`.

(1) Install `dvg`

```sh
pip install wheel
pip install dvg
```

(2) Install pdftotext. **(option)**

If you want to search PDF files, please install `poppler` according to either (2.1) or (2.2) below.

(2.1) Use [Chocolatey](https://chocolatey.org/)

You can install Poppler as follows:

```sh
choco install poppler
```

(2.2) Install Poppler manually.

Download and extract Poppler from the following page.

https://blog.alivate.com.au/poppler-windows/

Then, add a directory where `pdftotext.exe` is located to your PATH. For example, if the extracted directory is "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0" then add "C:\Users\toshihiro\apps\pdftotext.exe poppler-0.68.0_x86\poppler-0.68.0\bin\" to PATH.

Make sure you can run pdftotext from a DOS prompt, etc.

(3) Japanese Model **(option)** 

If you want to use the Japanese model, please install it with `[ja]` as follows:

```sh
pip install dvg[ja]
```

However, if you run dvg without PyTorch, Tensorflow, or Flax installed, you will get the warning message **"None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ..."** This will not have any harmful effect on execution, but if you are concerned about the warning message, please install PyTorch as follows.

```sh
pip install torch
```
