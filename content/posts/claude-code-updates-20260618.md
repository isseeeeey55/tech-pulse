---
title: "【Claude Code】v2.1.181 リリースノートまとめ"
date: 2026-06-18T08:01:32+09:00
draft: true
tags: ["claude-code", "config", "bun", "apple-events", "mcp", "oauth", "remote-control", "subagent", "aws", "foundry"]
categories: ["Claude Code Updates"]
summary: "v2.1.181 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.181 リリース：プロンプトからの設定変更とストリーミング改善

## はじめに

Claude Code v2.1.181 がリリースされました。このバージョンでは、プロンプトから直接設定を変更できる `/config` コマンドの追加、ストリーミング表示の改善、API接続の自動リトライ機能の強化が行われています。また、macOS上でのApple Events関連の問題修正や、ネットワークドライブでのファイル書き込みバグの修正など、多数の安定性向上が含まれています。

## 注目アップデート深掘り

### `/config` コマンドによる柔軟な設定変更

プロンプトから任意の設定を変更できる `/config key=value` 構文が追加されました。例えば `/config thinking=false` のように指定することで、インタラクティブモード、`-p` オプション、Remote Control のいずれでも設定を変更できます。

これにより、セッション中に設定ファイルを直接編集することなく、会話の流れに応じて動作をカスタマイズできるようになりました。特に思考モードの切り替えなど、タスクに応じて頻繁に変更する設定を素早く調整できる点が実用的です。

### ストリーミング表示とAPI接続の信頼性向上

長い段落のストリーミング表示が改善され、最初の改行を待たずに行単位でテキストが表示されるようになりました。また、API接続が思考中に切断された場合、「Connection closed while thinking」エラーを表示する代わりに自動的にリトライするようになりました。

これらの改善により、長いコードやドキュメントの生成時に出力の進行状況をリアルタイムで確認しやすくなり、ネットワーク不安定時の作業中断も減少します。

## 実用的な活用ポイント

起動時のパフォーマンス改善により、MCPサーバーが未設定の新規環境で最大120ms（2.1.169で発生していた回帰）の起動遅延が解消されました。また、ネットワークドライブやクラウド同期フォルダでのファイル書き込み時に0バイトファイルや切り詰められたファイルが生成される問題が修正されており、共有ストレージ上での作業の信頼性が向上しています。

macOS環境では、`CLAUDE_CLIENT_PRESENCE_FILE` 環境変数を設定することで、マーカーファイルを通じてモバイルプッシュ通知を抑制できるようになりました。また、`sandbox.allowAppleEvents` 設定によりサンドボックス化されたコマンドからApple Eventsを送信できるようになり、`open`、`osascript`、ブラウザベース認証フローが正常に動作するようになりました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | `/config key=value` 構文 | プロンプトから任意の設定を変更可能（interactive、`-p`、Remote Control で動作） |
| Feature | `sandbox.allowAppleEvents` 設定 | macOSでサンドボックス化コマンドからApple Eventsを送信可能に（オプトイン） |
| Feature | `CLAUDE_CLIENT_PRESENCE_FILE` 環境変数 | マーカーファイルを通じてモバイルプッシュ通知を抑制 |
| Improvement | Bun 1.4へのアップグレード | バンドルされたBunランタイムを1.4に更新 |
| Improvement | 長い段落のストリーミング改善 | 最初の改行を待たずに行単位でテキストを表示 |
| Improvement | API自動リトライ改善 | 思考中の接続切断時に自動リトライ（従来のエラー表示から変更） |
| Improvement | subagentパネル改善 | アイドル状態のsubagentは30秒後に自動非表示、リスト表示は5行まで、キーボードヒントをフッターに表示 |
| Improvement | MCP OAuth画面の改善 | Claude Codeの視覚スタイルに統一し、成功時に自動クローズ |
| Improvement | メモリ更新表示の簡素化 | `Improved N memories` 行が詳細モード外では個別ファイルを列挙しないように変更 |
| Breaking | フルスクリーンモードのURL開封 | Cmd+click（macOS）/ Ctrl+clickを要求（ネイティブターミナルの動作に合わせた変更） |
| Fix | カスタム `ANTHROPIC_BASE_URL` とFoundryでのプロンプトキャッシング | リクエストごとの認証トークン変化による読み込み失敗を修正 |
| Fix | ネットワークドライブでのファイル書き込み | Write/Editが0バイトまたは切り詰められたファイルを生成する問題を修正 |
| Fix | macOS上での `open`、`osascript`、認証フロー | エラー-600を修正（Apple Events entitlementを追加） |
| Fix | 起動時の遅延（回帰修正） | MCPサーバー未設定時に最初のプロンプトが設定取得を待機する問題を修正（最大120ms改善） |
| Fix | ネットワーク不良時の起動ブロック | アカウント設定取得が遅い場合に最大15秒間空白画面で停止する問題を修正 |
| Fix | 起動時クラッシュ | `.claude.json` に破損したnullプロジェクトエントリがある場合のTypeErrorを修正 |
| Fix | macOS TUIのフリーズ | Spotlight再インデックス中にセッション開始時Ctrl+Cが応答しなくなる問題を修正 |
| Fix | 長時間アイドルセッションの履歴喪失 | 他のClaude Codeプロセスが30日トランスクリプトクリーンアップを実行した際の履歴消失を修正 |
| Fix | foreground subagentの無制限ネスト | 5レベル深さ制限を適用（background subagentと同様） |
| Fix | モデル切り替え後の `/recap` とフォーク | 直前のモデルを使用する問題を修正 |
| Fix | subagent「Thinking」時間表示 | 親エージェントの経過時間ではなくsubagent自身の時間を表示 |
| Fix | ネストされたagent待機中の表示 | エージェントパネルで「waiting」ではなくティック表示されていた問題を修正 |
| Fix | APIリトライインジケーター残存 | リトライ成功後も画面に残る「Retrying in 0s · attempt N/10」を修正 |
| Fix | AWS `awsCredentialExport` 認証情報の頻繁更新 | 残存期間が短い場合の毎分更新を修正、`aws configure export-credentials` のJSON形式に対応 |
| Fix | `claude mcp get`/`list` の状態表示 | tools/list失敗時に `✓ Connected` と表示される問題を修正（`! Connected · tools fetch failed` とエラー詳細を表示） |
| Fix | `/remote-control` の接続確認 | 古い「connecting…」行が残る問題を修正（接続後トランスクリプトに確認表示） |
| Fix | ExitWorktree のクリーンworktree削除拒否 | Windows上で `git` が解決できない場合の「Could not verify worktree state」エラーを修正 |
| Fix | 設定変更時のENOENTエラー | `~/.claude` がシンボリックリンクで `~/.claude/settings.json` が相対シンボリックリンクの場合に `/effort` や `/model` が失敗する問題を修正 |
| Fix | IDE選択行番号のオフセット | コンテキストリマインダーで1行ずれていた問題を修正（IntelliJ、VS Code） |
| Fix | フルスクリーン Ctrl+C のクリップボード上書き | ネイティブターミナル選択後にアプリの前選択で上書きされる問題を修正 |
| Fix | Ctrl+V の誤エラー表示 | クリップボードにテキストがある場合に「No image found in clipboard」を表示する問題を修正 |
| Fix | agent作成時のEEXISTエラー | agentsディレクトリが既に存在する場合の失敗を修正（Windows/OneDrive） |
| Fix | AskUserQuestion プレビューの切り詰め | ダイアログ端でコンテンツが切れる問題を修正（ワードラップに変更） |
| Fix | AskUserQuestion 複数選択時の「Other」テキスト喪失 | 送信時に入力された自由記述回答が削除される問題を修正 |
| Fix | `/stats` の日付表示 | UTC負のタイムゾーンで「Most active day」と日次トークンチャートが1日早く表示される問題を修正 |
| Fix | Linux上での `/copy` とcopy-on-select | Claude Code起動後にインストールされたクリップボードユーティリティを検出しない問題を修正 |
| Fix | Writeプレビューのインデント | タブインデントコードが誤ったインデントで表示される問題を修正 |
| Fix | ターン途中のユーザープロンプト表示 | トランスクリプトで全幅背景ハイライトが表示されない問題を修正 |
| Fix | Ghosttyでのアクティビティスピナー表示 | パルスが誤ったグリフサイズで滞留する問題を修正 |

## まとめ

v2.1.181 は、ユーザビリティと安定性を中心としたメンテナンスリリースです。プロンプトからの設定変更、ストリーミング表示の改善、API接続の自動リトライといった日常的な使い勝手の向上に加え、起動時のパフォーマンス改善、ネットワークドライブでのファイル操作の信頼性向上、macOS上でのApple Events関連の問題修正など、幅広い環境での動作安定性が向上しています。特にsubagentの挙動修正やクリップボード処理、各種UI表示の不具合修正により、より快適な作業環境が提供されます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)