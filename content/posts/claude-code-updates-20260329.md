---
title: "【Claude Code】v2.1.87 リリースノートまとめ"
date: 2026-03-29T12:00:00+09:00
draft: false
tags: ["claude-code", "cowork", "bug-fix"]
categories: ["Claude Code Updates"]
summary: "v2.1.87 のClaude Codeリリースノートまとめ。Cowork Dispatch のメッセージ配信バグを修正"
---

![](/tech-pulse/images/claude-code-updates-20260329/header.png)

## はじめに

Claude Code v2.1.87 がリリースされた。今回はバグ修正1件のみのホットフィックスリリース。Cowork 機能のメッセージ配信（Dispatch）が正しく届かないケースがあった問題が修正されている。

## 注目アップデート深掘り

### Cowork Dispatch のメッセージ配信修正

![Cowork Dispatch の修正内容](/tech-pulse/images/claude-code-updates-20260329/cowork-dispatch-fix.png)

> **Cowork とは？**
> Claude Code のバックグラウンドエージェント機能。ターミナルを閉じていてもエージェントが作業を継続し、完了時に通知を送ってくれる。長時間タスクを投げておいて、後から結果を確認する使い方ができる。

Cowork でエージェントが作業を完了した際の通知メッセージ（Dispatch）が、一部のケースで受信側に届かないバグがあった。v2.1.87 でこれが修正され、Dispatch メッセージの配信が安定した。

**影響範囲**

Cowork を使ってバックグラウンドタスクを実行している場合、完了通知が届かずにタスクの結果を見落とす可能性があった。特に複数の Cowork セッションを並行して走らせているケースで発生しやすかったと思われる。

**対応**

`claude update` で v2.1.87 に更新するだけで OK。

```bash
claude update
claude --version  # 2.1.87 であることを確認
```

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Fix | Cowork Dispatch メッセージ配信 | Cowork からの通知メッセージが届かないバグを修正 |

## まとめ

バグ修正1件のホットフィックス。Cowork を日常的に使っている人は早めにアップデートしておくといい。通知が来ないのは地味にストレスなので、修正されたのはありがたい。
