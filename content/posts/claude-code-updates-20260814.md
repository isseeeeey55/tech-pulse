---
title: "【Claude Code】v2.1.231 リリースノートまとめ"
date: 2026-08-14T08:00:57+09:00
draft: false
tags: ["claude-code", "mcp", "oauth", "slack"]
categories: ["Claude Code Updates"]
summary: "v2.1.231 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260814/header.png)

## はじめに

Claude Code v2.1.231 がリリースされました。このバージョンは、MCP（Model Context Protocol）サーバーとの OAuth 認証における不具合を修正するメンテナンスリリースです。

主な変更点は以下の通りです：

- **OAuth 認証の修正**: 事前登録済み OAuth クライアントを使用する MCP サーバーで発生していたリダイレクト URI 不一致によるサインイン失敗の問題を解決

## 注目アップデート深掘り

### MCP OAuth サインインのリダイレクト URI 不一致問題の修正

今回のリリースでは、特定の MCP サーバーで OAuth サインインが失敗する問題が修正されました。公式リリースノートには次のように記載されています：

> Fixed MCP OAuth sign-in failing with a redirect URI mismatch for servers that use a pre-registered OAuth client, such as Slack

この問題は、Slack などの事前登録済み OAuth クライアントを使用する MCP サーバーに接続する際、リダイレクト URI の不一致によって認証フローが完了できなかった不具合です。

**修正の意義**

MCP は Claude Code が外部ツールやデータソースと連携するためのプロトコルであり、OAuth 認証は安全な接続を確立するための重要な仕組みです。この不具合により、Slack を含む一部の MCP サーバーへの接続が阻害されていましたが、今回の修正によって正常にサインインできるようになりました。

> **Note:** MCP（Model Context Protocol）は、Claude Code が外部ツールやサービスと統合するための標準プロトコルです。

## 実用的な活用ポイント

このバージョンにアップデートすることで、Slack などの事前登録済み OAuth クライアントを持つ MCP サーバーへの接続が安定します。特に、これまで OAuth 認証エラーで接続できなかった MCP サーバーを利用している場合、この修正によって問題が解決される可能性があります。

既に MCP サーバー接続で OAuth 関連のエラーを経験している場合は、v2.1.231 へのアップデートを検討してください。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Fix | MCP OAuth サインインの修正 | 事前登録済み OAuth クライアントを使用する MCP サーバー（Slack など）でリダイレクト URI 不一致により認証が失敗していた問題を修正 |

## まとめ

v2.1.231 は、MCP サーバーとの OAuth 認証における特定の不具合の修正に絞ったリリースです。事前登録済み OAuth クライアントを使用する外部サービスとの連携が正常に動作するようになり、Claude Code の外部ツール統合の信頼性が向上しました。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)