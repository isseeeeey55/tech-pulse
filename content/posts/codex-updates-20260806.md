---
title: "【Codex CLI】0.146.1 リリースノートまとめ"
date: 2026-08-06T08:01:36+09:00
draft: false
tags: ["codex", "cyber-capable-models", "automatic-review", "permissions", "terminal-interface", "bug-fix"]
categories: ["Codex CLI Updates"]
summary: "0.146.1 のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260806/header.png)

# OpenAI Codex CLI 0.146.1 リリース解説

## はじめに

OpenAI Codex CLI のバージョン **0.146.1** がリリースされました。0.146.0 に続くパッチリリースで、リリースノートに記載されている変更は 1 件のみです。

> Apply safer automatic-review defaults for cyber-capable models and explain permission changes in the terminal interface. (#37057)
> （サイバー能力対応モデルに、より安全な自動レビューのデフォルト設定を適用し、パーミッションの変更をターミナルインターフェース上で説明する）

該当の PR #37057 は「[0.146] Backport safer cyber-model auto-review defaults」というタイトルで、0.146 ブランチへのバックポートとして取り込まれています。

## 変更内容

このリリースには 2 つの側面があります。いずれも同一の PR に含まれています。

### 1. サイバー能力対応モデルの自動レビューのデフォルト設定を安全側に変更

「cyber-capable models（サイバー能力対応モデル）」に適用される自動レビュー（automatic review）のデフォルト値が、より安全な設定に変更されました。

リリースノートが述べているのは「より安全なデフォルトを適用した」という点までで、**変更前後の具体的な閾値や、どのモデルが cyber-capable に分類されるのかは示されていません**。挙動の詳細を確認したい場合は、PR #37057 の差分か、Codex CLI の設定ドキュメントを直接参照してください。

なお Codex CLI の自動レビューは、Guardian によるレビュー機構の一部です。後続の 0.148.0 では Guardian V2 の拡張（リスクスコアの永続化、自動レビュー制御の強化など）が続いており、この領域は継続的に手が入っています。

### 2. パーミッション変更のターミナル表示

パーミッションの変更内容が、ターミナルインターフェース上で説明されるようになりました。

これも、リリースノートに記されているのは「explain permission changes in the terminal interface」という一文のみです。表示される項目や書式は明示されていないため、実際の出力は手元でアップデート後に確認してください。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Bug Fix | サイバー能力対応モデルの自動レビューデフォルトの安全化とパーミッション変更の説明表示 | cyber-capable モデルに、より安全な自動レビューのデフォルト設定を適用。あわせてパーミッションの変更をターミナルインターフェース上で説明 (#37057) |

**関連 Pull Request:**
- [#37057](https://github.com/openai/codex/pull/37057): [0.146] Backport safer cyber-model auto-review defaults

**Full Changelog:** [rust-v0.146.0...rust-v0.146.1](https://github.com/openai/codex/compare/rust-v0.146.0...rust-v0.146.1)

## まとめ

0.146.1 は、変更 1 件のみのパッチリリースです。新機能の追加はなく、サイバー能力対応モデルを扱う際のデフォルト設定を安全側に倒すことと、パーミッション変更の可視化が内容になります。

セキュリティに関わるデフォルト値の変更はバックポートされているため、cyber-capable モデルを業務で利用している場合は、アップデートしておくとよいでしょう。設定を明示的にカスタマイズしている環境では、デフォルト変更の影響を受けるかどうかを事前に確認しておくと安全です。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)
