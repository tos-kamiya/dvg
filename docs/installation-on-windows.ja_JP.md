## Windowsでのインストール

Pythonのバージョン`3.8`から`3.10`までに対応しています。

### フルインストール

(1) [https://www.python.org/downloads/](https://www.python.org/downloads/) から Python の **3.10.x またはそれ以前** をインストール。  
("Downloads" &rarr; "Windows" &rarr; "Python releases for Windows"ページ)

* 他のバージョンのPythonがインストールされている場合は（おそらく）アンインストールする必要があります。
* インストーラのダイアログで、**"Add Python 3.10 to PATH"というチェックボックスにチェック** を入れておいてください。

(2) Chocolatey [https://chocolatey.org/](https://chocolatey.org/) をインストール。

(3) 管理者モードのコマンドプロンプト（あるいはPowerShell）で次を実行。

```
choco install vcredist140
choco install poppler
pip install wheel
pip install torch
pip install dvg[docopt-ng,ja]
dvg -m en --diagnostic
dvg -m ja --diagnostic
```

Popplerに含まれるpdftotextコマンドを実行するには [Visual C++ Redistributable for Visual Studio 2015](`https://www.microsoft.com/en-us/download/details.aspx?id=48145`) をインストーする必要があるかもしれません。

(4) 次の「ステップバイステップのインストール」の「(2) NKFをインストール **(推奨)**」にしたがってNKFをインストールしてください。

### ステップバイステップのインストール

(1) [https://www.python.org/downloads/](https://www.python.org/downloads/) から Python の **3.10.x またはそれ以前** をインストール。  
("Downloads" &rarr; "Windows" &rarr; "Python releases for Windows"ページ)

* 他のバージョンのPythonがインストールされている場合は（おそらく）アンインストールする必要があります。
* インストーラのダイアログで、**"Add Python 3.10 to PATH"というチェックボックスにチェック** を入れておいてください。

(2) `dvg`をインストール

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

(3) NKFをインストール **(推奨)**

**文字コードがUTF-8のテキストファイルも検索対象にするには、NKFをインストールしてください。**
(いわゆるShiftJISのテキストファイルと、UTF-8のテキストファイルが混在しているときに、NKFを用いることで、文字コードを判別して読み込みます。)

[ネットワーク用漢字コード変換フィルタ シフトJIS,EUC-JP,ISO-2022-JP,UTF-8,UTF-16](https://www.vector.co.jp/soft/win95/util/se295331.html)
からダウンロードして展開したディレクトリ「vc2005 > win32(98,Me,NT,2000,XP,Vista,7)Windows-31J」の中にあるファイル`nkf32.exe`を利用します。

dvgのbinディレクトリを、コマンドプロンプトなどで次を実行することで確認してください。

```sh
dvg --bin-dir
```

このディレクトリに、先の`nkf32.exe`をコピーしてください。

(4) `pdftotext`コマンドをインストール **（任意)**

PDFファイルを検索対象としたい場合には、`poppler` が必要です。

[Chocolatey](https://chocolatey.org/)を利用すれば、管理者モードのコマンドプロンプト（あるいはPowerShell）上で、次のコマンドラインでインストールできます。

```
choco install poppler
```

コマンドプロンプト（あるいはPowerShell）上で`pdftotext`コマンドが実行できることを確認してください。`pdftotext`コマンドを実行するには [Visual C++ Redistributable for Visual Studio 2015](`https://www.microsoft.com/en-us/download/details.aspx?id=48145`) をインストーする必要があるかもしれません。

(5) モデルファイルのダウンロード **(任意)**

ツール `dvg` は単語トークン化および SCDV モデルのファイルを必要とします。これらのファイルは必要に応じて実行時に動的にダウンロードされますが、事前にダウンロードしておくことも可能です。

```sh
dvg -m en --diagnostic
dvg -m ja --diagnostic
```
