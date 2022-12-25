## Installation on Ubuntu / macOS

The `dvg` is compatible with Python versions from `3.8` to `3.10`.

### Full install

Run the following (in case of Ubuntu):

```
sudo apt -y install python3-pip
sudo apt -y install build-essential libpoppler-cpp-dev pkg-config python3-dev
```

or the following commands (in case of macOS):

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
```
brew install pkg-config poppler python
```

Then run the following commands:

```
python3 -m pip install --user pdftotext
python3 -m pip install --user torch
python3 -m pip install --user dvg[docopt-ng,ja]
dvg -m en --diagnostic
dvg -m ja --diagnostic
```

### Step-by-step install

(1) Install pip or brew.

Run the following (in case of Ubuntu):

```
sudo apt -y install python3-pip
```

or the following commands (in case of macOS):

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

(2) Install the `dvg`.

To make `dvg` compatible with both `docopt` and `docopt-ng`, dependencies on them are now explicitly extra dependencies.

If you know either `docopt` or `docopt-ng` is already installed on your system, just try the following:

```sh
python3 -m pip install --user dvg
```

If you are unsure `docopt` or `docopt-ng` is installed on your system, try the following:

```sh
python3 -m pip install --user dvg[docopt-ng]
```

(3) Install pdftotext **(option)**

If you want to search PDF files, install `pdftotext` according to the instructions at https://github.com/jalan/pdftotext.

Specifically, run the following:

In case of Ubuntu:

```sh
sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev
python3 -m pip install --user pdftotext
```

In case of macOS:

```
brew install pkg-config poppler python
python3 -m pip install --user pdftotext
```

(4) Download data files **(option)**

Tool `dvg` needs data files of word tokenization and SCDV model.
These files are downloaded dynamically when needed at runtime, but can also be downloaded in advance.

```sh
dvg -m en --diagnostic
```

(5) Japanese Model **(option)**

If you want to use the Japanese model, please install it with `[ja]` as follows:

```sh
python3 -m pip install --user dvg[ja]
```

However, if you run dvg without PyTorch, Tensorflow, or Flax installed, you will get the warning message **"None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ..."** This will not have any harmful effect on execution, but if you are concerned about the warning message, please install PyTorch as follows.

```sh
python3 -m pip install --user torch
```

To download the data file for Japanese in advance, run the following command line:

```sh
dvg -m ja --diagnostic
```

