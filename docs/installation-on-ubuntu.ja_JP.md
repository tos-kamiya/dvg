## Ubuntu / macOSでのインストール

下記の手順はUbuntu 20.04とmacOS Catalina (+ コマンドライン・デベロッパツールのPython)で確認したものです。

Pythonのバージョン`3.8`から`3.10`に対応しています。

(1) `dvg`をインストール

`dvg`を`docopt`と`docopt-ng`の双方と互換性を持たせるため、それらへの依存はextra dependencyとして記述しました。

システムに`docopt`か`docopt-ng`がインストールされているとわかっている場合には、次のコマンドラインでインストールしてください。

```sh
python3 -m pip install --user dvg[ja]
```

不明の場合には、次のコマンドラインを試してみてください。

```sh
python3 -m pip install --user dvg[ja,docopt-ng]
```

PyTorch、Tensorflow, Flaxのいずれもインストールしていない場合には、dvgを実行すると **「None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ...」** という警告メッセージが出力されるため（実行に支障はありませんが）、気になる場合には次のようにしてPyTorchをインストールしてください。

```sh
python3 -m pip install --user torch
```

(2) pdftotextをインストール **（任意)**

PDFファイルを検索対象としたい場合には、`pdftotext`を記述 https://github.com/jalan/pdftotext に従ってインストールしてください。
