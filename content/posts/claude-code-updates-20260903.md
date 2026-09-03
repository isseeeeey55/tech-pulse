---
title: "【Claude Code】v2.1.259・v2.1.258 リリースノートまとめ"
date: 2026-09-03T08:01:47+09:00
draft: false
tags: ["claude-code", "mcp", "oauth", "gitlab", "vscode", "opentelemetry"]
categories: ["Claude Code Updates"]
summary: "v2.1.259・v2.1.258 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260903/header.png)

## はじめに

2026年9月3日、Claude Code の v2.1.259 および v2.1.258 がリリースされました。v2.1.259 では、組織全体への MCP サーバー配信を可能にする `managedMcpServers` 設定の追加、無人実行向けの `--permission-prompts none` オプション、GitLab マージリクエストの認識機能が導入されました。また、並行セッション時の設定ファイル競合問題や、シェルコマンド読み取り権限の回避、プロンプトキャッシュの無効化など、多数の不具合が修正されています。v2.1.258 では、macOS 12（Monterey）での起動失敗とリモート・スケジュール実行セッションでの権限承認エラーが修正されました。

## 注目アップデート深掘り

### 組織管理型 MCP サーバー配信機能の追加

v2.1.259 で `managedMcpServers` 設定が追加され、組織がすべてのユーザーに対して HTTP/SSE 型の MCP サーバーを提供できるようになりました。エントリの形式は `.mcp.json` と同じですが、コマンドを実行する形式のエントリはスキップされます。この機能により、管理者は標準化されたツールセットをユーザーごとに手動で設定させることなく配布できるようになります。

なお、`allowedMcpServers` の動作が変更され、今後はユーザーが追加するサーバーのみを制御します。以前は `managed-mcp.json` で提供されたサーバーも許可リストでフィルタリングされていましたが、アップグレード後は自動的に読み込まれます。特定のサーバーを除外するには `deniedMcpServers` を使用する必要があります。

### 並行セッション時の設定競合問題の修正

複数のセッションを同時に実行している場合、お互いに `~/.claude.json` への変更を上書きしてしまう問題が修正されました。この不具合により、ワークスペースの信頼設定がリセットされたり、MCP やプロジェクトの状態が失われたりしていました。修正後は、複数セッションを並行実行してもそれぞれの設定変更が正しく保持されるようになります。

## 実用的な活用ポイント

無人実行環境では `--permission-prompts none` オプションが有効です。このオプションを指定すると、プロンプトが必要な操作は自動的に拒否され、通常の権限モード（auto モードを含む）が引き続き判断を行います。

GitLab を使用している場合、`glab mr create/merge/close/reopen/note/update` コマンドが認識され、マージリクエストが折りたたみツール要約内で `MR !N` として表示されるようになり、フッターの MR バッジも更新されます。

`claude plugin validate` に `--json` フラグを追加すると、機械可読な検証レポートが得られます。

## 全変更点一覧

> **MCP（Model Context Protocol）とは？** Claude が外部ツールやデータソースと接続するためのプロトコルです。Slack・GitHub・データベースなどと Claude Code を連携させる際に使います。今回の `managedMcpServers` 設定により、組織の管理者がすべてのユーザーへ HTTP/SSE 型 MCP サーバーを一括配布できるようになります。

> **OpenTelemetry とは？** 分散システムのトレース・メトリクス・ログを標準化して収集するオープンソースの可観測性フレームワークです。Claude Code ではクラウドセッションの使用状況や動作ログを送出するために使用しています。

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | `managedMcpServers` 設定追加 | 組織が HTTP/SSE MCP サーバーを全ユーザーに配信可能に（コマンド実行型エントリはスキップ） |
| Feature | `--permission-prompts none` オプション追加 | 無人ヘッドレス実行時に、プロンプトが必要な操作を自動的に拒否 |
| Feature | GitLab MR コマンド認識追加 | `glab mr create/merge/close/reopen/note/update` を認識し、折りたたみツール要約とフッターバッジに `MR !N` 表示 |
| Feature | `claude plugin validate --json` 追加 | 機械可読な検証レポートを出力 |
| Feature | セッションリストのフィルタ機能追加（VSCode） | Active クイックフィルタと状態フィルタメニュー（Needs input, Working, Completed）を追加 |
| Fix | 並行セッション時の `~/.claude.json` 競合修正 | 複数セッション実行時にワークスペース信頼設定や MCP/プロジェクト状態が失われる問題を修正 |
| Fix | 思考拒否後の連続拒否問題修正 | 一度思考が拒否された会話が、以降のすべてのターンで再度拒否される不具合を修正 |
| Fix | Bash `Read()` 拒否ルールのカバレッジ拡大 | オプション値（`--ignore-revs-file=.env`, `-f.env`, `@file`）、`git diff`/`git grep` のファイルオペランド、`cd DIR && cat FILE` 複合コマンドなどを対象に追加 |
| Fix | OAuth トークン更新時のキャッシュ無効化修正 | テレメトリ無効セッションで OAuth トークン更新時にプロンプトキャッシュが無効化される問題を修正 |
| Fix | フルスクリーンモード時の会話表示問題修正 | 数百のツール呼び出しを含む長いターンの後、フルスクリーンモードで空白の会話が表示される不具合を修正 |
| Fix | カスタムコマンド・スキル実行時のモデル選択修正 | フロントマター `model:` で指定されたモデルを自動モードが実行できない場合でも、セッションモデルを維持するよう修正 |
| Fix | `CLAUDE_CODE_MAX_CONTEXT_TOKENS` の認識修正 | Vertex スタイルモデル ID（`@YYYYMMDD` サフィックス）で、Claude Code が認識しないモデルバージョンでも環境変数を適用 |
| Fix | シェルコマンドライブ出力プレビュー修正 | 実行中のシェルコマンド出力で、前の行が折り返した際に最新行が隠れる問題を修正 |
| Fix | GitHub 接続チェックの頻度修正 | claude.ai ユーザーの起動時に毎回実行されていたバックグラウンド GitHub 接続チェックを、起動間で結果を記憶するよう変更 |
| Fix | `--resume` と `--continue` 失敗問題修正 | ペイロードのない添付エントリを含む保存済みセッションで `--resume` が失敗し、`--continue` が空の会話を開く不具合を修正 |
| Fix | フロントマター `model:` の無視問題修正 | インタラクティブセッションでカスタムコマンドとスキルのフロントマター `model:` が無視される問題を修正 |
| Fix | Artifact 公開エラー修正 | 古いバージョンから継続した会話で、Artifact 公開が「unexpected parameter `note`」エラーで一度失敗する問題を修正 |
| Fix | `forceRemoteSettingsRefresh` 無視問題修正 | MDM または管理設定ファイルで構成されたポリシーヘルパーが既に実行されている場合、起動時に管理設定の `forceRemoteSettingsRefresh` が無視される不具合を修正 |
| Fix | ワークツリー分離の拒否問題修正 | `git rev-parse` が「not a git repository」以外のメッセージで失敗する環境で、フック作成ワークツリーをワークツリー分離機能が拒否する問題を修正 |
| Fix | OpenTelemetry 属性欠落修正 | クラウドセッションからの OpenTelemetry メトリクスとイベントで `user.email`、`organization.id`、`user.account_uuid` 属性が欠落していた問題を修正 |
| Fix | MCP サーバー起動時切断の表示修正 | 起動時のツールリスト取得中に切断された MCP サーバーが、ツールなしで接続済みと表示される代わりにエラーを報告するよう修正 |
| Fix | ファイル編集権限ダイアログ表示修正 | ファイル編集権限ダイアログで、変更行が途中で切れたまま表示される場合がある問題を修正 |
| Fix | リポジトリ検出の ID 消失問題修正 | 一時的な git プローブ失敗後に、既知のリポジトリ ID が失われる不具合を修正 |
| Fix | 管理設定解析失敗時の起動許可修正 | 管理設定ファイル、ドロップイン、MDM plist、HKLM 値がパース不能な場合、Claude Code が起動を拒否してソースを明示するよう変更 |
| Fix | リモートコントロールセッションでの Stop 修正 | リモートコントロールセッションで Stop がバックグラウンドエージェントとワークフローを実際に停止しない問題を修正；停止タスクはプロセス終了まで表示・再停止可能 |
| Fix | ワークフロー実行再開時の重複実行修正 | 停止中のワークフロー実行がまだ終了していない状態で再開すると、エージェントが重複実行される可能性があった問題を修正 |
| Fix | Marketplace リポジトリ URL 修正 | github.com 上の Marketplace リポジトリ URL の末尾スラッシュや余分な `?`/`#` が、使用不可能な `.git` クローン URL を生成する問題を修正 |
| Fix | Stop フック後の推論消失修正 | ブロック Stop フック後のターンでモデルの推論が失われ、一部のモデルでプロンプトキャッシュが無効化される問題を修正 |
| Fix | リモートセッションの MCP サーバー消失対応修正 | リモート（claude.ai）セッションで、ブラウザホスト型 MCP サーバーのページが消えた後、ターン開始に 60 秒かかる問題を修正 |
| Fix | ワークツリー分離セッションのコマンド拒否修正 | ワークツリー分離セッションで、メインチェックアウトに到達できない一般的な Bash ループ、xargs パイプライン、ランチャーラップコマンドを拒否する問題を修正 |
| Fix | macOS 12 起動失敗修正（v2.1.258） | macOS 12（Monterey）で Claude Code が起動しない不具合を修正（v2.1.255 で発生した回帰） |
| Fix | 権限承認再送エラー修正（v2.1.258） | リモート・スケジュール実行セッションで、再送された権限承認が適用できず「user messages must have non-empty content」エラーが発生する問題を修正 |
| Improvement | ターミナル描画パフォーマンス向上 | 長い応答に対して、テキスト測定を再利用することでターミナルのリサイズと初回レンダリング性能を改善 |
| Improvement | `/workflows` エージェント詳細表示改善 | JSON 結果のシンタックスハイライトと実際の改行での pretty-print 表示、長い結果には展開トグルを追加 |
| Improvement | ヘッドレス/SDK セッション開始高速化 | MCP サーバーの接続完了時、最初のターンが最大 50 ms 早く開始されるよう改善 |
| Improvement | `/install-github-app` メッセージ改善 | GitHub 専用であることを説明し、GitLab リポジトリ内で実行された場合は GitLab CI/CD ドキュメントへのリンクを表示 |
| Improvement | 入れ子サブエージェント結果の保存改善 | 入れ子のバックグラウンドサブエージェント結果を親サブエージェントのトランスクリプトに保存し、再開時や共有トランスクリプトで保持・表示 |
| Change | `allowedMcpServers` 適用範囲変更 | ユーザーが追加するサーバーのみを制御対象に変更；`managed-mcp.json` サーバーは自動的にロードされるようになり、除外するには `deniedMcpServers` を使用 |
| Fix | 権限承認再送後のセッション停止修正 | 一時停止中のセッションでコネクタツールの権限プロンプトが承認された後、何も反応しなくなる問題を修正 |

## まとめ

v2.1.259 は、組織による MCP サーバーの集中管理機能と無人実行向けの権限制御オプションの追加により、エンタープライズ運用の柔軟性を強化しました。GitLab マージリクエストの認識やプラグイン検証の JSON 出力など、ユーザビリティ向上も図られています。一方で、並行セッション時の設定競合・OAuth トークン更新時のキャッシュ無効化・worktree 分離の誤拒否など、本番運用で踏みやすいバグが集中的に直っています。v2.1.258 は macOS 12 での起動失敗とリモート・スケジュール実行セッションでの権限承認エラーを修正し、互換性と信頼性を維持しています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)