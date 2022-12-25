## Ubuntu / macOSでのインストール

`dvg`はPythonのバージョン`3.8`から`3.10`に対応しています。

### フルインストール

Ubuntuの場合は次をターミナルで実行します。

```
sudo apt -y install python3-pip
sudo apt -y install build-essential libpoppler-cpp-dev pkg-config python3-dev
```

macOSの場合は次を実行します。

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
```
brew install pkg-config poppler python
```

その後、ターミナルで次のコマンドを実行してください。

```
python3 -m pip install --user pdftotext
python3 -m pip install --user torch
python3 -m pip install --user dvg[docopt-ng,ja]
dvg -m en --diagnostic
dvg -m ja --diagnostic
```

### ステップバイステップのインストール

(1) pipやbrewのインストール

Ubuntuの場合は次を実行します。

```
sudo apt -y install python3-pip
```

macOSの場合は次を実行します。

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

(2) `dvg`をインストール

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

(3) pdftotextをインストール **（任意)**

PDFファイルを検索対象としたい場合には、`pdftotext`を記述 https://github.com/jalan/pdftotext に従ってインストールしてください。

具体的には、次のようにしてください。

Ubuntuの場合

```sh
sudo apt install build-essential libpoppler-cpp-dev pkg-config python3-dev
python3 -m pip install --user pdftotext
```

macOSの場合

```
brew install pkg-config poppler python
```

(4) データファイルのダウンロード **(任意)**

ツール `dvg` は単語トークン化および SCDV モデルのデータファイルを必要とします。これらのファイルは必要に応じて実行時に動的にダウンロードされますが、事前にダウンロードしておくことも可能です。

```sh
dvg -m en --diagnostic
dvg -m ja --diagnostic
```
