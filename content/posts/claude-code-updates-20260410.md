---
title: "【Claude Code】v2.1.98 リリースノートまとめ"
date: 2026-04-10T08:01:12+09:00
draft: false
tags: ["claude-code", "security", "vertex-ai", "perforce", "lsp", "otel", "traceparent", "bash", "permissions"]
categories: ["Claude Code Updates"]
summary: "v2.1.98 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260410/header.png)

## はじめに

v2.1.98 は Feature 7件、Fix 30件超、Improvement 8件と、内容の濃いリリースです。Google Vertex AI セットアップウィザードや Perforce 連携モードといった新機能が追加された一方、Bash ツールに関する**重大なセキュリティ脆弱性の修正**が含まれているので、優先的にアップデートしておきたいバージョンです。

特に注目したいのは Linux 環境向けのサブプロセスサンドボックス（PID 名前空間分離）と、OTEL トレーシング対応の TRACEPARENT 環境変数注入です。

## 注目アップデート深掘り

### 重大なセキュリティ修正：Bash ツール権限バイパス

![Bash ツール権限バイパスの修正内容](/images/claude-code-updates-20260410/bash-permission-fix.png)

最優先で確認したいのが、Bash ツールの権限バイパス脆弱性の修正です。**バックスラッシュエスケープされたフラグが read-only として自動許可され、任意コード実行につながる可能性があった**問題が修正されました。

これに関連して以下も同時に修正されています：

- 複合コマンド（`cmd1 && cmd2` のようなパイプ・連結）が、auto モード/bypass モードで強制プロンプトをすり抜けていた
- `env-var prefix` 付きの read-only コマンドが、`LANG` `TZ` `NO_COLOR` 以外の未知の環境変数では確認プロンプトを出していなかった
- `/dev/tcp/...` や `/dev/udp/...` へのリダイレクトが自動許可されていた（任意ホストへの通信が可能）
- `Bash(...)` の deny ルールが、`cd` を含むパイプコマンドではプロンプトに降格されていた

**特に `/dev/tcp` リダイレクトの自動許可は深刻**で、シェルから任意の TCP ソケットを開ける挙動だったので、必ずアップデートしてください。

### サブプロセスサンドボックス（PID 名前空間分離）

> **PID 名前空間（PID namespace）とは？**
> Linux カーネルの機能で、プロセスから見える PID ツリーを隔離する仕組みです。コンテナ技術（Docker、Podman など）の基盤にもなっています。サンドボックス内のプロセスからはホスト側のプロセスが見えなくなり、ホスト側のプロセスへのシグナル送信も不可になります。

`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` 環境変数を設定すると、Linux 上で起動するサブプロセスが PID 名前空間で隔離されるようになりました。サブプロセス内から `ps` を実行してもホストのプロセス一覧が見えず、`kill` でホストの他プロセスに影響を与えることもできません。

```bash
# サンドボックス有効化
$ export CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1

# スクリプト実行回数の上限設定
$ export CLAUDE_CODE_SCRIPT_CAPS=50
```

`CLAUDE_CODE_SCRIPT_CAPS` はセッションあたりのスクリプト起動回数の上限で、無限ループや暴走スクリプトからの保護に使えます。

注意点として、**現時点では Linux のみ対応**で、macOS や Windows では動作しません。CI/CD パイプラインで Claude Code を動かしているケースで特に有効です。

### Google Vertex AI セットアップウィザード

ログイン画面で「3rd-party platform」を選ぶと、対話形式の Vertex AI セットアップウィザードが起動します。GCP 認証 → プロジェクト・リージョン設定 → 認証情報の検証 → モデルピン留めまでをガイドしてくれます。

これまで Vertex AI を使うには、`gcloud` での認証や `ANTHROPIC_VERTEX_PROJECT_ID` などの環境変数設定を手動で進める必要がありました。新しい開発メンバーのオンボーディングや、複数 GCP プロジェクトを切り替える運用が楽になります。

### W3C TRACEPARENT 環境変数の注入

OTEL トレーシングを有効にしている場合、Bash ツールが起動するサブプロセスに W3C `TRACEPARENT` 環境変数が自動注入されるようになりました。

```python
# サブプロセスから親トレースに紐づくスパンを生成
import os
trace_parent = os.environ.get('TRACEPARENT')
# OTel SDK が TRACEPARENT を解釈してスパンを継承
```

OTel 対応のスクリプト/CLI ツールであれば、Claude Code のセッションをルートとした分散トレースツリーに、子プロセスのスパンが正しく紐づきます。Datadog、Honeycomb、Grafana Tempo などの APM ツールで、Claude Code のターン全体を一気通貫で追跡できるようになります。

## 実用的な活用ポイント

**Perforce ユーザー向けの新モード**: `CLAUDE_CODE_PERFORCE_MODE` を設定すると、read-only ファイルへの Edit/Write/NotebookEdit が `p4 edit` のヒント付きで失敗するようになります。Perforce の lock 状態のファイルを誤って上書きする事故を防げます。

**`/agents` のタブレイアウト改善**: Running タブで稼働中のサブエージェントが、Library タブで Run agent と View running instance のアクションが使えるようになりました。複数エージェントを並行で動かすワークフローで便利です。

**Monitor ツール**: バックグラウンドスクリプトのイベントをストリーミングできる新ツールが追加されました。長時間ジョブの進捗をリアルタイムで把握できます。

**LSP の clientInfo 対応**: Claude Code が LSP の initialize リクエストで `clientInfo` を送るようになりました。言語サーバー側で Claude Code 固有の挙動制御がしやすくなります。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Security | Bash ツール権限バイパス修正 | バックスラッシュエスケープによる任意コード実行を防止 |
| Security | 複合コマンドの権限プロンプト強制 | `&&` や `\|` 連結で deny ルールが降格される問題を修正 |
| Security | env-var prefix 付きコマンドの確認 | 未知の環境変数では必ずプロンプトを出すように変更 |
| Security | `/dev/tcp` `/dev/udp` リダイレクト | 自動許可されていた問題を修正 |
| Feature | Vertex AI セットアップウィザード | 対話形式での GCP 認証・プロジェクト設定 |
| Feature | サブプロセス PID 名前空間分離 | Linux 限定、`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` で有効化 |
| Feature | スクリプト実行回数上限 | `CLAUDE_CODE_SCRIPT_CAPS` 環境変数で設定 |
| Feature | Perforce モード | `CLAUDE_CODE_PERFORCE_MODE` で read-only 保護 |
| Feature | Monitor ツール | バックグラウンドスクリプトのイベントストリーミング |
| Feature | TRACEPARENT 環境変数注入 | OTEL 有効時に Bash サブプロセスへ自動注入 |
| Feature | `--exclude-dynamic-system-prompt-sections` | クロスユーザーのプロンプトキャッシュ最適化 |
| Improvement | LSP `clientInfo` 対応 | 言語サーバーへ Claude Code を識別情報として送信 |
| Improvement | `/agents` タブレイアウト | Running タブと Library タブを追加 |
| Improvement | `/reload-plugins` 改善 | プラグイン提供スキルを再起動なしで取得 |
| Improvement | OTEL トレーシング改善 | ターン境界とインタラクションスパンの紐付け修正 |
| Fix | ストリーミング応答のスタック | タイムアウト時に non-streaming へフォールバック |
| Fix | 429 リトライバックオフ | 小さな Retry-After で全リトライ消費する問題を修正 |
| Fix | `/resume` 関連バグ多数 | 編集不可・検索消失・diff 消失・選択不可など一括修正 |
| Fix | macOS テキスト置換 | トリガー語が削除されるだけで置換が走らない問題を修正 |
| Fix | xterm/VS Code の大文字入力 | kitty キーボードプロトコル有効時に小文字化される問題を修正 |
| Fix | `/export` 絶対パス・`~` 対応 | 拡張子が勝手に `.txt` に書き換わる問題も同時修正 |
| Fix | Bash 権限ルールのワイルドカード | 余分な空白・タブでマッチ失敗する問題を修正 |
| Fix | サブエージェントの worktree クリーンアップ | untracked ファイルがある worktree を消す問題を修正 |

## まとめ

v2.1.98 は Bash ツールの**重大なセキュリティ脆弱性の修正**が入っているので、本番環境や CI/CD で Claude Code を使っているなら最優先でアップデートしてください。`/dev/tcp` リダイレクトの自動許可と、バックスラッシュエスケープによる権限バイパスは、悪意あるプロンプト注入のリスクが具体的にあります。

新機能の Vertex AI ウィザードと PID 名前空間サンドボックスは、エンタープライズ運用での Claude Code 活用の幅を広げるアップデートです。`/resume` 周りのバグ修正もまとめて入っているので、長時間セッションを再開する運用にも効きます。
