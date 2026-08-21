---
title: "【Claude Code】v2.1.238・v2.1.237 リリースノートまとめ"
date: 2026-08-21T08:01:38+09:00
draft: false
tags: ["claude-code", "keybindings", "plugin", "marketplace", "self-hosted-runner", "mcp", "remote-control", "output-style", "concise"]
categories: ["Claude Code Updates"]
summary: "v2.1.238・v2.1.237 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260821/header.png)

## はじめに

2026年8月21日、Claude Code の v2.1.238 および v2.1.237 がリリースされました。v2.1.238 では長時間セッションにおけるメモリリーク修正、プラグインマーケットプレイスの認証機構強化、セルフホストランナーのグレースフルシャットダウン機能など多数の改善が行われました。v2.1.237 では LLM ゲートウェイ経由でのプロンプトキャッシング不具合修正と、新たな「Concise」出力スタイルが追加されています。

## 注目アップデート深掘り

### 長時間セッションのメモリ管理改善

v2.1.238 では、長時間対話セッションにおけるメモリ無制限増加の問題が修正されました（"Fixed unbounded memory growth in long interactive sessions"）。subagent のツール実行結果が最近の表示ウィンドウから外れた後に適切に解放されるようになり、長期間動作させるセッションでも安定性が向上します。

### プラグインマーケットプレイスの認証強化

v2.1.238 では、プラグインマーケットプレイスに `headersHelper` 機能が追加されました。URL マーケットプレイスまたはカタログエントリに対して、短命なトークンなど HTTP ヘッダーを生成するコマンドを実行できます。カタログエントリの `headersHelper` はプラグインのインストールまたは更新時にのみ実行され、コマンドが表示された後に `claude plugin install/update` が `[y/N]` で確認を求める（または `-y` で自動承認）仕様となっています。

### Concise 出力スタイルの追加

v2.1.237 では、新しい組み込み出力スタイル「Concise」が追加されました。このスタイルでは、Claude が結果を先頭に提示し、前置きや説明を省略する一方で、作業自体は徹底的に実行します（"Claude leads with results and skips preamble and narration, while doing the work just as thoroughly"）。`/config` から Output style で選択できます。

## 実用的な活用ポイント

長時間対話を伴うセッションでは、v2.1.238 のメモリリーク修正により安定性が向上します。プラグインマーケットプレイスを運用する場合、`headersHelper` を用いて短命トークンによる認証を実装し、インストール・更新時に明示的な確認プロンプトでセキュリティを確保できます。

LLM ゲートウェイやカスタムベース URL を使用する環境では、v2.1.237 のプロンプトキャッシング修正により、期待通りのキャッシュ動作が得られます。「Concise」出力スタイルは、結果を素早く確認したいワークフローに適しており、冗長な説明を省いて効率的な作業を実現します。

## 全変更点一覧

### v2.1.238

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | `keybindingFlavor` 設定追加 | `"readline"` 設定で Ctrl+W がホワイトスペースまで削除（Bash 風）、デフォルトは `"classic"` |
| Feature | プラグインマーケットプレイス `headersHelper` | 短命トークンなど HTTP ヘッダーを生成するコマンドをカタログ・アーカイブ取得時に実行 |
| Feature | カタログエントリ `headersHelper` | プラグインインストール/更新時にコマンド表示後 `[y/N]` 確認（`-y` で自動承認） |
| Feature | `--defer-shutdown-max-min` オプション | セルフホストランナーが SIGTERM 受信後、接続セッションを指定分数維持してから終了 |
| Feature | `--proxy-authorization-command` / `--proxy-authorization-file` | Egress プロキシ向けに接続ごとに新規 `Proxy-Authorization` ヘッダーを発行 |
| Fix | 長時間セッションのメモリリーク修正 | subagent ツール結果が表示ウィンドウ外に出た後に解放されるように |
| Fix | 出力スタイル設定の維持 | カスタム・プロジェクト・プラグイン出力スタイルがセッション途中でデフォルトに戻る問題を修正 |
| Fix | `CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION=true` 動作 | 利用制限近接時にプロンプト提案が維持されない問題を修正 |
| Fix | worktree-isolation Bash リダイレクト誤検出 | リダイレクトが無いコマンドでリダイレクト削除を促す誤ったメッセージを修正 |
| Fix | セルフホストランナーの誤削除 | 単一の遅延・紛失ポーリングでサーバーがランナーを削除し健全セッションを他ランナーに移す問題を修正 |
| Fix | MCP 誘導ダイアログの表示 | 4,096 文字超 URL で何も表示されない問題、およびパーミッションプロンプトで「再度尋ねない」オプション消失を修正 |
| Fix | `/tmp/claude-*-cwd` ファイル残留 | Bash コマンド kill、タイムアウト、中断時に一時ファイルが残る問題を修正 |
| Fix | Backspace 連続入力の無視 | Ctrl+H を Backspace として送信する端末でキーストークバースト時に無視される問題を修正 |
| Fix | パーミッションプロンプトのテキスト折り返し | 絵文字やタブを含む行がクリップされる問題を修正 |
| Fix | 中断セッションの端末状態 | Ctrl+Z 中断セッション終了時に bracketed-paste モード・カーソル非表示が残る問題を修正 |
| Fix | stdio MCP サーバーの初期化順序 | `initialize` 前に `server/discover` が送信され、遅延起動サーバーがセッション開始毎にバックエンド起動する問題を修正 |
| Fix | プロキシ接続拒否エラーメッセージ | プロキシ拒否が汎用ネットワークエラーとして報告され、プロキシ名が表示されない問題を修正 |
| Fix | `/model` と `/effort` キャッシュ警告 | プロンプトキャッシュ期限切れ時に不要なキャッシュミス警告が表示される問題を修正 |
| Fix | Remote Control タスクパネルの Stop 動作 | CLI ホストセッションで Stop が機能しない問題を修正 |
| Fix | リモートセッションの終了条件 | クライアントが無効な role のメッセージを送信した際にセッションが終了する問題を修正 |
| Fix | Remote Control 環境変数継承 | `claude remote-control` 起動時にシェルのセッションスコープ環境変数を継承する問題を修正 |
| Fix | クラッシュ Remote Control セッションの再利用 | プロセスクラッシュ後、`claude remote-control` 再起動まで利用不可になる問題を修正 |
| Fix | Remote Control メッセージ消失 | Web/Desktop から送信されたメッセージがターン終了後にトランスクリプトから消える問題を修正 |
| Fix | Remote Control モデル表示同期 | 電話・Web でのモデル選択が端末のモデル表示に反映されない問題を修正 |
| Fix | Remote Control 再接続エラー | ネットワーク瞬断でサインイン更新が遅延した際の "login expired" 切断を修正、リトライして接続維持 |
| Fix | サインアウト時の再接続エラー報告 | サインアウト時に再接続失敗を報告する代わりに、明確なメッセージでセッション終了 |
| Fix | `ListAgents`/`SendMessage` 接続エラー | `claude remote-control` / Desktop / IDE ホストで "Remote Control is not connected" エラーが表示される問題を修正 |
| Fix | `ListAgents` / `SendMessage` アイドルワーカー表示 | 次回バックグラウンドセッション用に事前準備されたワーカーが表示される問題を修正、タスク割り当て時のみ表示 |
| Improvement | クロスセッションメッセージング拒否通知 | `crossSessionInbound: "refuse"` セッションへの送信が成功として報告される代わりに "refused" を返す |
| Improvement | クロスセッションメッセージング配信失敗通知 | レート制限・キュー満杯で受信箱がメッセージをドロップした際、送信側に通知 |
| Improvement | macOS 起動高速化 | 素の `claude` コマンド起動が早くなる |
| Improvement | Bash ツールパーミッション検証 | シェル条件文での zsh 固有構文のチェックを改善 |
| Improvement | Remote Control 接続回復性 | ネットワークエッジ・VPN・プロキシによる HTTP 403 拒否を最大 3 分間許容、継続ブロック時に拒否元を表示 |
| Improvement | 起動時応答性向上 | 自動更新チェックを起動約 10 秒後に実行し、起動時 CPU 競合を回避 |
| Improvement | `claude-api` スキル更新 | Managed Agents 8/19 リリース対応: Web 検索/取得ドメイン設定、セルフホストサンドボックスでのメモリストア |
| Change | Ctrl+L / Cmd+K の動作変更 | フルスクリーンで常に再描画のみ、ダブルプレス `/clear` ショートカット削除、1 行 nvim 端末での自動 `/clear` ループを廃止 |
| Change | `claude mcp list` / `get` の無効サーバー表示 | ヘルスチェック接続の代わりに `⊘ Disabled` と表示 |
| Change | MCP `headersHelper` 信頼ダイアログ要求 | プロジェクト `.mcp.json` の `headersHelper`、インライン MCP サーバーが当該フォルダの信頼ダイアログ承認を要求 |
| Change | MCP `headersHelper` 環境変数継承無効化 | プロジェクト `.mcp.json`、プラグイン、エージェントファイルの `headersHelper` が認証情報環境変数を継承しない。ユーザー・マネージド・claude.ai スコープヘルパーは Claude 設定ディレクトリから実行 |

### v2.1.237

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Fix | プロンプトキャッシングの修正 | LLM ゲートウェイまたはカスタムベース URL を使用するセッションでプロンプトキャッシングが動作するよう修正 |
| Feature | Concise 出力スタイル追加 | 結果を先頭に提示し、前置き・説明を省略する組み込みスタイル。`/config` の Output style から選択 |

## まとめ

v2.1.238 および v2.1.237 は、メモリ管理の改善、プラグインマーケットプレイスのセキュリティ強化、Remote Control の安定性向上、およびプロンプトキャッシングの修正を含む包括的なリリースです。v2.1.238 では 20 件以上の不具合修正が行われ、長時間運用やセルフホストランナー、クロスセッションメッセージングなど多岐にわたる領域で信頼性が向上しました。v2.1.237 の「Concise」出力スタイル追加により、結果重視のワークフローにも対応しています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)