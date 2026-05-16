---
title: "【Claude Code】v2.1.143・v2.1.142 リリースノートまとめ"
date: 2026-05-16T08:01:12+09:00
draft: false
tags: ["claude-code", "background-agents", "plugins", "powershell", "mcp", "worktree"]
categories: ["Claude Code Updates"]
summary: "v2.1.143・v2.1.142 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260516/header.png)

## はじめに

Claude Code が 2 リリース連続で更新されました。**v2.1.142**（2026-05-14 UTC）と **v2.1.143**（2026-05-15 UTC）です。両リリースとも、`claude agents` / `/bg` に代表されるバックグラウンドエージェント運用まわりの設定オプション拡充と、Windows・macOS・MCP の修正が中心です。v2.1.142 では Fast モードが Opus 4.7 へ既定で更新され、v2.1.143 では PowerShell ツールが `-ExecutionPolicy Bypass` で起動するなど、Windows での実用性が一段上がっています。

> **Note:** MCP (Model Context Protocol) は、Claude Code が外部ツールやデータソースと連携するための仕組みです。

## 注目アップデート深掘り

### `claude agents` のフラグ群拡充とバックグラウンド継承（v2.1.142 + v2.1.143）

`claude agents` に多数の新フラグが追加され、バックグラウンドで起動するセッションのコンテキストを呼び出し側から細かく指定できるようになりました。

v2.1.142 で追加されたのは `--add-dir` / `--settings` / `--mcp-config` / `--plugin-dir` / `--permission-mode` / `--model` / `--effort` / `--dangerously-skip-permissions` の 8 つのフラグです。v2.1.143 では、これらが `claude agents` のダッシュボードと、そこから派生する個別セッションの両方に適用されるようになりました。

あわせて `/bg` および ← デタッチでも `--mcp-config` / `--settings` / `--add-dir` / `--plugin-dir` / `--strict-mcp-config` / `--fallback-model` / `--allow-dangerously-skip-permissions` が引き継がれるようになり、再開後のバックグラウンドワーカーが同じ MCP サーバー・設定・フォールバックモデルを保持します。複数のリポジトリやテナントを行き来する運用で、毎回 `/mcp` や設定再読込をやり直す必要がなくなります。

### PowerShell ツールの ExecutionPolicy Bypass（v2.1.143）

v2.1.143 で、Claude Code 内部の PowerShell ツールが `-ExecutionPolicy Bypass` 付きで PowerShell を起動するようになりました。実行ポリシーで `Restricted` などが設定されている環境でも、Claude Code 経由のスクリプト実行がブロックされなくなります。オプトアウトは環境変数 `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY=1` です。

同リリースで、Bedrock / Vertex / Foundry を使う Windows ユーザーでは PowerShell ツールが既定で有効化されました（無効化は `CLAUDE_CODE_USE_POWERSHELL_TOOL=0`）。エンタープライズ配布された Windows 端末で、Claude Code がシェルとして PowerShell を経由するルートが標準になります。

## 実用的な活用ポイント

- **Fast モードが Opus 4.7 に**（v2.1.142）: 既定モデルが Opus 4.6 → 4.7。旧版に固定したい場合は `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE=1`。
- **`worktree.bgIsolation: "none"`**（v2.1.143）: バックグラウンドセッションが worktree を作らず作業コピーを直接編集できる設定が追加。サブモジュール多用・ローカル変更が多い・worktree 運用が難しいリポジトリ向け。
- **MCP の 60 秒上限解消**（v2.1.142）: リモート HTTP / SSE の MCP サーバーで `MCP_TOOL_TIMEOUT` が反映されず 60 秒で打ち切られていた問題を修正。長時間ツールコールが実用になります。
- **macOS スリープ／復帰**（v2.1.142）: macOS のスリープ・ウェイクでバックグラウンドセッションが消失／デーモン再接続が失敗していた問題を、時刻ジャンプ検知で修正。
- **Windows ネットワークドライブ**（v2.1.142）: `claude agents` がネットワークドライブ上の作業ディレクトリでデッドロックする問題を修正。起動中の Ctrl+C も効くようになりました。
- **stop hook の無限ブロック対策**（v2.1.143）: stop hook が繰り返しブロックし続けるとターンが終わらない問題に、8 回連続ブロックでターン終了する上限が追加（`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` で調整可）。
- **`/plugin` マーケットプレースにトークン見積もり**（v2.1.143）: マーケットプレースの一覧画面に、プラグインごとのターン単位・呼び出し単位のトークン消費見積もりが表示されます。プラグイン選定時の参考に。
- **プラグイン依存関係の強制**（v2.1.143）: `claude plugin disable` は依存している別プラグインがあれば拒否（解除手順のヒント付き）、`claude plugin enable` は推移的な依存を自動有効化します。
- **macOS の `~/Documents`・`~/Desktop`・`~/Downloads` の "Operation not permitted"**（v2.1.143）: フルディスクアクセスを付与してもバックグラウンドジョブが読めなかった問題を修正。

## 主な変更点一覧

| カテゴリ | バージョン | 内容 | 概要 |
|---------|---------|------|------|
| Feature | v2.1.142 | `claude agents` の新フラグ群 | `--add-dir` / `--settings` / `--mcp-config` / `--plugin-dir` / `--permission-mode` / `--model` / `--effort` / `--dangerously-skip-permissions` |
| Feature | v2.1.142 | Fast モードを Opus 4.7 に既定変更 | 旧 Opus 4.6 への固定は `CLAUDE_CODE_OPUS_4_6_FAST_MODE_OVERRIDE=1` |
| Feature | v2.1.142 | ルート `SKILL.md` を Skill として認識 | `skills/` サブディレクトリなしのプラグインも Skill 公開可能に |
| Feature | v2.1.143 | プラグイン依存関係の強制 | `disable` は依存があれば拒否、`enable` は推移的依存を自動有効化 |
| Feature | v2.1.143 | `/plugin` マーケットプレースにトークン見積もり表示 | ターン単位・呼び出し単位のコスト推計 |
| Feature | v2.1.143 | `worktree.bgIsolation: "none"` 設定 | バックグラウンドセッションが worktree を使わず作業コピーを直接編集 |
| Improvement | v2.1.143 | PowerShell ツールが `-ExecutionPolicy Bypass` で起動 | Bedrock / Vertex / Foundry の Windows で既定有効化 |
| Improvement | v2.1.143 | アイドル復帰後のモデル／effort 保持 | 起動時の `--model` / `--effort` をウェイク後も維持 |
| Improvement | v2.1.143 | `/bg`・← デタッチで MCP・設定・フォールバックモデルを継承 | 再開後のワーカーが同じ設定で起動 |
| Fix | v2.1.142 | リモート MCP の `MCP_TOOL_TIMEOUT` 不反映 | HTTP / SSE で 60 秒上限に貼り付いていた問題を修正 |
| Fix | v2.1.142 | バックグラウンドが既存 worktree を認識せず Edit がブロック | `EnterWorktree` の重複作成拒否と組み合わさるデッドロックを解消 |
| Fix | v2.1.142 | macOS スリープ／復帰でセッション消失 | デーモンが時刻ジャンプを検知してアイドル誤判定を回避 |
| Fix | v2.1.142 | Windows ネットワークドライブで `claude agents` がデッドロック | 起動中の Ctrl+C も効くように修正 |
| Fix | v2.1.143 | stop hook の無限ブロック | 8 回連続で警告と共にターン終了（`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP` で調整可） |
| Fix | v2.1.143 | macOS `~/Documents` 等で "Operation not permitted" | バックグラウンドジョブの読み取り問題を修正 |
| Fix | v2.1.143 | `/bg` 単体実行で "continue" が送信される | プロンプトなしのフォークが入力待ちで止まるように修正 |

## まとめ

2 リリースを通じて、バックグラウンドエージェント運用（`claude agents`・`/bg`・← デタッチ）が大きく前進しました。`--add-dir` / `--settings` / `--mcp-config` などのフラグで起動時のコンテキストが完全に指定でき、再開後にも MCP・設定・フォールバックモデルが引き継がれます。Windows では PowerShell ツールの `-ExecutionPolicy Bypass` 化とネットワークドライブのデッドロック修正、macOS ではスリープ／復帰時のセッション消失や `~/Documents` 配下のアクセス問題が片付き、プラットフォーム横断で安定性が底上げされています。Fast モードの Opus 4.7 化も含め、日常的に Claude Code を回している環境ほど更新価値が大きい 2 本です。

- 公式リリースノート: <https://github.com/anthropics/claude-code/releases/tag/v2.1.143> / <https://github.com/anthropics/claude-code/releases/tag/v2.1.142>
- 公開日時: 2026-05-15 22:28 UTC / 2026-05-14 22:55 UTC

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
