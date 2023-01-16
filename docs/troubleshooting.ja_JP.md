## トラブルシューティング

### <a id="no-docopt" />「ModuleNotFoundError: No module named 'docopt'」といったエラーメッセージ

`docopt`または`docopt-ng`パッケージのインストールが必要です。pipコマンドで`pip3 install docopt-ng`を実行してください。

### <a id="no-fugashi" />「ModuleNotFoundError: No module named 'fugashi'」といったエラーメッセージ

pipコマンドで`pip3 install dvg[ja]`のように`[ja]`をつけて再インストールしてください。 

### <a id="command-not-found" />「dvg: command not found」といったエラーメッセージ

`dvg`の実行ファイルにPATHが通っていないようです。

Windowsを使っている場合は、システムの詳細設定→環境変数から、PATH変数を確認してください。
`C:\Users\<username>\AppData\Local\Programs\Python\Python39\Scripts\` (パスは利用しているPythonのバージョンによって異なります）が含まれるようにしてください。

macOSを使っている場合は、`.zprofile`のPATH変数を確認してください。
`~/Python/3.8/bin` (パスは利用しているPythonのバージョンによって異なります）が含まれるようにしてください。

Ubuntuを使っている場合は、`~/.profile` や `~/.bashrc` 等のシェル設定ファイルでのPATH変数を確認してください。
`~/.local/bin` が含まれるようにしてください。

何らかの理由により、環境変数PATHを設定したくない場合には、次のように実行することもできます。

```sh
python3 -m dvg ...  # dvgスクリプトを実行
```

### <a id="none-of-pytorch" /> 「None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ...」という警告メッセージ

インストールの説明にあるPyTorchのインストールを行ってください。

### <a id="cp932" /> 「UnicodeEncodeError: 'cp932' codec can't encode character ...」とっいたエラーメッセージ

ファイルの文字コードに関するエラーです。Windows上で実行している場合は「NKFのインストール」を行ってみてください。

### <a id="segfault" /> セグメンテーションフォールト(SIGSEGV)で中断

入力ファイルが何らかの理由により壊れている場合や、バイナリファイルを読み込んだ場合に、セグメンテーションフォールトで中断することがあります。どのファイルが壊れているかを特定するには、`dvg`の`--vv`オプションを使って、読み込んでいるファイルを表示させてください。
