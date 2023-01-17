## Installation on Windows

The `dvg` is compatible with Python versions from `3.8` to `3.10`.

### Full install

(1) Install Python **3.10.x or earlier** from [https://www.python.org/downloads/](https://www.python.org/downloads/)  
("Downloads" &rarr; "Windows" &rarr; "Python releases for Windows" page)

* If you have other versions of Python installed, you will probably need to uninstall them.
* In the installer dialog, **check the "Add Python 3.10 to PATH" checkbox**.

(2) Install Chocolatey [https://chocolatey.org/](https://chocolatey.org/).

(3) Run following commands in command prompt (or PowerShell) in Admin mode.

```
choco install vcredist140
choco install poppler
pip install wheel
pip install torch
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

(3) Install the `pdftotext` command. **(option)**

`Poppler` is needed to search PDF files.

With [Chocolatey](https://chocolatey.org/), you can install `Poppler` in command prompt (or PowerShell) in Admin mode as follows:

```sh
choco install vcredist140
choco install poppler
```

Make sure you can run `pdftotext` on command prompt or PowerShell.

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

