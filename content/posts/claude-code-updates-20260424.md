---
title: "【Claude Code】v2.1.118 リリースノートまとめ"
date: 2026-04-24T08:01:23+09:00
draft: false
tags: ["claude-code", "vim", "usage", "mcp", "wsl", "auto-mode", "oauth", "custom-theme", "hooks", "plugin"]
categories: ["Claude Code Updates"]
summary: "v2.1.118 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260424/header.png)

## はじめに

2026年4月24日、Claude Code v2.1.118 がリリースされました。OAuth / MCP 周りの Fix が大量に入った回で、加えて Vim ユーザー向けのビジュアルモード、コマンド統合（`/cost` と `/stats` → `/usage`）、Hooks からの MCP ツール直接呼び出しなど、日常操作に効いてくる機能追加も揃っています。

本記事で深掘りするのは次の 2 つ。

- **Hooks が `type: "mcp_tool"` で MCP ツールを直接呼び出せるように** — フック内から外部ツール統合が素直に書ける
- **`/cost` と `/stats` が `/usage` に統合** — 使用状況関連の情報が単一コマンドに集約（`/cost` / `/stats` は typing shortcut として残存）

OAuth / MCP 認証系の Fix は 10 件近く入っていて、これまで引っかかっていたケース（expires_in 欠落で毎時再認証、macOS キーチェーンの race、ログイン中に `CLAUDE_CODE_OAUTH_TOKEN` で詰まる）が軒並み潰されています。

## 注目アップデート深掘り

### 1. Hooks が MCP ツールを直接呼べるようになった

![Hooks に mcp_tool type が追加](/images/claude-code-updates-20260424/hooks-mcp-tool.png)

公式リリースノートより（原文）:

> Hooks can now invoke MCP tools directly via `type: "mcp_tool"`

> **Hooks とは？**
> Claude Code のライフサイクルイベント（`PreToolUse`、`PostToolUse`、`Stop`、`SubagentStop`、`UserPromptSubmit` など）に対して、ユーザー定義の処理を差し込める仕組み。通常はシェルコマンドを実行する形式で登録します。

これまで Hooks の `type` はシェルコマンド実行を前提としていました。v2.1.118 では `type: "mcp_tool"` が追加され、**Hooks の定義から直接 MCP ツールを起動できる**ようになります。

#### 何が嬉しいか

フックからシェル経由で MCP ツールを叩きたい場合、従来は `mcp-cli` 相当のラッパーをシェルコマンドとして呼ぶ必要がありました。`type: "mcp_tool"` を使えば、シェルを経由せずにフック設定から MCP ツール名と引数を指定して呼び出せます。フックのイベント発火時に、登録済みの MCP サーバに対して直接アクション（通知、ログ記録、外部システム更新など）を流し込めるようになるイメージです。

具体的な設定形式の詳細は、`~/.claude/settings.json` の `hooks` セクションや Claude Code ドキュメントを参照してください（本リリースで新設された `type` なので、利用時は公式ドキュメントで最新のスキーマを確認するのが確実）。

---

### 2. `/cost` と `/stats` が `/usage` に統合

![/usage コマンドへの統合](/images/claude-code-updates-20260424/usage-merge.png)

公式リリースノートより（原文）:

> Merged `/cost` and `/stats` into `/usage` — both remain as typing shortcuts that open the relevant tab

#### 整理内容

v2.1.118 で `/usage` コマンドが導入され、そこにコスト情報と統計情報がタブ構成で集約されました。旧コマンドの `/cost` と `/stats` は **typing shortcut として残り、それぞれ対応するタブを開く**挙動に変わっています。既存ユーザーが `/cost` と打ち慣れていても、そのまま使い続けられる設計です。

地味ですが、これまで「コストだけ見たいのか、統計だけ見たいのか」を意識してコマンドを選んでいた部分が、`/usage` で一本化されました。タブ切り替えで両方を並べて確認できるため、チーム利用や個人の利用状況のレビュー時に使いやすくなります。

---

## 実用的な活用ポイント

### Vim ビジュアルモード対応

`v`（ビジュアルモード）と `V`（ビジュアルラインモード）が追加されました。selection、operators、visual feedback 込みで実装されているとのことで、Vim 派にとってはテキスト操作時の違和感が減る方向の変更です。

### カスタムテーマ

`/theme` から名前付きカスタムテーマを作成・切り替えできるようになりました。`~/.claude/themes/` 配下の JSON を手編集する方法も選択可能。**プラグインからも `themes/` ディレクトリでテーマを同梱できる**ため、チーム標準のテーマをプラグイン経由で配布する運用も可能です。

### WSL で Windows 側の managed settings を継承

`wslInheritsWindowsSettings` ポリシーキーを有効にすると、WSL 環境で Windows 側の managed settings を継承できるようになりました。組織で Windows 側に managed settings を配布しているチームは、WSL 側の設定二重管理を減らせます。

### Auto Mode のカスタマイズ

`autoMode.allow` / `autoMode.soft_deny` / `autoMode.environment` に `"$defaults"` を含めておくと、built-in ルールを**置き換える**のではなく**並列に追加**する形でカスタムルールを書けるようになりました。これまで built-in ルールを活かしたまま追加したいケースで、設定が書きづらい問題が解消されます。加えて、auto mode の opt-in プロンプトに「Don't ask again」オプションが追加されました。

### `DISABLE_UPDATES` 環境変数

`DISABLE_AUTOUPDATER` より強く、**手動 `claude update` も含めて全ての更新パスをブロック**する環境変数が追加されました。エンタープライズ環境でバージョン固定を厳しく求められるケース向け。

### `claude plugin tag`

プラグイン用のリリース用 git タグをバージョン検証付きで作成できるコマンドが追加されました。プラグイン作者向け機能。

### OAuth / MCP 系 Fix（抜粋）

これまで詰まりやすかった箇所が軒並み修正されています。

- MCP サーバの OAuth レスポンスに `expires_in` がないと毎時再認証が必要だった問題
- macOS keychain の race で MCP トークン更新が別トークンを上書きし「Please run /login」が出る問題
- MCP OAuth refresh でクロスプロセスロックが効かず競合する問題
- `CLAUDE_CODE_OAUTH_TOKEN` で起動したセッションで `/login` が無効化される問題（env token が clear されて disk credentials が効くように）
- `~/.claude/.credentials.json` が Linux/Windows で crash save により破損する問題
- `/mcp` メニューで `headersHelper` 設定時に OAuth の Authenticate / Re-authenticate が隠れる問題

MCP サーバを複数運用しているチームは、今回の Fix 群でアップデートの価値が大きい回です。

---

## 全変更点一覧

| カテゴリ | 変更内容 |
|---|---|
| **Feature** | Vim visual mode (`v`) / visual-line mode (`V`) 対応 |
| **Feature** | `/usage` コマンド導入。`/cost` と `/stats` を統合（両者は typing shortcut として残存） |
| **Feature** | `/theme` で名前付きカスタムテーマを作成・切り替え。`~/.claude/themes/` JSON も手編集可。plugin から `themes/` で配布可 |
| **Feature** | Hooks が `type: "mcp_tool"` で MCP ツールを直接呼び出せる |
| **Feature** | `DISABLE_UPDATES` 環境変数追加。`DISABLE_AUTOUPDATER` より強く、手動 update も含めて全ブロック |
| **Feature** | `wslInheritsWindowsSettings` ポリシーキーで WSL が Windows 側 managed settings を継承 |
| **Feature** | `autoMode.allow`/`soft_deny`/`environment` に `"$defaults"` を含めて built-in と並列にカスタムルール追加可能 |
| **Feature** | auto mode opt-in プロンプトに「Don't ask again」オプション |
| **Feature** | `claude plugin tag` コマンド追加（バージョン検証付きで git タグを作成） |
| **Improvement** | `--continue` / `--resume` が `/add-dir` で現ディレクトリを追加したセッションも対象に |
| **Improvement** | `/color` が Remote Control 接続時に claude.ai/code と session accent color を同期 |
| **Improvement** | `/model` picker が `ANTHROPIC_BASE_URL` カスタムゲートウェイ使用時に `ANTHROPIC_DEFAULT_*_MODEL_NAME`/`_DESCRIPTION` の override を反映 |
| **Improvement** | auto-update 時にプラグインの version 制約で skip された場合、`/doctor` と `/plugin` Errors タブに表示 |
| **Fix** | `/mcp` メニューで `headersHelper` 設定サーバの OAuth Authenticate/Re-authenticate が隠れる問題 |
| **Fix** | HTTP/SSE MCP サーバでカスタムヘッダがある場合、transient 401 後に「needs authentication」で固まる問題 |
| **Fix** | MCP サーバの OAuth レスポンスに `expires_in` が無いと毎時再認証が発生する問題 |
| **Fix** | MCP step-up authorization で、既にトークンが持っているスコープを名指しされた 403 `insufficient_scope` で silent refresh していた問題 |
| **Fix** | MCP サーバの OAuth flow タイムアウト/キャンセル時の unhandled promise rejection |
| **Fix** | MCP OAuth refresh のクロスプロセスロックが競合時に機能していなかった |
| **Fix** | macOS keychain race で MCP トークン更新が OAuth トークンを上書きする問題（「Please run /login」の誤表示原因） |
| **Fix** | OAuth token refresh がサーバ側トークン失効時に失敗する問題 |
| **Fix** | Linux/Windows で credential save crash が `~/.claude/.credentials.json` を破損させる問題 |
| **Fix** | `CLAUDE_CODE_OAUTH_TOKEN` で起動したセッションで `/login` が無効化される問題 |
| **Fix** | 「new messages」スクロール pill と `/plugin` バッジのテキストが読めない問題 |
| **Fix** | `--dangerously-skip-permissions` 起動時に plan acceptance ダイアログが「auto mode」を提示する問題（正: 「bypass permissions」） |
| **Fix** | `Stop` / `SubagentStop` 以外のイベントで agent-type hooks が「Messages are required」エラーで失敗する問題 |
| **Fix** | agent-hook verifier subagent のツール呼び出しで `prompt` hooks が再発火する問題 |
| **Fix** | `/fork` が親会話全文をフォーク毎にディスクに書いていた問題（ポインタ＋読み込み時 hydrate に変更） |
| **Fix** | Alt+K / Alt+X / Alt+^ / Alt+_ でキーボード入力が凍る問題 |
| **Fix** | リモートセッション接続時に `~/.claude/settings.json` の `model` 設定が上書きされる問題 |
| **Fix** | `/` 始まりのファイルパスを貼り付けると typeahead が「No commands match」を出す問題 |
| **Fix** | `plugin install` が既存プラグインに対して、依存が誤バージョンで入っている場合に再解決しない問題 |
| **Fix** | 無効パスや fd 枯渇時の file watcher の unhandled errors |
| **Fix** | JWT refresh 時の transient CCR 初期化 blip で Remote Control セッションが archive される問題 |
| **Fix** | `SendMessage` 経由で resume した subagent が、spawn 時の明示的な `cwd` を復元していなかった問題 |

## まとめ

v2.1.118 は OAuth / MCP 認証系の Fix がまとまって入った回で、MCP サーバを複数使っているチームには実利の大きいアップデートです。特に `expires_in` 欠落時の毎時再認証、macOS keychain の race、プロセス間ロック未動作、`CLAUDE_CODE_OAUTH_TOKEN` 起動時の `/login` 無効化、のあたりは該当ケースを踏んでいた人には効きます。

機能追加では、Hooks の `type: "mcp_tool"` 対応が今後の Hooks の書き方を変えるポテンシャルがある変更。シェル経由で MCP ツールを叩いていたフックを、直接呼び出しに書き換えられます。`/cost` + `/stats` → `/usage` の統合は typing shortcut 維持付きでの無痛移行になっていて、既存の習慣を壊さない配慮が入っています。

運用的には、`DISABLE_UPDATES` がエンタープライズ用途で使える選択肢として増えた点と、WSL の `wslInheritsWindowsSettings` で Windows 側 managed settings を継承できるようになった点が、Windows 環境の組織導入で地味に効いてきそうです。
