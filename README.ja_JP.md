[![Tests](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml) [![CodeQL](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml)

⚠ `dvg` は**CPython 3.11とは非互換**です。一部の依存がCPython 3.11と非互換のためです。参考: Python 3.11 Readiness [https://pyreadiness.org/3.11/](https://pyreadiness.org/3.11/)  

⚠️ バージョン 1.0.0b9では、モデルファイルが刷新され、語彙数と（ベクトルの）次元が大きなものとなりました。容量の制限のためモデルファイルはPyPIに登録されているパッケージには含まれません。 **`dvg`の初回実行時にウェブサイト (https://toshihirokamiya.com/) からダウンロード** されます。  

ℹ️ `dvg`とよく似たCLIで、Sentence-Transformerのモデルを利用する `stng` ([PyPI](https://pypi.org/project/stng/), [GitHub](https://github.com/tos-kamiya/stng/)) のアルファ版をリリースいたしました。GPUの性能にもよりますが、一般的なPCだと重いです。  

# dvg

`dvg`は、インストールすれば即利用可能な、意味的類似検索を行う(grepのような)コマンドラインツールです。Windows, macOS, Ubuntuに対応しています。

SCDVモデルを使って、クエリのフレーズに似た部分を含む文書ファイルを検索します。
テキストファイル（.txt）、PDFファイル（.pdf）、MS Wordファイル（.docx）からの検索に対応しています。

## インストール

基本的には`pip dvg[ja]`でインストールできますが、文字コードの自動判定やPDFのファイルを対象にするには、オプションのインストールを行ってください。

&rarr; [Ubuntu / macOSでのインストール](docs/installation-on-ubuntu.ja_JP.md)  
&rarr; [Windowsでのインストール](docs/installation-on-windows.ja_JP.md)  

## TL;DR（典型的な利用法）

文書ファイルからクエリとなるフレーズに近いものを探す。

```sh
dvg -v -m ja <クエリとなるフレーズ> <文書ファイル>...
```

検索の実行例:  
![](docs/images/run1.png)

出力の各行は、左から順に、類似度（数字が1に近いほど類似度が高い）、パラグラフの長さ（文字数）、ファイル名、行番号の範囲となっています。

## コマンドラインオプション

`dvg`にはいくつかオプションがあります。よく使われるであろうものを説明します。

`-v, --verbose`  
Verboseオプションです。指定すると、検索の進行中に、その時点で最も類似度の高いドキュメントを表示します。

`-m MODEL, --model=MODEL`  
使用可能なモデルは、`en` (英語の文書向け)、`ja` (日本語の文書向け)です。

`-k NUM, --top-k=NUM`  
上位のNUMドキュメントを結果として表示します。既定値は20です。
0を指定すると、検索されたすべての文書を、クエリとの一致度でソートして表示します。

`-p, --paragraph`  
このオプションを指定すると、1つの文書ファイル内のそれぞれのパラグラフがドキュメントとみなされます。検索結果に1つの文書ファイルの複数のパラグラフが出力されるようになります。
このオプションが指定されていない場合、1つの文書ファイルが1つのドキュメントとみなされます。検索結果に1つの文書ファイルはたかだか1回だけ表示されます。

`-w NUM, --window=NUM`  
この数字で指定された行のかたまりを1つのパラグラフとして認識します。
既定値は20です。

`-f QUERYFILE, --query-file=QUERYFILE`  
ファイルからクエリテキストを読み込みます。
クエリファイルは、文書ファイルのようにテキストファイル以外にPDFなども可能です。

（試した限りでは、クエリをファイルで指定する場合、--windowオプションでパラグラフのサイズを大きくしたほうが結果が良いようです。例えば `-w 80` など）

`-i TEXT, --include=TEXT`  
指定された文字列が含まれていないパラグラフを検索結果から取り除きます。

`-e TEXT, --exclude=TEXT`  
指定された文字列が含まれているパラグラフを検索結果から取り除きます。

`-l CHARS, --min-length=CHARS`  
これより短いパラグラフには類似度の値を下げる処理を行います。短いパラグラフを検索結果から除外したい場合に利用してください。既定値は80です。

`-t CHARS, --excerpt-length=CHARS`  
検索結果の右端のカラムに表示される抜粋の長さです。既定値は80です。

`-q, --quote`  
検索結果のパラグラフ全体を（抜粋することなく）示します。

`-H, --header`  
出力に見出しの行を追加します。

`-j NUM, --worker=NUM`  
ワーカープロセスの数。並列実行のためのオプションです。

## ヒント

&rarr; [テキストファイルの各行を検索する](docs/search-individual-lines.ja_JP.md)  

&rarr; [検索速度を向上させる](docs/improve-search-speed.ja_JP.md)  

## トラブルシューティング

&rarr; [「ModuleNotFoundError: No module named 'docopt'」といったエラーメッセージ](docs/troubleshooting.ja_JP.md#no-docopt)

&rarr; [「ModuleNotFoundError: No module named 'fugashi'」といったエラーメッセージ](docs/troubleshooting.ja_JP.md#no-fugashi)

&rarr; [「dvg: command not found」といったエラーメッセージ](docs/troubleshooting.ja_JP.md#command-not-found)

&rarr; [「None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ...」という警告メッセージ](docs/troubleshooting.ja_JP.md#no-fugashi)

&rarr; [「UnicodeEncodeError: 'cp932' codec can't encode character ...」とっいたエラーメッセージ](docs/troubleshooting.ja_JP.md#cp932)

&rarr; [セグメンテーションフォールト(SIGSEGV)で中断](docs/troubleshooting.ja_JP.md#segfault)

## 謝辞

膨大な言語コーパスを提供されているWikipediaに感謝いたします:  
https://dumps.wikimedia.org/

## ライセンス

dvgは [BSD-2](https://opensource.org/licenses/BSD-2-Clause) ライセンスで配布されます。

## リンク

* PyPIページ https://pypi.org/project/dvg/

* D. Mekala et al., "SCDV: Sparse Composite Document Vectors using soft clustering over distributional representations," https://arxiv.org/abs/1612.06778
