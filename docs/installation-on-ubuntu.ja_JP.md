## Ubuntuでのインストール

下記の手順はUbuntu 20.04で確認したものです。

Pythonのバージョン`3.8`と`3.9`に対応しています(PyTorchが必要であるためPython `3.10`ではインストールできません）。

(1) 依存ライブラリを`apt`や`pip'を使ってインストール

**重要:** dvgのインストールの前に、`pdftotext`を記述 https://github.com/jalan/pdftotext に従ってインストールしてください。

(2) `dvg`をインストール

```sh
pip3 install dvg[ja]
```

または

```sh
pip3 install dvg-xxxxxxxx-py3-none-any.whl[ja]
```
