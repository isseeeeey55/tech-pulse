---
title: "【Claude Code】v2.1.173 リリースノートまとめ"
date: 2026-06-12T08:00:51+09:00
draft: false
tags: ["claude-code", "fable-5", "sandbox", "windows"]
categories: ["Claude Code Updates"]
summary: "v2.1.173 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260612/header.png)

# Claude Code v2.1.173 リリース情報

## はじめに

2026年6月12日、Claude Code v2.1.173 がリリースされました。このバージョンでは、Fable 5 モデル名の正規化に関する問題と、Windows 環境でのサンドボックス起動時の誤警告という 2 件の不具合が修正されています。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Fix | Fable 5 モデル名の `[1m]` サフィックス正規化 | Fable 5 モデルは標準で 1M コンテキストを含むため、モデル名に付与された `[1m]` サフィックスが自動的に削除されるようになった |
| Fix | Windows でのサンドボックス起動警告 | サンドボックスが設定で有効化されている場合に、Windows 環境で誤った "sandbox dependencies missing" 警告が表示される問題を修正 |

## まとめ

v2.1.173 は、モデル名の正規化処理とプラットフォーム固有の警告表示に関する 2 件の不具合を修正したメンテナンスリリースです。Fable 5 モデルのコンテキストサイズ表記の一貫性と、Windows 環境でのサンドボックス機能の利用体験が改善されています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)