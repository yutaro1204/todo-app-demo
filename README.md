# TODO app demo with project-kernel

## project-kernel

自作の Claude Code プラグインです。
与えられたプロジェクトの仕様に基づいて、プロダクト要求仕様書、開発ガイドライン、アーキテクチャ仕様書、テスト仕様書などを生成します。
また、実装指示書を作成することもでき、Claude Code に仕様書に従った実装を行わせることができます。
https://github.com/yutaro1204/project-kernel

## このデモアプリについて

このデモアプリには　project-kernel プラグインが組み込まれています。
そして、これを利用して仕様書の作成と実装を Claude Code に行わせています。

仕様書の生成元となったプロジェクト仕様の定義は PROJECT_SPEC.md に記載されています。
スキル create-development-documents はこのファイルを基に docs ディレクトリ以下に仕様書を生成します。

```bash
# プラグインのパスを指定して Claude Code を起動
$ claude --plugin-dir ./project-kernel

# プラグインのスキルを実行
> /project-kernel:create-development-document
```

実装には create-steering-file スキルと implement-steering-file スキルを利用します。
steering-file は実装指示書のことです。

create-steering-file スキルはこの実装指示書を作成します。
作成した実装指示書は .steerings ディレクトリに作成されます。
実装指示書にはバグ、新規機能、リファクタに分類され、それぞれ bugs, features, refactoring ディレクトリに格納されます。
それぞれには ID が付与され、それがファイル名のプリフィックスになります(e.g. F001)。
実装指示書は templates 配下のテンプレートマークダウンに従って生成されます。

```bash
# create-steering-file に実装してほしい内容を伝える
> /project-kernel:create-steering-file Implement sign-in feature
```

implement-steering-file スキルは実装指示書に従って Claude Code に実装させます。
implement-steering-file スキルに実装したい対応の ID を渡せば、Claude Code はその実装指示書を確認し、実装を開始します。
実装が完了したら、.steerings/README.md の completed の項目に実装済みの対応が記載されます。

```bash
# 実装仕様書の ID を指定して実装をお願いする
> /project-kernel:implement-steering-file F001
```

上記のようなフローを辿れば Claude Code でアプリケーションを開発することができます。
