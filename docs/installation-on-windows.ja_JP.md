## Windowsでのインストール

下記の手順は Windows 10 (+ [Python公式webサイト](https://www.python.org) で配布しているPython)で確認したものです。

Pythonのバージョン`3.8`から`3.10`までに対応しています。

(1) `dvg`をインストール

`dvg`を`docopt`と`docopt-ng`の双方と互換性を持たせるため、それらへの依存はextra dependencyとして記述しました。

システムに`docopt`か`docopt-ng`がインストールされているとわかっている場合には、次のコマンドラインはスキップしてください
（言い換えると、`docopt`や`docopt-ng`のインストールが不明の場合には、次のコマンドラインを試してみてください）

```sh
pip install docopt-ng
```

あとは、dvgを次のようにしてインストールしてください。

```sh
pip install wheel
pip install dvg[ja]
```

PyTorch、Tensorflow, Flaxのいずれもインストールしていない場合には、dvgを実行すると **「None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ...」** という警告メッセージが出力されるため（実行に支障はありませんが）、気になる場合には次のようにしてPyTorchをインストールしてください。

```sh
pip install torch
```

(2) NKFをインストール **(推奨)**

**文字コードがUTF-8のテキストファイルも検索対象にするには、NKFをインストールしてください。**
(いわゆるShiftJISのテキストファイルと、UTF-8のテキストファイルが混在しているときに、NKFを用いることで、文字コードを判別して読み込みます。)

[ネットワーク用漢字コード変換フィルタ シフトJIS,EUC-JP,ISO-2022-JP,UTF-8,UTF-16](https://www.vector.co.jp/soft/win95/util/se295331.html)
からダウンロードして展開したディレクトリ「vc2005 > win32(98,Me,NT,2000,XP,Vista,7)Windows-31J」の中にあるファイル`nkf32.exe`を利用します。

dvgのbinディレクトリを、コマンドプロンプトなどで次を実行することで確認してください。

```sh
dvg --bin-dir
```

このディレクトリに、先の`nkf32.exe`をコピーしてください。

(3) pdftotextをインストール **（任意)**

PDFファイルを検索対象としたい場合には、次の(3.1)または(3.2)のいずれかの方法により`poppler`をインストールしてください。

(3.1) [Chocolatey](https://chocolatey.org/)を利用する

次でインストールしてください。

```
choco install poppler
```

(3.2) Popplerを手動でインストーする

まず、Popplerを次のページからダウンロードして展開してください。

https://blog.alivate.com.au/poppler-windows/

次に、展開した先の、`pdftotext.exe`があるディレクトリ（例えば、展開した先が "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0" なら "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0\bin\" )にPATHを通してください。

コマンドプロンプト等から、pdftotextを実行できることを確認してください。

(3) データファイルのダウンロード **(任意)**

ツール `dvg` は単語トークン化および SCDV モデルのデータファイルを必要とします。これらのファイルは必要に応じて実行時に動的にダウンロードされますが、事前にダウンロードしておくことも可能です。

```sh
dvg -m en --diagnostic
dvg -m ja --diagnostic
```
