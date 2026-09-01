---
title: "【Claude Code】v2.1.257 リリースノートまとめ"
date: 2026-09-02T08:03:08+09:00
draft: true
tags: ["claude-code", "claude-fable-5-1", "mcp", "remote-control", "bedrock", "vertex", "foundry", "mantle", "vscode", "oauth", "bash", "powershell", "gitlab"]
categories: ["Claude Code Updates"]
summary: "v2.1.257 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.257 リリース情報

## はじめに

Claude Code v2.1.257 がリリースされました。このバージョンでは、新モデル Claude Fable 5.1 がデフォルトの Fable モデルとして追加され、1M コンテキストと最適化された料金体系（$10/$50 per Mtok、キャッシュ読み取りは $0.25/Mtok）が利用可能になりました。セキュリティ面では、クラウドメタデータ認証情報の取得やクロステナントアクセスを auto モードでデフォルト承認しないよう Containment Escape ルールが追加されました。タイムゾーン・時刻フォーマット設定の追加、多数のバグ修正と動作改善が含まれています。

## 注目アップデート深掘り

### Claude Fable 5.1 モデルの追加とデフォルト化

Claude Fable 5.1（`claude-fable-5-1`）が追加され、デフォルトの Fable モデルとして設定されました。このモデルは 1M トークンのコンテキストウィンドウに対応し、料金体系は入力 $10/Mtok、出力 $50/Mtok、プロンプトキャッシュ読み取りは $0.25/Mtok となっています。

従来の Fable モデルと比較して、より長い文脈を扱えるようになり、キャッシュ機構を活用することでコスト効率も向上しています。なお、Claude apps gateway セッションでは `fable` および `best` 指定は当面 Fable 5 を解決し続けます。これは、まだ Fable 5.1 に対応していない gateway がリクエストを拒否するのを防ぐためです。Fable 5.1 を使用したい場合は `/model` で明示的に選択してください。

### Containment Escape ルールによるセキュリティ強化

auto モードに Containment Escape ルールが追加され、クラウドメタデータ認証情報の取得、egress evasion、クロステナント到達が、環境で明示的に期待されているとマークされていない限り自動承認されなくなりました。

これにより、意図しないクラウド環境の認証情報漏洩や、サンドボックスからの不正なネットワークアクセスを防止できます。クラウド環境で Claude Code を利用する際の安全性が大幅に向上する重要な変更です。

## 実用的な活用ポイント

今回のリリースでは、時刻表示のカスタマイズが可能になり、`timeFormat` 設定（12時間、24時間、24時間 UTC、または strftime パターン）と `timeZone` 設定により、turn-end クロックとトランスクリプトビューのタイムスタンプを調整できるようになりました。

また、`CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 環境変数が追加され、`CLAUDE_CODE_SUBAGENT_MODEL`（またはメインモデル）をすべてのサブエージェントに適用し、spawn ごとやエージェント定義のモデルオーバーライドを無視できるようになりました。`/effort` コマンドに `s` オプションが追加され、`/model` と同様に現在のセッションのみで effort を変更できるようになっています。

ファイル読み取り権限管理も強化され、auto モードで初めて作業ディレクトリ外のファイルを読み取る前にプロンプトが表示され、そのような読み取りをブロックするオプション（`permissions.blockReadsOutsideWorkingDirectories`）が追加されました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Claude Fable 5.1 追加 | `claude-fable-5-1` をデフォルト Fable モデルとして追加。1M コンテキスト、$10/$50 per Mtok、キャッシュ読み取り $0.25/Mtok |
| Feature | 時刻フォーマット設定 | `timeFormat` と `timeZone` 設定を追加。12時間/24時間/24時間 UTC/strftime パターンで表示可能 |
| Feature | Containment Escape ルール | auto モードでクラウドメタデータ認証情報取得やクロステナントアクセスをデフォルト拒否 |
| Feature | サブエージェントモデル強制 | `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` 環境変数を追加し、全サブエージェントに同一モデルを適用可能に |
| Feature | セッション effort 変更 | `/effort` に `s` オプションを追加し、現在セッションのみで effort 変更可能に |
| Feature | サンドボックスマスクファイル警告 | `/doctor` で kill されたセッションが残したサンドボックスマスクファイルを警告 |
| Feature | 作業ディレクトリ外読み取りプロンプト | auto モードで初回の作業ディレクトリ外ファイル読み取り前にプロンプト表示。ブロックオプション追加 |
| Feature | ゲートウェイモデル description 対応 | ゲートウェイ提供の `/model` ピッカーエントリに `description` をサポート |
| Feature | VSCode アカウント・使用状況セクション | セッションリストパネルに折りたたみ可能な ACCOUNT & USAGE セクションヘッダーを追加 |
| Feature | VSCode モデル pill | 入力フッターに現在のモデルを表示し、モデルピッカーを開く pill を追加 |
| Feature | VSCode 出力スタイル選択 | コマンドメニューに出力スタイル選択を追加 |
| Feature | VSCode アーカイブ機能 | セッション削除を「アーカイブ」に変更。アーカイブセッションは専用グループに移動 |
| Fix | 起動後の `.claude/` 設定読み込み | 起動後に作成された `.claude/` フォルダの設定が再起動まで反映されない問題を修正 |
| Fix | エージェントビューからの permission mode | エージェントビューから `←` で開いたセッションが元セッションの permission mode で開始される問題を修正 |
| Fix | `keybindings.json` の Ctrl+G 無視 | `claude agents` で Ctrl+G の rebind が無視される問題を修正。Ctrl+S/Ctrl+T も新 `Agents` コンテキストで rebind 可能に |
| Fix | バックグラウンドセッション起動失敗 | macOS npm インストールの自己更新中や Windows の古いデーモンロックファイル問題でバックグラウンドセッション起動失敗を修正 |
| Fix | スラッシュコマンドパネル中のスピナー | スラッシュコマンドパネル後ろでレスポンスストリーム中にスピナーが停止する問題を修正 |
| Fix | バックグラウンドセッション state.json | スケジュール起動後の `state.json` `detail` が dispatch プロンプトを繰り返す問題を修正 |
| Fix | Completed 順序 | `claude agents` で再プロンプトしたバックグラウンドセッションが Completed に残る問題を修正。最新完了順に並び替え |
| Fix | 削除ディレクトリからの `--bg` | 削除されたディレクトリから `claude --bg` 実行時にクラッシュセッション行を残す問題を修正 |
| Fix | Remote Control プロンプトキャッシュミス | セッション途中で Remote Control 接続時に Bash ツール定義を再送信しプロンプトキャッシュミスする問題を修正 |
| Fix | カスタム Authorization ヘッダー | 二重リストのカスタム `Authorization` ヘッダーが Bedrock、Mantle、Vertex、WIF で設定認証情報を上書きする問題を修正 |
| Fix | Claude apps gateway の不要ヘッダー | Claude apps gateway が Foundry、Vertex、Bedrock に不要な `Authorization` やプロファイルヘッダーを送信する問題を修正 |
| Fix | Foundry API キーと認証トークン | Foundry API キーモードで不要な Anthropic API キーや認証トークンが送信される問題を修正 |
| Fix | `/schedule` ルーチン | メッセージロールなしで保存されたプロンプトを持つ `/schedule` ルーチンの問題を修正 |
| Fix | バックグラウンドセッション承認待ち表示 | `claude agents` でバックグラウンドセッションが承認待ちであることや送信者を表示しない問題を修正 |
| Fix | Ctrl+S プロンプト消失 | バックグラウンドセッション内で Ctrl+S で保存したプロンプトがアイドル時に消失する問題を修正 |
| Fix | テレメトリ設定 | サーバー管理設定経由でプッシュされたテレメトリ設定がウォームスタート時に無視される問題を修正 |
| Fix | チームメイト permission request 二重応答 | リーダーのメールボックス書き込みロック時にチームメイト permission request が二重応答される問題を修正 |
| Fix | 重複スラッシュコマンド行 | コマンドの自動継続レスポンスストリーム中に重複スラッシュコマンド行がレンダリングされる問題を修正 |
| Fix | policyHelper タイマー最大値 | `policyHelper` の `timeoutMs` および `refreshIntervalMs` がタイマー最大値を超えて失敗する問題を修正。クランプ処理を追加 |
| Fix | トークンカウンター | サブエージェントトランスクリプト切り替え後のトークンカウンターフリーズを修正。バックグラウンドカウンターのライブ更新を実装 |
| Fix | 末尾ドット付きホスト名 | サンドボックスネットワークホストの末尾ドット（`example.com.`）で `deniedDomains` が機能しない問題を修正 |
| Fix | Remote Control 同意プロンプト | Remote Control 同意プロンプトを Esc/`n` で却下しても同意としてカウントされる問題を修正 |
| Fix | `/mcp` 再接続 | `/mcp` reconnect と enable が設定ファイルの MCP サーバーをブロックすべき場合に接続する問題を修正 |
| Fix | `claude mcp remove` OAuth 認証情報 | `strictPluginOnlyCustomization` 時に `claude mcp remove` がリモートサーバーの OAuth 認証情報を残す問題を修正 |
| Fix | Remote Control モデル選択 | Claude app から開始した Remote Control セッションが選択モデルを無視する問題を修正 |
| Fix | `--disallowedTools` 設定リロード | `allowManagedPermissionRulesOnly` 有効時に `--disallowedTools` が最初の設定リロード後にドロップされる問題を修正 |
| Fix | `--resume` バックグラウンドセッション | `--resume` がバックグラウンドセッションを二重リスト、`--continue` が古いコピーを開く問題を修正 |
| Fix | フルスクリーンモード `!` 出力 | フルスクリーンモードで `!` シェルコマンド出力の展開クリックができない問題を修正 |
| Fix | 古いバイナリのバックグラウンドセッション | 自動更新後に古い Claude Code バイナリで動作するバックグラウンドセッションが蓄積する問題を修正 |
| Fix | `claude agents --json` 端末モード | `claude agents --json` が一時的に raw モードに切り替わり他プログラムの端末設定を上書きする問題を修正 |
| Fix | Proactive 出力スタイルビジーループ | Proactive 出力スタイルセッションがバックグラウンドコマンドや Monitor 実行中にビジーループする問題を修正 |
| Fix | サブエージェント接続切断時の停止 | レスポンスがスリープ、接続切断、サーバーエラーで途中で切断された時にサブエージェントが停止する問題を修正。自動継続を実装 |
| Fix | `/btw` パネル内の `←` | `claude agents` セッション内の `/btw` パネルで `←` が機能しない問題を修正 |
| Fix | advisor モデルプロンプトキャッシュ | advisor モデル設定時にバックグラウンドリクエストでプロンプトキャッシュミスする問題を修正 |
| Fix | `claude -p` Monitor 待機 | `claude -p` が Monitor 実行中に最終結果後約5秒で終了する問題を修正 |
| Fix | 複合コマンド内の `permissions.ask` | auto モードで複合コマンドやサブシェル内の `permissions.ask` ルールがスキップされる問題を修正 |
| Fix | プラグインシンボリックリンク | プラグインがシンボリックリンク経由でディレクトリ外のファイルを読み取れる問題を修正 |
| Fix | `/add-dir` カレントディレクトリ拒否 | `/add-dir` がカレントディレクトリ内のディレクトリを拒否する問題を修正 |
| Fix | メインエージェントへのサブエージェント再開通知 | トランスクリプトビューから停止したサブエージェントを再開してもメインエージェントに通知されない問題を修正 |
| Fix | ANSI カラーテキストペースト | ダイアログに ANSI カラーテキストをペーストするとクラッシュする問題を修正 |
| Fix | `claude mcp` FIFO ハング | `.mcp.json` が FIFO やデバイスファイルシンボリックリンクの場合にハングする問題を修正 |
| Fix | stream-json メモリ増大 | `claude -p --input-format stream-json` に非 JSONL データをパイプするとメモリが無制限に増大する問題を修正 |
| Fix | バックグラウンド時のツール拒否 | サブエージェント実行中にバックグラウンド化すると稀にツールが拒否扱いされる問題を修正 |
| Fix | Bash Read/Edit deny ルール | Bash `Read()`/`Edit()` deny ルールが `< file` リダイレクトや `tac`、`egrep` に適用されない問題を修正 |
| Fix | サブエージェント再開 5MB 超過 | 5MB を超えるトランスクリプトを持つサブエージェントの再開やメッセージ送信が失敗する問題を修正 |
| Fix | worktree 隔離セッション | worktree 隔離セッションが git に触れない Bash ループや変数読み取りを拒否する問題を修正 |
| Fix | `/model` と `/effort` キャッシュ警告 | 会話を空に巻き戻した後に `/model` と `/effort` でプロンプトキャッシュ警告が表示される問題を修正 |
| Fix | スクリーンショット多用時のキャッシュミス | スクリーンショット多用セッションで画像がリクエストサイズ上限を超えた後のプロンプトキャッシュミスを修正 |
| Fix | Edit パーミッションプロンプト diff 表示 | Edit パーミッションプロンプトの diff ビューで絵文字や複数コードポイント文字の幅が不正確になる問題を修正 |
| Fix | WebSocket MCP サーバーエラーログ | WebSocket MCP サーバー接続失敗が "[object ErrorEvent]" としてログされる問題を修正 |
| Fix | npm 更新中のバックグラウンドサービス | npm 更新ダウンロード中にバックグラウンドサービスが起動失敗する問題を修正 |
| Fix | detach したバックグラウンドコマンド | `timeout` や `setsid` 下で detach したバックグラウンドコマンドがタスク停止後も生き残る問題を修正 |
| Fix | バックグラウンドコマンド停止通知 | タスクパネルやクライアントからバックグラウンドコマンドを停止しても Claude に通知されない問題を修正 |
| Fix | バックグラウンドサブエージェント monitors | バックグラウンドサブエージェント停止時に monitors が実行され続ける問題を修正 |
| Fix | リンクされた worktree の git コマンド | リンクされた worktree のサンドボックス化 git コマンドがサブディレクトリ cd 後に共通 `.git` への書き込みアクセスを失う問題を修正 |
| Fix | Bedrock と Mantle の長時間 thinking | Opus 4.7 以降の長時間 hidden-thinking 中に Bedrock と Bedrock Mantle リクエストがサイレントになりタイムアウトする問題を修正 |
| Fix | Gateway セッション期限切れ | Claude apps gateway セッション期限切れや取り消し後の起動時にネットワークエラーではなく適切なメッセージと `/login` を表示 |
| Fix | クラウドセッション認証情報回復 | クラウドセッションでネットワークプロキシ起動失敗時に git/GitHub 認証情報が失われる問題を修正。バックグラウンドリトライを実装 |
| Fix | `cc-daemon-*` フォルダ残留 | 中断されたバックグラウンドデーモン起動後にシステム一時ディレクトリに残る `cc-daemon-*` フォルダを `cleanupPeriodDays` で削除 |
| Fix | `[[ ]]` 条件式の bash/zsh パース差 | bash と zsh で異なるパース結果を持つ `[[ ]]` 条件式を自動承認する問題を修正 |
| Fix | managed-settings テレメトリプロンプト | テレメトリ設定変更時の managed-settings 承認プロンプトが汎用警告を表示する問題を修正 |
| Fix | tmux/iTerm2 teammates シャットダウン | tmux/iTerm2 panes の agent-team teammates がシャットダウンリクエスト承認後も開いたまま残る問題を修正 |
| Fix | keyless Console サインイン設定 | keyless Console サインイン時にサーバー管理設定が適用されず、`/status` で Organization が表示されない問題を修正 |
| Fix | VSCode サードパーティプロバイダー | VSCode でサードパーティプロバイダー使用時に claude.ai 専用機能が表示され claude.ai を呼び出す問題を修正 |
| Fix | VSCode 使用量メーター | セッションリストパネルの使用量メーターがパネルロード後も空白のままになる問題を修正 |
| Fix | VSCode Remote Control トグル | "Enable Remote Control for all sessions" トグルが既存セッションに適用されない問題を修正 |
| Fix | VSCode スクリーンリーダー | フェンスや見出し前の制御文字で可視行がスピーチから欠落する問題を修正 |
| Improvement | レンダリングパフォーマンス | 長い会話での turn ごとの再レンダリング作業を削減。ストリーミング速度の低下とバックグラウンドエージェント更新時の全画面再レンダリングを改善 |
| Improvement | プロンプト入力レスポンシブ性 | キーストロークごとのレンダリング作業を削減し、プロンプト入力レスポンシブ性を向上 |
| Improvement | policy helper 診断 | 更新失敗を `/status` に表示。managed-settings ダイアログ拒否時に終了理由を出力。ヘルパータイムアウトをタイムアウトとして報告 |
| Improvement | `/code-review --comment` GitLab 対応 | `/code-review --comment` で GitLab マージリクエストに `glab mr note` 経由で findings を投稿 |
| Improvement | 通知 | 別ダイアログ下でキューイングされた MCP elicitation や permission ask が可視 ask と同じ遅延でアイドルデスクトップ通知を送信 |
| Improvement | verbose/transcript 出力 | 同時到着する非同期フック完了通知を 1 行に集約 |
| Improvement | `claude self-hosted-runner --configure-git` | git push negotiation も有効化し、古いクローンからの新ブランチ初回 push が新コミットのみをアップロードするよう改善 |
| Improvement | SDK ホストへの liveness 報告 | gateway keep-alive でレスポンスが保持されている間の liveness 報告を改善 |
| Improvement | MCP 認証情報ログ redaction | MCP 接続と OAuth のデバッグ/エラーログでサーバー URL やリクエストヘッダーの認証情報を redact |
| Improvement | `/fork` プロンプトキャッシュ保持 | `/fork` で元会話のプロンプトキャッシュを新バックグラウンドセッションに保持。worktree briefing をメッセージとして送信 |
| Improvement | emoji オートコンプリート | 残りの GitHub/Slack shortcode エイリアス（`:satisfied:`、`:telephone:`、`:collision:` など）に対応 |
| Change | `--effort` デフォルト hold 解除 | `--effort` が新モデルのデフォルト effort hold を永続的ではなくセッションのみ解除。Remote Control セッションで claude.ai で選択した effort を hold 中に適用 |
| Change | `policyHelper` シャドウ時の実行 | MDM や `managed-settings.json` の `policyHelper` がキャッシュされたサーバー管理設定でシャドウされた場合、削除報告時に即座に実行 |
| Change | `managedSourcesBehavior: "merge"` | `sandbox.credentials.awsPairs` と `sandbox.ripgrep` をソースごとに結合せず、最上位管理ソースから丸ごと取得 |
| Change | gateway モデルディスカバリー | `CLAUDE_CODE_ENABLE_GATEWAY_MODEL_DISCOVERY=1` を `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 設定時も実行 |
| Change | `--resume --bg` 動作 | `claude --resume <session-id> --bg` が実行中でないセッションを独自 ID で継続。コピーの場合はアナウンス |
| Change | `/btw` 履歴ブラウジングキー | `/btw` 履歴ブラウジングを `←`/`→` から `Shift+←`/`Shift+→`（または `[`/`]`）に変更 |
| Change | `defaultMode: "bypassPermissions"` 無視 | `.claude/settings.json` や `.claude/settings.local.json` の `defaultMode: "bypassPermissions"` を `"auto"` と同様に無視 |
| Change | gateway での `fable`/`best` 解決 | Claude apps gateway セッションで `fable` と `best` が当面 Fable 5 を解決。Fable 5.1 未対応 gateway での拒否を回避 |
| Change | `--add-dir` ネットワークパス拒否 | `--add-dir`、`/add-dir`、`additionalDirectories` でネットワークパス（UNC 共有、`/net/<host>` automounts）を拒否。Windows ではマップされたドライブレターを使用 |
| Change | Claude apps gateway TLS 証明書検証 | Claude apps gateway サインインとトークン更新リクエストで gateway のピン留め TLS 証明書を検証 |
| Change | Cowork と claude.ai artifact 読み取り | Cowork と claude.ai クラウドセッションで他ユーザーの artifact 読み取り時に auto モードでも常に確認 |
| Change | VSCode スラッシュコマンドダイアログ | アクションメニューのスラッシュコマンドをフィルタ可能な "Slash commands" ダイアログに表示。MCP サーバーダイアログもフィルタボックスを追加 |
| Removed | Bash/PowerShell プロンプト Ctrl+E | Bash と PowerShell パーミッションプロンプトの Ctrl+E コマンド説明を削除 |

## まとめ

v2.1.257 は、新モデル Claude Fable 5.1 の追加とセキュリティ強化を軸としたリリースです。Containment Escape ルールによりクラウド環境でのメタデータ認証情報アクセスがデフォルトで制限され、より安全な実行環境が提供されます。時刻表示のカスタマイズや effort の柔軟な変更など、ユーザビリティ向上も図られています。

多数のバグ修正により、バックグラウンドセッション、MCP サーバー、Remote Control、サブエージェント、worktree 隔離、プロンプトキャッシュなど、さまざまな機能の安定性と一貫性が向上しています。レンダリングパフォーマンスの改善により、長い会話やストリーミング応答での応答性も向上しました。VSCode 拡張機能では、UI の整理とアクセシビリティ改善が行われています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)