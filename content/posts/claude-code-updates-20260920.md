---
title: "【Claude Code】v2.1.278 リリースノートまとめ"
date: 2026-09-20T08:01:00+09:00
draft: true
tags: ["claude-code", "auto-mode", "bedrock", "vertex", "foundry", "status"]
categories: ["Claude Code Updates"]
summary: "v2.1.278 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.278 リリース情報

## はじめに

2026年9月20日、Claude Code v2.1.278 がリリースされました。このバージョンでは、Claude API・Enterprise ユーザー、および Bedrock・Vertex・Foundry・ゲートウェイ環境における Auto モードのデフォルト動作が変更され、サーバーサイド分類器が標準となりました。また、`/status` コマンドに Auto モード分類器の実行場所を表示する機能が追加されています。

## 注目アップデート深掘り

### Auto モードのサーバーサイド分類器への移行

Claude API・Enterprise ユーザー、および Bedrock・Vertex・Foundry・ゲートウェイ環境において、Auto モードがデフォルトでサーバーサイド分類器を使用するよう変更されました。

この変更により、分類器のオーバーヘッドに対する課金が発生しなくなります。公式リリースノートによれば、この新しい動作は "does not charge for classifier overhead" と明記されており、従来のクライアントサイド分類器で発生していた追加課金が不要になります。

Bedrock・Vertex・Foundry・ゲートウェイ環境では、環境変数 `CLAUDE_CODE_AUTO_MODE_SERVER=0` を設定することで、従来のクライアントサイド分類器にオプトアウトすることも可能です。また、課金が発生するフォールバック動作が実行された場合には警告が表示されます。

詳細な課金情報については、公式ドキュメント（https://code.claude.com/docs/en/auto-mode-classifier-billing）で確認できます。

## 実用的な活用ポイント

Claude API・Enterprise ユーザー、および Bedrock・Vertex・Foundry・ゲートウェイを利用している場合、このバージョンへのアップデートにより Auto モード利用時の課金が自動的に最適化されます。特別な設定変更は不要で、デフォルトでサーバーサイド分類器が適用されます。

新しく追加された `/status` コマンドの `Auto mode server` 行を確認することで、現在のセッションでサーバーサイド分類器が有効になっているかを即座に把握できます。課金フォールバックの警告が表示された場合は、公式ドキュメントを参照して原因を確認することを推奨します。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | サーバーサイド分類器のデフォルト化 | Claude API・Enterprise・Bedrock・Vertex・Foundry・ゲートウェイ環境の Auto モードで、分類器オーバーヘッド課金が発生しないサーバーサイド分類器をデフォルトに変更。`CLAUDE_CODE_AUTO_MODE_SERVER=0` でオプトアウト可能 |
| Feature | `/status` への Auto モード分類器情報の追加 | `/status` コマンドに `Auto mode server` 行を追加し、現在のセッションで Auto モード分類器がサーバー上で実行されているかを表示 |

## まとめ

v2.1.278 は、Auto モードの課金最適化を目的とした重要なアップデートです。サーバーサイド分類器への移行により、対象プラットフォームのユーザーは分類器オーバーヘッドの追加課金なしで Auto モードを利用できるようになります。`/status` コマンドの拡張により、分類器の実行状況を簡単に確認できる透明性も向上しています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)