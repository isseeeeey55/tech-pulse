---
title: "【Claude Code】v2.1.207 リリースノートまとめ"
date: 2026-07-12T08:01:28+09:00
draft: true
tags: ["claude-code", "auto-mode", "bedrock", "vertex-ai", "foundry", "remote-control", "deep-research", "mcp", "opus-4.8"]
categories: ["Claude Code Updates"]
summary: "v2.1.207 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.207 リリース情報

## はじめに

Claude Code v2.1.207 がリリースされました。このバージョンでは、Auto mode が Bedrock、Vertex AI、Foundry で正式に一般提供され、オプトインフラグなしで利用可能になったほか、ターミナルの応答性改善、設定管理の不具合修正、セキュリティ強化など、20 件を超える修正と改善が含まれています。

## 注目アップデート深掘り

### Auto mode の一般提供と設定変更

Auto mode が Bedrock、Vertex AI、Foundry で `CLAUDE_CODE_ENABLE_AUTO_MODE` フラグなしで利用可能になりました。これまでは環境変数による明示的なオプトインが必要でしたが、今回のリリースでこれらのプラットフォームでは標準機能として提供されます。無効化したい場合は、設定ファイルの `disableAutoMode` オプションで制御できます。

また、Auto mode の設定読み取り元が変更され、プロジェクトごとの `.claude/settings.local.json` からの `autoMode` 設定読み込みが廃止されました。今後はユーザー設定ファイル `~/.claude/settings.json` を使用する必要があります。

### プラグインにおけるシェルインジェクション対策

プラグインの hooks、monitors、MCP の headersHelper において、シェル形式コマンド内での `${user_config.*}` 変数展開が禁止されました。これはシェルインジェクション攻撃を防ぐセキュリティ修正です。hooks では exec 形式（`args` 配列）または環境変数 `$CLAUDE_PLUGIN_OPTION_<KEY>` を使用し、monitors と headersHelper では設定ファイルまたはサーバーの `env` ブロックでスクリプト内部から値を読み取る必要があります。

さらに、プロジェクトレベルの `.claude/settings.json` からのプラグインオプション値（`pluginConfigs`）の読み込みが無効化され、ユーザー設定、`--settings` フラグ、管理された設定からのみ読み込まれるようになりました。

## 実用的な活用ポイント

今回のリリースでは、日常的な開発作業における複数の問題が解決されています。ターミナルでの長いリスト、テーブル、コードブロックのストリーミング時に発生していたフリーズとキーストロークの遅延が修正され、応答性が改善されました。

また、`cd` を含む複合コマンドで `/dev/null` へのリダイレクトのみの場合に不要な権限プロンプトが表示される問題が修正され、ワークフローがスムーズになります。自動更新機能による `~/.local/bin/claude` のカスタムランチャースクリプトやシンボリックリンクの上書きも修正され、`/doctor` コマンドで外部管理されたランチャーが報告されるようになりました。

Bedrock ユーザー向けには、IAM Identity Center からの AWS SSO 認証情報の繰り返し要求が修正され、Windows での AWS 認証情報解決のスタール時に無期限ハングが発生する問題に 60 秒のタイムアウトガードが追加されました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Auto mode の一般提供 | Bedrock、Vertex AI、Foundry で `CLAUDE_CODE_ENABLE_AUTO_MODE` なしで利用可能に。設定での無効化は `disableAutoMode` で可能 |
| Fix | ターミナルフリーズの修正 | 非常に長いリスト、テーブル、段落、コードブロックを含む応答のストリーミング中にターミナルがフリーズしキーストロークが遅延する問題を修正 |
| Fix | リモート管理設定の永続化問題の修正 | 非インタラクティブ実行（`claude -p`、SDK）でのリモート管理設定がセキュリティ同意ダイアログを表示せず永続的に同意済みとして記録される問題を修正 |
| Fix | 誤検知のプロンプトインジェクション警告の修正 | システム生成の会話更新により誤って発生するプロンプトインジェクション警告を修正 |
| Fix | 自動更新によるランチャースクリプト上書きの修正 | 自動更新が毎回 `~/.local/bin/claude` のカスタムランチャースクリプトやシンボリックリンクを上書きする問題を修正。`/doctor` で外部管理されたランチャーを報告 |
| Fix | cd コマンド権限プロンプトの修正 | `/dev/null` へのリダイレクトのみの場合に `cd` を含む複合コマンドが権限を要求する問題を修正 |
| Fix | トランスクリプトジャンプの修正 | 応答のストリーミング完了時にトランスクリプトが回答の開始位置より上にジャンプする問題を修正 |
| Fix | worktreeConfig の残留問題の修正 | 最後の `worktree.sparsePaths` ワークツリー削除後も `.git/config` に `extensions.worktreeConfig` が残る問題を修正（go-git ツールの破損を防止） |
| Fix | 不正な括弧パターンの修正 | rules globs、skill paths、`.ignore`、`.worktreeinclude` での不正な括弧パターンがファイル読み込み、ファイル提案、ワークツリー作成を破壊する問題を修正 |
| Fix | エージェントチームのクラッシュループ修正 | 不正なチームメイトメールボックスメッセージが 1 秒ごとにエラーを繰り返し発生させるクラッシュループを修正 |
| Fix | バックグラウンドセッション名表示の修正 | プラン承認で自動命名されたバックグラウンドセッションがエージェントビューの行に名前を表示しない問題を修正 |
| Fix | ワークツリーバックグラウンドセッションの修正 | git ワークツリーに入ったバックグラウンドセッションがエージェントリストからのコールドリオープン後に空白で再開する問題を修正 |
| Fix | Remote Control ステータス更新の修正 | ネットワーク中断または認証情報更新からの接続回復時に Remote Control タスクステータス更新が失われる問題を修正 |
| Fix | Remote Control バックグラウンド進捗の修正 | デスクトップアプリがホストする Remote Control セッションがモバイルとウェブでバックグラウンドエージェントとワークフローの進捗を表示しない問題を修正 |
| Fix | Deep Research ラベル表示の修正 | Deep Research 実行で Fetch フェーズのエージェントがすべて「unknown」とラベル付けされる問題を修正。チップにソースホスト名を表示 |
| Fix | Bedrock 認証情報の再要求問題の修正 | Bedrock が毎回の API リクエストで IAM Identity Center から新しい AWS SSO 認証情報を繰り返し要求する問題を修正 |
| Improvement | エージェントビューの貼り付け改善 | 同じテキストを再度貼り付けると、2 つ目を追加する代わりに折りたたまれた `[Pasted text #N]` プレースホルダーを展開するように改善 |
| Improvement | エージェントビューのセッション表示改善 | ブロックされたセッションのピークビューで質問を先頭に表示し、同じタイムスタンプを 2 回表示する代わりに語句による鮮度時計（`waiting 3m`）を表示 |
| Breaking | デフォルトモデルの変更 | Bedrock、Vertex、Claude Platform on AWS のデフォルトを Claude Opus 4.8 に変更 |
| Breaking | Auto mode 設定読み込み元の変更 | `.claude/settings.local.json`（リポジトリ内）からの `autoMode` 読み込みを廃止。`~/.claude/settings.json` を使用 |
| Fix | Windows での AWS 認証情報スタールハング修正 | AWS 認証情報解決がスタール時（例: スタックした `credential_process`）に Windows で無期限ハングする問題を修正。60 秒のスタールガードを実装 |
| Breaking | プラグインのシェルインジェクション修正 | プラグイン hooks/monitors/MCP headersHelper でシェル形式コマンド内の `${user_config.*}` を拒否。hooks は exec 形式または `$CLAUDE_PLUGIN_OPTION_<KEY>` を使用、monitors と headersHelper はスクリプト内で値を読み取る |
| Breaking | プラグイン設定の読み込み制限 | プロジェクトレベル `.claude/settings.json` からのプラグインオプション値（`pluginConfigs`）読み込みを無効化。ユーザー設定、`--settings`、管理された設定からのみ読み込み |
| Fix | `/usage-credits` 入力検証の改善 | 不正な値（タイムスタンプなど）を数字に無言で削除する代わりにエラーで拒否。$1,000 超の金額は入力確認が必要 |

## まとめ

v2.1.207 は、Auto mode の一般提供という大きな機能変更に加え、ターミナルの応答性、設定管理、セキュリティ、バックグラウンドセッション、Remote Control、Deep Research など、幅広い領域での安定性と信頼性を向上させるメンテナンスリリースです。特にプラグインのシェルインジェクション対策と設定読み込み制限は、セキュリティ強化のための重要な変更です。Bedrock ユーザーにとっては認証情報の繰り返し要求問題の修正が大きな改善となるでしょう。デフォルトモデルの Opus 4.8 への変更により、より高性能なモデルが標準で利用可能になりました。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)