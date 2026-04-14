---
title: "【Claude Code】v2.1.108 / v2.1.107 リリースノートまとめ"
date: 2026-04-15T08:01:11+09:00
draft: false
tags: ["claude-code", "prompt-caching", "recap", "slash-commands", "skill-tool", "resume", "memory", "error-messages"]
categories: ["Claude Code Updates"]
summary: "v2.1.108 / v2.1.107 の変更点を解説します。prompt caching TTL の環境変数制御（`ENABLE_PROMPT_CACHING_1H` / `FORCE_PROMPT_CACHING_5M`）、`recap` 機能、Skill tool からの built-in slash command 呼び出し、`/undo` = `/rewind` エイリアス、`/model` 切替警告、エラーメッセージ区別などが追加されました。"
---

![](/images/claude-code-updates-20260415/header.png)

## はじめに

Claude Code の **v2.1.108** と **v2.1.107** が相次いでリリースされました。v2.1.107 は「長時間処理中の thinking hints を早めに表示」1 点のみの軽いリリース、v2.1.108 は prompt caching 周りの制御強化、`recap` 機能、Skill tool からの built-in slash command 呼び出しなどを含む中規模リリースです。

目玉は **prompt caching TTL の環境変数制御** と **`recap` 機能** の 2 つ。特に prompt caching の TTL を 1 時間まで延ばせるようになった点は、同じ context を繰り返し読むタイプのワークフロー（長時間のコードレビューや、同じリポジトリでの連続タスク）で API 料金と応答速度の両面で効きます。

## 注目アップデート深掘り

### Prompt caching TTL の環境変数制御 — 1 時間キャッシュ対応

![Prompt caching TTL 設定の比較](/images/claude-code-updates-20260415/prompt-cache-ttl.png)

Claude Code の prompt caching は従来デフォルトで **5 分 TTL** で動作していましたが、v2.1.108 から **1 時間 TTL** を opt-in で選べるようになりました。対応プロバイダは API キー直叩き、Amazon Bedrock、Google Vertex AI、Microsoft Foundry の 4 系統すべてです。

> **Prompt caching とは？**
> 同じプロンプト接頭辞（システムプロンプト、ツール定義、CLAUDE.md 等）を一定時間キャッシュし、次回のリクエストでは再トークン化せずに再利用することで課金と応答速度を改善する Anthropic API の機能です。Claude Code は起動時・ツール呼び出し時・ユーザー入力ごとに、キャッシュ可能な prefix を自動で認識して利用します。

環境変数は次の 3 つ:

```bash
# 1 時間 TTL を opt-in（API key / Bedrock / Vertex / Foundry すべて対応）
$ export ENABLE_PROMPT_CACHING_1H=1

# 5 分 TTL を強制（1時間がデフォルトになっている環境で元に戻したいとき）
$ export FORCE_PROMPT_CACHING_5M=1

# prompt caching 自体を無効化（デバッグ用途など）
$ export DISABLE_PROMPT_CACHING=1
```

注意点がいくつかあります。

- 従来の `ENABLE_PROMPT_CACHING_1H_BEDROCK` は **deprecated** になりました（まだ動作はしますが、今後は `ENABLE_PROMPT_CACHING_1H` に統一）。
- `DISABLE_PROMPT_CACHING*` で caching を無効化していると、起動時に警告が表示されるようになりました。意図せず無効化したまま運用しているケースに気づきやすくなっています。
- v2.1.108 で、`DISABLE_TELEMETRY` を設定しているサブスクライバが本来 1 時間 TTL を使えるはずなのに 5 分 TTL にフォールバックしてしまう **バグが修正** されました。該当する環境では TTL が実際に長くなります。

1 時間 TTL が効くのは、CLAUDE.md やシステムプロンプト、MCP ツール定義などの**変化しない prefix を同じセッション内で 1 時間以上繰り返し参照する**ケースです。1 日中同じリポジトリに張り付いて作業するタイプの使い方では、API コストがはっきり下がります。

### `recap` 機能 — セッション復帰時のコンテキスト提供

![recap 機能のフロー](/images/claude-code-updates-20260415/recap-flow.png)

長時間の作業を中断して `--resume` や `/resume` でセッションに戻ったとき、Claude が以前の会話を要約して出すための **`recap`** 機能が追加されました。「前回どこまでやっていたか」をクリック一つで思い出せる仕組みで、数日またぎの調査やインシデント対応の引き継ぎで効きます。

呼び出し方は 3 通り:

**1. `/config` で設定して自動起動**

`/config` から `recap` の設定項目を選んで有効化しておくと、セッション復帰時に自動で要約が表示されます。

**2. `/recap` で手動呼び出し**

必要なときだけ手動で呼びたい場合は `/recap` コマンド。

**3. `CLAUDE_CODE_ENABLE_AWAY_SUMMARY=1` で強制**

テレメトリを無効化している環境（`DISABLE_TELEMETRY=1`）では、通常 `recap` は無効化されていますが、`CLAUDE_CODE_ENABLE_AWAY_SUMMARY` を立てると強制的に有効化できます。

```bash
# テレメトリ無効化環境でも recap を使いたい場合
$ export DISABLE_TELEMETRY=1
$ export CLAUDE_CODE_ENABLE_AWAY_SUMMARY=1
$ claude --resume "incident-2026-04-15"
```

特に効くのは、障害対応で「昨日の夜中に調べた仮説、どこまで検証したんだっけ」と次の日に戻ってくるパターン、または複数プロジェクトを並行で回していて各セッションの文脈を素早く取り戻したいときです。

### Built-in slash commands が Skill tool から呼べるように

v2.1.108 のもう一つ地味に重要な変更は、`/init`、`/review`、`/security-review` といった Claude Code 標準の built-in slash commands を、**モデルが Skill tool 経由で自律的に呼び出せる**ようになった点です。

> **Skill tool とは？**
> Claude Code に組み込まれた `Skill` ツールで、マーケットプレイスや `.claude/skills/` ディレクトリに置かれた skill 定義を呼び出します。skill は「名前 + description + 実行内容」をまとめた再利用可能な指示セットで、会話中にモデルが必要に応じて自律的に呼び出すことができます。

これまで `/init` や `/security-review` は人間が明示的に `/コマンド` で呼ぶ必要がありましたが、今後はモデルが「このリポジトリの初期化が必要そうなので `/init` を呼びます」「このコード変更はセキュリティレビューすべきなので `/security-review` を呼びます」と自律判断できるようになります。エージェント的なワークフロー（例: PR 作成前に自動でセキュリティレビューを回す）を組む際の表現力が上がります。

## 実用的な活用ポイント

**エラーメッセージの区別**: v2.1.108 では、サーバー側のレート制限とプランの利用制限が別々に表示されるようになりました。従来は「どちらに引っかかっているのか」を判断しにくかった場面で、オンコール中の切り分けが速くなります。5xx / 529 エラーには `status.claude.com` へのリンクが付くので、障害発生時の外部ステータスページ確認も 1 タップになります。不明なスラッシュコマンドを叩いたときは、近い名前が候補として提示されるようになりました。

**`/model` 切替警告**: セッション途中でモデルを変えると、次のレスポンスで履歴を **uncached で再読込** する必要があります（Claude Code は利用モデルごとにキャッシュが別物のため）。v2.1.108 ではこの挙動を事前に警告してくれるので、長時間セッションの途中での軽率なモデル切替を避けられます。

**`/resume` picker の改善**: デフォルトで現在のディレクトリから起動されたセッションだけを表示するようになりました。`Ctrl+A` で全プロジェクトに切り替え可能です。大量のセッションが蓄積している環境で、目的のセッションに辿り着くのが楽になります。

**`/undo` = `/rewind` エイリアス**: 既存の `/rewind` コマンドに `/undo` という別名が追加されました。入力しやすい方を選べます。

**メモリフットプリント削減**: ファイル read、edit、syntax highlighting 用の **language grammar が on-demand ロード** になりました。大規模リポジトリで様々な言語が混在する環境で、Claude Code 自体のメモリ使用量が下がります。

**v2.1.107 の `thinking hints` 早期表示**: 長時間処理中に、Claude が何を考えているかを示すヒントがより早いタイミングで表示されるようになりました。体感で「止まっている？」と感じる時間が短くなる変更です。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Added | `ENABLE_PROMPT_CACHING_1H` env var | 1 時間 prompt cache TTL に opt-in、API key/Bedrock/Vertex/Foundry 対応 |
| Added | `FORCE_PROMPT_CACHING_5M` env var | 5 分 TTL を明示的に強制 |
| Added | `recap` 機能 | セッション復帰時のコンテキスト要約、`/config` / `/recap` / `CLAUDE_CODE_ENABLE_AWAY_SUMMARY` |
| Added | Built-in slash commands via Skill tool | モデルが `/init` / `/review` / `/security-review` を自律的に呼び出し可能 |
| Added | `/undo` = `/rewind` alias | 既存 `/rewind` の別名 |
| Improved | `/model` 切替時の警告 | 次のレスポンスが uncached で履歴を再読込することを事前警告 |
| Improved | エラーメッセージ区別 | server rate limit vs plan limit、5xx/529 で status.claude.com リンク、不明コマンド近似提案 |
| Improved | メモリフットプリント削減 | ファイル read/edit/syntax highlighting で language grammar を on-demand ロード |
| Fixed | 多数のバグ修正 | `DISABLE_TELEMETRY` で 5 分 TTL fallback、`--resume` 系の session 復元、`/feedback` リトライ ほか |
| v2.1.107 | Thinking hints の早期表示 | 長時間処理中のヒントをより早いタイミングで表示 |

## まとめ

v2.1.108 は **prompt caching TTL の 1 時間対応** と **`recap` 機能** の 2 つが大きめの目玉で、残りはオンコールや長時間セッションで体感が変わる改善とバグ修正が並びます。Bedrock を使っていて `ENABLE_PROMPT_CACHING_1H_BEDROCK` を設定していた環境は、新しい統一変数名 `ENABLE_PROMPT_CACHING_1H` への切り替えを次のアップデート機会で済ませておくと良さそうです。v2.1.107 は thinking hints の表示タイミング改善だけの軽量リリースで、直接設定する項目はありません。
