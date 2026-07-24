---
title: "【Claude Code】v2.1.219 リリースノートまとめ"
date: 2026-07-25T08:01:30+09:00
draft: true
tags: ["claude-code", "claude-opus-5", "sandbox", "mcp", "directoryAdded", "workflowSizeGuideline", "subagent", "stream-json", "claude-api", "vim", "remote-control"]
categories: ["Claude Code Updates"]
summary: "v2.1.219 のClaude Codeリリースノートまとめ"
---

## Claude Code v2.1.219 リリース情報

Claude Code v2.1.219 がリリースされました。本バージョンでは、新しいフラッグシップモデル Claude Opus 5 がデフォルトの Opus モデルとして追加され、100万トークンのコンテキスト長を持つようになりました。また、サンドボックス環境のネットワーク制御強化、MCP サーバーエラーの詳細表示、セルフホストランナーの安定性改善など、多岐にわたる機能追加と不具合修正が含まれています。

## 注目アップデート深掘り

### Claude Opus 5 のデフォルト化と fast モードの変更

Claude Opus 5 (`claude-opus-5`) が新たにデフォルトの Opus モデルとして追加されました。このモデルは 1M（100万トークン）のコンテキスト長を持ち、fast モードでの料金は入力 $10 / 出力 $50 per Mtok となっています。

これに伴い、Opus 4.7 が fast モードから削除され、`/fast` コマンドは現在 Opus 5 と Opus 4.8 に適用されるようになりました。また、claude-api スキルも Claude Opus 5 をデフォルトとするよう更新され、Opus 4.8 からの移行パスが提供されています。

動的ワークフローについても変更があり、デフォルトで中程度のサイズガイドライン（15 エージェント未満を目標）が設定されるようになりました。異なるサイズや制限なしの設定は、`/config` の Dynamic workflow size から変更できます。

### サンドボックスネットワークの厳密な許可リスト設定

`sandbox.network.strictAllowlist` 設定が追加されました。この設定を有効にすると、サンドボックス化されたコマンドが許可リストに含まれていないホストへのアクセスを試みた際、プロンプトを表示せずに拒否されるようになります。

これにより、開発環境のネットワークセキュリティをより厳格に制御できるようになり、意図しない外部接続を防止できます。特に本番環境に近い設定でテストを行う場合や、セキュリティポリシーが厳格なプロジェクトでの利用に有効です。

## 実用的な活用ポイント

Claude Opus 5 の 1M コンテキスト長により、大規模なコードベースやドキュメントを一度に処理できるようになります。fast モードの料金体系も明確化されているため、コスト管理がしやすくなっています。

MCP サーバーの接続エラー時に HTTP ステータスとエラーテキストが `claude mcp list` および `/mcp` コマンドで表示されるようになり、設定値の先頭・末尾の空白文字に対する警告も追加されたため、MCP サーバーの設定トラブルシューティングが容易になります。

セルフホストランナーについては、再起動中に承認した権限が失われる問題や、起動中に SIGTERM を受信した際の不具合が修正され、構造化された失敗カテゴリが追加されたことで、フックエラー、ランナークラッシュ、設定エラーを区別できるようになりました。

サブエージェントは、デフォルトで深さ 3 までネストしたサブエージェントを生成できるようになりました（従来は深さ 1）。ネストを無効化したい場合は `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` を設定します。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Claude Opus 5 の追加 | `claude-opus-5` がデフォルト Opus モデルとして追加。1M コンテキスト、fast モードは $10/$50 per Mtok |
| Feature | `sandbox.network.strictAllowlist` 設定 | サンドボックスコマンドで許可リストにないホストをプロンプトなしで拒否 |
| Feature | `DirectoryAdded` フック | `/add-dir` または SDK `register_repo_root` でセッション中に新しい作業ディレクトリが登録された後に発火 |
| Feature | `mcp_server_errors` のストリーム JSON 初期化イベント | `--mcp-config` エントリで設定検証によりスキップされた項目をリスト化。ターミナル実行時は起動警告を表示 |
| Feature | `workflowSizeGuideline` 設定キー | 動的ワークフローのサイズガイドラインを任意の設定ファイルから設定可能。設定中は `/config` 行を非表示 |
| Feature | ネストされたサブエージェント転送 | stream-json で深さ 2+ のサブエージェントが `--forward-subagent-text` 設定時に表示され、生成元 Agent の `tool_use` id でキー化 |
| Fix | `claude -p` のテキスト出力ドロップ | ターン中の API エラーで既に生成された回答が失われる問題を修正 |
| Feature | MCP 接続エラーの詳細表示 | `claude mcp list` と `/mcp` で HTTP ステータスとエラーテキストを表示。先頭・末尾の空白文字に警告 |
| Fix | セルフホストランナー再起動時の権限消失 | 再起動中に承認された権限がセッション再開時に失われ、承認済みアクションが実行されなかった問題を修正 |
| Fix | Fable モデルの表示ラベル | キャッシュされた古いラベルが含まれるプランで "Requires usage credits" と表示される問題を修正 |
| Fix | セルフホストランナー起動中の SIGTERM 処理 | 起動中に SIGTERM を受信するとリース期限まで stale なアクティブ行が残る問題を修正。正常に登録解除されるように |
| Feature | セルフホストランナーの構造化失敗カテゴリ | フックエラー、ランナークラッシュ、設定エラーを区別可能に |
| Fix | `/model` ピッカーの Opus 表示 | 統合された Opus 行が "Opus (1M context)" ではなく単に "Opus" と表示される問題を修正 |
| Fix | GNU screen でのコピー動作 | screen 内でコピーオンセレクトを実行すると base64 がターミナルに出力される問題を修正 |
| Fix | Remote Control クライアントの fast モードステータス | モデル切り替え、再接続、組織チェック失敗後に古い fast モードステータスが保持される問題を修正 |
| Fix | Windows での `CLAUDE_CODE_GIT_BASH_PATH` 処理 | パスが bash/sh バイナリでない場合に終了または bash として使用される問題を修正。警告を表示して無視するように |
| Fix | Vim モードの動作 | 空のプロンプトで ← キーを押すと NORMAL モードからエージェントビューに戻らない（INSERT モードのみ対応していた）問題を修正 |
| Fix | スクリーンリーダーモード | キー入力ごとに入力行全体を書き換えず、入力文字のみをエコーするように修正 |
| Improvement | Remote Control エラーメッセージの改善 | エラーの原因となった具体的な設定を表示 |
| Improvement | `claude --teleport` の表示改善 | 現在のチェックアウトがセッションのリポジトリと一致しない場合、どのリポジトリを指しているか表示 |
| Change | 動的ワークフローのデフォルトサイズ | 中程度のサイズガイドライン（15 エージェント未満）にデフォルト変更。`/config` で他のサイズまたは制限なしに変更可能 |
| Change | 管理 MCP 許可/拒否リストの `${VAR}` 解決 | 起動環境と managed-settings env から解決するように変更（settings-file env からではなく） |
| Change | `/model` ピッカーのハイライト | 最新モデルの名前のみをハイライトし、リストの任意のサブセットではなく新リリースをマークするように変更 |
| Feature | 実行中ワークフローのステータス行 | 現在のデフォルトワークフローサイズを表示し、変更用の `/config` へのポインタを提供 |
| Change | Opus 4.7 の fast モード削除 | `/fast` は Opus 5 と Opus 4.8 に適用 |
| Change | claude-api スキルのデフォルト更新 | Claude Opus 5 をデフォルトに、Opus 4.8 からの移行パスを提供 |
| Change | サブエージェントのネスト深度変更 | デフォルトで深さ 3 までネスト可能に（従来は 1）。`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` でネスト無効化可能 |

## まとめ

v2.1.219 は、Claude Opus 5 という新しいフラッグシップモデルの導入を中心に、多数の実用的な改善と不具合修正が行われたメジャーアップデートです。1M コンテキスト長による大規模処理能力の向上に加え、サンドボックスネットワークの厳密な制御、MCP サーバーエラーの可視性向上、セルフホストランナーの安定性改善など、開発体験と信頼性の両面で強化が図られています。動的ワークフローのサイズガイドラインがデフォルト化され、サブエージェントのネスト深度も拡張されたことで、より柔軟なワークフロー構築が可能になりました。細かな UI/UX の修正も含め、全体として堅牢性と使いやすさが向上したリリースと言えます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)