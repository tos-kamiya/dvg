## Ubuntuでのインストール

下記の手順はUbuntu 20.04で確認したものです。

Pythonのバージョン`3.8`と`3.9`に対応しています(PyTorchが必要であるためPython `3.10`ではインストールできません）。

(1) `dvg`をインストール

githubのリリースページからファイル`dvg-xxxxxxxx-py3-none-any.whl`をダウンロードして、pipでインストールしてください。

```sh
pip3 install dvg-xxxxxxxx-py3-none-any.whl[ja]
```

(2) pdftotextをインストール **（任意)**

PDFファイルを検索対象としたい場合には、`pdftotext`を記述 https://github.com/jalan/pdftotext に従ってインストールしてください。
