---
title: "【Codex CLI】rust-v0.154.0 リリースノートまとめ"
date: 2026-09-10T08:02:09+09:00
draft: false
tags: ["codex", "gpt-6-astra", "worktree", "windows", "daemon", "mcp", "oauth", "vim", "sandbox", "guardian", "approval-mode", "plugin", "tui", "security", "trust", "bedrock", "rich-text", "inline-questions", "fork", "resume"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.154.0 のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260910/header.png)

# Codex CLI rust-v0.154.0 リリースノート

## はじめに

OpenAI Codex CLI の **rust-v0.154.0** が 2026年9月10日（JST。GitHub リリース日は 9月9日 UTC）に公開されました。New Features には、GPT-6-Astra のモデルピッカー・Amazon Bedrock カタログへの追加、実験的な worktree サポート、作業中のインライン質問応答、Windows でのバックグラウンド Codex サーバー共有、Vim の `R` 置換モード、書式を保ったコピーの6項目が並びます。

また、プラグインツールの自動リロード、MCP OAuth トークン更新の協調制御、セキュリティ強化（サンドボックス・trust 確立前のヘルパー実行防止）、approval 自動化の堅牢化など、修正も含まれています。また、非推奨だった `codex mcp-server` エントリーポイントが削除されました。

---

## 注目アップデート深掘り

### 1. 実験的 worktree サポート：並行作業の分離と再開を実現

本リリースでは、複数の作業を並行して進める際に Git の worktree 機能を活用できる実験的機能が導入されました。リリースノートの原文は次の通りです。

> Experimental worktree support lets you create isolated checkouts for new or forked sessions using `--worktree` or `/worktree`, then browse and resume them.

この機能により、新しいセッションや fork したセッションに対して、分離されたファイルツリー上で作業を進められます。関連 PR には `codex exec` への managed worktree の追加（#42652）、対話セッションと fork での対応（#43069）、TUI のセッションコマンドからの作成（#43120）、TUI の worktree ブラウザ（#43286）が含まれます。

**使い方**  
リリースノートが示すのは、起動時の `--worktree` オプションと、TUI 内の `/worktree` コマンドの2つです。新規セッションや fork したセッション用に分離されたチェックアウトを作成し、あとから一覧を見て再開できます。

> **Note:** リリースノート上、worktree サポートは Experimental（実験的）と位置づけられています。

---

### 2. Windows でのバックグラウンド Codex サーバー共有とライフサイクル管理

Windows のセッションが、バックグラウンドの Codex サーバーを共有できるようになりました。リリースノートの原文は次の通りです。

> Windows sessions can now share a background Codex server, with daemon lifecycle commands and managed updates.

デーモンのライフサイクル管理コマンドと、管理されたアップデートも提供されます（#42405, #42392）。関連する Changelog 項目には、Windows での app-server デーモン対応（#42405）、管理された app-server ライフサイクル（#42381）、グレースフルなデーモン停止（#42364）、停止用ファイルからソケットリクエストへの置き換え（#43308）があります。具体的なコマンド名はリリースノートには書かれていないため、公式ドキュメントで確認してください。

---

## 実用的な活用ポイント

### 日常の開発ワークフローへの影響

**インライン質問応答**: Codex が作業を続けている間に、質問にその場で回答できるようになりました。

> Answer questions inline while Codex continues working, using suggested choices or custom text without losing your main draft.

提示された選択肢か自由記述で答えられ、入力中のメインのドラフトは失われません（#42891, #42894, #42897）。

### プラグインとツールの動的リフレッシュ

既存のセッションが、新しくインストールしたプラグインのツールを取り込み、外部でのプラグインのアップグレードやロールバック後にスキルとフックを更新するようになりました。

> Existing sessions pick up newly installed plugin tools and refresh skills and hooks after external plugin upgrades or rollbacks.

また MCP 接続では、OAuth トークンのリフレッシュが協調して行われ、リフレッシュに失敗した場合はログインを求める表示が出ます。拒否されたツール呼び出しを自動で再実行することはありません（#42413, #42552）。

### セキュリティと信頼性の向上

起動時、ワークスペースの信頼が確立する前にワークスペース側が制御するヘルパーを実行しないようになり、macOS のサンドボックスがターミナル入力のインジェクションをブロックするようになりました。

> Startup avoids running workspace-controlled helpers before trust is established, and the macOS sandbox blocks terminal input injection.

外部からクローンしたリポジトリなど、信頼を確立していないワークスペースで Codex を起動する場合に関係する修正です（#42324, #42590）。

---

## 全変更点一覧

以下、本リリースに含まれる主要な変更をカテゴリ別にまとめます：

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| **Feature** | GPT-6-Astra モデル対応 | モデルピッカーおよび Amazon Bedrock カタログに GPT-6-Astra を追加 (#42879, #42619) |
| **Feature** | 実験的 worktree サポート | `--worktree` または `/worktree` で分離されたチェックアウトを作成・再開可能 (#42652, #43069, #43120, #43286) |
| **Feature** | インライン質問応答機能 | Codex 作業中に並行して質問に回答でき、ドラフトを失わない (#42891, #42894, #42897) |
| **Feature** | Windows バックグラウンドサーバー共有 | Windows セッション間でデーモン共有、ライフサイクル管理とアップデート対応 (#42405, #42392) |
| **Feature** | Vim 置換モード | TUI コンポーザーで `R` 置換モード、undo と dot-repeat 対応 (#42194) |
| **Feature** | レガシーターミナルでの Escape 処理改善 | レガシーターミナルでの Vim の Escape 入力をより確実に処理 (#42584) |
| **Feature** | リッチテキストフォーマット保持コピー | 応答コピー時に Markdown フォーマットを保持、`/copy` でステータス出力やフィールドコピー可能 (#42847, #43055) |
| **Fix** | プラグインツールのリフレッシュ | 既存セッションで新規インストールされたプラグインツールを自動取得、スキルとフックをリフレッシュ (#42284, #42593, #42990) |
| **Fix** | MCP OAuth トークン更新協調 | MCP 接続で OAuth トークンリフレッシュを協調、更新失敗時にログイン要求を表示、拒否されたツール呼び出しを自動リプレイしない (#42413, #42552) |
| **Fix** | 起動時セキュリティ強化 | ワークスペース制御ヘルパーを trust 確立前に実行しない、macOS サンドボックスでターミナル入力インジェクションをブロック (#42324, #42590) |
| **Fix** | リモート resume と fork での権限保持 | リモート resume/fork 時に保存された権限を保持、新規セッションと fork はサーバーモデルデフォルトを尊重 (#43330, #43177, #43355) |
| **Fix** | 同時オープン会話の読み取り専用表示 | 別アプリで開いている会話を再開すると読み取り専用トランスクリプトとリトライオプションを表示、ドラフトは保持 (#43253) |
| **Fix** | Guardian 自動承認のコンテキスト保持 | 自動承認レビューがコンパクション後も権限コンテキストを保持、新しいユーザー指示や回答で無効化された承認を拒否 (#42844, #42852, #43442) |
| **Docs** | OpenAI Docs スキル更新 | GPT-6-Astra 移行、互換性、プロンプティングガイダンスを含むスキル更新 (#42931) |
| **Chores** | `codex mcp-server` 削除 | 非推奨だった `codex mcp-server` エントリーポイントを削除 (#42993) |

---


## まとめ

rust-v0.154.0 では、GPT-6-Astra の追加、実験的な worktree サポート、作業中のインライン質問応答、Windows でのバックグラウンドサーバー共有、Vim の `R` 置換モード、書式を保ったコピーが加わりました。修正では、既存セッションでのプラグインツールの取り込み、MCP の OAuth リフレッシュの協調、信頼確立前のヘルパー実行の防止と macOS サンドボックスの強化などが含まれます。

非推奨だった `codex mcp-server` エントリーポイントは使えなくなったため、利用している場合は移行が必要です。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)