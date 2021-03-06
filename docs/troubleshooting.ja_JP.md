## トラブルシューティング

### <a id="no-docopt" /> dvgを実行しようとすると、「ModuleNotFoundError: No module named 'docopt'」といったエラーメッセージが出る。

`docopt`または`docopt-ng`パッケージのインストールが必要です。pipコマンドで`pip3 install docopt-ng`を実行してください。

### <a id="no-fugashi" /> dvgを実行しようとすると 「ModuleNotFoundError: No module named 'fugashi'」といったエラーメッセージが出る。

pipコマンドで`pip3 install dvg[ja]`のように`[ja]`をつけて再インストールしてください。 

### <a id="command-not-found" /> dvgを実行しようとすると 「dvg: command not found」といったエラーメッセージが出る。

`dvg`の実行ファイルにPATHが通っていないようです。

Windowsを使っている場合は、システムの詳細設定→環境変数から、PATH変数を確認してください。
`C:\Users\<username>\AppData\Local\Programs\Python\Python39\Scripts\` (パスは利用しているPythonのバージョンによって異なります）が含まれるようにしてください。

macOSを使っている場合は、`.zprofile`のPATH変数を確認してください。
`~/Python/3.8/bin` (パスは利用しているPythonのバージョンによって異なります）が含まれるようにしてください。

Ubuntuを使っている場合は、`~/.profile` や `~/.bashrc` 等のシェル設定ファイルでのPATH変数を確認してください。
`~/.local/bin` が含まれるようにしてください。

何らかの理由により、環境変数PATHを設定したくない場合には、次のように実行することもできます。

```sh
python3 -m dvg dvg ...  # dvgスクリプトを実行
```

```sh
python3 -m dvg dvgi ...  # dvgiスクリプトを実行
```

### <a id="none-of-pytorch" /> dvgを実行中に 「None of PyTorch, TensorFlow >= 2.0, or Flax have been found. ...」という警告メッセージが表示される。

インストールの説明にあるPyTorchのインストールを行ってください。

### <a id="cp932" /> dvgを実行中に「UnicodeEncodeError: 'cp932' codec can't encode character ...」とっいたエラーメッセージが出る。

ファイルの文字コードに関するエラーです。Windows上で実行している場合は「NKFのインストール」を行ってみてください。
