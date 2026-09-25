---
title: "【Codex CLI】rust-v0.157.0 リリースノートまとめ"
date: 2026-09-26T08:01:46+09:00
draft: true
tags: ["codex", "gpt-6", "sol", "luna", "amazon-bedrock", "fullscreen", "transcript", "background-server", "fork", "import", "network-policy", "proxy", "websocket", "http", "mcp", "agent", "guardian", "sqlite", "codex-doctor", "terminal", "unicode", "tmux", "file-upload", "realtime", "tui", "sandbox", "oauth", "voice"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.157.0 のCodex CLIリリースノートまとめ"
---

# OpenAI Codex CLI rust-v0.157.0 リリース解説

## はじめに

OpenAI Codex CLI の rust-v0.157.0 がリリースされました。このバージョンでは、次世代モデル GPT-6 Sol と Luna のサポート、UI/UX の大幅な改善、そしてネットワークポリシーやセキュリティ強化など、多岐にわたるアップデートが含まれています。

主な変更点は以下の通りです：

- **GPT-6 Sol および Luna モデルの追加**（Amazon Bedrock サポート含む）
- **フルスクリーン転写のデフォルト有効化**と Shift-click による選択拡張機能
- **バックグラウンドサーバーの自動起動機能**のデフォルト有効化
- **会話のフォーク機能**（`f` ショートカット）の追加
- **`/import` コマンド**のリモートセッション・バックグラウンドサーバーセッション対応
- **ターミナルレンダリングの改善**（Unicode 箇条書き、チェックボックス、数式表記）
- **ネットワークポリシー適用の徹底**（リダイレクト、WebSocket を含む全通信）
- **プロキシルーティングの修正**（リアルタイム接続、Web 検索）

本記事では、これらのアップデートの中から特に重要な変更を深掘りし、日常的な開発ワークフローへの影響と活用方法を解説します。

## 注目アップデート深掘り

### GPT-6 Sol と Luna モデルの追加

今回のリリースで最も注目すべき機能は、新世代モデル GPT-6 Sol と Luna のサポートです。リリースノートには「Added GPT-6 Sol and Luna, including Amazon Bedrock support and migration prompts for older models」と記載されており、これらのモデルは Amazon Bedrock 経由でも利用可能になっています。

この変更が重要な理由は、旧モデルからの移行プロンプトが含まれている点です。これにより、既存のワークフローを GPT-6 シリーズへスムーズに移行できる配慮がなされています。また、Amazon Bedrock サポートにより、AWS インフラストラクチャを活用している組織は、既存のセキュリティポリシーとコンプライアンス要件を維持しながら最新モデルを導入できます。

> **Note:** Codex CLI では、モデル選択は会話ごとに行うことができ、特定のユースケースに応じて最適なモデルを使い分けることが可能です。

リリースノートには「Update model catalog descriptions and GPT-5.6-Sol priority」「Remove the `ultrafast` service tier from `gpt-5.6-sol`」といった変更も含まれており、モデルカタログ全体の整理と優先順位の調整が行われています。これらの変更により、より適切なモデル選択が可能になり、従来の GPT-5.6-Sol の ultrafast ティアは削除されています。

### ネットワークポリシー適用の全面強化

セキュリティとコンプライアンスの観点で重要なのが、ネットワークポリシー適用の徹底です。今回のリリースでは、「Enforced network restrictions across redirects and ongoing HTTP and WebSocket traffic, including cancellation when policy changes revoke access」という大きな改善が含まれています。

この変更により、HTTP リクエストや WebSocket 通信においてリダイレクトが発生した場合でも、ネットワークポリシーが一貫して適用されます。さらに重要なのは、ポリシー変更によってアクセスが取り消された場合、進行中の通信も即座にキャンセルされる点です。これは、動的なセキュリティポリシー管理が必要な企業環境において非常に重要な機能です。

関連する修正として、以下の変更も含まれています：

- 「Fixed configured proxy routing for realtime connections and standalone web search, including search redirects」：リアルタイム接続やスタンドアロン Web 検索におけるプロキシルーティングの修正
- 「Honor configured proxies for realtime WebSocket connections」：リアルタイム WebSocket 接続での設定済みプロキシの尊重
- 「Enforce network policy throughout HTTP and WebSocket requests」：HTTP および WebSocket リクエスト全体へのネットワークポリシー適用

これらの変更により、企業のプロキシ環境や厳格なネットワークポリシー下でも、Codex CLI が安定して動作するようになりました。SRE やインフラエンジニアにとって、ネットワークセグメンテーションやゼロトラストアーキテクチャの実装がより容易になります。

## 実用的な活用ポイント

### 日常の開発ワークフローへの影響

今回のリリースでは、UI/UX の改善により日常的な使い勝手が大きく向上しています。特に「Enabled fullscreen transcripts by default」により、会話履歴がフルスクリーン表示されるようになり、長い会話の追跡が容易になりました。また「Support Shift-click to extend transcript selections」により、Shift キーを押しながらクリックすることでテキスト選択を拡張できるようになり、コードスニペットのコピーがスムーズになります。

バックグラウンドサーバーの自動起動（「Enabled automatic background-server startup for eligible interactive sessions」）がデフォルトで有効化されたことで、セッション開始時の手動設定が不要になり、すぐに作業を開始できます。サーバー設定に互換性がない場合は、リカバリーオプションが提示されます（「with recovery choices when server settings are incompatible」）。

### すぐに試せる Tips

新しい会話フォーク機能を活用すると、他のアプリで開いている会話を素早く複製できます。リリースノートによれば「Added an `f` shortcut to fork conversations open in another app, preserving drafts and queued prompts」とあり、`f` キーを押すだけでドラフトやキュー済みプロンプトを保持したまま会話をフォークできます。

また、`/import` コマンドがリモートセッションやローカルバックグラウンドサーバーセッションで利用可能になりました（「Made `/import` available in remote sessions and local background-server sessions」）。これにより、外部ファイルやコンテキストのインポートがより柔軟に行えます。

### SRE/インフラエンジニア向けの活用シーン

SRE やインフラエンジニアにとって、今回のネットワークポリシー強化は大きな意味を持ちます。「Enforce application network policy throughout embedded Codex startup」により、埋め込み Codex 起動時から一貫したネットワークポリシーが適用されるため、セキュリティ境界が明確になります。

また、「Identify failed SQLite databases in `codex doctor` output」により、`codex doctor` コマンドで SQLite データベースの問題を診断できるようになりました。トラブルシューティング時の初動対応が迅速化されます。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | GPT-6 Sol および Luna モデル追加 | Amazon Bedrock サポートと旧モデルからの移行プロンプトを含む |
| Feature | フルスクリーン転写のデフォルト有効化 | Shift-click によるテキスト選択拡張機能を追加 |
| Feature | バックグラウンドサーバー自動起動 | 対象インタラクティブセッションでデフォルト有効、設定非互換時のリカバリーオプション付き |
| Feature | 会話フォーク機能（`f` ショートカット） | 他のアプリで開いている会話をドラフトとキュー済みプロンプト保持でフォーク |
| Feature | `/import` コマンド対応拡大 | リモートセッションとローカルバックグラウンドサーバーセッションで利用可能に |
| Improvement | ターミナルレンダリング改善 | Unicode 箇条書き、チェックボックス、整列数式、最適化記法のサポート |
| Fix | 音声会話の保持 | スレッド切り替え時にアクティブな音声会話を保持 |
| Fix | 未送信回答の復元 | ターン終了時に未送信の質問回答をコンポーザーに復元、履歴検索を妨げない |
| Fix | tmux マウス設定の尊重 | 自動画面モードで SSH 経由 Terminal.app のネイティブスクロールバックを復元 |
| Fix | プロキシルーティング修正 | リアルタイム接続とスタンドアロン Web 検索（リダイレクト含む）で設定済みプロキシを適用 |
| Fix | ファイルアップロード安定性向上 | 一時的な障害のリトライ追加、アップロードタイムアウトを 5 分に延長 |
| Fix | ネットワーク制限の徹底適用 | リダイレクトおよび進行中の HTTP・WebSocket 通信全体に適用、ポリシー変更時の即時キャンセル |
| Improvement | MCP リクエスト追跡 | トランスポートワーカー間でトレースコンテキストを保持 |
| Improvement | エージェント操作の統合 | `AgentControl` 実装への集約 |
| Improvement | Guardian スレッドコンテキスト | デフォルトで有効化 |
| Improvement | TUI メニュー表記統一 | 説明文言と句読点の標準化 |
| Improvement | `codex doctor` 診断強化 | 失敗した SQLite データベースの識別、ステータス別のパス・URL 色分け |
| Improvement | 環境設定の適用タイミング | ターン境界で継承環境設定を適用、アクティブターン中の環境選択更新を許可 |

## まとめ

rust-v0.157.0 は、新世代モデルのサポート、UI/UX の大幅改善、そしてセキュリティ・ネットワークポリシーの全面強化という三本柱で構成された重要なリリースです。

特に注目すべきは、GPT-6 Sol と Luna の追加により、最新の AI 機能を活用できるようになった点と、ネットワークポリシー適用の徹底により、エンタープライズ環境でのセキュリティ要件に対応できるようになった点です。また、バックグラウンドサーバーの自動起動やフルスクリーン転写のデフォルト有効化など、日常的な使い勝手を向上させる細かな改善も多数含まれています。

変更ログを見ると、100 を超えるコミットが含まれており、エージェント操作の統合、MCP（Model Context Protocol）の改善、Guardian レビュー機能の強化など、内部アーキテクチャの整理も進んでいることがわかります。これらの基盤整備により、今後のさらなる機能拡張が期待できます。

開発者、SRE、インフラエンジニアそれぞれにとって、実用的な価値のあるアップデートが含まれているため、積極的にアップグレードを検討する価値があるリリースと言えるでしょう。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)