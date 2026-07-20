---
title: "【Claude Code】v2.1.215 リリースノートまとめ"
date: 2026-07-20T08:00:58+09:00
draft: false
tags: ["claude-code", "verify", "code-review"]
categories: ["Claude Code Updates"]
summary: "v2.1.215 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260720/header.png)

# Claude Code v2.1.215 リリース情報

## はじめに

Claude Code v2.1.215 がリリースされました。このバージョンでは、`/verify` および `/code-review` スキルの実行方式が変更され、Claudeによる自動実行が廃止されました。これらのスキルは、ユーザーが明示的にコマンドを呼び出した場合のみ実行されるようになります。

## 注目アップデート深掘り

### スキル実行方式の変更：手動トリガーへの移行

今回のリリースでは、`/verify` と `/code-review` スキルの実行制御がユーザーに委譲されました。従来、Claudeはこれらのスキルを自律的に実行していましたが、v2.1.215以降は明示的なコマンド呼び出しが必要になります。

**変更内容**

リリースノートによれば、"Claude no longer runs the `/verify` and `/code-review` skills on its own; invoke them with `/verify` or `/code-review` when you want them" とされています。つまり、検証やコードレビューが必要な場面では、ユーザー自身が `/verify` または `/code-review` コマンドを入力する必要があります。

**なぜこの変更が重要なのか**

この変更により、検証・レビューを走らせるタイミングはユーザーの明示的な操作に一本化されます。Claudeの判断で自動的に実行されることがなくなるため、これらのスキルを呼び出す箇所は開発者自身が決めることになります。

> **Note:** `/verify` および `/code-review` は Claude Code のスキル機能で、コードの検証とレビューを実行するコマンドです。

## 実用的な活用ポイント

v2.1.215では、検証・レビュープロセスがユーザー主導になりました。コード生成や修正の後、品質チェックが必要だと判断した時点で `/verify` や `/code-review` を実行する運用になります。これまで自動実行を前提にしていた場合は、コミット前やPR作成前など、チェックを挟みたい箇所を作業フローの中で決めておくとよいでしょう。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| 変更 | スキル実行方式の変更 | `/verify` と `/code-review` スキルの自動実行を廃止。明示的なコマンド呼び出し時のみ実行される |

## まとめ

v2.1.215は、`/verify` と `/code-review` の実行方式を自動から手動トリガーへ変更する1項目のリリースです。この変更により、検証・レビューを実行するタイミングはユーザーが明示的に決めることになります。既存の運用で自動実行に依存していた場合は、必要な箇所で明示的にコマンドを呼び出すよう作業フローの見直しが必要です。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)