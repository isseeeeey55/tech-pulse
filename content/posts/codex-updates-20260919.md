---
title: "【Codex CLI】rust-v0.155.1 リリースノートまとめ"
date: 2026-09-19T08:01:18+09:00
draft: false
tags: ["codex", "tui", "reasoning-summary", "bug-fix"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.155.1 のCodex CLIリリースノートまとめ"
---

# OpenAI Codex CLI rust-v0.155.1 リリース情報

![](/images/codex-updates-20260919/header.png)

## はじめに

2026年9月19日（JST）、OpenAI Codex CLI の Rust 実装版 **rust-v0.155.1** がリリースされました。rust-v0.155.0 からのパッチリリースで、変更は Bug Fixes の1件（#46467）のみです。

新規のローカル TUI セッションで reasoning summary がデフォルトで無効になり、reasoning summary をサポートしないプロバイダーでリクエストが拒否される問題が修正されました。

## 注目アップデート深掘り

### TUI セッションの reasoning summary デフォルト設定修正

リリースノートの記載は次のとおりです。

> New local TUI sessions now leave reasoning summaries disabled by default, fixing request rejection by providers that do not support them. Explicit reasoning-summary settings remain respected. (#46467)

対応する PR #46467 のタイトルは "Restore none as the TUI reasoning summary default" で、TUI の reasoning summary のデフォルト値を `none` に戻す変更です。

**変更の詳細**

- **対象**: 新規のローカル TUI セッション
- **変更後のデフォルト**: reasoning summary は無効
- **修正される問題**: reasoning summary をサポートしないプロバイダーでのリクエスト拒否
- **明示設定**: reasoning summary を明示的に設定している場合は、その設定が引き続き尊重される

> **Note:** TUI は Codex CLI のターミナルベースのインタラクティブインターフェースです。

## 実用的な活用ポイント

reasoning summary をサポートしないプロバイダーでローカル TUI セッションを使っていて、リクエストが拒否されていた場合は rust-v0.155.1 へのアップグレードが対象になります。reasoning summary を使いたい場合は、従来どおり明示的に設定してください。明示設定はこの変更の影響を受けません。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Fix | TUI reasoning summary デフォルト設定の修正 | 新規ローカル TUI セッションで reasoning summary をデフォルト無効化。未対応プロバイダーでのリクエスト拒否問題を解消。明示的な設定は引き続き尊重される。(#46467) |

## まとめ

rust-v0.155.1 は、新規ローカル TUI セッションの reasoning summary デフォルトを無効に戻すバグ修正1件のみのパッチリリースです。reasoning summary 非対応のプロバイダーでのリクエスト拒否が解消され、明示的な設定は引き続き尊重されます。

詳細は [GitHub Release ページ](https://github.com/openai/codex/releases/tag/rust-v0.155.1) と [変更差分](https://github.com/openai/codex/compare/rust-v0.155.0...rust-v0.155.1) を参照してください。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)