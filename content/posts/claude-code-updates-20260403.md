---
title: "【Claude Code】v2.1.90 リリースノートまとめ"
date: 2026-04-03T08:01:11+09:00
draft: false
tags: ["claude-code", "powerup", "performance", "powershell-security", "resume", "auto-mode"]
categories: ["Claude Code Updates"]
summary: "v2.1.90 のClaude Codeリリースノートまとめ。/powerupで対話型レッスン、パフォーマンス3件のO(n²)→O(n)改善、自動モードのユーザー境界尊重など19件"
---

![](/tech-pulse/images/claude-code-updates-20260403/header.png)

## はじめに

Claude Code v2.1.90 がリリースされました。新コマンド `/powerup` による対話型レッスン、パフォーマンス改善3件（いずれも O(n²) → O(n)）、PowerShell セキュリティ強化が主なトピックです。バグ修正は9件。`--resume` のキャッシュミス回帰や自動モードのユーザー指示無視など、日常的に引っかかる問題が潰されています。

## 注目アップデート深掘り

### /powerup — 対話型レッスン機能

Claude Code の機能をアニメーション付きデモで学べる `/powerup` コマンドが追加されました。

```
> /powerup
```

フック、MCP、スキルなど、ドキュメントを読むだけでは掴みにくい機能を実際に動くデモで体験できます。新しくチームに入ったメンバーのオンボーディングにも使えそうです。

### パフォーマンス改善 — 3つの O(n²) → O(n) 修正

![パフォーマンス改善の比較](/tech-pulse/images/claude-code-updates-20260403/performance.png)

今回のリリースで地味に効くのが、3箇所の二次時間計算量を線形に改善したパフォーマンス修正です。

1. **MCP ツールスキーマのキャッシュキー生成**: ターンごとに全 MCP ツールスキーマを `JSON.stringify` していた処理を除去
2. **SSE トランスポートのフレーム処理**: 大きなストリーミングフレームの処理が二次時間だったのを線形に
3. **SDK セッションのトランスクリプト書き込み**: 長い会話でトランスクリプト書き込みが二次時間で遅くなっていたのを線形に

> **SSE（Server-Sent Events）トランスポートとは？**
> Claude Code がモデルからのストリーミング応答を受信する際の通信方式です。HTTP 上でサーバーからクライアントへの一方向リアルタイム通信を行います。

MCP サーバーを複数接続している環境や、長時間セッションで体感速度が落ちていた場合、アップグレードで改善するはずです。

### --resume のプロンプトキャッシュミス回帰修正

v2.1.69 以降、deferred tools・MCP サーバー・カスタムエージェントを使っているユーザーで `--resume` 時に最初のリクエストのプロンプトキャッシュが完全にミスする回帰がありました。キャッシュミスはレイテンシとコストの両方に響くので、対象ユーザーには体感で分かる改善です。

## 実用的な活用ポイント

自動モードで「don't push」「wait for X before Y」といったユーザー指示が無視されるバグが修正されました。自動モードを使っているなら、意図しない操作が実行されるリスクが減ります。

> **PostToolUse フックとは？**
> Claude Code がツール（Edit, Write, Bash等）を実行した直後に自動実行されるシェルコマンドです。`settings.json` で設定し、ファイル編集後の自動フォーマットや自動リントに使います。

PostToolUse フックで format-on-save（prettier 等）を動かしている場合、連続した Edit/Write で「File content has changed」エラーが出ていた問題も修正されています。フック経由でファイルが書き換わるケースでの競合が解消されました。

`/resume` の全プロジェクト一覧がセッションを並列ロードするようになり、プロジェクト数が多い環境での表示が速くなっています。`--resume` ピッカーから `claude -p` や SDK 経由のセッションが除外されるようになり、一覧も見やすくなりました。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | `/powerup` コマンド追加 | アニメーション付きデモで Claude Code 機能を学べる |
| Feature | `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` 環境変数 | オフライン環境で `git pull` 失敗時もマーケットプレイスキャッシュを保持 |
| Feature | `.husky` を保護ディレクトリに追加 | acceptEdits モードでの誤編集を防止 |
| Fix | レート制限ダイアログの無限ループ | 使用量上限到達時にダイアログが繰り返し開いてクラッシュ |
| Fix | `--resume` プロンプトキャッシュミス | deferred tools/MCP/カスタムエージェント使用時の回帰（v2.1.69以降） |
| Fix | Edit/Write「File content has changed」 | PostToolUse の format-on-save フックとの競合を解消 |
| Fix | PreToolUse フックの exit code 2 処理 | JSON stdout + exit code 2 でツール呼び出しがブロックされない問題 |
| Fix | 検索/読み取りサマリーバッジの重複表示 | CLAUDE.md 自動読み込み時にバッジが複数表示される |
| Fix | 自動モードのユーザー境界無視 | 「don't push」等の明示的な制約を尊重するよう修正 |
| Fix | ライトテーマでのホバーテキスト不可視 | click-to-expand テキストの視認性を改善 |
| Fix | パーミッションダイアログの UI クラッシュ | 不正なツール入力時の異常終了を修正 |
| Fix | 選択画面のヘッダー消失 | `/model`、`/config` 等のスクロール時にヘッダーが消える問題 |
| Security | PowerShell ツール権限チェック強化 | trailing `&` バイパス、`-ErrorAction Break` ハング、TOCTOU、フォールバック劣化を修正 |
| Security | DNS キャッシュコマンドの自動許可除去 | `Get-DnsClientCache` / `ipconfig /displaydns` をプライバシー保護のため除外 |
| Performance | MCP ツールスキーマの JSON.stringify 除去 | キャッシュキー生成のターンごとシリアライズを排除 |
| Performance | SSE フレーム処理の線形化 | 大きなフレームの処理が O(n²) → O(n) |
| Performance | トランスクリプト書き込みの線形化 | 長い会話での書き込みが O(n²) → O(n) |
| Improvement | `/resume` 一覧の並列ロード | 全プロジェクトセッションの読み込みを並列化 |
| Change | `--resume` ピッカーのフィルタリング | `claude -p` や SDK セッションを非表示に |

## まとめ

v2.1.90 は `/powerup` が新機能の目玉ですが、パフォーマンス修正3件の方が日常的なインパクトは大きいかもしれません。MCP サーバーを複数使っている環境や、長いセッションを `--resume` で継続している場合、体感速度が変わるはずです。PowerShell 周りのセキュリティ強化も4つのベクトルをまとめて塞いでおり、Windows 環境での利用がより安全になっています。
