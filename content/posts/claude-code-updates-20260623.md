---
title: "【Claude Code】v2.1.186 リリースノートまとめ"
date: 2026-06-23T08:01:30+09:00
draft: true
tags: ["claude-code", "mcp", "workflows", "bash", "subagent", "skills", "plugin", "iterm2", "aws", "tmux", "pane", "yaml"]
categories: ["Claude Code Updates"]
summary: "v2.1.186 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.186 リリース情報

## はじめに

2026年6月23日、Claude Code v2.1.186 がリリースされました。本バージョンでは、MCP サーバー認証の CLI 対応、bash コマンド出力への自動応答機能、ワークフローのステータスフィルタリングといった新機能が追加されました。また、マシンのスリープ後のストリーミングエラーや subagent の UI 表示に関する不具合など、20件以上の修正が含まれています。

## 注目アップデート深掘り

### MCP サーバー認証の CLI コマンド対応

本リリースでは、`claude mcp login <name>` および `claude mcp logout <name>` コマンドが追加され、対話型の `/mcp` メニューを開かずに CLI から直接 MCP サーバーを認証できるようになりました。さらに `--no-browser` オプションにより、SSH 経由で標準入力からリダイレクトして認証を完了することも可能です。

これまで MCP サーバーの認証には対話型メニューが必須でしたが、本変更により自動化スクリプトやリモート環境でのセットアップが容易になりました。特に SSH 経由でのヘッドレス環境では、ブラウザを起動できないケースでも認証フローを完結できます。

### bash コマンド出力への自動応答

`!` で始まる bash コマンドの出力に対して、Claude が自動的に応答するようになりました。従来はコンテキストに出力が追加されるのみでしたが、この変更により対話的なスクリプト実行が可能になります。以前の挙動を維持したい場合は、settings.json に `"respondToBashCommands": false` を設定することで無効化できます。

この機能により、コマンド実行後の結果を踏まえた次のアクションを即座に提案・実行できるようになり、運用スクリプトの実行フローがよりスムーズになります。

## 実用的な活用ポイント

本リリースでは、CLI からの MCP サーバー認証が可能になったことで、リモート環境やCI/CD パイプラインでのセットアップ自動化が進められます。bash コマンドの自動応答機能は、デフォルトで有効化されているため、既存のワークフローで意図しない挙動が発生する場合は settings.json での無効化を検討してください。

また、ワークフロー詳細ビューでステータスフィルタリング（`f` キー）が使えるようになったことで、大量のエージェント実行履歴から特定状態のものを素早く絞り込めます。Skills の表示が `/plugin` の Installed タブに追加されたことで、インストール済みプラグインの管理がより直感的になりました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | `claude mcp login/logout <name>` コマンド追加 | CLI から MCP サーバー認証が可能に。`--no-browser` で SSH 経由の stdin リダイレクトに対応 |
| Feature | ワークフロー詳細ビューにステータスフィルタリング追加 | `/workflows` のエージェント詳細ビューで `f` キーによるフィルタリングが可能に |
| Feature | `/plugin` Installed タブに Skills セクション追加 | インストール済みプラグインに Skills 情報を表示 |
| Feature | `teammateMode: "iterm2"` 設定追加 | auto モードで `it2` CLI が見つからない場合に警告を表示 |
| Feature | AWS 認証情報のリフレッシュオプション追加 | `/login` に「Claude Platform on AWS - refresh credentials」オプションを追加（`awsAuthRefresh` 設定時） |
| Feature | `!` bash コマンドの自動応答 | bash コマンド出力に Claude が自動応答。`"respondToBashCommands": false` で従来の挙動に戻せる |
| Fix | スリープ後のストリーミングエラー修正 | マシンのスリープ復帰後に「Content block not found」や JSON パースエラーが発生する問題を修正 |
| Fix | subagent トランスクリプトのスクロール位置修正 | subagent 終了時にメイントランスクリプトへスクロール位置が漏れる問題を修正 |
| Fix | バックグラウンドタスクプレビューの表示修正 | エージェントのプラン読み込み前に生のツール名が点滅表示される問題を修正 |
| Fix | Chrome タブグループ分離の適用修正 | 並行 CLI セッション時に製品内パーミッションゲートがオフでもタブグループ分離を適用 |
| Fix | バックグラウンドセッション要約の重複修正 | エージェント自身のターン終了サマリーが要約行として表示されるように修正 |
| Fix | `claude agents` からのセッションオープン時の画面残像修正 | バックグラウンドセッションを開いた際に前画面が背後に残る問題を修正 |
| Fix | subagent スポーン時の `Agent(type)` ルール適用修正 | 名前付き subagent スポーン時に deny ルールと allowed-types 制限が適用されない問題を修正 |
| Fix | メインターン終了後の Esc/Ctrl+C 応答修正 | バックグラウンドエージェント実行中に Esc や Ctrl+C が効かない問題を修正 |
| Fix | パーミッションプロンプトの選択肢番号修正 | オプションテキストがオーバーフローした際に番号の位置がずれる問題を修正 |
| Fix | 完了 subagent の `x` キー動作修正 | エージェントパネルで完了した subagent に `x` を押しても閉じない問題を修正 |
| Fix | MCP サーバー切断通知の誤表示修正 | 古いセッション再開時に意図的に廃止されたツールで「MCP server disconnected」と誤表示される問題を修正 |
| Fix | `/plugin` Installed のスクロールインジケータ修正 | 最上部にスクロール済みでも「more above」が表示される問題を修正 |
| Fix | マークダウン打ち消し線のレンダリング修正 | アシスタントメッセージで `~~strikethrough~~` がチルダとして表示される問題を修正 |
| Fix | `--tools` フラグのフィーチャーゲートツール漏洩修正 | 初回起動時のフラグ読み込み前にゲート対象ツールが使える問題を修正 |
| Fix | `claude agents` のジョブステータス表示修正 | 返信後に古い「needs input」メッセージが残る問題を修正 |
| Fix | ライトテーマ時のダークフラッシュ修正 | ライトターミナルで `claude agents` からセッションを開く際にダークテーマが一瞬表示される問題を修正 |
| Fix | `claude agents` のテキスト選択ハイライト修正 | マウス選択したテキストを削除後もハイライトが残る問題を修正 |
| Fix | セッションコスト表示修正 | 使用量ベースの Enterprise/Team サブスクライバーでコストが表示されない問題を修正 |
| Fix | エージェントチーム `--effort` 継承修正 | tmux/pane バックエンドでスポーンされた teammate がリーダーの `--effort` レベルを継承するように修正 |
| Fix | ワークフロー subagent のスキーマ検証ループ修正 | スキーマ検証失敗の繰り返し時に無限ループせず、5回の試行後に中断するように修正 |
| Improvement | `claude mcp get/remove` のエラー提案改善 | タイポ時に最も近い設定済みサーバー名を提案し、長いリストを切り詰めるように改善 |
| Improvement | メモリ機能の改善 | サイズ制限に近づいた際に `MEMORY.md` インデックスの圧縮を促すように改善 |
| Improvement | スキル frontmatter のキー記法対応拡大 | `display-name`, `default-enabled`, `fallback`, `metadata.*` で kebab-case, snake_case, camelCase を許可 |
| Improvement | 不正な `SKILL.md` YAML frontmatter のハンドリング改善 | 失敗時も空のメタデータでスキル本体を読み込むように改善（サイレント失敗を回避） |
| Breaking | `CLAUDE_CODE_MAX_RETRIES` の上限変更 | 上限を 15 に制限。無人セッションでは `CLAUDE_CODE_RETRY_WATCHDOG` を使用 |
| Breaking | バックグラウンド subagent のパーミッションプロンプト表示変更 | 自動拒否ではなくメインセッションでプロンプトを表示。どのエージェントが要求しているか明示され、Esc でそのツールのみ拒否 |
| Breaking | `/review <pr>` のレビューエンジン変更 | `/code-review medium` と同じエンジンを使用するように変更 |

## まとめ

v2.1.186 は、CLI からの MCP サーバー認証や bash コマンド出力への自動応答といった開発体験の向上に加え、スリープ復帰時のストリーミングエラーや UI 表示に関する多数の不具合が修正されたリリースです。バックグラウンド subagent のパーミッションプロンプトがメインセッションに統合されるなど、エージェントチームの運用性も改善されています。破壊的変更として `CLAUDE_CODE_MAX_RETRIES` の上限制限と `/review` のエンジン統一が含まれるため、既存のワークフローへの影響を確認してください。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)