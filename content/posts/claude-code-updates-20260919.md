---
title: "【Claude Code】v2.1.277・v2.1.276・v2.1.275 リリースノートまとめ"
date: 2026-09-19T08:05:16+09:00
draft: true
tags: ["claude-code", "agents.md", "claude-apps-gateway", "mcp", "plugin", "artifact", "vscode", "claude-tag", "anthropic-api", "bedrock", "vertex", "foundry", "remote-control", "cowork"]
categories: ["Claude Code Updates"]
summary: "v2.1.277・v2.1.276・v2.1.275 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.277・v2.1.276・v2.1.275 リリース情報

## はじめに

2026年9月19日、Claude Code の 3 つのバージョン（v2.1.277・v2.1.276・v2.1.275）がリリースされました。v2.1.275 では新機能として AGENTS.md 対応やメッセージ送信の改善が導入され、v2.1.276 では v2.1.275 で発生した回帰バグが修正されました。v2.1.277 では AGENTS.md サポートの完成、プロキシ環境のネットワーク制御強化、および多数の安定性修正が実施されています。

## 注目アップデート深掘り

### AGENTS.md サポートとプロジェクト設定の柔軟化（v2.1.277）

v2.1.277 で `AGENTS.md` サポートが追加され、プロジェクトに `CLAUDE.md` が存在しない場合に Claude Code が代わりに `AGENTS.md` を読み込むようになりました。設定は `/config` の "Project instructions" から変更できます（Bedrock、Vertex、Foundry ではまだ利用できません）。

この変更により、プロジェクトごとに異なる設定ファイル名を使い分けることが可能になり、複数のエージェント型 AI ツールを並行利用するプロジェクトでの設定管理が柔軟になります。

### プロキシ環境のネットワーク制御強化（v2.1.277）

`CLAUDE_GATEWAY_PROXY_IS_EGRESS_BOUNDARY=1` 環境変数が追加され、Claude apps ゲートウェイの唯一の外部接続先がフォワードプロキシである場合に、すべての外向きリクエストがローカル DNS 解決ではなくプロキシにホスト名を渡すようになりました。また、ゲートウェイの upstream に対して静的ヘッダーを送信するための `headers:` マップも追加されています。

これらの機能により、厳格なネットワークポリシーを持つ環境でのプロキシ経由の接続制御がより細かく行えるようになります。

### プロキシ経由利用時の回帰バグ修正（v2.1.276）

v2.1.275 で発生した重大な回帰バグが v2.1.276 で修正されました。`ANTHROPIC_BASE_URL` がプロキシやゲートウェイを指している際に、すべてのリクエストが `400 … Input tag 'advisor_20260301'` エラーで失敗する問題が解消されています。

### メッセージ送信の即時実行機能（v2.1.275）

v2.1.275 で send-now キー（ctrl+enter、または ctrl+x ctrl+s）が追加され、現在のターンを中断してキューに入っているすべてのメッセージを一度に送信できるようになりました。送信済みおよびキュー中のメッセージは、モデルが受信するまでグレー表示されます。

この機能により、複数の指示を連続して送りたい場合に、前のターンの完了を待たずに次々と指示を投入できるようになります。

## 実用的な活用ポイント

### プロジェクト設定ファイルの使い分け

AGENTS.md サポートにより、複数の AI エージェントツールを併用するプロジェクトでも、それぞれに適した設定ファイル名を使えるようになりました。CLAUDE.md が存在しない場合は AGENTS.md が自動的に読み込まれるため、プロジェクト構成に応じた柔軟な設定管理が可能です。

### プロキシ環境での安定運用

プロキシやゲートウェイを経由する環境では、v2.1.276 以降の利用が必須です。v2.1.275 で発生したプロキシ環境での全リクエスト失敗問題が修正されており、`CLAUDE_GATEWAY_PROXY_IS_EGRESS_BOUNDARY` 環境変数により、外部接続の境界制御もより細かく設定できます。

### セッション再開とエラーハンドリングの改善

v2.1.277 では `claude -p` や Agent SDK セッションが内部エラー後にハングする問題が修正され、エラーを報告して終了コード 1 で終了するようになりました。また、多数のセッション復帰関連のバグ修正により、`--resume` や `--continue` での作業再開がより安定しています。

## 全変更点一覧

### v2.1.277

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | AGENTS.md サポート | CLAUDE.md がない場合に AGENTS.md を読み込む（Bedrock/Vertex/Foundry 未対応） |
| Feature | プロキシ境界設定 | `CLAUDE_GATEWAY_PROXY_IS_EGRESS_BOUNDARY=1` でプロキシへのホスト名渡しを有効化 |
| Feature | upstream 静的ヘッダー | Claude apps ゲートウェイの upstream に `headers:` マップで静的ヘッダーを送信可能 |
| Improvement | バックグラウンドタスク通知 | タスク完了時に `/tasks` などのパネルが開いている場合、更新待機中であることを表示 |
| Fix | セッションハング | `claude -p` と Agent SDK セッションが内部エラー後にハングせず、エラー報告して終了コード 1 で終了 |
| Fix | 空テキストブロックエラー | 空のテキストブロックを含む assistant ターン後に "text content blocks must be non-empty" でリクエストが失敗する問題 |
| Fix | ログアウト問題 | 古い Claude Code ビルドが同じマシンで動作した際に予期せずログアウトされる問題 |
| Fix | 起動ハング | `ANTHROPIC_API_KEY` ユーザーが `~/.claude.json` の `customApiKeyResponses` が不正な場合に起動がハングまたはエラー表示 |
| Fix | アップデートチェックエラー | プロキシが無効なバージョンを返す場合に 30 分ごとにエラーが発生、`claude update` がハングする問題 |
| Fix | アップデート報告 | winget/apk 管理のインストールでバージョン確認失敗時に "up to date" と誤報告する問題 |
| Fix | プラグインインストール | `claude plugin install` で再インストール時にセッション使用中のプラグインが壊れる問題 |
| Fix | Grep/Glob エラー | システムリソース不足時に "no matches" ではなくエラーを返すよう修正 |
| Fix | Write ツールエラー | 既存ディレクトリへの Write が declined permission として終了せず明確なエラーを報告 |
| Fix | Edit ツールエスケープ | エスケープされたバックスラッシュと `uXXXX` テキストを誤って `\uXXXX` エスケープとして扱う問題 |
| Fix | Edit ツールエラーメッセージ | 非 ASCII テキストを含む大きな Edit が一致しない場合のエラーメッセージ |
| Fix | null バイトエスケープ | ツール呼び出しのファイルパスに `\u0000` エスケープシーケンスが含まれる場合のエラー |
| Fix | バックグラウンドセッション | プラグインの LSP サーバー終了時に `claude --bg` が終了する問題 |
| Fix | MCP/plugin manage クラッシュ | `~/.claude.json` の `claudeAiMcpEverConnected` が不正な場合のクラッシュ |
| Fix | テーマ設定クラッシュ | `~/.claude.json` の `theme` が不正な場合の起動時クラッシュ |
| Fix | プロンプトカラーコードクラッシュ | ターミナルカラーコードを含むプロンプトでのクラッシュ |
| Fix | セッション復帰クラッシュ | 履歴に文字列として保存された assistant メッセージを含むセッションの復帰時クラッシュ |
| Fix | スピナー表示時の終了 | 重負荷マシンで最初のスピナー表示時に "unrecoverable interface error" で終了する問題 |
| Fix | 画面更新停止 | 内部レンダリングエラー後に画面更新が停止する稀なケース |
| Fix | Windows メモリエラー | Windows で Claude の返信直後にツール呼び出しが実行されない "Out of memory" エラー |
| Fix | SessionStart フックとキャッシュ | `/clear` 後の再開で SessionStart フックの出力により最初のメッセージが欠ける問題 |
| Fix | サブエージェントメッセージ表示 | 他エージェントからのメッセージがターン中に "Ran N shell commands" 行の下に表示される問題 |
| Fix | コピー通知 | フルスクリーン `/resume` ピッカーでのテキスト選択後に "copied" 通知が表示されない問題 |
| Fix | $TMPDIR 展開 | サンドボックス有効時に Bash コマンドで `$TMPDIR` が空に展開される問題 |
| Fix | WebFetch/WebSearch エラー | Cowork クラウドセッションで拒否理由（予算超過やポリシー）が Claude に伝わらない問題 |
| Fix | テレメトリリレー | Claude apps ゲートウェイのテレメトリリレーが `NO_PROXY` のホスト/ドメインを無視する問題 |
| Fix | マーケットプレイスポリシー | 不正な `strictKnownMarketplaces` または `blockedMarketplaces` エントリがポリシー全体を無効化する問題 |
| Fix | 自動更新の残骸 | 失敗した自動更新が `~/.cache/claude/staging` に大きなファイルを残す問題 |
| Fix | プラグインパネルの制御文字 | `/plugin` の Installed タブでメッセージからターミナル制御文字が除去されない問題 |
| Fix | スキル/コマンド名クラッシュ | `constructor` や `toString` のような Object プロパティ名のスキルで `/plugin` や `/skills` がクラッシュ |
| Fix | プラグインインストールエラー | 複数選択インストールがすべて失敗した場合にメッセージなしで閉じる問題 |
| Fix | アンインストール後の表示 | アンインストールされたプラグインが `/plugin` Installed に "failed to load" として再表示される問題 |
| Fix | プラグインコミット記録 | 公式マーケットプレイスのプラグインがコミットなしで `installed_plugins.json` に記録される問題 |
| Fix | プラグインリロードキャッシュ | リロードプレビューがすべてのプレビューコピーを終了まで保持、`--plugin-url` アーカイブを上書きする問題 |
| Fix | Remote Control セッション | `~/.claude.json` に不正なプレースホルダーレコードがある場合の失敗 |
| Fix | ログイン失効エラー | 失効した claude.ai ログイン後のエラーが "expired Anthropic profile" と表示、`/login` を案内するよう修正 |
| Fix | 入力スクランブル | `claude agents` の dispatch 入力でキーリピートまたは高速入力時にテキストが乱れる問題 |
| Fix | フック要約クラッシュ | 保存された transcript に不正な stop フック要約が含まれる場合の復帰時クラッシュ |
| Fix | Enter キー動作 | `keybindings.json` で Chat コンテキストの Enter を再バインドした場合の agent パネル行での Enter 動作 |
| Fix | PDF 読み取り | Windows で作業フォルダのパスが長い（約 120 文字以上）場合の PDF ページ読み取り失敗 |
| Fix | ヘッドレス統計 | `claude -p --resume`、SDK、VS Code 拡張のウィンドウリロード時にセッションのコストと使用量が 0 から開始する問題 |
| Fix | worktree スキル | `.claude/skills` が未追跡の場合に `--worktree` セッションでメインリポジトリのプロジェクトスキルが読み込まれない問題 |
| Fix | サンドボックス除外 | `sandbox.excludedCommands` の glob が複合 Bash コマンド全体を除外する問題 |
| Fix | サブエージェント MCP 再レンダリング | 復帰したサブエージェントとチームメイトが MCP ツール定義を再レンダリングする問題 |
| Fix | Artifact リトライ | レート制限された Artifact 公開で Claude に停止を指示する問題 |
| Fix | Attachment 再レンダリング | 会話中の以前の添付ファイルが復帰/再起動後に再レンダリングされる問題 |
| Fix | Console サインインエラー | サーバーが API キー作成を拒否した場合に "Request failed with status code 400" のみ表示する問題 |
| Fix | 作業中のメッセージ無視 | Claude がまだ作業中にタイプされたメッセージがモデルに無視される場合がある問題 |
| Improvement | SDK/ヘッドレス起動 | SDK と `claude -p` の起動時に最初のターンがディレクトリごとの CLAUDE.md 検索を待たない |
| Improvement | ゲートウェイエラーメッセージ | Claude apps ゲートウェイのループバックエラーメッセージが `CLAUDE_GATEWAY_ALLOW_LOOPBACK` を明記 |
| Improvement | MCP サーバー表示 | `/plugin` Installed で MCP サーバーがどのプラグインに属するかを表示 |
| Improvement | プラグインインストールメッセージ | すでにインストール済みのプラグインで新バージョンがある場合に通知、`claude plugin update` を提示 |
| Improvement | 起動通知オーバーフロー | ロゴ下の起動通知オーバーフロー行が "+N more · /status" ではなく "N more notices hidden" と表示 |
| Improvement | プロンプトクリーニング | プロンプト内の不可視 Unicode 書式・タグ文字を除去し、送信前にクリーン後のプロンプトを表示 |
| Improvement | /ultrareview メッセージ | レビュー対象がない場合の状況別メッセージと最新コミットレビューコマンドの提示 |
| Improvement | Artifact リンク処理 | Artifact ツールが利用可能な場合に claude.ai の Artifact リンクを WebFetch ではなく Artifact ツールで読み込み |
| Improvement | rm 許可プロンプト | 危険な rm コマンドを明記し `${VAR:?}` ガードを提案、ヘッドレス実行での復旧を支援 |
| Improvement | Artifact 許可プロンプト | 短文化、ページと Artifact をタイトル/ファイル名で表示、リンクをテキスト後に配置 |
| Breaking | Fable 表示 | Anthropic API の `/model` で Fable が常に表示され、組織設定で無効の場合のみグレーアウト |
| Breaking | サンドボックス説明 | Bedrock/Vertex/Foundry で Bash サンドボックス説明をファーストパーティ文言に変更 |
| Breaking | /ultrareview 拒否 | 非対話セッションでリポジトリにベースブランチまたは共有履歴がない場合に `/ultrareview` を拒否 |
| Breaking | サブエージェント結果表示 | サブエージェント結果をヘッダー付きでインデント表示、結果内テキストがセッション指示として扱われないよう変更 |
| Breaking | スクリプト prompt フレーミング | Bedrock/Vertex/Foundry で workflow スクリプトの `agent()` prompt がスクリプト作成テキストとしてフレーム化 |
| Breaking | Haiku 自動タイトル削除 | SDK/IDE 外で起動された `claude -p` からバックグラウンド Haiku 自動タイトルリクエストを削除 |
| Breaking | TaskOutput ツール削除 | 非推奨の TaskOutput ツールを削除、Read ツールでバックグラウンドタスク出力ファイルを読み込み |
| Feature | VSCode サインアウト | パネルメニューに Sign out 行を追加、タイプコマンドメニューに `/logout` を追加 |
| Feature | VSCode タスク管理 | エージェントマップにバックグラウンドシェルと実行中タスクを表示、各タスクに Stop ボタン、タイプコマンド `/tasks` |
| Feature | VSCode 応答コピー | 応答に Copy response ボタンとタイプコマンド `/copy` を追加 |
| Feature | VSCode アーカイブ通知 | 非アクティブセッションの自動アーカイブ時に 1 回限りの通知と Archived sessions グループに "Unarchive all" アクション |
| Feature | VSCode コスト/使用量表示 | プラン制限が適用されない環境（Vertex/Bedrock/Foundry/API key）で Account & usage ダイアログとセッションマネージャーにコスト/トークン使用量を表示 |
| Fix | VSCode 設定ダイアログ | "General config" メニュー行が `/config` 使用法テキストを表示せず設定を開くよう修正、タイプコマンド `/mcp`/`/hooks`/`/memory`/`/rewind` がダイアログを開く |
| Fix | VSCode Effort スライダー | `/effort` で保存したレベルが後続セッションで保持されない問題 |
| Fix | VSCode Auto モード | 保存されたモデル設定が "Sonnet" のような大文字小文字の異なるエイリアスの場合に Auto がピッカーから消える問題 |
| Fix | VSCode /fast 保存 | `/fast` が高速モードをデフォルトとして保存せず、拡張再起動後に失われる問題 |
| Fix | Web 環境ピッカー | Team/Enterprise プランの環境ピッカーに Personal/Organization セクションを追加、管理者が個人環境を組織と共有可能に |
| Fix | Web 組織環境 | Team/Enterprise プランで組織環境が Code タブから読み取り専用サマリーとして開き、Admin settings → Cloud environments で編集 |
| Fix | Web カスタムネットワークアクセス | Custom network access でドメインなしで保存した場合に Trusted に戻る問題、最低 1 ドメインを要求 |
| Fix | Web 管理設定ラベル | 管理 Claude Code 設定の "Web" ラベルを "Cloud sessions" に変更、冗長な読み取り専用 Mobile 行を削除 |
| Fix | Tag ルーチンチャンネル読み取り | Enterprise Grid org-wide インストールの Slack チャンネルで作成されたルーチンが実行時に他の公開チャンネルを読めない問題 |
| Fix | Tag 認証情報リンク | Claude Tag アクセスバンドルの認証プリセットの "Learn more" リンクが各ベンダーの認証セットアップページを開く |
| Fix | Tag Pylon プリセット | Claude Tag アクセスバンドルの Pylon 認証プリセットで管理者が Pylon の EU ホストを指定可能に |
| Fix | Tag Google Cloud 認証 | Claude Tag アクセスバンドルの Google Cloud 認証フォームで拒否されたキーファイルの理由表示、ウェブサイト/スコープのロック、拒否されたローテーション時のキー保持 |
| Fix | Tag ネットワークイベントログ | Claude Tag 管理設定のネットワークイベントログで AWS 署名/クライアント証明書/カスタム CA を使用する接続の応答ステータスが表示されない問題 |

### v2.1.276

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Fix | プロキシ経由のリクエスト失敗 | `ANTHROPIC_BASE_URL` がプロキシまたはゲートウェイを指す場合に `400 … Input tag 'advisor_20260301'` で全リクエストが失敗する v2.1.275 回帰バグを修正 |

### v2.1.275

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | ゲートウェイサインイン時のアカウント確認 | Claude apps ゲートウェイサインイン時にゲートウェイが指定したアカウントを確認してから認証情報を保存、`/status` で表示 |
| Feature | send-now キー | ctrl+enter（または ctrl+x ctrl+s）で現在のターンを中断し、キューに入ったメッセージを一度に送信、送信済みとキュー中のメッセージはモデル受信までグレー表示 |
| Feature | otelHeadersHelper 警告 | 設定された `otelHeadersHelper` が失敗した場合に起動時に警告、テレメトリが無音でエクスポートされないセッションを通知 |
| Feature | スキル・プラグイン同期 | claude.ai アカウントで有効化されたスキルとプラグインをターミナルセッションに同期、`syncClaudeAiSkills: false` または `syncClaudeAiPlugins: false` でオプトアウト |
| Feature | マーケットプレイス指定インストール | `/plugin install <plugin> --marketplace <source>` でプラグインインストール前にマーケットプレイスを追加提案 |
| Fix | メモリファイル age note | 復元されたメモリファイルの age note が compaction または resume 後にリクエスト間で変化し、プロンプトキャッシュミスが発生する問題 |
| Fix | サブエージェント出力欠落 | `--forward-subagent-text` の stream-json と SDK 出力で `context: fork` スキルが生成したサブエージェントのメッセージが欠落する問題 |
| Fix | @-mention ファイル提案 | カスタム `fileSuggestion` コマンドまたは `@.`/`@./` 入力時に @-mention ファイル提案が MCP リソースの下に埋もれる問題 |
| Fix | バックグラウンドタスク完了通知 | フルスクリーンモードで長いターンの折りたたまれたツール行の下に通知が配置される問題、各通知が開いた行を閉じるよう修正 |
| Fix | マーケットプレイス削除 | `claude plugin marketplace update` でフェッチ失敗時にリポジトリ名の GitHub マーケットプレイスのローカルコピーが削除される問題 |
| Fix | URL 内の認証情報表示 | プラグインとマーケットプレイスのメッセージ、ログ、`claude plugin marketplace list` で git/ssh/マーケットプレイス URL に保存されたパスワード/トークンが表示される問題 |
| Fix | クラウドセッション質問 | 復帰したクラウドセッションでキューに入ったメッセージが質問を置き換えた後、未回答の質問がトランスクリプトに残る問題 |
| Fix | vim モードカーソル | vim モードでドット繰り返し "!" または高速入力 "i!" が空でないプロンプトをシェルモードに切り替えた後、カーソルが 1 文字右に配置される問題 |
| Fix | フルスクリーンフリーズ | フルスクリーンモードで大きなファイル diff の上にスクロールした際に数秒間フリーズまたは空白になる問題 |
| Fix | ccmemory 閉じタグ | 応答に `</ccmemory>` スタイルの閉じタグが時々表示される問題 |
| Fix | プラグインサーバー表示 | プラグインメッセージ、ログ、VS Code プラグインダイアログで一部の git アドレスに対して間違ったサーバーが表示される問題 |
| Fix | ネットワークゲートウェイ API エラー | ベータリクエストヘッダーが拒否された際に API エラー応答を書き換えるネットワークゲートウェイ背後のユーザーでターンごとに `API Error: 400` が発生する問題 |
| Fix | サンドボックス終了コード | サンドボックス化された Linux の Bash コマンドでシェルが zsh の場合に失敗したコマンドが終了コード 0 を報告する問題 |
| Fix | Read ツールハング | メモリ圧迫下で大きなファイルの一部がデコードできない場合に Read ツールがエラーではなくハングする問題 |
| Fix | セッション復帰失敗 | `--resume`、resume ピッカープレビュー、復帰したバックグラウンドエージェント、トランスクリプトビューが不正な task-reminder または @-file attachment エントリを含むセッションで失敗する問題 |
| Fix | トランスクリプト復帰クラッシュ | 不正なメッセージエントリを含むトランスクリプトのセッション復帰時クラッシュ、スクロールアップ中の新メッセージ受信時のフルスクリーンクラッシュ |
| Fix | 不正メッセージブロック | 不正なメッセージコンテンツブロックを含む保存トランスクリプトのセッション復帰/起動失敗 |
| Fix | Grep/Glob ハング | 20MB 出力上限を超える検索で Grep、Glob、@-file 提案がハングまたはメモリ不足、システム ripgrep が警告氾濫後にエラーではなく "no matches" を報告する問題 |
| Fix | /rewind ファイル破損 | フォークまたはバックグラウンドセッションの `/rewind` でファイル履歴バックアップが完全にコピーできない場合にゼロ埋めまたは切り詰められたファイルが復元される問題 |
| Fix | フルスクリーン終了 | スラッシュコマンドドロップダウンが開いた状態で高速入力またはキー押下時に "Claude Code exited after an unrecoverable interface error" でフルスクリーンセッションが終了する問題 |
| Fix | バックグラウンドセッションクラッシュ | ファイルディスクリプタ不足のマシンで stdin から供給されたコマンド実行時にバックグラウンドセッションがクラッシュし worker を再起動する問題 |
| Fix | mcpNeedsAuthNoticed クラッシュ | `~/.claude.json` に不正な `mcpNeedsAuthNoticed` 値がある場合の起動時クラッシュ |
| Fix | ビルトインツール thinking 欠落 | `--resume` と `--continue` でサーバー側フラグによってオフにされたビルトインツールで開始した会話の以前の thinking が欠落する問題 |
| Fix | セッションピッカーコピー | フルスクリーン `claude --resume` セッションピッカーでマウス選択したテキストがクリップボードに到達しない問題 |
| Fix | プラグインリロードファイル上書き | `--plugin-dir` または `--plugin-url` アーカイブから読み込まれたプラグインのリロードプレビューが実行中セッションの抽出済みプラグインファイルを置き換える問題 |
| Fix | セルフホストランナー結果損失 | `--drain-wait-sec` を使用するセルフホストランナーが SIGTERM drain 中に完了したターンの最終結果を損失、ターンが報告されるまで待機するよう修正 |
| Fix | SubagentStop フック | 特定の `matcher` を持つ `SubagentStop` フックがエージェントタイプが空のすべての停止サブエージェントで発動する問題 |
| Fix | サンドボックス書き込み制限 | サンドボックス化された Bash コマンドが `hooks/` または `config/` という名前のプロジェクトディレクトリに書き込めない問題 |
| Fix | Artifact 復元 | セッションが別マシンで復帰またはスクラッチパッドがクリアされた後に Artifact 更新が "File not found" で失敗、ページの最終公開バージョンを復元 |
| Fix | /update-config 許可ルール | `/update-config` がファイル許可チェックと一致しない `Write(path)` 許可ルールを書き込む問題、`Edit(path)` ルールを書くよう修正 |
| Fix | ドキュメントリンク | バンドルされた claude-api スキルの live-sources テーブル内の 4 つの無効なドキュメント URL（Pricing、Computer Use、Skills、CLI）を修正 |
| Improvement | system-prompt キャッシング | `__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__` 行を含む `--system-prompt` でその上のテキストをグローバルにキャッシュ、SDK の配列形式と同様 |
| Improvement | /desktop エラーメッセージ | Claude Desktop が開かない場合の `/desktop` エラーで理由と次のアクションを提示 |
| Improvement | Artifact ツール結果 | Artifact ツールの publish と read 結果でページを開ける人と所有者の Share メニューの提供内容を表示 |
| Improvement | Artifact publish 結果 | 送信されたタブアイコンを明記、ページに NUL バイトが含まれる場合に警告、古い publish 後のマージ用の新しいページフェッチをリトライ |
| Improvement | 画像保存 | ペーストおよび添付された画像を許可プロンプトなしで Claude が開けるファイルとして保存、Desktop と VS Code を含む |
| Improvement | Artifact 更新ガイダンス | 共有 Artifact への編集アクセスが与えられた場合に Claude が別コピーを公開せず所定の場所で更新するようガイダンスを改善 |
| Improvement | プラン使用量読み取り | エディタウィンドウと 1 マシン上の非対話セッションが直近 1 分間の読み取りを共有、usage エンドポイントの呼び出しを削減 |
| Improvement | ListPlugins ツール説明 | `ListPlugins` ツール説明で Claude が claude.ai アカウントで有効化されたプラグインをリストし、`/plugin` でローカルインストールされたプラグインでないことを認識 |
| Improvement | 出力応答性 | ターミナルが遅いまたは一時停止時の応答性を改善、ターミナルがキャッチアップ中に出力がさらに遅れなくなった |
| Improvement | account-skills フォルダ結果 | 同期されたアカウントスキルフォルダ内のファイルに対する Write と Edit 結果で変更がアカウントに保存されず保存方法を表示 |
| Breaking | ゲートウェイ /logout | Claude apps ゲートウェイサインインの `/logout` でトークン失効を通知するゲートウェイ上のセッションも終了 |
| Breaking | 許可プロンプト保持 | ホストされたセッションがコンテナ再起動後に未回答の許可プロンプトを再度尋ねず保持 |
| Breaking | Artifact タブアイコン | Artifact ツールが最初の公開時に emoji favicon ではなく 1 ワードのタブアイコンを要求 |
| Breaking | Chrome 自動モード | 自動モードの Chrome の Claude が分類器承認呼び出しに対する拡張のサイトごとチェックをスキップ、バイパスモード同様に `browser_batch` の "Permission denied" 修正 |
| Breaking | npm プラグインインストール | npm ソースからインストールされたプラグインを `npm pack --ignore-scripts` でフェッチし整合性検証、パッケージのインストールスクリプトが実行されなくなった |
| Breaking | ルーチン Artifact 保存 | スケジュールおよび Run now のルーチン実行が尋ねずに編集可能な Artifact のデータ保存とページ再公開を実行、公開 Artifact、最初の公開、削除は依然として確認 |
| Breaking | ルーチン起動通知削除 | 前回セッション以降に実行された 1 回限りスケジュールルーチンを通知する起動通知を削除 |
| Feature | VSCode メモリ管理 | Memory ダイアログ内で保存されたメモリの表示、編集、削除 |
| Feature | VSCode 画像送信 | テキストを入力せずに添付画像を送信可能 |
| Feature | VSCode MCP サーバーリトライ | サーバーリスト読み込み失敗時に MCP サーバーダイアログに Retry リンクを追加 |
| Feature | VSCode 変更ごとの承認 | 提案変更 diff タブで各変更の下に承認/拒否ボタンを追加、変更ごとのレビューが可能 |
| Fix | VSCode トランスクリプトスクロール | 許可カード待機中にコンテンツが到着すると小刻みに下にスクロールする問題 |
| Fix | VSCode 許可モード | 巻き戻しおよびフォークされた会話が元の会話で選択された許可モードを保持しない問題 |
| Fix | VSCode CLAUDE_CONFIG_DIR | `environmentVariables` 設定の空の `CLAUDE_CONFIG_DIR` エントリが Claude Code のファイルをワークスペースに保持する問題 |
| Fix | VSCode プラグインインストールリンク | リンクで使用できないプラグイン名とマーケットプレイスアドレスのプラグインインストールリンクが Manage plugins ダイアログを開く問題 |
| Fix | VSCode Remote Control 表示 | Claude Code が失敗と報告したオフ操作後に Remote Control が接続中として表示される問題、オフとして表示 |
| Fix | VSCode 送信時の下スクロール | 送信時の下スクロールが返信到着中に下まで到達しない問題 |
| Fix | VSCode エージェントマップ状態 | セッション再開後にクラッシュで未完了のままのエージェントがエージェントマップで失敗ではなく停止として表示される問題 |
| Fix | VSCode 継続通知 | バックグラウンドタスクが実行中のクラッシュ後のリロードで "Continuing the step" 通知が表示されず継続制限がリセットされる問題 |
| Fix | VSCode セッションリスト | セッションリストがウィンドウリロード後など最後に再開された時刻を表示し、最後のメッセージ送信時刻を表示しない問題 |
| Fix | VSCode Fork 失敗 | Claude が作業中に送信されたメッセージの直後のメッセージで "Fork conversation from here" が失敗する問題 |
| Fix | VSCode プロンプトキャッシュクロック | Claude が作業中に送信されたメッセージを含むセッションを再開後にプロンプトキャッシュクロックが少なすぎる分数を表示する問題 |
| Fix | VSCode バックグラウンドエージェント完了 | Claude がツールを実行中にバックグラウンドエージェントが完了した場合、ウィンドウリロード後に完了通知とエージェントマップ上の結果が失われる問題 |
| Fix | VSCode git-ignored ファイル選択 | 拡張が数秒間無応答後に git-ignored ファイルで選択されたテキストが Claude に送信される稀なケース |
| Fix | VSCode セッション名変更 | 実行中セッションの名前変更が生成された名前に戻る問題（v2.1.269 の回帰） |
| Fix | VSCode claude.ai/code セッション | 一部の claude.ai/code セッションが VS Code でメッセージのない空の会話として開く問題 |
| Fix | VSCode スラッシュコマンド送信 | Claude が応答中にタイプされたスラッシュコマンドが応答完了後に実行されずテキストとしてモデルに送信される問題 |
| Fix | VSCode High Contrast Light | High Contrast Light テーマでプランプレビュー、Hooks、Permission rules ダイアログのコードが読めない問題 |
| Fix | VSCode /remote-control 無視 | Remote Control 接続中に `/remote-control` が無視される問題、再実行で Remote Control を即座にオフ |
| Fix | VSCode 返信中スクロール | 返信ストリーム中にスクロールアップ後に会話が下に引き戻される問題、送信時のジャンプをオフにする `claudeCode.scrollToBottomOnSend` 設定を追加 |
| Fix | VSCode マーケットプレイス URL 表示 | Manage plugins ダイアログでマーケットプレイス URL に入力されたパスワードまたはトークンが表示される問題 |
| Improvement | VSCode エージェントマップ | pill が実行中エージェントをカウントし失敗後に赤に変化、メインエージェントがマップスクロール中も表示、エージェントを状態→終了時刻でソート |
| Breaking | VSCode New session | Preferred Location が Sidebar 設定時に Claude エディタタブの New session がタブではなくサイドバーに開く |
| Breaking | VSCode 作業中メッセージ | Claude が作業中に送信されたメッセージが Claude が開始するまで会話の下で待機 |
| Feature | Web ルーチンリンク | ルーチンリンクが解決しなくなったページに "New routine" ボタンとルーチンリストへのリンクを追加 |
| Fix | Web ルーチン通知 | ルーチンの "paused" と "on hold" 通知が途中で切れる問題、paused-subscription 通知でルーチンを自分で再度オンにするよう案内 |
| Fix | Web ドメインリスト保存 | 許可ドメインリストが非常に長いクラウド環境が正常に保存され、その後すべてのセッション開始が失敗する問題、保存時に失敗し削減量を提示 |
| Fix | Web GitHub アクセス | 個人アカウントのクラウドセッションが GitHub アクセスを拒否された場合のガイダンスで管理設定ページではなく claude.ai/connect-github へのリンク |
| Improvement | Web ルーチン編集 | Claude に自分が作成していないルーチンの編集、削除、実行を依頼された場合に、自分で行えるようルーチンページへのリンク |
| Feature | Tag アクセスバンドル条件 | Claude Tag 設定のアクセスバンドルに attach 条件を追加、Owner がゲストまたは Slack Connect チャンネルでもバンドルを適用可能、メンバーのみのチャンネルに限定しない |
| Feature | Tag 認証情報プリセット | アクセスバンドルの Credentials タブに Amazon CloudWatch、CloudWatch Logs、Amazon SNS、Google Cloud Monitoring、Cloud Logging プリセットを追加 |
| Feature | Tag Datadog プリセット | US3、AP1、AP2、US1-FED サイトの Datadog プリセットを追加、新しい Datadog 接続を Datadog の読み取りとクエリ API ルートに制限 |
| Fix | Tag S3 アップロード | 最近の AWS CLI と SDK バージョンからの S3 アップロードが AWS 接続経由で 502 エラーで失敗する問題 |
| Fix | Tag チャンネル非アクティブ | ルーチンまたはスレッドからチャンネルに投稿中にチャンネルを非アクティブと扱い、タグなしメッセージをスキップする問題 |
| Fix | Tag スレッド表示名 | スレッドの "Claude [task]" 表示名がセッション更新または再起動後に "Claude" に戻る問題 |
| Fix | Tag モデル戻り | Slack スレッドで切り替えたモデルがスレッドのセッション再起動または更新後にチャンネルのデフォルトに戻る問題 |
| Fix | Tag 二重返信 | 別のアプリまたはボットがトップレベルチャンネルメッセージで @mention した際に Claude が時々二度返信する問題 |
| Improvement | Tag Enterprise Grid 通知 | ワークスペース間で共有される Enterprise Grid チャンネルの Claude の通知で、まだワークスペースが設定されていない場合や組織デフォルトのみが適用される理由を表示 |
| Fix | Code Review 分析欠落 | レビューエージェントの 1 つが予期しない形式で結果を返した場合にレビューが分析の一部を欠落する問題 |
| Fix | Code Review 完全再レビュー | 100 件以上の Claude レビューを持つプルリクエストがベースブランチからのクリーンマージごとに軽量なマージ重視レビューではなく完全再レビューされる問題 |

## まとめ

3 つのリリース全体を通じて、Claude Code の安定性と使いやすさが大幅に向上しました。v2.1.275 では新機能として AGENTS.md サポート、メッセージ送信の即時実行、claude.ai スキル・プラグインの同期などが導入され、開発者の作業効率を高める改善が多数実施されました。v2.1.276 では v2.1.275 で発生したプロキシ経由利用時の重大な回帰バグが迅速に修正され、v2.1.277 ではプロキシ環境のネットワーク制御強化と多数のバグ修正によって全体の安定性がさらに向上しています。

特に v2.1.277 では、セッションハング問題、エラーハンドリング、プラグインインストール周りの修正が多数実施され、ヘッドレス実行や SDK 利用時の信頼性が大きく改善されました。また、VS Code 拡張、Web 版、Claude Tag（Slack 統合）など、各プラットフォームでの機能強化と問題修正も含まれており、幅広い利用環境での品質向上が図られています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)