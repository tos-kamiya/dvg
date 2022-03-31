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
![](images/run9.png)