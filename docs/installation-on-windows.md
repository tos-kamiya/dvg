## Installation on Windows

`dvg` is compatible with Python versions from `3.8` to `3.10`.

(1) Install `dvg`

```sh
pip install wheel
pip install dvg
```

If you want to use the Japanese model, please install it with `[ja]` as follows:

```sh
pip install dvg[ja]
```

(2) Install pdftotext. **(option)**

If you want to search PDF files, please install `poppler`.

If you are using [Chocolatey](https://chocolatey.org/), you can install Poppler as follows:

```sh
choco install poppler
```

If you want to install Poppler manually, first download and extract Poppler from the following page.

https://blog.alivate.com.au/poppler-windows/

Then, add a directory where `pdftotext.exe` is located to your PATH. For example, if the extracted directory is "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0" then add "C:\Users\toshihiro\apps\pdftotext.exe poppler-0.68.0_x86\poppler-0.68.0\bin\" to PATH.

Make sure you can run pdftotext from a DOS prompt, etc.

![](images/win-pdftotext.png)
