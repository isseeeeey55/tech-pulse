---
title: "【Codex CLI】rust-v0.157.0 リリースノートまとめ"
date: 2026-09-26T08:01:46+09:00
draft: false
tags: ["codex", "gpt-6", "sol", "luna", "amazon-bedrock", "fullscreen", "transcript", "background-server", "fork", "import", "network-policy", "proxy", "websocket", "http", "mcp", "agent", "guardian", "sqlite", "codex-doctor", "terminal", "unicode", "tmux", "file-upload", "realtime", "tui", "sandbox", "oauth", "voice"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.157.0 のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260926/header.png)

# Codex CLI rust-v0.157.0 リリースノート

## はじめに

OpenAI Codex CLI の rust-v0.157.0 が 2026年9月25日（GitHub リリース日、UTC）に公開されました。GPT-6 Sol と Luna のサポート、UI の改善、ネットワークポリシー適用の強化などが含まれます。Changelog セクションには 126 件の PR が列挙されています。

主な変更点は以下の通りです：

- **GPT-6 Sol および Luna モデルの追加**（Amazon Bedrock サポート含む）
- **フルスクリーンのトランスクリプト表示のデフォルト有効化**と Shift-click による選択拡張機能
- **バックグラウンドサーバーの自動起動機能**のデフォルト有効化
- **会話のフォーク機能**（`f` ショートカット）の追加
- **`/import` コマンド**のリモートセッション・バックグラウンドサーバーセッション対応
- **ターミナルレンダリングの改善**（Unicode 箇条書き、チェックボックス、数式表記）
- **ネットワークポリシー適用の徹底**（リダイレクト、WebSocket を含む全通信）
- **プロキシルーティングの修正**（リアルタイム接続、Web 検索）

本記事では、これらのアップデートの中から特に重要な変更を深掘りし、日常的な開発ワークフローへの影響と活用方法を解説します。

## 注目アップデート深掘り

### GPT-6 Sol と Luna モデルの追加

GPT-6 Sol と Luna が追加されました。リリースノートの原文は「Added GPT-6 Sol and Luna, including Amazon Bedrock support and migration prompts for older models」で、Amazon Bedrock 経由での利用と、旧モデル向けの移行プロンプトを含みます（#47332, #47347）。

リリースノートには「Update model catalog descriptions and GPT-5.6-Sol priority」「Remove the `ultrafast` service tier from `gpt-5.6-sol`」という変更も含まれ、`gpt-5.6-sol` の `ultrafast` サービスティアは削除されました。

### ネットワークポリシー適用の全面強化

Bug Fixes には、「Enforced network restrictions across redirects and ongoing HTTP and WebSocket traffic, including cancellation when policy changes revoke access」という修正が含まれています。

リダイレクトや、進行中の HTTP・WebSocket 通信にもネットワーク制限が適用され、ポリシーの変更でアクセスが取り消された場合は通信がキャンセルされます（#47389, #47407）。

関連する修正として、以下の変更も含まれています：

- 「Fixed configured proxy routing for realtime connections and standalone web search, including search redirects」：リアルタイム接続やスタンドアロン Web 検索におけるプロキシルーティングの修正
- 「Honor configured proxies for realtime WebSocket connections」：リアルタイム WebSocket 接続での設定済みプロキシの尊重
- 「Enforce network policy throughout HTTP and WebSocket requests」：HTTP および WebSocket リクエスト全体へのネットワークポリシー適用

プロキシやネットワークポリシーを設定している環境で Codex を使っている場合に関係する修正です。

## 実用的な活用ポイント

### 日常の開発ワークフローへの影響

フルスクリーンのトランスクリプト表示がデフォルトで有効になり、Shift を押しながらクリックすると選択範囲を広げられるようになりました（#47178, #47414）。

バックグラウンドサーバーの自動起動（「Enabled automatic background-server startup for eligible interactive sessions」）により、対象となる対話セッションではバックグラウンドサーバーが自動で起動します。サーバー設定に互換性がない場合は、復旧の選択肢が提示されます（#47179, #47318）。

### すぐに試せる Tips

他のアプリで開いている会話は、`f` キーでフォークできます。ドラフトとキュー済みのプロンプトは保持されます（#47185）。

また、`/import` コマンドがリモートセッションやローカルバックグラウンドサーバーセッションで利用可能になりました（#47317）。

### SRE/インフラエンジニア向けの活用シーン

Changelog には、埋め込み Codex の起動処理全体で共有のネットワークポリシーを適用する変更（#47411 "Apply shared network policy throughout embedded Codex startup"）や、AWS 認証とテレメトリへのアプリケーションネットワークポリシーの適用（#47408）も含まれます。

また、「Identify failed SQLite databases in `codex doctor` output」（#47358 と合わせて）により、`codex doctor` の出力で失敗した SQLite データベースが示され、パスや URL がチェック結果に応じて色分けされるようになりました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | GPT-6 Sol および Luna モデル追加 | Amazon Bedrock サポートと旧モデルからの移行プロンプトを含む |
| Feature | フルスクリーントランスクリプトのデフォルト有効化 | Shift-click によるテキスト選択拡張機能を追加 |
| Feature | バックグラウンドサーバー自動起動 | 対象インタラクティブセッションでデフォルト有効、設定非互換時のリカバリーオプション付き |
| Feature | 会話フォーク機能（`f` ショートカット） | 他のアプリで開いている会話をドラフトとキュー済みプロンプト保持でフォーク |
| Feature | `/import` コマンド対応拡大 | リモートセッションとローカルバックグラウンドサーバーセッションで利用可能に |
| Improvement | ターミナルレンダリング改善 | Unicode 箇条書き、チェックボックス、整列数式、最適化記法のサポート |
| Fix | 音声会話の保持 | スレッド切り替え時にアクティブな音声会話を保持 |
| Fix | 未送信回答の復元 | ターン終了時に未送信の質問回答をコンポーザーに復元、履歴検索を妨げない |
| Fix | tmux マウス設定の尊重 | tmux のマウス設定を尊重し、自動画面モードで SSH 経由の Terminal.app のネイティブスクロールバックを復元 |
| Fix | プロキシルーティング修正 | リアルタイム接続とスタンドアロン Web 検索（リダイレクト含む）で設定済みプロキシを適用 |
| Fix | ファイルアップロード安定性向上 | 一時的な障害のリトライ追加、アップロードタイムアウトを 5 分に延長 |
| Fix | ネットワーク制限の徹底適用 | リダイレクトおよび進行中の HTTP・WebSocket 通信にも適用、ポリシー変更でアクセスが取り消された場合はキャンセル |
| Improvement | MCP リクエスト追跡 | トランスポートワーカー間でトレースコンテキストを保持 |
| Improvement | エージェント操作の統合 | `AgentControl` 実装への集約 |
| Improvement | Guardian スレッドコンテキスト | デフォルトで有効化 |
| Improvement | TUI メニュー表記統一 | 説明文言と句読点の標準化 |
| Improvement | `codex doctor` 診断強化 | 失敗した SQLite データベースの識別、ステータス別のパス・URL 色分け |
| Improvement | 環境設定の適用タイミング | ターン境界で継承環境設定を適用、アクティブターン中の環境選択更新を許可 |

## まとめ

rust-v0.157.0 では、GPT-6 Sol と Luna（Amazon Bedrock 対応を含む）、フルスクリーントランスクリプトのデフォルト有効化、バックグラウンドサーバーの自動起動、`f` による会話のフォーク、`/import` の対応範囲拡大、ターミナル描画の改善が加わりました。修正では、ネットワーク制限をリダイレクトや進行中の通信にも適用する変更、プロキシルーティング、ファイルアップロードのリトライとタイムアウト延長（5分）などが含まれます。

フルスクリーン表示とバックグラウンドサーバーの自動起動はデフォルトの挙動が変わるため、アップグレード後の表示や起動の挙動を確認してください。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)