---
title: "【Claude Code】v2.1.278 リリースノートまとめ"
date: 2026-09-20T08:01:00+09:00
draft: false
tags: ["claude-code", "auto-mode", "bedrock", "vertex", "foundry", "status"]
categories: ["Claude Code Updates"]
summary: "v2.1.278 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260920/header.png)

# Claude Code v2.1.278 リリース情報

## はじめに

2026年9月19日、Claude Code v2.1.278 がリリースされました。このバージョンでは、Claude API・Enterprise ユーザー、および Bedrock・Vertex・Foundry・ゲートウェイ環境における Auto モードのデフォルト動作が変更され、サーバーサイド分類器が標準となりました。また、`/status` コマンドに Auto モード分類器の実行場所を表示する機能が追加されています。

## 注目アップデート深掘り

### Auto モードのサーバーサイド分類器への移行

Claude API・Enterprise ユーザー、および Bedrock・Vertex・Foundry・ゲートウェイ環境において、Auto モードがデフォルトでサーバーサイド分類器を使用するよう変更されました。

公式リリースノートでは、このサーバーサイド分類器について "does not charge for classifier overhead"（分類器のオーバーヘッド分を課金しない）と記載されています。

Bedrock・Vertex・Foundry・ゲートウェイ環境では、環境変数 `CLAUDE_CODE_AUTO_MODE_SERVER=0` を設定することでオプトアウトできます。また、課金対象のフォールバック（billed fallback）が発生した場合には警告が表示されます。

詳細な課金情報については、[公式ドキュメント](https://code.claude.com/docs/en/auto-mode-classifier-billing)で確認できます。

## 実用的な活用ポイント

Claude API・Enterprise ユーザー、および Bedrock・Vertex・Foundry・ゲートウェイを利用している場合、このバージョンでは特別な設定変更なしにサーバーサイド分類器がデフォルトで適用されます。

`/status` に新しく追加された `Auto mode server` 行を確認することで、現在のセッションでサーバーサイド分類器が有効になっているかを即座に把握できます。課金フォールバックの警告が表示された場合は、公式ドキュメントを参照して原因を確認することを推奨します。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Change | サーバーサイド分類器のデフォルト化 | Claude API・Enterprise・Bedrock・Vertex・Foundry・ゲートウェイ環境の Auto モードで、分類器オーバーヘッド課金が発生しないサーバーサイド分類器をデフォルトに変更。`CLAUDE_CODE_AUTO_MODE_SERVER=0` でオプトアウト可能 |
| Feature | `/status` への Auto モード分類器情報の追加 | `/status` コマンドに `Auto mode server` 行を追加し、現在のセッションで Auto モード分類器がサーバー上で実行されているかを表示 |

## まとめ

v2.1.278 は Auto モードの分類器まわりに絞った2件の変更です。対象プラットフォームではサーバーサイド分類器がデフォルトとなり、分類器オーバーヘッド分は課金されません。あわせて `/status` に `Auto mode server` 行が追加され、分類器がサーバー上で動作しているかを確認できるようになりました。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)