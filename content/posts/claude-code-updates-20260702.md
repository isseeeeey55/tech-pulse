---
title: "【Claude Code】v2.1.198 リリースノートまとめ"
date: 2026-07-02T08:01:28+09:00
draft: true
tags: ["claude-code", "chrome", "agents", "notification", "hooks", "dataviz", "gateway", "anthropicaws", "aws", "worktree", "explore", "opus", "haiku", "ssh", "warp", "macos"]
categories: ["Claude Code Updates"]
summary: "v2.1.198 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.198 リリース情報

## はじめに

Claude Code v2.1.198 がリリースされました。このバージョンでは、Claude in Chrome の一般提供開始、バックグラウンドエージェントの通知機能追加、Gateway への AWS 上の Claude Platform（anthropicAws）のアップストリームプロバイダー追加、そして多数の不具合修正と改善が含まれています。

## 注目アップデート深掘り

### Claude in Chrome の一般提供開始

Claude in Chrome が正式に一般提供となりました。これにより、ブラウザ環境での Claude Code の利用が本番環境で正式にサポートされることになります。

### バックグラウンドエージェントの通知システム

`claude agents` でバックグラウンドエージェントセッションが入力待ち状態になったとき、または完了したときに `Notification` フック（`agent_needs_input` / `agent_completed`）が発火するようになりました。これにより、バックグラウンドで動作しているエージェントの状態変化を外部から検知し、適切に対応できるようになります。

> **Note:** Hooks は Claude Code のカスタマイズ機構で、特定のイベント発生時にユーザー定義の処理を実行できる仕組みです。

### Gateway の AWS Claude Platform サポート

Gateway に AWS 上の Claude Platform（anthropicAws）がアップストリームプロバイダーとして追加されました。さらに、モデルが見つからないレスポンスが返された場合、フェイルオーバーチェーンが自動的に次のプロバイダーに進むようになりました。これにより、複数のプロバイダーを活用した可用性の高い構成が実現できます。

## 実用的な活用ポイント

バックグラウンドエージェントが `claude agents` から起動された場合、コード作業を worktree で完了すると、自動的にコミット、プッシュ、ドラフト PR のオープンを行うようになりました。これにより、ユーザーの確認待ちで停止することなく、一連のコード変更プロセスが自動化されます。

また、サブエージェントとコンテキスト圧縮がセッションの拡張思考設定を継承するようになり、委譲されたタスクでの出力品質が向上しました。組み込みの Explore エージェントもメインセッションのモデル（opus まで）を継承するようになり、haiku で実行されていた以前の挙動から改善されています。

ネットワークの一時的な切断が応答中に発生した場合、ECONNRESET のような一時的なエラーでターンが中断されずに、バックオフ付きリトライが実行されるようになりました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Claude in Chrome 一般提供 | Claude in Chrome が正式に一般提供開始 |
| Feature | バックグラウンドエージェント通知 | `claude agents` でセッションが入力待ちまたは完了時に `Notification` フック（`agent_needs_input` / `agent_completed`）を発火 |
| Feature | `/dataviz` スキル追加 | チャートとダッシュボードデザインガイダンスに、実行可能なカラーパレットバリデーターを提供 |
| Feature | Gateway: AWS Claude Platform サポート | anthropicAws をアップストリームプロバイダーとして追加、モデル未検出時にフェイルオーバーチェーンを進行 |
| Improvement | バックグラウンドエージェントの PR 自動作成 | `claude agents` から起動したバックグラウンドエージェントが worktree でコード作業完了時、自動的にコミット、プッシュ、ドラフト PR 作成 |
| Improvement | Explore エージェントのモデル継承 | 組み込み Explore エージェントがメインセッションのモデル（opus まで）を継承、haiku から変更 |
| Improvement | サブエージェントの拡張思考継承 | サブエージェントとコンテキスト圧縮がセッションの拡張思考設定を継承し、委譲タスクの出力品質が向上 |
| Fix | ネットワーク一時切断時のリトライ | 応答中の短時間のネットワーク切断で ECONNRESET などの一時エラー発生時、バックオフ付きリトライを実行 |
| Fix | サンドボックス環境の過剰な分類リクエスト | サンドボックスプロセスが同じネットワークホストに繰り返しアクセス時の過剰なバックグラウンド分類リクエストを修正 |
| Fix | バックグラウンドタスクの状態表示 | Web、デスクトップ、VS Code のタスクパネルでバックグラウンドタスクが完了後またはセッション再開後に "Running" で固まる問題を修正 |
| Fix | エージェントチームのエラー処理 | API エラーでチームメイトが停止時、リードに "failed" を報告し、スタックしたチームメイトへのメッセージで即座にリトライを起動 |
| Fix | `/diff` パネルの更新 | セッション外でのブランチ切り替えやコミット時に `/diff` パネルが更新されない問題を修正 |
| Fix | マークダウンテーブルの表示 | フルスクリーンモードでマークダウンテーブルがオーバーフローして右ボーダーが折り返される問題を修正 |
| Fix | AWS STS トークン自動更新 | AWS 上の Claude Platform と Mantle セッションで STS トークン期限切れ時の "Please run /login" エラーを修正、`awsAuthRefresh` を自動実行 |
| Fix | macOS ローカルネットワークアクセス | macOS バックグラウンドエージェントセッションでローカルネットワークホストへの "no route to host" エラーを修正、Local Network エンタイトルメントを宣言 |
| Fix | `/desktop` の作業ディレクトリエラー | worktree への出入り後に `/desktop` が "Cannot determine working directory" で失敗する問題を修正 |
| Fix | バックグラウンドエージェントの再接続表示 | macOS でエージェントビューを開いている間、約 52 秒ごとに "Reconnecting…" が表示される問題を修正 |
| Fix | `claude attach` でのキー操作 | `claude attach <id>` 内で `←` を押した際、エージェントビューを開く代わりにシェルに戻る問題を修正 |
| Fix | `claude --bg` のフラグ競合 | `claude --bg` と `--print`/`-p` を併用時、接続不可能なセッションが作成される問題を修正、競合フラグを事前拒否 |
| Fix | ワークフロー進捗ビューのエージェント表示 | SDK とデスクトップアプリセッションで、ワークフロー進捗ビューが最も古いエージェントをリストから除外する問題を修正 |
| Fix | シンボリックリンク経由の条件ルール | 対象ファイルがシンボリックリンクパス経由でアクセスされた場合に `.claude/rules/` の条件ルールが読み込まれない問題を修正 |
| Fix | Warp での URL クリック | macOS の Warp でフルスクリーンモード時に Cmd+クリックで URL が開かない問題を修正 |
| Fix | URL のダブルクリック選択 | フルスクリーンモードでダブルクリック時、スキーム部分を含む URL 全体を選択するよう修正 |
| Fix | プランモードの読み取り専用ツール呼び出し | セッションがプランモードで開始時、読み取り専用ツール呼び出しが自動許可されない問題を修正 |
| Fix | `/branch` のデフォルトフォーク名 | `/branch` が最初の実プロンプトではなく圧縮サマリーからデフォルトフォーク名を導出する問題を修正 |
| Improvement | フォーカスモード改善 | ターン内で起動されたサブエージェントがアクティビティサマリーに表示され、完了したバックグラウンド通知が単一カウントに集約 |
| Improvement | シンタックスハイライト精度向上 | highlight.js 11 へのアップグレードによりコードブロック、diff、ファイルプレビューのシンタックスハイライト精度が向上 |
| Improvement | キーボードショートカットヒント | SSH 経由で Mac から接続時、alt/super ではなく opt/cmd を表示 |
| Improvement | API リトライ UX 改善 | 2 回目の試行後にエラー理由を表示、API が過負荷時にスピナーチップをステータスページリンクに置換 |
| Improvement | `/login` の動作改善 | `claude agents` ビューからサインインダイアログを開くように変更 |
| Improvement | サブエージェントのメッセージ処理 | サブエージェントが起動元エージェントからのメッセージを通常のタスク指示として扱う、エージェントのメッセージはユーザー承認として扱わない |
| Breaking | `/agents` ウィザード削除 | `/agents` ウィザードを削除、Claude に依頼するか `.claude/agents/` を直接編集 |

## まとめ

v2.1.198 は、Claude in Chrome の正式リリース、バックグラウンドエージェント通知システム、AWS Claude Platform サポートといった新機能と、ネットワーク安定性、エージェント間連携、認証トークン管理、UI 表示など、多岐にわたる不具合修正が含まれる大型アップデートです。バックグラウンドエージェントの自動 PR 作成や拡張思考の継承など、ワークフロー自動化と出力品質の向上にも注力されています。`/agents` ウィザードの削除は破壊的変更ですが、`.claude/agents/` の直接編集または Claude への依頼による代替手段が提供されています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)