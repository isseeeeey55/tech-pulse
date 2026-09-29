---
title: "【Codex CLI】rust-v0.158.0 リリースノートまとめ"
date: 2026-09-29T08:02:04+09:00
draft: false
tags: ["codex", "rust-v0.158.0", "tui", "prompt-suggestions", "mcp", "oauth", "websocket", "exec-server", "image-generation", "terminal-approval", "sandbox", "windows", "linux", "macos", "guardian", "markdown", "copy-paste", "bearer-token", "seatbelt", "permissions", "git", "mermaid", "approval-mode", "agent-control", "otlp", "network-policy", "diagnostics", "v8"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.158.0 のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260929/header.png)

## はじめに

2026年9月28日（日本時間）、OpenAI Codex CLI の **rust-v0.158.0** がリリースされました。リリースノートの New Features には、TUIでのプロンプト候補（`tui.prompt_suggestions`）、フルスクリーンTUIでのコピー&ペースト機能の強化（Markdownフォーマット保持）、MCP（Model Context Protocol）サーバーへのOAuth認証対応、exec-serverのWebSocket接続セキュリティ向上、画像生成・編集における透明背景の明示的リクエスト、そして昇格した権限で実行されるコマンドでのターミナル入力承認のデフォルト有効化が並んでいます。Bug Fixes では、Windows・Linux のサンドボックスや macOS のパス権限チェックなどが修正されました。

## 注目アップデート深掘り

### TUIでのプロンプト候補（prompt suggestions）

`tui.prompt_suggestions` を有効にすると、ターンが成功した後にフォローアップの候補が提示されるようになりました（#47911, #47929）。候補は Tab で編集してから送信できます。

### TUIでのコピー機能強化とMarkdownフォーマット保持

フルスクリーンTUIで「copy-on-select（選択時自動コピー）」と「right-click paste（右クリックペースト）」が設定可能になり、トランスクリプトの選択範囲をコピーした際にMarkdownフォーマットが保持されるようになりました（#47639, #47896, #48118）。

Codex CLIとの対話内容をMarkdown対応のツール（GitHub Issues など）に転記する場面で、書式を保ったまま貼り付けられるのが利点です。なお、リリースノートには具体的な設定キーは記載されていません。

### MCP ServerへのOAuth認証サポート拡充

本バージョンでは、事前登録されたOAuthクライアントシークレットを必要とするMCPサーバーへの接続がサポートされました（#47891）。これにより、`codex mcp add --oauth-client-secret` コマンドを使用してクライアントシークレットを指定できるようになりました。

> **Note:** MCP（Model Context Protocol）は、Codex CLIが外部ツールやサービスと連携するためのプロトコルです。MCPサーバーを追加することで、Codexの機能を拡張できます。

OAuth クライアントを事前登録する方式の MCP サーバーは、クライアントシークレットがないと接続できません。社内ツールをそうした MCP サーバーとして公開している環境では、Codex から直接つなげられるようになります。

## 実用的な活用ポイント

今回のリリースは、日常的な開発ワークフローに複数の改善をもたらします。

**TUIでの作業効率化**: Markdownフォーマットを保持したコピー機能により、ポストモーテムや設計ドキュメントへの転記がしやすくなります。copy-on-selectを有効にすれば、選択するだけでコピーされます。

**MCP連携**: 事前登録型の OAuth クライアントを要求する MCP サーバーにも `codex mcp add --oauth-client-secret` で接続できます。

**権限管理の改善**: 昇格した権限で実行されるコマンドでは、ターミナル入力承認がデフォルトで有効になりました（#47799）。一方、runtime-only の権限付与では不要なレビューが発生しなくなっています（#48073）。

**プラットフォーム固有の修正**: Windows 10 の通常パスで起きていたサンドボックスの失敗（#47672）、Linux でネストされた書き込み可能ルートがあるときのサンドボックス起動（#47623）、macOS のシステムパスエイリアスによる不要な承認プロンプト（#47879）などが修正されています。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | TUIプロンプト候補 | `tui.prompt_suggestions` でターン成功後にフォローアップ候補を表示、Tab で編集してから送信 (#47911, #47929) |
| Feature | TUIコピー機能強化 | copy-on-selectと右クリックペーストの設定可能化、Markdownフォーマット保持 (#47639, #47896, #48118) |
| Feature | MCP OAuth認証 | 事前登録OAuthクライアントシークレットを使用したMCPサーバー接続サポート、`--oauth-client-secret`フラグ追加 (#47891) |
| Feature | exec-server WebSocketセキュリティ | ベアラートークンによる直接接続とapp-server経由接続のセキュア化 (#47601, #47648) |
| Feature | 画像生成機能拡張 | 画像生成・編集で透明背景を明示的にリクエスト可能に、編集がファイルとして保持された会話内画像を受け付けるように (#47484, #47956) |
| Feature | ターミナル入力承認 | 昇格した権限で実行されるコマンドでデフォルト有効化、runtime-only権限での不要レビュー削減 (#47799, #48073) |
| Fix | Windowsサンドボックス修正 | Windows 10の通常パス、拒否された保存済み認証情報、大規模な権限ポリシーでの失敗の不具合修正 (#47672, #47695, #47919) |
| Fix | Linuxサンドボックス修正 | ネストされた書き込み可能ルートでの起動修正、LinuxとmacOSでのGitメタデータ保護維持 (#47623, #47974) |
| Fix | macOSパス権限 | パッチ操作で既存権限がカバーするシステムパスエイリアスを認識し、不要な承認プロンプトを回避 (#47879) |
| Fix | 承認レビュー動作 | 新規ユーザー入力到着時のリトライ、ステータス質問による自動アボート防止 (#47819) |
| Fix | Mermaidレンダリング | クォートラベルとアンパサンドのサポート、未サポート図のフォールバック説明追加 (#47572, #47678) |
| Fix | コマンド完了イベント | 早期出力の含有、プロセス起動失敗のクライアント報告 (#47529, #47665) |
| Improvement | WebSocket認証基盤 | 認証処理の `codex-websocket-auth` への抽出 (#47447) |
| Improvement | 並列処理最適化 | 命令更新とツール準備の並列化 (#47458) |
| Improvement | セッション制御 | エージェント操作の `AgentControl` 経由ルーティング (#47520) |
| Improvement | 分析記録強化 | サンドボックスバックエンドの実行分析への記録 (#47568) |
| Improvement | Guardian認可レビューのコンテキスト | アシスタントコンテキストの保持、メッセージ順序保持、明示的ユーザーゴール更新保持 (#47582, #47584, #47585, #47811) |
| Improvement | プロセス起動基盤 | 共有チャイルドランチャーへのルーティング、POSIXネイティブ起動、Linux起動ヘルパー統合 (#47603-#47617) |
| Improvement | メトリクス収集 | グローバル操作メトリクスのバッファリング、実行RPC/プロセス起動トレーシング (#47619, #47680) |
| Improvement | リトライロジック | Retry-Afterヘッダー尊重、ファイルブロブアップロードのHTTP 502/504リトライ (#47641, #47926) |
| Improvement | OTLP統合 | 最終エージェント応答とGuardian評価のオプトインOTLPロギング追加 (#47649, #47870) |
| Improvement | ネットワークポリシー | 管理ネットワークポリシーの保持、拡張機能でのネットワークポリシー尊重 (#47663, #47742) |
| Improvement | 権限レンダリング | エグゼキューターコンテキストを使用したリモート権限パス表示 (#47867) |
| Improvement | TUIユーザー体験 | クリップボードコピー中の応答性維持、起動ヒントのトランスクリプト内移動 (#47847, #47954) |
| Improvement | 診断機能 | ロールアウト履歴の診断レポート添付、SQLiteログ失敗時の保持と警告、TUIクライアントログのアップロード含有 (#47653, #47886, #47887, #47889) |
| Improvement | 設定管理 | 設定マージ時のテーブルクローン削減、キーエイリアスの正規化、ネストされた正規パス対応、`tui.whimsy`エイリアス追加 (#47902-#47908) |
| Improvement | V8ビルド最適化 | 検証済みチェックサムマニフェストの再利用、macOSとLinuxでのプリビルトアーカイブ使用 (#47915, #47951) |
| Improvement | 起動高速化 | 起動時のWebSocket事前接続をツール探索と並行実行 (#47635) |
| Improvement | ビルド | Cargo と対象の Bazel rustc ジョブで Transparent Huge Pages を要求 (#47962) |

## まとめ

rust-v0.158.0は、ユーザー体験、セキュリティ、安定性の三つの軸でバランスの取れたアップデートとなっています。TUIではプロンプト候補とMarkdownを保持したコピーが加わり、MCPのOAuthクライアントシークレット対応とexec-serverのベアラートークン認証も追加されました。

また、各プラットフォームでのサンドボックス不具合修正や Guardian 認可レビューのコンテキスト改善など、内部基盤の変更も多く含まれています。リリースノートの Changelog には 190 件の PR が並んでいます。

SREやインフラエンジニアにとっては、昇格権限コマンドでのターミナル入力承認のデフォルト化など、権限まわりの挙動変更を押さえておくとよいでしょう。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)