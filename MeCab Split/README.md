# Alteryx Janapnes Tokeninze Tool
Alteryxで日本語形態素解析を行うためツール

## Requirements
事前にMecabのインストールを行う必要があります。
64bit版Mecabは以下からダウンロードしてください。

- [MeCab 0.996 64bit version](https://github.com/ikegami-yukino/mecab/releases)

Pythonから利用するために、システム環境変数のPathにインストール先のbinフォルダを追加してください。
デフォルトでは、"C:\Program Files\MeCab\bin\"となっています。

環境変数の追加方法については以下をご参照ください。

- [Windows 環境変数 Path の設定方法](http://next.matrix.jp/config-path-win7.html)

## How to install
ソースコードからインストールする場合は、全体をzipファイルとして圧縮したのち拡張子を"yxi"に変更します。
yxi形式のファイルはReleaseからダウンロード可能です。

yxiファイルからインストールすると、以下ツールがParseカテゴリに追加されます。

- MeCab Split

## How to use
本ツールは分解した形態素を縦持ちの形式で返すため、各レコードに一意なIDを事前に振っておく必要があります。
これにはRecord IDツールをご利用ください。

- Target Fieldには形態素解析の対象となる日本語が含まれる列を選択します
- Record ID Fieldには一意なIDの列を選択します