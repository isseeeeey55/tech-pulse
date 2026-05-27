---
title: "【Codex CLI】rust-v0.134.0 リリースノートまとめ"
date: 2026-05-27T21:50:16+09:00
draft: false
tags: ["codex", "conversation-history", "search", "profile", "permission-profile", "mcp", "oauth", "sandbox", "tui", "cli", "websocket", "remote-control", "compaction", "plugin", "auto-review", "proxy", "windows", "dotslash", "v8", "tracing", "analytics"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.134.0 のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260527/header.png)

# OpenAI Codex CLI rust-v0.134.0 リリース解説

## はじめに

2026年5月27日、OpenAI Codex CLI の **rust-v0.134.0** がリリースされました。

今回のリリースでは、ローカル会話履歴の検索、`--profile` の扱いの整理、MCP サーバー設定の強化、リモート接続まわりの信頼性改善などが含まれています。大きな単一機能というより、日々の利用で触れる検索・設定・接続・拡張まわりを広く整えるアップデートです。

主な変更点は以下の通りです。

- ローカル会話履歴を検索できるようになり、大文字小文字を区別しない本文一致と結果プレビューに対応
- `--profile` が CLI、TUI permissions、sandbox flows における主要な profile selector として整理され、legacy profile configs は migration guidance 経由で拒否
- MCP setup でサーバー単位の environment targeting と、streamable HTTP server 向け OAuth options に対応
- `readOnlyHint` を持つ read-only MCP tools の並行実行に対応
- exec-server websocket、remote control、remote compaction v2 まわりの retry/reconnect を改善
- Windows TUI の描画崩れ、workspace-specific usage-limit messages、Node-based tools の proxy 継承などを修正

参考: [GitHub Release rust-v0.134.0](https://github.com/openai/codex/releases/tag/rust-v0.134.0) / [Full Changelog](https://github.com/openai/codex/compare/rust-v0.133.0...rust-v0.134.0)

---

## 注目アップデート深掘り

### ローカル会話履歴の検索

今回のリリースでは、ローカル会話履歴を横断して検索できる機能が追加されました（#23519, #23921）。公式リリースノートでは、case-insensitive な content match と result preview が明記されています。

過去の会話を再利用したいとき、目的のやり取りを探すために履歴を目視でたどる負担が下がります。結果プレビューがあるため、単に一致箇所を見るだけでなく、その候補が目的の会話かを判断しやすくなる点も実用的です。

### `--profile` の整理と legacy profile config の扱い

`--profile` が、CLI、TUI permissions、sandbox flows をまたいだ主要な profile selector として整理されました（#23708, #23883, #23890, #24051, #24055, #24059, #24067, #24110）。あわせて legacy profile configs は migration guidance を通じて拒否されるようになっています。

> **Note:** ここでの profile は Codex CLI の権限や実行設定を選択するための profile です。今回のリリースでは、古い profile config をそのまま受け入れ続けるのではなく、移行ガイダンスへ寄せる変更が含まれています。

関連して、profile migration documentation links が config error に追加されています（#23879）。既存設定を持つ環境では、エラー表示を手がかりに新しい形式へ移行する流れになります。

### MCP setup と tool schema の改善

MCP setup では、サーバー単位の environment targeting と、streamable HTTP server 向け OAuth options が追加されました（#23583, #24120）。MCP server の接続先や認証を扱う設定が、より明示的に表現できる方向の変更です。

また、connector tool schemas については local `$ref` / `$defs` 構造を保持し、oversized schemas は公開前に compact する改善が入っています（#23357, #23904）。大きな schema を扱う connector や tool 連携で、schema の取り扱いをより堅くする変更として読めます。

さらに、`readOnlyHint` を advertise する read-only MCP tools は並行実行できるようになりました（#23750）。読み取り専用であることが示されている tool について、実行の扱いを最適化する変更です。

### リモート接続と実行環境まわりの修正

Bug Fixes では、remote reliability の改善がまとまっています。stale な exec-server websocket client の reconnect、auth recovery 後の remote control retry、remote compaction v2 streams の retry が含まれます（#23867, #23775, #23951）。

そのほか、Windows TUI rendering corruption の修正（#24082）、credit / spend-cap failure 時の workspace-specific usage-limit messages（#24114）、Node-based tools が Codex managed network proxy environment を引き継ぐ修正（#23905）も入っています。

---

## 実用的な活用ポイント

### 日常ワークフローへの影響

ローカル会話履歴検索は、過去の会話から必要な文脈を探す操作に直接効く変更です。case-insensitive search と result preview が入ったことで、検索語の大文字小文字を気にせず、候補の中身を確認しながら目的の会話へ戻りやすくなります。

`--profile` の整理は、既存の profile 設定を使っている環境ほど確認しておきたい変更です。legacy profile configs が migration guidance 経由で拒否されるため、手元の設定で警告やエラーが出る場合は、リリースノートと移行ドキュメントに沿って見直すのがよさそうです。

### SRE / インフラエンジニア視点

MCP setup の environment targeting と OAuth options は、接続先や認証の違いを明示的に扱いたい場面で重要です。公式リリースノートの記載範囲では、サーバー単位の environment targeting と streamable HTTP server 向け OAuth options が追加された、という点を押さえておくのが安全です。

remote reliability の修正も、リモート実行や remote control を使う環境では確認しておきたいポイントです。websocket reconnect、auth recovery 後の retry、remote compaction v2 stream retry が含まれており、接続まわりの失敗時の扱いが改善されています。

### すぐに確認したいこと

- ローカル会話履歴検索で、期待した履歴が case-insensitive に見つかるか
- 既存の profile 設定で migration guidance が出ないか
- MCP server 設定を使っている場合、environment targeting や OAuth options の変更点が関係するか
- Node-based tools を proxy 環境で使っている場合、managed network proxy environment の継承が効くか

---

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | ローカル会話履歴検索 (#23519, #23921) | case-insensitive な content match と result preview を含む検索を追加 |
| Feature | `--profile` の主要 selector 化 (#23708, #23883, #23890, #24051, #24055, #24059, #24067, #24110) | CLI、TUI permissions、sandbox flows で `--profile` を主要な profile selector として整理 |
| Feature | MCP setup の改善 (#23583, #24120) | per-server environment targeting と streamable HTTP server 向け OAuth options を追加 |
| Feature | connector tool schema の信頼性改善 (#23357, #23904) | local `$ref` / `$defs` の保持と oversized schema の compact に対応 |
| Feature | read-only MCP tools の並行実行 (#23750) | `readOnlyHint` を advertise する read-only MCP tools の並行実行に対応 |
| Feature | extension / hook context の拡充 (#22882, #23963) | extension tools への conversation history 提供と hook inputs への subagent identity 追加 |
| Fix | remote reliability の改善 (#23867, #23775, #23951) | exec-server websocket reconnect、auth recovery 後の retry、remote compaction v2 stream retry |
| Fix | Windows TUI rendering corruption 修正 (#24082) | 描画前に virtual terminal mode を復元 |
| Fix | workspace-specific usage-limit messages (#24114) | credit / spend-cap failure 時の message を workspace 別に表示 |
| Fix | plugin-level icon assets の再利用 (#23776) | plugin skills が共有 icon assets を再利用可能に |
| Fix | auto-review runtime settings の profile metadata 保持 (#23956) | active permission profile metadata を保持 |
| Fix | Node-based tools の proxy 継承 (#23905) | Codex managed network proxy environment を引き継ぐよう修正 |
| Documentation | installer path の README 追記 (#24106) | curl と PowerShell installer paths を README に記載 |
| Documentation | developer docs の test 手順更新 (#23910) | repo-local test runs で direct `cargo test` より `just test` を推奨 |
| Documentation | profile migration docs link 追加 (#23879) | relevant config errors に migration documentation links を追加 |
| Chore | release packaging の整理 (#23833, #23836, #24129, #24165) | canonical native artifacts、DotSlash fetching、macOS x64 zsh artifact まわりを改善 |
| Chore | V8 artifact の release build 対応 (#23934) | Codex-produced V8 artifacts の release build support を追加 |
| Chore | benchmarks / fixtures 追加 (#23935, #24152) | image re-encoding benchmarks と connector-style JSON schema policy fixtures を追加 |
| Chore | tracing / analytics 改善 (#23581, #23980, #24146) | websocket requests、turn starts、remote compaction v2 の tracing / analytics を改善 |

---

## まとめ

rust-v0.134.0 は、会話履歴検索、profile 選択、MCP setup、remote reliability など、日常利用の土台になる部分を広く整えるリリースです。

特に確認しておきたいのは、ローカル会話履歴検索と legacy profile config の扱いです。検索機能はすぐに体感しやすい改善であり、profile まわりは既存設定に影響する可能性があります。MCP や remote control を使っている場合は、environment targeting、OAuth options、retry/reconnect まわりの変更もあわせて見ておくとよさそうです。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)
