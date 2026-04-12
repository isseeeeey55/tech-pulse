---
title: "【Claude Code】v2.1.94 リリースノートまとめ"
date: 2026-04-08T08:01:15+09:00
draft: false
tags: ["claude-code", "amazon-bedrock", "slack", "plugins", "hooks", "cjk", "vscode"]
categories: ["Claude Code Updates"]
summary: "v2.1.94 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260408/header.png)

## はじめに

Claude Code v2.1.94 がリリースされました。Amazon Bedrock対応、デフォルトeffortレベルのhigh化、CJKテキストの文字化け修正など、計25項目の変更が含まれています。

## 注目アップデート深掘り

### Amazon Bedrock対応

![Bedrock対応セットアップフロー](/images/claude-code-updates-20260408/bedrock-setup-flow.png)

環境変数 `CLAUDE_CODE_USE_MANTLE=1` を設定するだけで、Amazon Bedrock経由でClaude Codeを利用できるようになりました。

```bash
# Bedrock経由での利用を有効化
export CLAUDE_CODE_USE_MANTLE=1

# あとは通常どおり起動するだけ
claude
```

> **Mantleとは？**
> AWSがBedrock基盤として提供しているインフラ層の名称です。既存のAWS認証情報（IAMロール、AWS SSO等）をそのまま使えるため、別途APIキーを管理する必要がなくなります。

AWS環境で運用しているチームにとっては、VPC内プライベート接続やCloudTrailでの監査ログ、KMS暗号化といったエンタープライズ要件を満たしたまま、Claude Codeを使えるようになった点が大きいです。CI/CDパイプラインでIAMロールを使っている場合、追加の認証設定なしで組み込めます。

```bash
# CI/CD環境での利用例（IAMロール認証）
export CLAUDE_CODE_USE_MANTLE=1
export AWS_REGION=us-east-1
claude --print "このPRの変更点をレビューして"
```

なお、Bedrock経由でSonnet 3.5 v2を呼び出す際の推論プロファイルIDが修正されるバグフィックスも同時に入っています。

### デフォルトeffortレベルのhigh化

API-key、Bedrock/Vertex/Foundry、Team、Enterpriseユーザーのデフォルトeffortレベルが `medium` から `high` に変更されました。

```bash
# 従来の手動切替は引き続き可能
/effort medium  # コスト重視で下げたい場合
/effort high    # デフォルト（v2.1.94〜）
```

> **effortレベルとは？**
> Claude Codeが回答を生成する際の推論の深さを制御するパラメータです。highにすると、より複雑なタスクで精度が上がる一方、トークン消費も増えます。`/effort` コマンドで切り替えられます。

体感としては、コード生成やリファクタリングの精度が上がるケースが多いはずです。トークン消費が気になる場合は `/effort medium` で戻せます。

### CJKテキストの文字化け修正

stream-jsonの入出力で、UTF-8シーケンスがチャンク境界で分割された際にCJK（日本語・中国語・韓国語）やマルチバイト文字が `U+FFFD`（�）に化ける問題が修正されました。

日本語環境でClaude Codeを使っている場合、長い出力の途中で文字化けが発生するケースがあった方は、このバージョンで解消されているはずです。

## 実用的な活用ポイント

**Bedrock対応の試し方**: まずは `export CLAUDE_CODE_USE_MANTLE=1` を `.bashrc` や `.zshrc` に追加するだけで試せます。Bedrockのモデルアクセス許可が事前に必要なので、AWSコンソールのBedrock設定で対象モデルを有効化しておいてください。

**プラグイン開発者向け**: スキルの呼び出し名がディレクトリ名ではなくfrontmatterの `name` フィールドに基づくよう変更されました。インストール方法によって呼び出し名が変わる問題が解消されています。`keep-coding-instructions` フィールドや `hookSpecificOutput.sessionTitle` の追加もあるので、プラグインを自作している方はリリースノートを確認してください。

**VS Code利用者**: セッション起動時のサブプロセス処理が軽量化されたほか、`settings.json` のパース失敗時に警告バナーが出るようになりました。パーミッション設定が効いていないのに気づけなかった問題の対策です。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Amazon Bedrock対応 | `CLAUDE_CODE_USE_MANTLE=1` でBedrock経由の利用が可能に |
| Feature | デフォルトeffortレベル変更 | API-key/Bedrock/Vertex/Team/Enterpriseユーザーのデフォルトをmedium→highに |
| Improvement | Slack MCP表示改善 | send-message時にコンパクトな `Slacked #channel` ヘッダーを表示 |
| Improvement | keep-coding-instructions対応 | プラグイン出力スタイル用のfrontmatterフィールド追加 |
| Improvement | sessionTitleフック対応 | `UserPromptSubmit` フックで `hookSpecificOutput.sessionTitle` が利用可能に |
| Improvement | スキル呼び出し名の安定化 | プラグインスキルの呼び出し名がディレクトリ名ではなくfrontmatter `name` に基づくよう変更 |
| Improvement | --resume改善 | 他のworktreeからのセッション再開が直接可能に（`cd` コマンドの表示ではなく） |
| Fix | レートリミット応答の改善 | 429応答で長いRetry-Afterが返った際にエージェントがスタックする問題を修正 |
| Fix | macOSログイン修正 | キーチェーンがロック時にConsoleログインが無言で失敗する問題を修正。`claude doctor` で診断可能に |
| Fix | プラグインスキルフック修正 | YAMLフロントマターで定義されたフックが無視される問題を修正 |
| Fix | CLAUDE_PLUGIN_ROOT修正 | 未設定時に "No such file or directory" で失敗する問題を修正 |
| Fix | プラグインルートパス修正 | `${CLAUDE_PLUGIN_ROOT}` がlocal-marketplaceプラグインで誤ったディレクトリに解決される問題を修正 |
| Fix | スクロールバック修正 | 長時間セッションで同じdiffが繰り返し表示される問題、空白ページの問題を修正 |
| Fix | 複数行プロンプト修正 | 折り返し行が `❯` キャレットの下にインデントされる問題を修正 |
| Fix | Shift+Space修正 | 検索入力でスペースの代わりに "space" という文字列が挿入される問題を修正 |
| Fix | tmuxハイパーリンク修正 | xterm.jsベースターミナル（VS Code, Hyper, Tabby）内のtmuxでリンクが2タブ開く問題を修正 |
| Fix | alt-screen描画修正 | スクロール中のコンテンツ高さ変更でゴーストラインが残る問題を修正 |
| Fix | FORCE_HYPERLINK修正 | settings.jsonのenvで設定した値が無視される問題を修正 |
| Fix | ターミナルカーソル修正 | ダイアログのタブ選択時にネイティブカーソルが追従しない問題を修正（スクリーンリーダー対応） |
| Fix | Bedrock Sonnet 3.5 v2修正 | `us.` 推論プロファイルIDを使用するよう修正 |
| Fix | SDK/printモード修正 | ストリーム中断時に部分的なアシスタント応答が会話履歴に保存されない問題を修正 |
| Fix | CJKテキスト修正 | UTF-8シーケンスのチャンク分割でマルチバイト文字がU+FFFDに化ける問題を修正 |
| VS Code | セッション起動の軽量化 | コールドオープン時のサブプロセス処理を削減 |
| VS Code | ドロップダウン修正 | キーボード操作中にマウス位置で誤った項目が選択される問題を修正 |
| VS Code | settings.jsonパース警告 | パース失敗時に警告バナーを表示（パーミッション設定の未適用を防止） |

## まとめ

Bedrock対応とeffortレベルのデフォルト変更が目玉です。Bedrock対応は環境変数1つで試せるので、AWS環境がある方はすぐに試してみてください。バグ修正も粒度の細かいものが多く、特にCJKテキストの文字化け修正とtmux内のハイパーリンク修正は、日本語環境・ターミナルマルチプレクサ環境での使い勝手を地味に改善してくれます。
