---
title: "【Claude Code】v2.1.126 リリースノートまとめ"
date: 2026-05-02T08:01:16+09:00
draft: false
tags: ["claude-code", "gateway", "project-management", "history-management", "permissions", "windows", "wsl", "security", "model-picker", "authentication"]
categories: ["Claude Code Updates"]
summary: "v2.1.126 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260502/header.png)

# Claude Code v2.1.126 リリース情報

## はじめに

2026年5月2日、Claude Code **v2.1.126** がリリースされました（公開: 2026-05-01 11:05 JST）。本バージョンでは、**Anthropic 互換ゲートウェイの `/v1/models` 連携**、**`claude project purge` コマンド追加**、**`--dangerously-skip-permissions` の保護パス拡張**、**OAuth ログインのリモート/コンテナ対応**、**Windows での PowerShell 7 検出改善**、**OpenTelemetry の `claude_code.skill_activated` イベント拡張** など、エンタープライズ運用に直結する強化が幅広く入っています。Mac sleep 復帰やモデル長時間思考中の偽 `Stream idle timeout`、Cursor / VS Code 1.92–1.104 の超高速トラックパッドスクロールなど、日常で気になっていたバグも一斉に潰されています。

参考: [Claude Code CHANGELOG（2.1.126）](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)

## 注目アップデート深掘り

### `/model` ピッカーが Anthropic 互換ゲートウェイの `/v1/models` から候補を取得

`/model` ピッカーは、`ANTHROPIC_BASE_URL` が Anthropic 互換ゲートウェイを指している場合、**ゲートウェイの `/v1/models` エンドポイント**から実際に利用可能なモデル一覧を取得して表示するようになりました。これまではクライアント内蔵のモデル一覧を表示していたため、ゲートウェイ側で許可していないモデルが選択肢に並んだり、追加されたカスタムモデルが見えなかったりするケースがありました。

```bash
# Bedrock / Vertex / 自前の互換 Gateway 経由運用
$ export ANTHROPIC_BASE_URL=https://gateway.example.com
$ claude
# /model 実行時、gateway.example.com/v1/models が返す候補のみが表示される
```

エンタープライズ環境で、社内ゲートウェイがアクセスログ・レート制限・モデル制限を一元管理している構成では、この変更で「ゲートウェイで管理しているモデル定義」が **クライアント側 UI と完全に整合**します。SRE が「このゲートウェイでは Sonnet と Opus のみ許可」とした場合、開発者の `/model` 一覧にもそれだけが並ぶ、という UX が実現します。

### `claude project purge` でプロジェクト状態をワンコマンド削除

新コマンド **`claude project purge [path]`** が追加され、特定プロジェクトに紐づく Claude Code の状態（**transcripts / tasks / file history / config エントリ**）を一括削除できます。サポートされるフラグは以下の4つ。

- `--dry-run`: 削除対象を表示するだけで実際には消さない
- `-y` / `--yes`: 確認プロンプトをスキップ
- `-i` / `--interactive`: ファイルごとに確認しながら削除
- `--all`: 引数で指定したパス配下のすべてのプロジェクトに対して実行

```bash
# 削除対象を確認
$ claude project purge ~/work/customer-a --dry-run

# 確認なしで一括削除（CI から呼び出す用途）
$ claude project purge ~/work/customer-a -y

# 顧客案件用ディレクトリ配下を一括 purge
$ claude project purge ~/work/customers --all -y
```

**機密情報を含む顧客案件の終了時クリーンアップ**や、CI ジョブ終了時の確実な状態リセットに使えます。`--dry-run` で必ず対象範囲を可視化してから本番実行するのが安全な運用です。

## 実用的な活用ポイント

### `--dangerously-skip-permissions` の保護パス拡張

`--dangerously-skip-permissions` は、これまでスキップされなかった `.claude/`、`.git/`、`.vscode/`、シェル設定ファイルなど、**従来「保護されていたパス」への書き込みプロンプトもバイパス**するようになりました。ただし、catastrophic な削除コマンド（システム全体に影響する `rm -rf /` 系）は安全網として引き続き確認が出ます。

CI で Claude Code を非インタラクティブに走らせるユースケース（例: lint 自動修正、依存更新 PR 自動生成）で、`.claude/` や `.vscode/` 配下への自動書き込みを許容したい場合に手数が減ります。一方で、ローカル開発で安易に常用すると `.git/config` を書き換えるツール呼び出しなども無確認になるため、**CI 専用で使うのが本来の用途** という点は意識すべきです。

### OAuth ログインのリモート/コンテナ対応

`claude auth login` は、ブラウザコールバックが `localhost` に到達できない環境（**WSL2 / SSH リモート / コンテナ / IPv6 only devcontainer**）で、ブラウザに表示された OAuth コードをターミナルに**貼り付ける形でログイン完了**できるようになりました。あわせて、遅い接続やプロキシ越しでのタイムアウト失敗、同時クレデンシャル書き込みで有効な OAuth refresh トークンがクリアされる稀な race condition も修正されています。

WSL2 や devcontainer をメイン環境にしている開発者は、これまで `claude auth login` の挙動に苦労していたケースが多く、今回の修正は実運用に直接効きます。

### `claude_code.skill_activated` OpenTelemetry イベントの拡張

OTEL の `claude_code.skill_activated` イベントが、**ユーザーが手で打ったスラッシュコマンドでも発火する**ようになり、新しい属性 `invocation_trigger` が以下のいずれかの値で付きます。

- `"user-slash"`: ユーザーが直接スキルを呼び出した
- `"claude-proactive"`: Claude が自動的に判断してスキルを起動した
- `"nested-skill"`: 別スキルから呼び出された（ネスト）

Grafana / Datadog 等で「ユーザーが直接呼んだスキル」と「Claude が proactive に呼んだスキル」を分離して可視化できるため、**スキル設計の効果検証**に直結します。`OTEL_LOG_USER_PROMPTS` ゲートと組み合わせて、特定スキルの利用パターンを継続観測する基盤として活用できます。

### Windows: PowerShell 7 検出と既定シェル化

Windows 上で **PowerShell 7** が以下の経路でインストールされている場合に検出されるようになりました。

- Microsoft Store 経由
- PATH なしの MSI インストール
- `.NET global tool`

さらに、PowerShell ツールが有効な場合、**Bash 既定ではなく PowerShell をプライマリシェルとして扱う**ようになりました。Windows ネイティブの開発環境を持つ組織にとって、この既定変更は地味に効きます。

その他、Windows でのクリップボード書き込みが **コピー内容をプロセスのコマンドライン引数に露出させない** ように修正され（EDR/SIEM テレメトリへの漏洩防止）、22KB を超える選択がクリップボードに渡らない問題も解消されています。日本語/韓国語/中国語が no-flicker mode で文字化けする問題も今回まとめて修正されました。

## 全変更点一覧

| カテゴリ | 変更内容 |
|---|---|
| Feature | `/model` ピッカーが `ANTHROPIC_BASE_URL` のゲートウェイ `/v1/models` から候補を取得 |
| Feature | `claude project purge [path]` 追加（`--dry-run` / `-y` / `-i` / `--all` サポート） |
| Feature | `--dangerously-skip-permissions` が `.claude/`・`.git/`・`.vscode/`・シェル設定ファイル等の保護パスもバイパス（catastrophic 削除は引き続き確認） |
| Feature | `claude auth login` が WSL2 / SSH / コンテナで OAuth コードのターミナル貼り付けに対応 |
| Feature | OTEL `claude_code.skill_activated` がユーザースラッシュコマンドでも発火、`invocation_trigger` 属性追加 |
| Feature | Auto mode のスピナーが permission チェック停滞時に赤色化（誤って「実行中」に見えていた問題を解消） |
| Improvement | Host-managed deployments（`CLAUDE_CODE_PROVIDER_MANAGED_BY_HOST`）が Bedrock / Vertex / Foundry 上で analytics を自動無効化しなくなった |
| Improvement | Windows: Microsoft Store / PATH なし MSI / .NET global tool 経由の PowerShell 7 を検出 |
| Improvement | Windows: PowerShell ツール有効時に PowerShell をプライマリシェルとして扱う（Bash 既定から変更） |
| Improvement | Read tool: per-file マルウェア評価リマインダー削除（誤拒否を防止） |
| Security Fix | 上位 managed-settings ソースに `sandbox` ブロックがない場合に `allowManagedDomainsOnly` / `allowManagedReadPathsOnly` が無視される問題 |
| Fix | 2000px を超える画像ペーストでセッションが壊れる問題（自動ダウンスケール、過大な履歴画像も自動削除して再試行） |
| Fix | "OAuth not allowed for organization" エラーで誤ってログイン画面が表示されていた挙動（管理者連絡を案内） |
| Fix | OAuth login が遅い接続 / プロキシ / IPv6-only devcontainer でタイムアウト失敗する問題 |
| Fix | 同時クレデンシャル書き込みで有効な OAuth refresh トークンがクリアされる稀な race condition |
| Fix | API リトライカウントダウンが "0s" で固まり実際にカウントダウンしていなかった問題 |
| Fix | Mac sleep 復帰後の "Stream idle timeout" エラー |
| Fix | バックグラウンド / リモートセッションが長時間モデル思考中に偽 "Stream idle timeout" で中断する問題 |
| Fix | アシスタントが思考完了後に空ターン続きで出力ゼロのままハングする問題 |
| Fix | Cursor / VS Code 1.92–1.104 の統合ターミナルでの超高速トラックパッドスクロール |
| Fix | claude.ai MCP コネクタが needs-auth 状態の手動サーバーで抑制される問題 |
| Fix | Windows no-flicker mode で日本語 / 韓国語 / 中国語が文字化けする問題 |
| Fix | `Ctrl+L` がプロンプト入力をクリアする挙動（readline 準拠の screen redraw のみに） |
| Fix | Deferred tools（WebSearch / WebFetch 等）が `context: fork` skill / subagent の初回ターンで利用不可だった問題 |
| Fix | `--channels` で起動した interactive session で plan-mode tools が利用不可だった問題 |
| Fix | `/plugin` Uninstall が "Enabled" と表示する問題 |
| Fix | linter が多数ファイルを変更したときの file-modified リマインダー総サイズを制限 |
| Fix | `/remote-control` リトライが "connecting…" で停止して見える挙動 |
| Fix | Remote Control 失敗通知に初回接続失敗時の理由が表示されない問題 |
| Fix | Windows: クリップボード書き込みがコピー内容をプロセスコマンドライン引数に露出する問題（22KB 超の選択も含めて修正） |
| Fix | PowerShell tool: 単独の `--`（例: `git diff -- file`）が `--%` stop-parsing トークンと誤判定される問題 |
| Fix | Agent SDK が並列ツール呼び出しで malformed tool name を受けるとハングする問題 |

## まとめ

v2.1.126 で実用上のインパクトが大きいのは、**`/model` ピッカーが `ANTHROPIC_BASE_URL` のゲートウェイ `/v1/models` に従うようになった点** と、**`claude project purge` コマンドの追加** の2点です。前者は社内ゲートウェイで管理しているモデル定義と CLI の UI が初めて完全に整合し、後者は顧客案件終了時の状態クリーンアップを単一コマンドで完結させます。

OAuth ログインの WSL2 / SSH / コンテナ対応、Windows の PowerShell 7 検出と既定シェル化、`claude_code.skill_activated` OTEL の `invocation_trigger` 属性追加など、それまで地味に詰まっていた実運用上のフリクションがまとめて解消されています。`allowManagedDomainsOnly` / `allowManagedReadPathsOnly` が無視される **Security Fix** も入っているため、managed-settings を運用しているチームは挙動を一度確認しておくのが無難です。

> **Note:** ここでいう「権限プロンプト」とは、Claude Code がツール実行・ファイル書き込みなどを行う前に表示する確認ダイアログを指します。`--dangerously-skip-permissions` はこの確認をバイパスするフラグで、v2.1.126 ではバイパス対象が `.claude/`・`.git/`・`.vscode/`・シェル設定ファイルなど従来「保護されていたパス」にも拡張されました（catastrophic な削除コマンドは引き続き確認が出ます）。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code CHANGELOG (anthropics/claude-code)](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)