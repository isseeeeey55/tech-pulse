---
title: "【Claude Code】v2.1.88 リリースノートまとめ"
date: 2026-03-31T09:00:00+09:00
draft: false
tags: ["claude-code", "alt-screen", "hooks", "subagents", "prompt-cache", "performance", "voice-mode", "windows"]
categories: ["Claude Code Updates"]
summary: "v2.1.88 のClaude Codeリリースノートまとめ。フリッカーフリー描画、PermissionDenied hook、名前付きサブエージェント@メンション、プロンプトキャッシュ修正など30件以上の変更"
---

![](/tech-pulse/images/claude-code-updates-20260331/header.png)

## はじめに

Claude Code v2.1.88 がリリースされました。今回は新機能3件、バグ修正24件、改善4件を含む大型リリースです。長時間セッションでのプロンプトキャッシュミス修正やメモリリーク解消など、安定性に関わる修正が多く含まれています。

## 注目アップデート深掘り

![主要な変更点](/tech-pulse/images/claude-code-updates-20260331/highlights.png)

### フリッカーフリー描画モード（CLAUDE_CODE_NO_FLICKER）

環境変数 `CLAUDE_CODE_NO_FLICKER=1` を設定すると、alt-screen レンダリングで画面のちらつきが解消されます。仮想化されたスクロールバックも有効になります。

```bash
# .bashrc / .zshrc / config.fish に追加
export CLAUDE_CODE_NO_FLICKER=1
```

ストリーミング中に画面がちらつく問題は、特に tmux + iTerm2 環境で顕著でした。このフラグで opt-in できるようになっています。

### PermissionDenied hook

自動モード（`--auto`）で、コマンド実行の可否を判定する内部の分類器（クラシファイア）が「危険」と判断して拒否した際に発火する `PermissionDenied` hook が追加されました。`{retry: true}` を返すとモデルにリトライを指示できます。

```json
{
  "hooks": {
    "PermissionDenied": [
      {
        "matcher": "",
        "command": "echo '{\"retry\": true}'"
      }
    ]
  }
}
```

自動モードで作業中に意図しない拒否が発生した場合のリカバリを自動化できます。拒否されたコマンドは `/permissions` の Recent タブにも表示されるようになりました。

### 名前付きサブエージェントの@メンション

`@` メンションのタイプアヘッドに、名前付きサブエージェントが候補として表示されるようになりました。複数のサブエージェントを使い分ける場合に、宛先の指定が楽になります。

### プロンプトキャッシュミスの修正（長時間セッション）

長時間セッション中にツールスキーマのバイト列が変わることで、プロンプトキャッシュが効かなくなるバグが修正されました。長いセッションでトークン消費が増えていた原因の一つです。

あわせて、ネストされた CLAUDE.md が長時間セッションで何十回も再注入される問題も修正されています。

### StructuredOutput スキーマキャッシュバグの修正

複数スキーマを使うワークフローで `StructuredOutput` の失敗率が約50%になるバグが修正されました。SDK 連携でスキーマを切り替えている場合に影響がありました。

### その他の主要な修正

- **メモリリーク修正**: 大きな JSON 入力が LRU キャッシュキーとして保持され続ける問題を解消
- **巨大ファイル Edit 時の OOM クラッシュ修正**: 1GiB 超のファイルで発生していた問題に対応
- **CJK/絵文字の履歴消失修正**: `~/.claude/history.jsonl` の 4KB 境界で CJK やデスクリプタが含まれるエントリが消える問題を修正
- **Edit/Write の CRLF 二重化修正**: Windows で改行が二重になる問題と Markdown ハードラインブレイクが消える問題を修正
- **LSP サーバーのゾンビ状態修正**: クラッシュ後にサーバーが自動再起動するようになりました
- **hooks の `if` 条件修正**: 複合コマンド（`ls && git push`）や環境変数プレフィックス付きコマンド（`FOO=bar git push`）にマッチしなかった問題を修正
- **Voice モード修正**: macOS Apple Silicon でのマイク権限、Windows での WebSocket エラー、push-to-talk の修飾キー問題を修正
- **/stats 修正**: 30日超の履歴データ消失とサブエージェント/フォークのトークン計上漏れを修正

### 動作変更

- **Thinking サマリーがデフォルトOFF**: 対話セッションでの Thinking サマリーはデフォルトで非表示になりました。`showThinkingSummaries: true` で復元できます
- **`/env` が PowerShell にも適用**: 以前は Bash のみでしたが、PowerShell でも有効になりました

## 全変更点一覧

| カテゴリ | 内容 |
|---------|------|
| New | `CLAUDE_CODE_NO_FLICKER=1` フリッカーフリー alt-screen 描画 |
| New | `PermissionDenied` hook（自動モード拒否時にリトライ指示可能） |
| New | 名前付きサブエージェントの `@` メンションタイプアヘッド対応 |
| Fix | 長時間セッションのプロンプトキャッシュミス |
| Fix | ネストされた CLAUDE.md の複数回再注入 |
| Fix | Edit/Write の CRLF 二重化・Markdown ハードラインブレイク消失（Windows） |
| Fix | StructuredOutput スキーマキャッシュバグ（~50% 失敗率） |
| Fix | 大きな JSON 入力によるメモリリーク |
| Fix | 1GiB 超ファイルの Edit 時 OOM クラッシュ |
| Fix | 50MB超セッションファイルのメッセージ削除時クラッシュ |
| Fix | `--resume` の旧バージョンツール結果によるクラッシュ |
| Fix | レート制限エラーメッセージの誤表示 |
| Fix | LSP サーバーのクラッシュ後ゾンビ状態 |
| Fix | hooks `if` 条件の複合コマンド・環境変数プレフィックス対応 |
| Fix | CJK/絵文字を含む履歴エントリの 4KB 境界消失 |
| Fix | /stats の30日超データ消失・サブエージェントトークン計上漏れ |
| Fix | 長時間セッションでのスクロールバック消失 |
| Fix | 検索/読取グループバッジの重複表示 |
| Fix | 通知 `invalidates` の即時クリア |
| Fix | バックグラウンドメッセージ到着時のプロンプト消失 |
| Fix | `/btw` の長文レスポンスクリップ |
| Fix | Devanagari 等の結合文字の切り詰め |
| Fix | メインスクリーン端末のレイアウトシフト後の描画アーティファクト |
| Fix | Voice モード: macOS Apple Silicon マイク権限 |
| Fix | Voice push-to-talk の修飾キーコンボ |
| Fix | Voice モード: Windows WebSocket エラー |
| Fix | Shift+Enter の動作（Windows Terminal Preview 1.25） |
| Fix | tmux + iTerm2 でのストリーミング中 UI ジッター |
| Fix | PowerShell の stderr 書き込みによる誤報告（Windows 5.1） |
| Fix | SDK エラーメッセージの `is_error: true` 設定漏れ |
| Fix | Ctrl+B でのバックグラウンド化時のタスク通知消失 |
| Fix | PreToolUse/PostToolUse hooks の `file_path` 絶対パス化 |
| Improve | PowerShell プロンプトのバージョン別構文ガイダンス |
| Change | Thinking サマリーがデフォルト OFF |
| Change | 自動モード拒否コマンドの通知・`/permissions` Recent 表示 |
| Change | `/env` が PowerShell にも適用 |
| Change | `/usage` の冗長な週間バー非表示（Pro/Enterprise） |
| Improve | ls/tree/du のツールサマリー表示改善 |
| Improve | 画像ペースト時の末尾スペース除去 |
| Improve | `!command` ペースト時の bash モード自動切り替え |

## まとめ

v2.1.88 は安定性とパフォーマンスに注力した大型リリースです。特に長時間セッションでのプロンプトキャッシュミスとメモリリークの修正は、トークン消費とメモリ使用量の両方に効きます。`CLAUDE_CODE_NO_FLICKER=1` は tmux ユーザーなら試す価値があります。`PermissionDenied` hook も自動モードのワークフロー改善に使えるので、hooks を活用している方はチェックしてみてください。
