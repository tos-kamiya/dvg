## Installation on Windows

`dvg` is compatible with Python versions `3.8` and `3.9` (cannot be installed with Python `3.10` because dvg requires PyTorch).

(1) Install the dependencies.

If you are using [Chocolatey](https://chocolatey.org/), you can install Poppler as follows:

```sh
choco install poppler
```

If you want to install Poppler manually, first download and extract Poppler from the following page.

https://blog.alivate.com.au/poppler-windows/

Then, add a directory where `pdftotext.exe` is located to your PATH. For example, if the extracted directory is "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0" then add "C:\Users\toshihiro\apps\pdftotext.exe poppler-0.68.0_x86\poppler-0.68.0\bin\" to PATH.

Make sure you can run pdftotext from a DOS prompt, etc.

![](images/win-pdftotext.png)

(2) Install `dvg`

Download the file `dvg-xxxxxxxx-py3-none-any.whl` from the github release page and install it with pip.


```sh
pip install wheel
pip install dvg-xxxxxxxx-py3-none-any.whl
```

If you want to use the Japanese model, change the last line of the above command line to the following:

```sh
pip install dvg-xxxxxxxx-py3-none-any.whl[ja]
```

