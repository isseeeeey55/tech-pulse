---
title: "【Claude Code】v2.1.97・v2.1.96 リリースノートまとめ"
date: 2026-04-09T08:01:18+09:00
draft: false
tags: ["claude-code", "no-flicker", "status-line", "mcp", "bedrock", "cedar", "permissions", "agent", "resume"]
categories: ["Claude Code Updates"]
summary: "v2.1.97・v2.1.96 のClaude Codeリリースノートまとめ"
---

![](/tech-pulse/images/claude-code-updates-20260409/header.png)

## はじめに

v2.1.97 は Feature 5件、Fix 20件超、Improvement 10件超という、修正系が中心のリリースです。v2.1.96 は Bedrock 認証の403エラー1件のみ。

新機能としてはフォーカスビュー（`Ctrl+O`）、ステータスラインの `refreshInterval` 設定、Cedar ポリシーのシンタックスハイライトあたりが実用的です。Fix 側は MCP の50MB/h バッファリーク修正や `/resume` 周りの大量バグ修正が目立ちます。

## 注目アップデート深掘り

### フォーカスビュー（Ctrl+O）

`NO_FLICKER` モードで `Ctrl+O` を押すと、表示がプロンプト・ツール実行の1行サマリー（edit diffstats 付き）・最終レスポンスだけに絞り込まれます。長いセッションで「今何をやっているか」だけ確認したいときに使えます。

ツール呼び出しが多い作業（大量のファイル編集やテスト実行のループなど）では、中間出力が画面を埋めて見失いがちですが、フォーカスビューならワンキーで要点だけ見られます。もう一度 `Ctrl+O` で元の全表示に戻ります。

### MCP HTTP/SSE バッファリークの修正

![MCP バッファリーク修正の Before/After](/tech-pulse/images/claude-code-updates-20260409/mcp-buffer-leak.png)

MCP サーバーが HTTP/SSE で接続している場合、再接続のたびに約50MB/hのペースでバッファが蓄積し続ける問題が修正されました。

長時間セッションや、MCP サーバーを多数接続している環境ではメモリ使用量が数GBに達するケースもあった問題です。特に `--resume` で前回のセッションを継続するワークフローでは影響が大きかった。

### Bedrock SigV4 認証の修正（v2.1.97）と 403 エラーの修正（v2.1.96）

Bedrock 関連の認証修正が2バージョンにわたって入っています。

**v2.1.96**: `AWS_BEARER_TOKEN_BEDROCK` または `CLAUDE_CODE_SKIP_BEDROCK_AUTH` を設定していると `403 "Authorization header is missing"` になるリグレッション（v2.1.94 起因）を修正。

**v2.1.97**: `AWS_BEARER_TOKEN_BEDROCK` や `ANTHROPIC_BEDROCK_BASE_URL` が空文字列に設定されている場合（GitHub Actions で未設定の inputs がそうなる）に SigV4 認証が失敗する問題を修正。

CI/CD パイプラインで Bedrock 連携している場合は、両方のバージョンを適用しておくのが安全です。

## 実用的な活用ポイント

**ステータスラインの `refreshInterval`**: ステータスラインコマンドを N 秒ごとに再実行する設定が追加されました。Git ブランチやビルド状況をリアルタイムで表示したい場合に便利です。

**`/agents` の稼働インジケーター**: サブエージェントが動いているとき、`/agents` 画面にエージェントタイプごとの `● N running` 表示が出るようになりました。バックグラウンドで動かしているエージェントの状態がひと目でわかります。

**`/resume` の安定化**: `/resume` 周りのバグが一気に8件修正されています。`--resume <name>` で開くと編集不可になる、検索がリロードで消える、10KB超のファイル編集 diff が消える、入力中のメッセージが保存されない、など。`/resume` を常用しているなら体感が変わるはずです。

**429 リトライのバックオフ改善**: サーバーが小さな `Retry-After` を返すと、全リトライが約13秒で使い切られていた問題が修正されました。指数バックオフが最低保証として適用されます。

## 全変更点一覧

> **Cedar ポリシーとは？**
> AWS が開発したオープンソースのアクセス制御言語です。Amazon Verified Permissions などで使われており、IAM ポリシーより柔軟な条件記述ができます。`.cedar` / `.cedarpolicy` ファイルで定義します。

| カテゴリ | 変更内容 | 概要 |
|---------|----------|------|
| Feature | フォーカスビュー切り替え（Ctrl+O） | NO_FLICKER モードでプロンプト・サマリー・レスポンスだけ表示 |
| Feature | ステータスライン refreshInterval | ステータスラインコマンドを N 秒ごとに再実行 |
| Feature | ステータスライン worktree 情報追加 | `workspace.git_worktree` を JSON 入力に追加 |
| Feature | /agents 稼働インジケーター | サブエージェントの `● N running` 表示 |
| Feature | Cedar ポリシーのシンタックスハイライト | `.cedar` / `.cedarpolicy` ファイル対応 |
| Fix | Bedrock 403 エラー（v2.1.96） | `AWS_BEARER_TOKEN_BEDROCK` 使用時のリグレッション修正 |
| Fix | Bedrock SigV4 認証（v2.1.97） | 空文字列の環境変数で認証失敗する問題を修正 |
| Fix | Bash ツールのパーミッション強化 | env-var prefix やネットワークリダイレクトのチェック強化 |
| Fix | MCP HTTP/SSE バッファリーク | 再接続時に ~50MB/h 蓄積する問題を修正 |
| Fix | MCP OAuth トークンリフレッシュ | `oauth.authServerMetadataUrl` が restart 後に無視される問題を修正 |
| Fix | 429 リトライのバックオフ | 小さな Retry-After で全リトライ消費する問題を修正 |
| Fix | /resume 関連バグ（8件） | 編集不可・検索消失・diff 消失・入力未保存など一括修正 |
| Fix | パーミッション管理の複数修正 | JS prototype 名、managed-settings 反映、additionalDirectories 競合 |
| Fix | サブエージェント worktree の cwd リーク | 親セッションの Bash ツールに作業ディレクトリが漏れる問題を修正 |
| Fix | NO_FLICKER モードの複数修正 | zellij レンダリング、URL コピー、メモリリーク、Windows スクロールなど |
| Fix | Hook 関連の修正 | Stop/SubagentStop が長セッションで失敗する問題を修正 |
| Fix | plugin update の判定修正 | git ベースプラグインで最新版を検出できない問題を修正 |
| Improvement | Accept Edits モードの自動承認拡張 | `LANG=C rm foo` のような安全なラッパー付きコマンドを自動承認 |
| Improvement | CJK 句読点後の補完対応 | 日本語・中国語入力後にスペースなしで `/` や `@` が使用可能に |
| Improvement | Bridge セッション表示改善 | claude.ai のセッションカードにローカルの Git リポジトリ・ブランチを表示 |
| Improvement | フッターレイアウト改善 | Focus・通知インジケーターがモード行に収まるように変更 |

## まとめ

v2.1.97 は Fix が中心で、特に `/resume` と NO_FLICKER の安定性が上がっています。MCP のバッファリーク修正は長時間セッションで確実に効くので、MCP を多用しているなら早めにアップデートしておきましょう。Bedrock を CI/CD で使っている場合は v2.1.96 → v2.1.97 の両方を適用してください。
