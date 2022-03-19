[![Tests](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/tests.yaml) [![CodeQL](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/tos-kamiya/dvg/actions/workflows/codeql-analysis.yml)

# dvg

`dvg`は、インストールすれば即利用可能な、意味的類似検索を行うコマンドラインngrepツールです。

SCDVモデルを使って、クエリのフレーズに似た部分を含む文書ファイルを検索します。
テキストファイル（.txt）、PDFファイル（.pdf）、MS Wordファイル（.docx）からの検索に対応しています。

## インストール

&rarr; [Ubuntuでのインストール](docs/installation-on-ubuntu.ja_JP.md)  
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

**この機能は実験段階のものであり、検索結果が通常の検索よりも悪くなる可能性があります（特に、類似度の数値が小さい文書ファイルに関して）。**

もし同じ文書ファイルを対象に検索を繰り返す場合は、文書ファイルをインデックス化することを検討してみてください。

いったんインデックスDBを作成すると、そのインデックスDBを利用して（明らかにクエリと関係がない）文書ファイルを足切りすることで検索の性能が向上します。
（類似度を計算するための浮動小数点の計算が減ること、文書ファイルよ読み込むためのファイルIOが減ること、の2点の効果があります。）

(1) インデックス化を行うには、文書ファイルが置いてあるディレクトリをカレントディレクトリにして、そのディレクトリで`dvgi --build`コマンドを実行します。

```sh
dvgi --build -m ja <文書ファイル>...
```

コマンドの名前が`dvgi`に代わっていることに注意してください。また、インデックス化を行うときに指定する文書ファイルは、以後の検索で対象となる可能性があるすべての文書ファイルとしてください。

このコマンドを実行することにより、カレントディレクトリに`.dvg`というサブディレクトリが作成され、インデックスDBが置かれます。

(2) インデックスDBを利用して検索を行うには、インデックス化を行ったときと同じカレントディレクトリで、コマンドを`dvg`を`dvgi`に変更したコマンドラインを実行してください。

```sh
dvgi -v -m ja <クエリとなるフレーズ> <文書ファイル>...
```

インデックスDBを利用した検索の例:  
![](docs/images/run9.png)

## トラブルシューティング

| 状況 | 対策 |
| --- | --- |
| dvgを実行しようとすると **「ModuleNotFoundError: No module named 'fugashi'」** といったエラーメッセージが出る。 | pipコマンドで`pip3 install dvg-xxxxxxxx-py3-none-any.whl[ja]`のように`[ja]`をつけて再インストールしてください。 |
| dvgを実行中に **「UnicodeEncodeError: 'cp932' codec can't encode character ...」** とっいたエラーメッセージが出る。 | ファイルの文字コードに関するエラーです。Windows上で実行している場合は「NKFのインストール」を行ってみてください。 |

## 謝辞

膨大な言語コーパスを提供されているWikipediaに感謝いたします:  
https://dumps.wikimedia.org/

SCDV(Sparse Composite Document Vectors)についてはD. Mekalaらのこちらの論文を参照してください:  
https://arxiv.org/abs/1612.06778

## ライセンス

dvgは [BSD-2](https://opensource.org/licenses/BSD-2-Clause) ライセンスで配布されます。
