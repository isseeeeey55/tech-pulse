---
title: "【Claude Code】v2.1.193 リリースノートまとめ"
date: 2026-06-26T08:01:17+09:00
draft: true
tags: ["claude-code", "auto-mode", "opentelemetry", "mcp", "bash", "powershell"]
categories: ["Claude Code Updates"]
summary: "v2.1.193 のClaude Codeリリースノートまとめ"
---

## はじめに

Claude Code v2.1.193 がリリースされました。このバージョンでは、自動モード（auto-mode）におけるシェルコマンド分類の制御強化、OpenTelemetry ログイベントの拡充、バックグラウンドエージェント周りの複数の不具合修正、MCP サーバー認証フローの改善など、運用性とセキュリティに関わる幅広いアップデートが行われています。

---

## 注目アップデート深掘り

### 1. 自動モード分類の全シェルコマンド適用オプション

新たに `autoMode.classifyAllShell` 設定が追加されました。これにより、従来は任意コード実行パターンのみを対象としていた自動モード分類器を、すべての Bash/PowerShell コマンドに適用できるようになります。

**背景と重要性**  
自動モードは、Claude がユーザーに確認を求めるべき操作とそうでない操作を分類する仕組みです。従来は特定パターンのコマンドのみが分類対象でしたが、この設定を有効化することで、すべてのシェルコマンドを分類器に通すことが可能になり、より細かい制御が実現します。

また、今回のリリースでは自動モードによる拒否理由が、トランスクリプト・拒否トースト・`/permissions` の最近の拒否履歴に記録されるようになりました。これにより、どのコマンドがなぜ自動実行されなかったのかが透明化され、運用時のトラブルシューティングが容易になります。

### 2. OpenTelemetry ログへのモデル応答テキスト追加

`claude_code.assistant_response` という新しい OpenTelemetry ログイベントが追加され、モデルの応答テキストが記録されるようになりました。デフォルトでは応答内容は編集（Redacted）されますが、`OTEL_LOG_ASSISTANT_RESPONSES=1` を設定することで記録できます。

**注意点**  
この環境変数が未設定の場合、既存の `OTEL_LOG_USER_PROMPTS` の設定に従います。つまり、すでにユーザープロンプトをログ出力している環境では、アップグレード後に応答内容も自動的にログに含まれるようになります。プロンプトのみをログ出力したい場合は、明示的に `OTEL_LOG_ASSISTANT_RESPONSES=0` を設定する必要があります。

---

## 実用的な活用ポイント

バックグラウンドエージェントやシェルコマンド実行の安定性が向上しており、特にメモリ逼迫時のバックグラウンドシェルコマンド自動刈り込み機能は長時間稼働するセッションで有用です（無効化するには `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` を設定）。

MCP サーバーの認証が必要な場合、起動時に `/mcp` へ誘導する通知が表示されるようになったほか、401/403 エラー時に `headersHelper` が自動再実行・再接続を行うようになり、認証フローがよりスムーズになりました。

また、bash モード（`!`）でのファイルパスライブ自動補完が追加され、コマンド入力の効率が向上しています。プラグインのマーケットプレース `renames` マップも自動追従されるため、設定ファイルを手動更新する手間が削減されます。

---

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | `autoMode.classifyAllShell` 設定の追加 | すべての Bash/PowerShell コマンドを自動モード分類器に通すオプション |
| Feature | 自動モード拒否理由の記録 | トランスクリプト・トースト・`/permissions` 最近の拒否履歴に拒否理由を追加 |
| Feature | `claude_code.assistant_response` OpenTelemetry ログイベント追加 | モデル応答テキストをログ出力（`OTEL_LOG_ASSISTANT_RESPONSES` で制御） |
| Feature | bash モード（`!`）にファイルパスライブ自動補完を追加 | コマンド入力時にファイルパスを補完 |
| Feature | MCP サーバー認証が必要な場合の起動通知 | `/mcp` への誘導通知を表示 |
| Feature | バックグラウンドシェルコマンドのメモリ逼迫時自動刈り込み | メモリ圧迫時にアイドルコマンドを自動終了（`CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` で無効化可） |
| Fix | `/login` 直後に `/model` 等のクライアントデータ依存 UI が古い/空の状態を表示する問題を修正 | ログイン後に UI が即座に最新状態を反映するよう修正 |
| Fix | バックグラウンド化（←←）時に全タスクが引き継がれるにもかかわらず誤って「N background tasks would be abandoned」でキャンセルされる問題を修正 | タスク引き継ぎロジックの不具合を解消 |
| Fix | 固定されたバックグラウンドエージェントが自動更新のたびに「Continue from where you left off」と再プロンプトされる問題を修正 | 自動更新後のエージェント状態保持を改善 |
| Fix | メインターンのバックグラウンド化時にメイン会話を再実行する幽霊のような「general-purpose (resumed)」サブエージェントが生成される問題を修正 | バックグラウンド化時の不要なサブエージェント生成を防止 |
| Fix | サブエージェント表示中にエージェントパネルが兄弟エージェントを隠す問題を修正 | エージェント階層の表示不具合を解消 |
| Improvement | バックグラウンドエージェント起動結果の改善 | Claude に「end your response」と指示せず、エージェント実行中に他のタスクを継続可能に |
| Improvement | MCP `headersHelper` 認証の改善 | ツール呼び出しが 401/403 を返した際にヘルパーが自動再実行・再接続 |
| Improvement | プラグイン自動リネームの改善 | マーケットプレース `renames` マップを自動追従し、設定を新名称に自動更新 |
| Improvement | `/add-dir` メッセージの改善 | ディレクトリがすでに作業ディレクトリに含まれている場合のメッセージを改善 |

---

## まとめ

v2.1.193 は、自動モード分類の柔軟性向上、OpenTelemetry ログの拡充、バックグラウンドエージェントおよびシェル実行周りの複数の不具合修正、MCP 認証フローの自動化など、運用性とセキュリティの強化を中心としたアップデートです。特にバックグラウンドタスク管理やエージェント UI の安定性が向上しており、長時間稼働や複雑なワークフローでの利用がよりスムーズになります。OpenTelemetry ログ出力を活用している環境では、環境変数の見直しを行うことで、必要なログレベルを維持できます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)