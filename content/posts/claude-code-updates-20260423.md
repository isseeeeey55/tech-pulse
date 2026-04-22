---
title: "【Claude Code】v2.1.117 リリースノートまとめ"
date: 2026-04-23T08:01:40+09:00
draft: false
tags: ["claude-code", "bfs", "ugrep", "subagent", "mcp", "opentelemetry", "observability", "plugin", "session-management", "performance", "grep", "glob"]
categories: ["Claude Code Updates"]
summary: "v2.1.117 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260423/header.png)

## はじめに

2026年4月23日、Claude Code v2.1.117 がリリースされました。パフォーマンス面と観測性まわりの地味だが効いてくる改善が中心で、Fix も多い回です。

本記事で深掘りするのは次の 2 つ。

- **ネイティブビルド (macOS/Linux) の Glob/Grep が bfs/ugrep ベースに** — ツールラウンドトリップを省いて検索を高速化
- **Forked subagents を external build でも有効化可能に** — 環境変数 `CLAUDE_CODE_FORK_SUBAGENT=1` で ON

他に、`/model` 選択がセッションをまたいで永続化、`/resume` の stale セッション自動サマライズ、OpenTelemetry の属性拡張、Opus 4.7 の `/context` 計算が 1M トークンに修正、など実務に効く修正が並んでいます。

## 注目アップデート深掘り

### 1. ネイティブビルドでの Glob/Grep が bfs/ugrep ベースに

![Glob/Grep が Bash 経由の bfs/ugrep に切り替わる様子](/images/claude-code-updates-20260423/native-search.png)

公式リリースノートより（原文）:

> Native builds on macOS and Linux: the `Glob` and `Grep` tools are replaced by embedded `bfs` and `ugrep` available through the Bash tool — faster searches without a separate tool round-trip (Windows and npm-installed builds unchanged)

ポイントは「ネイティブビルド（macOS/Linux）限定」「bfs/ugrep が Bash ツール経由で呼べるようになった」「別ツールとしてのラウンドトリップが省略される」の 3 点です。Windows と npm インストール版のビルドは従来通り。

> **bfs とは？**
> `tavianator/bfs` — `find` 互換のファイル検索ツール。名前は breadth-first search（幅優先探索）に由来。ディレクトリツリーを幅優先で走査するため、浅い階層のマッチを早く返せる。

> **ugrep とは？**
> PCRE2 互換の正規表現をサポートする高速 grep 実装。ripgrep と同系統の高速検索エンジンだが、PCRE2 対応が強みです。

#### 何が改善されたか

従来の Glob/Grep ツールは、Claude Code の内部ツールとして独立した実装を呼び出していました。今回の変更で、ネイティブビルド環境では bfs/ugrep のバイナリが同梱され、Bash ツール経由で直接呼び出されるようになります。この結果、ツール呼び出しのためのラウンドトリップ（エージェント ⇄ ツール層のやり取り）が 1 回減り、大規模コードベースでの検索レスポンスが体感で速くなります。

具体的な数値は公式リリースノートに記載がないため、手元のリポジトリで実測して確認するのが確実です。

#### 使い方は変わらない

エージェントから見たインタフェースは従来通りです。Glob や Grep をエージェントに使わせる書き方は何も変わりません。ネイティブビルドを使っていれば、自動的に bfs/ugrep 経由の呼び出しに切り替わります。

```text
# 従来どおり
「この関数の呼び出し箇所を全部探して」
「src 配下の全ての .ts ファイルを列挙して」
```

#### どのビルドを使っているかの確認

`claude --version` の出力や `which claude` の結果で、ネイティブビルド（Homebrew などで入れたもの）か npm インストール版かを確認できます。Homebrew 版 / DMG 版のようなネイティブビルドであれば今回の改善の恩恵を受けます。

---

### 2. Forked subagents が external build でも有効化可能に

公式リリースノートより（原文）:

> Forked subagents can now be enabled on external builds by setting `CLAUDE_CODE_FORK_SUBAGENT=1`

> **Forked subagents とは？**
> メインエージェントからプロセスを fork して並列にサブエージェントを動かす仕組み。コンテキストを独立させた並列タスク処理に使われます。これまで一部のビルドでは無効化されていました。

#### 有効化方法

環境変数を 1 つ立てるだけです。

```bash
$ export CLAUDE_CODE_FORK_SUBAGENT=1
$ claude
```

ドキュメントに記載されている設定ファイル上の特別なスキーマは存在せず、既存の `agents/` 下の subagent 定義がそのまま fork 方式で動くようになります。別途 agent を定義したい場合、`--agent` で起動するエージェント frontmatter の `mcpServers` が、main-thread のエージェントセッションでもロードされるようになった改善（こちらも v2.1.117）と合わせて使うと、MCP サーバ構成も agent 側に寄せやすくなります。

#### 使いどころ

fork 方式のサブエージェントは、親エージェントとコンテキストが分離されるため、以下のような場面で素直に使えます。

- **並列タスク**: リポジトリ全体の調査を複数のサブエージェントで分担
- **コンテキスト汚染の回避**: 大量の検索結果を別のサブエージェントに任せて、親のコンテキストを温存
- **独立した権限セットでの実行**: サブエージェント側で別の MCP サーバや権限を持たせる

---

## 実用的な活用ポイント

### `/model` の永続化と起動時ヘッダー

今回のリリースで `/model` の選択がセッションをまたいで永続化されるようになりました。プロジェクト側で別モデルが pin されている場合でも、個人の選択が優先されます。起動時のヘッダーには、有効なモデルがプロジェクトまたは managed-settings の pin 由来の場合にその旨が表示されます。

複数リポジトリで異なるモデルを使いたい開発者、Opus と Sonnet を気分で切り替える運用のどちらにも効く変更です。

### `/resume` の自動サマライズ

長時間動かしていた大きなセッションを `/resume` で再開しようとすると、読み直す前にサマライズを提案するようになりました。これは既に `--resume` で入っていた挙動が `/resume` コマンドにも揃った形。巨大セッションを開く際の起動時間短縮に効きます。

### OpenTelemetry 属性の拡張

observability プラットフォームに Claude Code のテレメトリを流している場合、以下の属性追加が入っています。

- `user_prompt` イベントに `command_name` と `command_source` が追加（スラッシュコマンドの識別）
- `cost.usage` / `token.usage` / `api_request` / `api_error` に `effort` 属性が追加（モデルが effort レベル対応のとき）
- カスタム/MCP コマンド名は `OTEL_LOG_TOOL_DETAILS=1` が無い限り redacted

コスト分析ダッシュボードで effort 別のトークン消費を出すと、high / medium / low の効き具合が見えるようになります。

### Opus 4.7 の `/context` 計算修正

地味ですが効く Fix。Opus 4.7 セッションで `/context` が 200K 基準で計算されていて、実際には 1M コンテキストなのに早期 autocompact が発動していた問題が修正されました。Opus 4.7 を常用しているなら、体感で autocompact の発動頻度が下がるはずです。

### Pro/Max の Opus 4.6 / Sonnet 4.6 のデフォルト effort が high に

Pro/Max 契約者は、これまで medium がデフォルトだった Opus 4.6 / Sonnet 4.6 で、デフォルトが high に変更されました。体感の思考深度は上がる代わりに、プロンプトあたりのトークン消費が増えます。効率重視なら明示的に medium / low を指定する運用も検討できます。

---

## 全変更点一覧

| カテゴリ | 変更内容 |
|---|---|
| **Feature** | Forked subagents が external build で有効化可能に（`CLAUDE_CODE_FORK_SUBAGENT=1`） |
| **Feature** | Agent frontmatter の `mcpServers` が `--agent` 経由の main-thread セッションでもロード |
| **Feature** | Native builds (macOS/Linux) で Glob/Grep が bfs/ugrep ベースに切り替え |
| **Improvement** | `/model` 選択がセッションをまたいで永続化。起動ヘッダーに pin 由来を表示 |
| **Improvement** | `/resume` が stale/large セッションのサマライズを提案 |
| **Improvement** | ローカル MCP と claude.ai MCP の並列接続が既定に。起動が高速化 |
| **Improvement** | `plugin install` が未インストール依存を自動で補完。marketplace add で auto-resolve |
| **Improvement** | Managed-settings の `blockedMarketplaces` / `strictKnownMarketplaces` を install/update/refresh/autoupdate 全てに適用 |
| **Improvement** | Advisor Tool に experimental ラベル・学習用リンク・起動通知を追加 |
| **Improvement** | `cleanupPeriodDays` の retention sweep が `~/.claude/tasks/`、`shell-snapshots/`、`backups/` も対象に |
| **Improvement** | OpenTelemetry に `command_name` / `command_source` / `effort` 属性を追加 |
| **Improvement** | Windows で `where.exe` 実行ファイル検索をプロセス単位でキャッシュ |
| **Improvement** | Pro/Max の Opus 4.6 / Sonnet 4.6 のデフォルト effort が `high` に |
| **Fix** | Plain-CLI OAuth で access token がセッション中に expire した際「Please run /login」で死ぬ問題を、401 での reactive refresh で修正 |
| **Fix** | `WebFetch` が巨大 HTML ページでハングする問題（変換前に truncate） |
| **Fix** | プロキシが HTTP 204 を返したときに TypeError になる問題 |
| **Fix** | `CLAUDE_CODE_OAUTH_TOKEN` で起動して token が expire した際、`/login` が無効化される問題 |
| **Fix** | プロンプト入力の undo (`Ctrl+_`) が、打鍵直後に効かない／状態が飛ぶ問題 |
| **Fix** | Bun 実行時に `NO_PROXY` がリモート API リクエストに効かない |
| **Fix** | 遅い接続でキー名が text で coalesce 到着する際の spurious escape/return |
| **Fix** | SDK `reload_plugins` が全ユーザ MCP サーバに直列再接続していた |
| **Fix** | Bedrock の application-inference-profile が Opus 4.7 + thinking disabled で 400 |
| **Fix** | MCP `elicitation/create` が print/SDK モードでサーバ接続途中に auto-cancel |
| **Fix** | サブエージェントがメインと別モデルで動く場合、ファイル読み込みが malware 警告を誤検知 |
| **Fix** | バックグラウンドタスク存在時のアイドル再描画ループ（Linux でメモリ増大） |
| **Fix** | [VSCode] 大規模 marketplace が複数あると「Manage Plugins」パネルが壊れる |
| **Fix** | Opus 4.7 セッションで `/context` が 200K 基準で計算されていた問題（1M が正） |

## まとめ

方向性としては、パフォーマンス（ネイティブビルドの検索高速化、並列 MCP 接続）、柔軟性（Forked subagents の有効化条件緩和、`/model` 永続化）、観測性（OpenTelemetry 属性拡張）の 3 軸で地味ながら効いてくる改善が入りました。Fix の多さも目を引く回で、特に Opus 4.7 の `/context` 計算修正と OAuth の 401 reactive refresh は、日常で引っかかっていた人には体感差が大きい変更です。

既存ユーザの実務目線で優先度をつけるなら、まずネイティブビルドを使っているかを確認して bfs/ugrep の恩恵を得ること、次に Opus 4.7 ユーザなら `/context` 修正で autocompact 挙動が変わっている点をチェック、というあたりが現実的です。Forked subagents の external build 対応は、該当するビルド環境で動かしているチーム向けの選択肢が増えた形です。
