---
title: "【Claude Code】v2.1.270 リリースノートまとめ"
date: 2026-09-13T08:00:51+09:00
draft: false
tags: ["claude-code", "bash", "git"]
categories: ["Claude Code Updates"]
summary: "v2.1.270 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260913/header.png)

# Claude Code v2.1.270 リリースノート

## はじめに

Claude Code v2.1.270 がリリースされました。変更は 1 件のみで、v2.1.269 で入ったリグレッション（機能退行）を修正するパッチリリースです。

- Bash ツールで、読み取り専用の git コマンドが予期せず権限確認を求める不具合の修正

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Fix | 読み取り専用 git コマンドの権限確認 | セッションをしばらく続けた後、Bash ツールで読み取り専用の git コマンドが予期せず権限確認を求める不具合を修正（v2.1.269 でのリグレッション） |

## まとめ

v2.1.269 以降、長めのセッションで `git status` のような読み取り専用の git コマンドに権限確認が出るようになっていた場合、v2.1.270 へのアップデートで解消します。

出典: [CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
