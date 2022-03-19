## Windowsでのインストール

Pythonのバージョン`3.8`から`3.10`までに対応しています。

![](images/win-pdftotext.png)

(1) `dvg`をインストール

```sh
pip install wheel
pip install dvg[ja]
```

(2) NKFをインストール **(推奨)**

**文字コードがUTF-8のテキストファイルも検索対象にするには、NKFをインストールしてください。**
(いわゆるShiftJISのテキストファイルと、UTF-8のテキストファイルが混在しているときに、NKFを用いることで、文字コードを判別して読み込みます。)

[ネットワーク用漢字コード変換フィルタ シフトJIS,EUC-JP,ISO-2022-JP,UTF-8,UTF-16](https://www.vector.co.jp/soft/win95/util/se295331.html)
からダウンロードして展開したディレクトリ「vc2005 > win32(98,Me,NT,2000,XP,Vista,7)Windows-31J」の中にあるファイル`nkf32.exe`を利用します。

dvgのbinディレクトリを、DOSプロンプトなどで次を実行することで確認してください。

```sh
dvg --bin-dir
```

このディレクトリに、先の`nkf32.exe`をコピーしてください。

(3) pdftotextをインストール **（任意)**

PDFファイルを検索対象としたい場合には、`poppler`をインストールしてください。

[Chocolatey](https://chocolatey.org/)を利用している場合には、Popplerを次でインストールしてください。

```
choco install poppler
```

Popplerを手動でインストーする場合には、まず、Popplerを次のページからダウンロードして展開してください。

https://blog.alivate.com.au/poppler-windows/

次に、展開した先の、`pdftotext.exe`があるディレクトリ（例えば、展開した先が "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0" なら "C:\Users\toshihiro\apps\poppler-0.68.0_x86\poppler-0.68.0\bin\" )にPATHを通してください。

DOSプロンプト等から、pdftotextを実行できることを確認してください。

