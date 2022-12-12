[![Tests](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml) [![CodeQL](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml)

⚠️ お断り: バージョン 1.0.0b7 はひどいエンバグをしていたので、インストールしてしまった場合には、すぐに 1.0.0b8 にアップデートしてください。

# dvg

`dvg`は、インストールすれば即利用可能な、意味的類似検索を行うコマンドラインgrepツールです。Windows, macOS, Ubuntuに対応しています。

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

`--verbose, -v`  
Verboseオプションです。指定すると、検索の進行中に、その時点で最も類似度の高いドキュメントを表示します。

`--model=MODEL, -m MODEL`  
使用可能なモデルは、`en` (英語の文書向け)、`ja` (日本語の文書向け)です。

`--top-n=NUM, -n NUM`  
上位のNUMドキュメントを結果として表示します。既定値は20です。
0を指定すると、検索されたすべての文書を、クエリとの一致度でソートして表示します。

`--paragraph, -p`  
このオプションを指定すると、1つの文書ファイル内のそれぞれのパラグラフがドキュメントとみなされます。検索結果に1つの文書ファイルの複数のパラグラフが出力されるようになります。
このオプションが指定されていない場合、1つの文書ファイルが1つのドキュメントとみなされます。検索結果に1つの文書ファイルはたかだか1回だけ表示されます。

`--window=NUM, -w NUM`  
この数字で指定された行のかたまりを1つのパラグラフとして認識します。
既定値は20です。

`--include=TEXT, -i TEXT`  
指定された文字列が含まれていないパラグラフを検索結果から取り除きます。

`--exclude=TEXT, -e TEXT`  
指定された文字列が含まれているパラグラフを検索結果から取り除きます。

`--min-length=CHARS, -l CHARS`  
これより短いパラグラフには類似度の値を下げる処理を行います。短いパラグラフを検索結果から除外したい場合に利用してください。既定値は80です。

`--excerpt-length=CHARS, -t CHARS`  
検索結果の右端のカラムに表示される抜粋の長さです。既定値は80です。

`--header, -H`  
出力に見出しの行を追加します。

`--worker=NUM, -j NUM`  
ワーカープロセスの数。並列実行のためのオプションです。

## テキストファイルの各行を検索する

オプション`--paragraph`と`--window=1`を同時に指定すると、テキストファイルの各行を対象とした検索を行うことができます。

辞書データ[ejdict-hand](https://github.com/kujirahand/EJDict)から検索した例:  
![](docs/images/run8-ja.png)

## インデックス化 (実験中)

&rarr; [インデックス化](docs/indexing.ja_JP.md)  

## トラブルシューティング

&rarr; [dvgを実行しようとすると、「ModuleNotFoundError: No module named 'docopt'」といったエラーメッセージが出る。](docs/troubleshooting.ja_JP.md#no-docopt)

&rarr; [dvgを実行しようとすると 「ModuleNotFoundError: No module named 'fugashi'」といったエラーメッセージが出る。](docs/troubleshooting.ja_JP.md#no-fugashi)

&rarr; [dvgを実行しようとすると 「dvg: command not found」といったエラーメッセージが出る。](docs/troubleshooting.ja_JP.md#command-not-found)

&rarr; [dvgを実行中に 「None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ...」という警告メッセージが表示される。](docs/troubleshooting.ja_JP.md#no-fugashi)

&rarr; [dvgを実行中に「UnicodeEncodeError: 'cp932' codec can't encode character ...」とっいたエラーメッセージが出る。](docs/troubleshooting.ja_JP.md#cp932)

## 謝辞

膨大な言語コーパスを提供されているWikipediaに感謝いたします:  
https://dumps.wikimedia.org/

SCDV(Sparse Composite Document Vectors)についてはD. Mekalaらのこちらの論文を参照してください:  
https://arxiv.org/abs/1612.06778

## ライセンス

dvgは [BSD-2](https://opensource.org/licenses/BSD-2-Clause) ライセンスで配布されます。
