## Installation on Windows

The `dvg` is compatible with Python versions from `3.8` to `3.10`.

### Full install

(1) Install Python **3.10.x or earlier** from [https://www.python.org/downloads/](https://www.python.org/downloads/).

* If you have other versions of Python installed, you will probably need to uninstall them.
* In the installer dialog, **check the "Add Python 3.10 to PATH" checkbox**.

(2) Install Chocolatey [https://chocolatey.org/](https://chocolatey.org/).

(3) Run following commands in command prompt.

```
choco install poppler
pip install wheel
pip install torch
pip install pdftotext
pip install dvg[docopt-ng,ja]
dvg -m en --diagnostic
dvg -m ja --diagnostic
```

### Step-by-step install

(1) Install Python **3.10.x or earlier** from [https://www.python.org/downloads/](https://www.python.org/downloads/).

* If you have other versions of Python installed, you will probably need to uninstall them.
* In the installer dialog, check the "Add Python 3.10 to PATH" checkbox.

(2) Install `dvg`

To make `dvg` compatible with both `docopt` and `docopt-ng`, dependencies on them are now explicitly extra dependencies.

If you know either `docopt` or `docopt-ng` is already installed on your system, skip the following
(In other words, if you are unsure `docopt` or `docopt-ng` is installed on your system, try the following):

```sh
pip install docopt-ng
```

Then install dvg as follows:

```sh
pip install wheel
pip install dvg
```

(3) Install pdftotext. **(option)**

If you want to search PDF files, please install `poppler` according to either (3.1) or (3.2) below.

(3.1) Use [Chocolatey](https://chocolatey.org/)

You can install Poppler as follows:

```sh
choco install poppler
```

(3.2) Install Poppler manually.

Download and extract Poppler from the following page.

https://blog.alivate.com.au/poppler-windows/

Then, add a directory where `pdftotext.exe` is located to your PATH. For example, if the extracted directory is "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0" then add "C:\Users\toshihiro\apps\pdftotext.exe poppler-0.68.0_x86\poppler-0.68.0\bin\" to PATH.

Make sure you can run pdftotext from (such as) a command prompt.

(4) Download model files **(option)**

Tool `dvg` needs model files of word tokenization and SCDV model.
These files are downloaded dynamically when needed at runtime, but can also be downloaded in advance.

```sh
dvg -m en --diagnostic
```

(5) Japanese Model **(option)** 

If you want to use the Japanese model, please install it with `[ja]` as follows:

```sh
pip install dvg[ja]
```

However, if you run dvg without PyTorch, Tensorflow, or Flax installed, you will get the warning message **"None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ..."** This will not have any harmful effect on execution, but if you are concerned about the warning message, please install PyTorch as follows.

```sh
pip install torch
```

To download the model file for Japanese in advance, run the following command line:

```sh
dvg -m ja --diagnostic
```

