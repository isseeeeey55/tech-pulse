---
title: "【Claude Code】v2.1.205・v2.1.204 リリースノートまとめ"
date: 2026-07-09T08:01:25+09:00
draft: false
tags: ["claude-code", "auto-mode", "json-schema", "hook", "mcp", "sessionstart"]
categories: ["Claude Code Updates"]
summary: "v2.1.205・v2.1.204 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260709/header.png)

# Claude Code v2.1.205・v2.1.204 リリース情報

## はじめに

2026年7月9日に、Claude Code の v2.1.205 と v2.1.204 がリリースされました。v2.1.205 では、セッション記録ファイルの改ざん防止、JSON スキーマ検証の修正、背景エージェント状態管理の改善、Windows 環境の安定性向上など、15件以上の修正と機能改善が行われました。v2.1.204 では、ヘッドレスセッションにおける Hook イベントストリーミングの不具合が修正されています。いずれも信頼性と安全性の向上を目的としたメンテナンスリリースです。

## 注目アップデート深掘り

### セッション記録ファイルの改ざん防止（v2.1.205）

v2.1.205 では、auto mode においてセッション記録（transcript）ファイルへの改ざんをブロックするルールが追加されました。これにより、Claude が過去の会話履歴や実行ログを不正に書き換えることが防止されます。

また、背景タスク通知では「人間による入力が行われていないこと」が明示的に記載されるようになり、記録内に捏造された承認がそのまま実行されることを防ぐ仕組みが強化されました。これらの変更は、Claude Code のセッション管理における透明性と監査可能性を高める重要な改善です。

### `--json-schema` の検証エラー修正（v2.1.205）

従来、`--json-schema` オプションに無効なスキーマを渡した場合、エラーが表示されず構造化されていない出力が生成されてしまう問題がありました。また、`format` キーワードを使用したスキーマが拒否される不具合も存在していました。

v2.1.205 では、これらの問題が修正され、スキーマ検証が適切に行われるようになりました。無効なスキーマが渡された場合は明確にエラーが通知され、`format` キーワードを含むスキーマも正しく受理されます。

### 破壊的操作の安全性向上（v2.1.205）

auto mode において、`rm -rf` コマンドが変数を含む形で実行される際、その変数がコンテキストから解決できない場合に、実行前に確認を求めるよう改善されました。これにより、意図しないファイル削除のリスクが軽減されます。

### ヘッドレスセッションの Hook イベントストリーミング修正（v2.1.204）

v2.1.204 では、ヘッドレスセッションにおいて SessionStart Hook 実行中に Hook イベントがストリーミングされない不具合が修正されました。この問題により、リモートワーカーが Hook 処理中にアイドル状態と誤認識され、不正に終了させられることがありました。修正により、長時間実行される Hook 処理が途中で中断されるリスクが解消されています。

> **Note:** Hook は、セッション開始時などに任意のスクリプトを自動実行する仕組みです。

## 実用的な活用ポイント

v2.1.205 では、背景エージェントの状態表示とセッション管理機能が大幅に改善されました。`claude agents` コマンドで表示されるエージェント一覧において、セッションが既存の Pull Request を編集・マージ・コメント・プッシュした場合に PR へのリンクが表示されるようになりました。また、各行には色付きの状態ワードと classifier が生成した見出しが表示され、ブロックされたセッションでは詳細なステータスと正確な問い合わせ内容が確認できます。

`/doctor` コマンドが拡張され、セットアップ全体をチェックして問題を診断・修正できる機能となりました。`/checkup` はそのエイリアスとして利用できます。

自動更新時のバイナリダウンロードがメモリバッファではなくディスクへの直接ストリーミングに変更され、updater のピークメモリ使用量が約 400 MB 削減されました。

v2.1.204 の修正により、ヘッドレスセッションで長時間実行される Hook を安全に利用できるようになりました。

## 全変更点一覧

### v2.1.205

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | auto mode rule for transcript tampering | セッション記録ファイルへの改ざんをブロックするルールを追加 |
| Fix | `--json-schema` validation | 無効なスキーマ時にエラーを表示せず非構造化出力を生成していた問題と、`format` キーワード使用時の拒否問題を修正 |
| Fix | Message loss at `--max-turns` | Claude 作業中に送信されたメッセージが `--max-turns` 制限でターン終了時に失われる問題を修正 |
| Fix | Windows worktree removal | NTFS junction やディレクトリシンボリックリンク存在時に worktree 外のファイルを削除してしまう問題を修正 |
| Fix | Background agent status display | `SendMessage` で再開した背景エージェントがエージェント一覧で "failed" または "completed" と表示され続ける問題を修正 |
| Fix | Background job status flip | エージェントのターンに読み取り可能なテキストがない場合に、背景ジョブが "needs input" から "working" に戻る問題を修正 |
| Fix | `claude attach` with upgrading agent | 背景エージェントがアップグレード再起動中に `claude attach` がエラーになる問題を修正（復帰を待機するように変更） |
| Fix | Session-to-PR linking | Bash 呼び出しで作成された PR の出力が 30K inline 制限を超えた場合にリンクが失われる問題を修正 |
| Fix | `claude mcp add-from-claude-desktop` | サーバー名に非対応文字が含まれる場合にスタックする問題を修正（無効な名前を報告し、残りのサーバーはインポート継続） |
| Fix | Plugin LSP server initialization | 初期化に失敗したプラグイン LSP サーバーが、同じ拡張子を扱う別の有効な LSP サーバーを妨げる問題を修正 |
| Fix | Windows crash on directory removal | Claude 起動ディレクトリがコマンド実行中に削除・ロック・アンマウントされた際のクラッシュを修正 |
| Fix | File watcher crash | ディレクトリスキャン実行中にファイルウォッチャーがクローズされた際のクラッシュを修正 |
| Fix | Project verify skills rewrite | ドキュメント化されたコマンド変更時のみでなく、毎セッション書き換えられていた問題を修正 |
| Fix | Agent view rendering | ジョブリストが画面を僅かにオーバーフローした際にヘッダーが1行上に描画され切れる問題を修正 |
| Fix | Web/mobile Remote Control stale status | メンバーシップ変更時に背景タスクが古い "Running" ステータスを表示する問題を修正（完全なタスク状態を転送） |
| Fix | Cowork VM-mode local-agent sessions | CLI 2.1.203 以降で "Not logged in · Please run /login" エラーで起動失敗する問題を修正 |
| Improvement | Auto mode `rm -rf` safety | コンテキストから解決できない変数に対する `rm -rf` 実行前に確認を求めるように改善 |
| Improvement | Auto-update memory usage | バイナリダウンロードをディスクストリーミングに変更し、updater のピークメモリ使用量を約 400 MB 削減 |
| Improvement | Background task notifications | 人間の入力が行われていないことを明示し、記録内の捏造承認が実行されることを防止 |
| Improvement | Agent view PR linking | 既存 PR を編集・マージ・コメント・プッシュしたセッションを `claude agents` でリンク表示 |
| Improvement | Agent view display | 色付き状態ワードと classifier 生成見出しを表示、ブロックされたセッションでは詳細ステータスと正確な問い合わせ内容を表示 |
| Improvement | `/doctor` command | セットアップチェックと診断・修正機能を備えたフルチェックアップに拡張（`/checkup` はエイリアス） |
| Feature | Reserved MCP server name | Claude Desktop ペイン名変更に先立ち、"Claude Browser" MCP サーバー名を予約（"Claude Preview" と同様、ユーザー設定では使用不可） |

### v2.1.204

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Fix | Hook event streaming | ヘッドレスセッションの SessionStart Hook 実行中に Hook イベントがストリーミングされず、リモートワーカーがアイドル判定で終了される問題を修正 |

## まとめ

v2.1.205 と v2.1.204 は、Claude Code の信頼性と安全性を高めるためのメンテナンスリリースです。v2.1.205 では、セッション記録の改ざん防止、JSON スキーマ検証の正常化、破壊的操作前の確認強化など、多岐にわたる修正が行われました。特に背景エージェントの状態管理と表示機能の改善により、複数セッションの監視と管理が容易になっています。v2.1.204 では、ヘッドレスセッションにおける Hook 実行の安定性が確保されました。いずれも、日常的な開発ワークフローにおける信頼性を底上げする重要な改善です。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)