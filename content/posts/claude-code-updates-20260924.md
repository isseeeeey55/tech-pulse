---
title: "【Claude Code】v2.1.281 リリースノートまとめ"
date: 2026-09-24T08:04:17+09:00
draft: true
tags: ["claude-code", "mcp", "bedrock", "claude-tag", "artifact", "worktree", "agent-sdk", "vscode"]
categories: ["Claude Code Updates"]
summary: "v2.1.281 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.281 リリースノート

## はじめに

Claude Code v2.1.281 は、Claude apps gateway の機能拡張、MCP 関連の改善、セッション再開時の安定性修正、UI/UX の多数の改善を含む大規模なリリースです。

主な変更点は以下のとおりです。

- **Claude apps gateway** への `assume_role`・Bedrock guardrail・テレメトリ属性などの新機能追加
- **MCP** の URL モード elicitation 対応、`claude plugin validate` によるサーバーチェック強化
- セッション再開時の無限リトライ・ターン重複送信・プロンプトキャッシュ消失などの **多数の Fix**
- `/insights`・`/skills`・`/plugin` など **UI コンポーネントの改善**
- **Claude Tag（Slack）** および **Claude Code on the web** の個別修正

---

## 注目アップデート深掘り

### Claude apps gateway への `assume_role` と Bedrock guardrail サポート

Claude apps gateway の Bedrock upstream に `assume_role` が追加されました。これにより、gateway は STS 経由で IAM ロールを引き受けて Bedrock を呼び出せるようになります。別の AWS アカウントへのクロスアカウントアクセスや、開発者ごとに 1 セッションを割り当てる構成にも対応しています。

また、`guardrail: {id, version}` を Bedrock upstream に設定すると、その upstream 経由のすべてのリクエストに Amazon Bedrock guardrail が適用されます。リリースノートでは「すべての Bedrock upstream に設定するか、いずれにも設定しないかのどちらかにすること」と明記されています。

さらに `telemetry.resource_attributes` も追加され、Claude Desktop および `/login` セッションのテレメトリに固定ラベルを付与できるようになりました。

### `claude plugin validate` によるサーバーチェックの強化

`claude plugin validate` に MCP サーバーチェックが追加されました。具体的には以下の問題を報告します。

- ロード時に警告なく除外される `.mcp.json` エントリ
- 未宣言の `${user_config.*}` 参照
- 安全でない URL

プラグイン設定の事前検証が強化されることで、実行時に初めて問題が発覚するケースを減らせます。

---

## 実用的な活用ポイント

リリースノートに記載された変更から、以下の点に注意して活用してください。

- **`"attribution": false` の設定**: `settings.json` に追加することでコミットおよび PR の帰属表示をすべて非表示にできます。リリースノートでは「旧バージョンの CLI はこのキーを含む設定ファイルをスキップするため、バージョン間で共有するファイルではオブジェクト形式を維持すること」と説明されています。
- **`/insights` の auto mode 推奨**: 直近のセッションで auto mode が処理できたであろう権限プロンプトの数を推定して表示するようになりました。
- **`--agents` の改善**: `-p` とともにインライン JSON に加えて JSON ファイルのパスも受け付けるようになり、`prompt` を空にすることも許可されました。
- **自己ホスト型ランナーの `--system-prompt` 変更**: system prompt がコマンドライン引数ではなくプライベートファイルとして渡されるようになりました。`--system-prompt` または `--append-system-prompt` を使うラッパーや `command` フックは `--system-prompt-file` または `--append-system-prompt-file` に切り替える必要があります。

---

## 全変更点一覧

| カテゴリ | 内容 |
|---|---|
| Feature | Claude apps gateway: `desktop` ポリシーブロックで新しい Claude Desktop キー（`blockReadsOutsideWorkingDirectories`、`disableBypassPermissionsMode`）をサポート |
| Feature | Claude apps gateway Bedrock upstream に `assume_role` を追加（STS 経由、クロスアカウント・開発者別セッション対応） |
| Feature | Claude apps gateway Bedrock upstream に `guardrail: {id, version}` を追加（Amazon Bedrock guardrail を全リクエストに適用） |
| Feature | Claude apps gateway config に `telemetry.resource_attributes` を追加（テレメトリへの固定ラベル付与） |
| Feature | `settings.json` に `"attribution": false` を追加してコミット・PR の帰属表示を非表示にする機能 |
| Feature | MCP URL モード elicitation を 2026-07-28 プロトコル接続でサポート（サーバーがブラウザフローを Claude Code に開かせられる） |
| Feature | `claude plugin validate` に MCP サーバーチェックを追加（`.mcp.json` の除外エントリ、未宣言 `${user_config.*}`、安全でない URL を報告） |
| Feature | `/insights` に auto mode 推奨を追加（直近セッションで auto mode が処理可能だったプロンプト数を推定表示） |
| Feature | `/skills`・`/mcp`・`/plugin` インストール済みリストにスクロールバーを追加（フルスクリーンモード） |
| Fix | API リクエストのリトライ中に「unrecoverable interface error」クラッシュが発生する問題を修正 |
| Fix | モデルが解析不能なツールコールと出力制限トランケーションを交互に返すとき `--max-turns` を無視して無限リトライする問題を修正 |
| Fix | 再開セッションが以前のターンを変更された形で再送信する問題（並列ツールコールターン・MCP ツールコール入力・ツール検索結果）を修正 |
| Fix | 非常に大きなセッションを再開したとき最後の数メッセージしか復元されない問題を修正 |
| Fix | 保留中の権限プロンプト中に再起動した後のセッション再開で異なる履歴が送信されプロンプトキャッシュが壊れる問題を修正 |
| Fix | ツールコール中に終了したセッションの再開を修正（Claude はコールを確認しその結果が不明だと通知され、手動再開に隠し「Continue」メッセージが追加されなくなった） |
| Fix | API が読めなくなった以前の advisor 結果を持つセッションが毎ターン 1 リクエスト失敗し以前の reasoning を繰り返し失う問題を修正 |
| Fix | ツール検索がオフの場合に MCP サーバーが会話中に切断またはセッション再開後に接続中のときプロンプトキャッシュが失われる問題を修正 |
| Fix | プロキシ・ゲートウェイがストリームをクリーンに閉じたとき応答が完全として表示される問題、および重複したストリームイベントでツールコールが 2 回実行される問題を修正 |
| Fix | プロキシがストリームイベントを途中で落としたとき「Content block not found」で応答が失敗する問題を修正（部分応答は保持され、ウェブ検索は到着済み結果を維持） |
| Fix | ストリームの最終イベント前に接続が切れたとき空の完了応答が 2 回リクエストされる問題を修正 |
| Fix | プロキシがトレーリングの usage のみのフレームを送るとき停止理由が失われる問題を修正 |
| Fix | `CLAUDE_CODE_RETRY_WATCHDOG` セッションが 429/529 待ちの後の最初の 5xx や接続切断で失敗する問題、および 5xx の長い `Retry-After` で無制限かつ無音でスリープする問題を修正 |
| Fix | fast mode がサーバーから `Retry-After: 0` を受けたとき rate-limited リクエストを連続リトライする問題を修正 |
| Fix | 大きすぎる画像を返したツールが兄弟ツールコールを未回答のままにするか、最終メッセージなしでターンを終了する問題を修正 |
| Fix | モデルが 200 文字超えのツール名でコールした後「tool_use.name: String should have at most 200 characters」で会話が永久にスタックする問題を修正 |
| Fix | Claude Code が自身のメモリ使用量を読めないとき（ファイルディスクリプタ枯渇など）ツールコールが「Failed to get memory usage」で失敗または実行後に失敗報告される問題を修正 |
| Fix | `--input-format stream-json` セッション（Agent SDK・VS Code 拡張）とスケジュールされたクラウドセッションが以前のアシスタントメッセージにプレーン文字列コンテンツがある場合に毎ターンエラーで失敗する問題を修正 |
| Fix | 非インタラクティブセッション（`-p`・Agent SDK）がセッション開始ディレクトリの削除後に次ターンで失敗する問題を修正 |
| Fix | ホスト側（SDK）MCP サーバーを持つヘッドレスセッションがホストがハンドシェイク中に応答を止めたとき最初のメッセージでスタックする問題を修正 |
| Fix | インタラクティブ起動が MCP サーバーやプラグインが未設定のとき managed-settings ネットワークリクエスト（約 80 ms、ネットワーク不達時 17 秒以上）を待機する問題を修正 |
| Fix | 3 MB 超の PDF 読み取りや @-メンションで最大 2 分の遅延が発生する問題を修正 |
| Fix | 特定 PDF ページの読み取りが中断されたときそのページレンダリングが最大 2 分間実行され続ける問題を修正 |
| Fix | macOS の `/.vol`・`/.nofollow`・`/.resolve`（ネットワークマウントに到達する可能性あり）以下のパスを承認前に権限ダイアログと添付チェックが読み取る問題を修正 |
| Fix | `rm -rf "$(pwd)"` のようにコマンド置換のみをターゲットにした再帰的 `rm` が auto および `--dangerously-skip-permissions` モードで未確認実行される問題を修正（Bash allow ルールがあっても確認を求めるようになった。`CLAUDE_CODE_DISABLE_SUBSTITUTION_RM_PROMPT=1` で無効化可能） |
| Fix | NUL バイトを含む権限ルールがワイルドカードマッチに展開される問題を修正（そのルールは何にもマッチしなくなった） |
| Fix | サンドボックスの `excludedCommands` エントリが `git rev-parse --git-dir`、シェルビルトインと同名のプログラム、`[WIP]` や `#` 行を含むコミットメッセージにマッチしない問題を修正 |
| Fix | `CLAUDE_CODE_TMPDIR` が設定されているときサンドボックス化された Bash コマンドが `$TMPDIR` に書き込めない問題を修正 |
| Fix | `claude --bg` がワークスペーストラストプロンプトを通過していないディレクトリでバックグラウンドセッションとプロジェクトフックを開始する問題を修正（インタラクティブでない場合はトラスト確認または終了） |
| Fix | `--setting-sources`（および SDK `settingSources`）が生成されたセッション（teammates・`/bg`・`claude agents`・`--worktree --tmux`）に転送されない問題を修正 |
| Fix | Read・Write・Edit・NotebookEdit でファイルパスに null バイトが含まれるとターン全体が終了する問題を修正（そのツールコールが明確なエラーで失敗するようになった） |
| Fix | Write がファイルパスまたはコンテンツを同一値で 2 つのパラメータ名で渡したコールを拒否する問題を修正 |
| Fix | ヘッドレス・SDK セッションで作業ディレクトリ内の `--add-dir` ディレクトリの CLAUDE.md やルールファイルがモデルに 2 回送信される問題を修正 |
| Fix | 権限プロンプトとサンドボックスネットワークアクセスプロンプトが重なって両方回答された後リモートセッションが「needs approval」のまま残る問題を修正 |
| Fix | クラウドセッションがワーカー再起動直前に完了したバックグラウンドエージェントを Claude に通知しない問題を修正 |
| Fix | リモートセッションのスケジュールルーティンと通知ターンが最初のツールコール後まで turn-start notices（利用可能なツール・MCP 変更・日付・todos）を受信しない問題を修正 |
| Fix | スケジュールタスクと `/loop` ウェイクアップが配信失敗時に毎秒再発火してターン終了時に Claude Code が終了する可能性がある問題を修正 |
| Fix | Remote Control が組織ポリシーがまだ読み込まれていないだけなのに「disabled by your organization's policy」と報告する問題を修正 |
| Fix | Artifact ツールが `claude remote-control` で起動する Remote Control セッションから欠落する問題を修正 |
| Fix | macOS でログインキーチェーンがロックされているとき（スリープ後など）クレデンシャル書き込みが MCP OAuth トークンを削除またはキーチェーンエントリを消去する問題を修正 |
| Fix | Claude Code の終了またはリフレッシュタイムアウト時に `gcpAuthRefresh`/`awsAuthRefresh` ログインプロセスが残留する（Windows ではコールバックポートを保持する）問題を修正 |
| Fix | 別の Claude Code プロセスからログインした後もセッションで「Not logged in · Run /login」フッターと欠落した claude.ai コネクタが残留する問題を修正 |
| Fix | `mcp_tool` フックがブロッキングイベント（PreToolUse 等）で MCP サーバーがまだ接続中のときスキップされる問題を修正（MCP 接続タイムアウトまで待機するようになった） |
| Fix | プラグインまたは claude.ai コネクタと設定済みサーバーの URL 表記が異なる（ホストの大文字小文字・デフォルトポート・末尾スラッシュ）とき同じ MCP サーバーが 2 回接続される問題を修正 |
| Fix | `MCP_CONNECTION_NONBLOCKING=0` が `MCP_CONNECT_TIMEOUT_MS` を無視して claude.ai コネクタを 1 秒後に諦める問題を修正 |
| Fix | `--channels` プラグインエントリがインストール済みプラグインのマーケットプレイスのみに対してチェックされる問題を修正（インストール済みプラグインの名前もエントリと一致する必要がある） |
| Fix | `--plugin-dir` が `.claude-plugin/marketplace.json` を持つプラグインフォルダで 1 つの空プラグインをロードする問題を修正 |
| Fix | `claude plugin uninstall` が無効化されているプロジェクトスコープのプラグインを「enabled at project scope」と言って削除拒否する問題を修正 |
| Fix | `claude plugin update` で `--scope` を省略したとき project スコープのプラグインが失敗する問題を修正（user と決め打ちせずインストール済みスコープを解決するようになった） |
| Fix | `claude plugin validate` が `privacyPolicyUrl`・`supportUrl` などのリスティングメタデータキーを未知フィールドとして報告する問題を修正 |
| Fix | `known_marketplaces.json` がリモートに到達できず `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE` が既存クローンを維持したときマーケットプレイスをリフレッシュ済みとして記録する問題を修正 |
| Fix | `/plugin` Errors タブで最後のエラーが解決された後に確認が表示されない問題を修正 |
| Fix | `/plugin` で最初の処理中に Enter を再度押すと同じプラグインの 2 回目のアンインストールまたは更新が開始する問題を修正 |
| Fix | `/plugin` がマーケットプレイスソースを確認中に `y` を押し続けると「Add marketplace?」の質問が表示された瞬間にマーケットプレイスが追加される問題を修正 |
| Fix | `/permissions` の削除・ディレクトリ削除確認で No にポインタがあるのに `1` が Yes に回答してワークスペースディレクトリを連続削除できる問題を修正 |
| Fix | Alt+T と `/config` が thinking をオフにできないモデルでもオフにするオプションを提供する問題を修正 |
| Fix | `/context` の合計が最後のレスポンス以降に追加されたメッセージを除外する問題を修正 |
| Fix | `/model` が拒否時に生の API エラー JSON とリクエスト ID を表示する問題を修正（サーバーのメッセージを表示してモデルが変更されなかったことを伝えるようになった） |
| Fix | HTML エラーページからの API エラー（プロキシの 429 や 502 ページ等）が生マークアップを印刷したりステータスを省略したりする問題を修正 |
| Fix | `/feedback`・`/bug`・`/share` が送信中にキャンセルしても送信を続ける問題を修正 |
| Fix | `/feedback`・`/bug`・`/share` がダイアログ開中に Remote Control Stop が届くと以後すべての送信が「Couldn't send feedback」で失敗する問題を修正 |
| Fix | `/ide` が実行中の IDE をリストしながらも「No available IDEs detected」を表示する問題を修正 |
| Fix | `/setup-bedrock` または `/setup-vertex` が新設定を適用するために Claude Code を再起動するとターミナルが壊れた状態（クラッシュまたは入力文字化け）になる問題を修正 |
| Fix | `~/.claude.json` の `respectGitignore` または `copyFullResponse` が `null` のとき `/config` が終了する問題を修正 |
| Fix | `/rename` のセッション名が Claude が複数選択の質問をしている間に消える問題を修正 |
| Fix | VS Code または Remote Control からのプロンプトや展開されたペーストプレースホルダーで 1 行のペーストが独立した行に表示される問題を修正 |
| Fix | Claude が作業中にキューに入れたメッセージの IDE 選択が失われるまたは変わる問題、およびキューに入れたメッセージが選択を表示しない問題を修正 |
| Fix | Shift+Tab を素早く 2 回押すと間違った権限モードに移動する問題を修正 |
| Fix | Ctrl+C または Ctrl+D を 2 回押すとダイアログを閉じる代わりに Claude Code が終了する問題（`/memory`・`/hooks`・`/mcp`・`/export`・`/copy`・`/theme`・`/teleport` など残りのダイアログとピッカーで修正） |
| Fix | 1 バースト入力で届くキー（Remote Control 経由の矢印キー+Enter・`x`・`s` など）が以前の選択に作用する問題（`/effort` のモデルピッカーでの古い effort レベル、`/skills`・バックグラウンドタスク行・MCP サーバープロンプト・`/install-github-app` での以前ハイライト行）を修正 |
| Fix | `/install-github-app` が「Skip workflow update」選択後にワークフローを更新する・繰り返し Enter でセットアップを 2 回実行する・リポジトリステップで ↑ がリポジトリ名入力をブロックする問題を修正 |
| Fix | vim モード: `dj`/`dk`/`dG`/`dgg` とその `c`/`y` 形式が行の一部にしか作用しない・`1G` が最終行に移動する・`d0`/`c0`/`y0` が何もしない・`.` がインサート繰り返し後にカーソルが 1 つずれる・`o`/`p` が `!` プレフィックス行でシェルモードに切り替わる問題を修正 |
| Fix | vim モード: `cw` がスペース・空行・単語の最終文字・1 文字単語で次の単語も変更する・ヒンディー語・ベンガル語等のスクリプトで単語モーションが単語内で止まる・`!` で始まるテキストを挿入する `.`/`p`/`P` がシェルモードに切り替わる・テキストが失われる・間違った文字を編集する問題を修正 |
| Fix | アクセントをそのままキー入力した後にプロンプトカーソルが 1 文字多く移動する問題を修正 |
| Fix | 箇条書きテキストが次の行から始まるリスト項目の上に余分な空行が表示される問題（スクリーンリーダーモード・引用リスト・長いリスト）を修正 |
| Fix | 数字の箇条書き（`- 316.` 等）が文字・ローマ数字・間違った数字として表示される問題を修正 |
| Fix | エージェントパネルのフッターヒントが `keybindings.json` でリバインドされたキーを無視する問題、および stop-all-agents ショートカットがバインドされていないとき ` · ` が残留する問題を修正 |
| Fix | エージェントパネルフッターが既に表示中のエージェントに「Enter to view」と「x to stop」を提供する問題、およびメインが既に表示中のメインロウに「Enter to view」を提供する問題を修正 |
| Fix | エージェントパネル行のマウスクリックでキーボードカーソルが以前の選択行に残る問題を修正 |
| Fix | Esc が選択中のエージェントパネル行の選択解除ではなく実行中のターンを中断する問題を修正 |
| Fix | フルスクリーンモードのダイアログリスト（`/skills` など）で PgUp・PgDn が機能しない問題を修正 |
| Fix | `/heapdump` サマリーがメモリの大部分が JS ヒープスナップショット内にあるときネイティブと表示する問題を修正 |
| Fix | Bash edit-diff スナップショットディレクトリが temp フォルダに蓄積される問題を修正（放棄されたものは即時削除、残りは Claude Code 終了時に削除） |
| Fix | `/workflows` でリストが開いているときに新しい実行が開始するとポインタが別の実行に移動し `x` がそれを停止する問題を修正 |
| Fix | タブ付きダイアログ（`/config`・`/plugin`・`/permissions`）でカラーオフ（`NO_COLOR`）のときタブバーにフォーカスがある間、選択タブのハイライトが表示されない問題を修正 |
| Fix | `/plugin` インストール済みリスト上のマウスホイールがリストではなく背後のペインをスクロールする問題を修正 |
| Fix | フルスクリーンモードでスクロールやフィルタリングによりリスト行がマウスから離れた後もホバーハイライトが残留する問題を修正 |
| Fix | `/remote-control` メニューなどの長いリスト行が狭いターミナルで 2 行に折り返す問題を修正（`…` でカットするようになった） |
| Fix | `/hooks` と `/mcp` の詳細ビューで長い値が狭いターミナルで下の行に印刷される問題を修正 |
| Fix | `/plugin` のスキル状態オプションなどのリストがスクリーンリーダーモードで数字入力に応答しない問題を修正 |
| Fix | Windows: `$TMPDIR/…` に書き込む Bash コマンドが「Permission denied」で失敗する問題を修正 |
| Fix | Windows: 同時に更新する Claude Code セッションが互いの `claude.exe` バックアップを削除して `claude.exe` が残らなくなる可能性があるレースコンディションを修正 |
| Improvement | Claude Desktop サインインと使用制限エラーメッセージがターミナルコマンドではなくアプリを指すよう改善 |
| Improvement | 起動改善: managed settings とポリシーのフェッチが成功しないリクエストのリトライを行わなくなった |
| Improvement | インタラクティブ起動時間の改善: git 読み取り・起動テレメトリ・Bedrock/Vertex モデルアップグレードチェックが最初のフレームより前に実行されなくなった |
| Improvement | 多数のファイルを読み取った長いセッションの再開時間を改善（復元されたファイルキャッシュが読み取り時と一致するようになった） |
| Improvement | 非常に長い圧縮済みセッション（Agent SDK・Claude Desktop 経由が特に顕著）の再開時間を改善 |
| Improvement | 1 つの非常に大きな最初のプロンプトが占める「Prompt is too long」からの回復を改善（そのプロンプトが単独でサマライズされるようになった） |
| Improvement | セッション再開後の auto mode 改善: 権限クラシファイアが以前のプロンプトキャッシュを再利用できるようになった |
| Improvement | auto mode の拒否メッセージを改善: Claude が拒否を正確なコマンドだけでなく結果全体をカバーするものとして扱うようになった |
| Improvement | dangerous-rm チェックの改善: シェル変数にトップレベルのディレクトリ名が続く、作業ディレクトリから派生した変数、バックスラッシュのみのターゲットへの削除もフラグするようになった |
| Improvement | macOS サンドボックスガイダンスの改善: ローカル dev サーバーがポートをバインドできないとき `sandbox.network.allowLocalBinding` を案内するようになった |
| Improvement | `--agents` が `-p` とともにインライン JSON に加えて JSON ファイルのパスも受け付けるようになり、空の `prompt` を許可 |
| Improvement | `/batch` が WorktreeCreate フックがエージェントのワークツリーを提供する場所で実行できるように改善（git リポジトリ内のみでなくなった） |
| Improvement | プラグインフックの失敗エラーが問題のあるプラグインを明示するよう改善、および `claude plugin validate` がシェル形式のフックで `${CLAUDE_PLUGIN_ROOT}` が引用符なしのときに警告を追加 |
| Improvement | `/` メニュー・`/skills`・`/context`・`/plugin` インストール済みリストが claude.ai から同期されたスキルを短縮名で表示するよう改善（他のコマンドが同名を使用しない場合に `anthropic-skills:<name>` ではなく） |
| Improvement | `/deep-research` の長いリサーチブリーフでの信頼性を改善（スコープステップの出力から未使用の required フィールドを削除） |
| Improvement | パブリッシュされたアーティファクトページのライティングを改善（バンドルされたアーティファクトデザインスキルが平易で直接的な文章を求めるようになった） |
| Improvement | 低速接続でのアーティファクトパブリッシュを改善（大きなページアップロードが圧縮送信されるようになった） |
| Improvement | 大きな CLAUDE.md 起動通知が instruction ファイルをまとめてカウントするよう改善（多数の中サイズファイルと @-インポートも検出されるようになった） |
| Improvement | `env` 変数がセッションの起動環境ですでに設定されているため無視される場合にデバッグログで名前を表示するよう改善 |
| Improvement | タブ付きダイアログ（`/permissions`・`/usage`）のキーボードナビゲーション改善: ↑/↓ でタブ行とコンテンツ間のフォーカス移動、フォーカスがあるときのみリストがキーに応答 |
| Improvement | `/help` と `/sandbox` の改善: ←/→ と Tab でリスト内からタブ切り替え、`/help` の空の Custom commands タブで ↓ がキーをスタックさせなくなった |
| Improvement | `/install-github-app`・`/desktop`・`/permissions` の auto mode 環境プロンプト・`/plugin` の「Add marketplace?」と「Run this command?」プロンプトを標準ダイアログフレームに統一 |
| Improvement | `/workflows` と `/mcp` リストの改善: PgUp/PgDn・Home/End・j/k・マウスをサポート、`x` で `/workflows` のポインタ上の実行を停止 |
| Improvement | `/plugin` プラグイン・マーケットプレイス詳細メニューと `/remote-control` 接続済みメニューが Home/End と行クリックをサポート |
| Improvement | プロンプト下のバックグラウンドワークフロー行を改善: 名前・プログレスバー・広いターミナルでエージェント数・経過時間・合計トークン・大規模ワークフロー警告を表示 |
| Improvement | `/plugin` インストール済みリストの行が列（ステータス・名前・タイプ・詳細）で揃うよう改善 |
| Improvement | `/skills`: 各行がスキル名で始まり ✔ または ◯ のみ on/off を示し、狭いターミナルで 1 行に収まるよう改善 |
| Improvement | 狭いリスト行（`/skills`・`/workflows`・`/feedback`）の改善: 名前は最初の詳細の隣に 20 列を確保、詳細は完全に表示されるかまったく表示されないかのどちらか |
| Improvement | `/diff`: 変更ファイルの長いリストでスクロールバーが位置を示し、長いパスが行を折り返さなくなった |
| Improvement | `/hooks`: フックの詳細画面でフックの種類と変更場所を表示（常に settings.json を指す代わりに）、フック無効・セーフモード・managed-hooks-only 通知がそれぞれ 1 文で説明 |
| Improvement | `/mcp` のスクリーンリーダー出力改善: 無効なサーバーが「pending」ではなく「off」として読み上げられるようになった |
| Improvement | Remote Control 確認の改善: ターミナルウィンドウがフォーカスを取り戻した後に選択肢が短時間非アクティブになり、切り替え中に押されたキーが回答してしまわないようになった |
| Breaking | 自己ホスト型ランナーがシステムプロンプトをコマンドライン引数ではなくプライベートファイルとして渡すようになった: `--system-prompt` または `--append-system-prompt` を使うラッパーや `command` フックは `--system-prompt-file` または `--append-system-prompt-file` に切り替える必要がある |
| Change | send now（Ctrl+Enter または Ctrl+X Ctrl+S）が実行中のツールをキャンセルする代わりにバックグラウンドに移動するようになった |
| Change | auto mode でクラシファイアレビューがサーバーサイドで実行される場合、読み取り専用とサンドボックス化されたシェルコマンドもそのレビューを待機しフラグされたときブロックされるようになった |
| Change | `CLAUDE_CODE_AUTO_MODE_SERVER` が Anthropic API 直接接続でも適用されるようになった: `0` でサーバーサイド auto mode クラシファイアをオプトアウト（ローカルクラシファイアが使用量にカウントされる）、`1` でオプトイン |
| Change | `--dangerously-skip-permissions` および auto mode での危険な `rm` プロンプトが回答を 2 分間待ち、その後コマンドを書き直しヒントとともに拒否するようになった（`CLAUDE_CODE_DISABLE_DANGEROUS_RM_TIMEOUT=1` で無効化可能） |
| Change | Claude apps gateway が `managedMcpServers` エントリの `envHelper` パスが `\??\` または `/??/` で始まる場合に起動を拒否するようになった |
| Change | キューに入れたメッセージがスピナーの下ではなくスピナーの上の会話内に表示されるようになった |
| Change | プロンプト下のセッションアーティファクトリンクが 1 つのフッターピル（`⧉ name` または `⧉ N`）にまとめられ `/artifacts` を開くようになった（このセッションのアーティファクトを最初にリスト） |
| Change | Artifact ツールが artifact ページで unpkg.com からスクリプトをロードできるようになった |
| Change | フルスクリーンモードのリスト行（`/config` を含む）へのホバーが、フォーカス行の隣に 2 つ目の ❯ ポインタを描く代わりに行をティントするようになった |
| Change | `/mcp`: 各サーバーの行がステータスアイコンと名前で始まり状態を 1 回表示、狭いターミナルでは「managed」などの末尾情報を名前短縮より先に削除するようになった |
| Change | `/workflows`: 各実行の行がステータスアイコンと経過時間で始まり、狭いターミナルでは実行名と時間を保持してエージェント数とトークン数を先に削除するようになった |
| Change | Remote Control 添付ファイルダウンロードが接続を再利用し、セッション内で既にダウンロード済みのファイルをスキップするようになった |
| Change | MCP リソースリスト（リソースリストツールと @-メンション提案）が MCP Apps UI リソースをスキップするようになった（URI での読み取りは引き続き可能） |
| Change | `claude plugin uninstall --json` と `/plugin` ダイアログが別のインストール済みプラグインが同フォルダを使うまたはインストール記録が読めないためフォルダが残る場合にその旨を通知するようになった |
| Change | バックグラウンドタスクリスト（`/tasks`）で実行中の `/ultrareview` に `x` を押すと停止前に確認を求めるようになった |
| Change | 残留していた「(removed)」`/agents` エントリをコマンドメニューと `/help` から削除（`/agents` と入力すると移動先を説明） |
| Feature | [VSCode] VS Code と JetBrains パネルで auto mode がビルドクラシファイアリクエストにフォールバックするとき Continue/Stop プロンプトを追加 |
| Fix | [VSCode] メッセージなしで Web セッションを開くと再開できない空のローカルコピーが保存される問題を修正 |
| Fix | [VSCode] claude.ai/code セッションがサーバーの履歴返却失敗・一部ロード失敗・ネットワークサインインページの代替応答で空または会話の一部だけ開く問題を修正 |
| Fix | [VSCode] 拡張ホスト再起動後にエディタタブの会話がサイレントにハングする問題を修正 |
| Fix | [VSCode] チャットパネルでの複数選択の質問に Claude がオプションプレビューを添付する問題を修正 |
| Fix | [VSCode] セッションマネージャーのコストと使用量ブロックが狭いサイドバーで途中でテキストが折れる問題、およびアカウント切り替え後に以前のログインからの合計を表示する問題を修正 |
| Feature | [Claude Code on the web] クラウドセッションのコンポーザーのモデルメニューに Fast mode スイッチを追加（プランが fast mode を含み選択モデルが対応している場合） |
| Feature | [Claude Code on the web] GitHub セットアップヒントに設定ショートカット、リポジトリピッカーに「Troubleshoot GitHub connection」リンクを追加 |
| Fix | [Claude Code on the web] GitHub トリガーを持つルーティンが PR のドラフト変換時に発火しない問題を修正 |
| Fix | [Claude Code on the web] GitHub でホストされていないリポジトリのクラウドセッションに機能しない Create PR ボタンが表示される問題を修正 |
| Fix | [Claude Code on the web] GitHub セットアップヒントがリポジトリピッカーの検索ボックスと行を覆う問題を修正 |
| Improvement | [Claude Code on the web] クラウドセッションがファイルを開けないときのファイルカードを改善（ファイルが存在しないかセッションの権限設定がブロックしているかを表示） |
| Feature | [Claude Tag] 誰かが Stop を押した後に Slack スレッドに誰が止めたかを示す短い行を追加 |
| Fix | [Claude Tag] Claude が Slack のスレッド内返信への応答を永久に停止する問題を修正（影響チャンネルは次の新規メッセージで自動回復） |
| Fix | [Claude Tag] Slack でチェックインやバックグラウンドタスク終了時に Stop 後に中断されたリクエストを再開する問題を修正 |
| Fix | [Claude Tag] Claude のセッションがタスク途中でクラッシュした後 Slack への返信が数分後または永遠に届かない問題を修正（数分以内に自動再起動） |
| Fix | [Claude Tag] セッション設定が大きすぎて起動できないとき Slack が自動再起動を約束してから汎用エラーを出す問題を修正（理由と再試行方法をスレッドに表示） |
| Fix | [Claude Tag] 非常に長い Slack スレッドで Claude が数週間前のメッセージを参照して返信を保留する問題、およびスレッドの深い場所での再起動が最近のコンテキストを失う問題を修正 |
| Fix | [Claude Tag] Enterprise Grid の org-wide 共有から単一ワークスペースに移動した Slack チャンネルで「Couldn't check this channel just now」を返す問題を修正 |
| Fix | [Claude Tag] 共有チャンネルを多用する大規模 Enterprise Grid ワークスペースで静止時間後に「Couldn't check this channel」が再発する問題を修正 |
| Fix | [Claude Tag] 組織の inference フックによってブロックされた Slack リクエストが汎用リトライ通知を表示する問題を修正（フックの拒否メッセージを表示し Claude はリトライしなくなった） |
| Fix | [Claude Tag] Claude in Slack が組織が使用できないモデルへの切り替えを提案する問題を修正 |
| Fix | [Claude Tag] AWS 接続経由の DynamoDB と Kinesis アカウントベースエンドポイントへのリクエストが認証に失敗する問題を修正 |
| Fix | [Claude Tag] Claude Tag 管理設定の Plugins セクションが組織管理者でロードに失敗しプラグインが生 ID で表示される問題を修正 |
| Change | [Claude Tag] Slack スレッドで質問されたときのルーティンリストがチャンネルのすべてのルーティンではなくそのスレッドのスケジュールタスクをデフォルトで表示するようになった |
| Fix | [Code Review] レビュー済みコミットが失敗リトライ中にフォースプッシュされた場合に、全プッシュをレビューしない設定のリポジトリで PR がレビューされない問題を修正 |

---

## まとめ

v2.1.281 は Feature・Fix・Improvement・Change を合わせて 100 項目以上に及ぶ大規模なリリースです。

Claude apps gateway への `assume_role`・Bedrock guardrail・テレメトリ属性の追加が目立つ機能追加です。MCP まわりでは `claude plugin validate` によるサーバーチェック強化と URL モード elicitation の対応が加わりました。

Fix の大部分はセッション再開の安定性（ターン重複送信・プロンプトキャッシュ消失・無限リトライ）と、プロキシ・ゲートウェイ経由の接続品質に集中しています。UI 面では vim モード・スクリーンリーダー・狭いターミナルでの表示など細部にわたる修正と改善が含まれています。

自己ホスト型ランナーを利用している場合は、`--system-prompt` / `--append-system-prompt` から `--system-prompt-file` / `--append-system-prompt-file` への移行が必要な点に注意してください。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)