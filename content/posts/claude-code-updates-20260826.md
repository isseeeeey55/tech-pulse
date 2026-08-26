---
title: "【Claude Code】v2.1.246・v2.1.245・v2.1.243 リリースノートまとめ"
date: 2026-08-26T08:03:31+09:00
draft: false
tags: ["claude-code"]
categories: ["Claude Code Updates"]
summary: "v2.1.246・v2.1.245・v2.1.243 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260826/header.png)
# Claude Code v2.1.246/v2.1.245/v2.1.243 リリース情報

## はじめに

2026年8月25日から26日にかけて、Claude Code の v2.1.243、v2.1.245、v2.1.246 がリリースされました。v2.1.246 では Bash wildcard allow ルールに対する起動時警告や、バックグラウンドセッション起動失敗の複数修正、長い単一行を含む diff のレンダリング高速化など、61件の修正・改善が含まれています。v2.1.245 は glibc 2.44 を搭載する Linux ディストリビューション（Arch Linux、CachyOS、Fedora Rawhide など）での起動時クラッシュを修正したホットフィックスです。v2.1.243 では Loops 統計の表示、`modelPicker` 設定によるモデル選択のカスタマイズ、`promptCacheTtl` 設定の追加、組織の契約レートを反映する `modelPricing` マネージド設定、API キー不要のコンソールサインインなどが追加されました。

## 注目アップデート深掘り

### Loops 統計表示と Bash wildcard 警告の追加（v2.1.246 / v2.1.243）

v2.1.243 で `/usage` コマンドに Loops の詳細統計が追加されました。ループごとの実行回数、総トークン数、1実行あたりのトークン数、最終実行時刻が表示されるため、暴走したタスクや過度に多弁な `/loop` タスクを容易に特定できるようになりました。

v2.1.246 では、Bash allow ルールでサブコマンドの前にワイルドカードが使われている場合（例: `Bash(git * main)`）に起動時警告が追加されました。これらのルールはサブコマンドの前に挿入されるオプションにもマッチするため、意図しないコマンドを許可してしまう可能性があります。

### モデル選択とキャッシュ設定のカスタマイズ（v2.1.243）

`modelPicker` 設定により、`/model` コマンドで表示されるモデル一覧を組織向けにカスタマイズできるようになりました。ラベル付きのモデルリストを順序指定で定義でき、Vertex AI や Bedrock の ID 形式も含め任意のモデル ID 表記に対応します。組織の標準モデルを優先表示させたり、ビルトインのラインナップに追加または置き換えることが可能です。

`promptCacheTtl` と `subagentPromptCacheTtl` 設定が追加され、API キーまたはクラウドプロバイダーユーザーは、メインの会話では 1 時間のプロンプトキャッシュを維持しつつ、サブエージェントは 5 分に抑えるといった細かな制御ができるようになりました。

### 組織契約レートの反映とコンソールサインイン（v2.1.243）

`modelPricing` マネージド設定により、組織が契約したモデルごとの単価や割引率が `/cost` の表示、ステータスラインのコスト表示、テレメトリのコスト数値に反映されるようになりました。これまでリスト価格で計算されていたコストが、実際の契約条件に基づいて表示されます。

`/login` メニューに「Sign in with your Console account」という API キー不要のサインインオプションが追加されました。API キーの作成を許可しない組織でも、コンソールアカウントでのサインインが可能になります。

## 実用的な活用ポイント

v2.1.243 の Loops 統計表示により、自動化タスクのトークン消費量を定期的に監視し、コスト効率を改善できます。`modelPricing` 設定と組み合わせることで、組織の実コストに基づいたループタスクの最適化が可能です。

`modelPicker` 設定でプロジェクトや組織の推奨モデルを固定化することで、チーム間での一貫性を確保できます。Bedrock や Vertex AI を利用している場合も、カスタムラベル付きでモデル一覧を統一できます。

v2.1.246 のバックグラウンドセッション起動失敗の複数修正（起動ディレクトリ削除、マシンスリープ、他プロセスの npm パッケージ再インストールなど）により、長時間実行タスクやバッチ処理の信頼性が向上しました。

v2.1.245 により、最新の Linux ディストリビューション（glibc 2.44 搭載）での起動が安定化し、エッジ環境や CI/CD パイプラインでの利用が容易になりました。

## 全変更点一覧

### v2.1.246

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Bash wildcard 起動時警告 | サブコマンド前のワイルドカードを含む allow ルール（例: `Bash(git * main)`）に対し、オプションとのマッチ警告を起動時に表示 |
| Feature | Auto mode タブ追加 | `/permissions` に Auto mode classifier ルールを表示・編集するタブを追加 |
| Feature | 完了時刻の表示 | ターン終了時の duration 行に完了時刻を追加（例: `✻ Sautéed for 23s · done 6:05 PM`） |
| Fix | フルスクリーンモードの空白 | ターミナルリサイズと底部ジャンプ後に transcript が空白になり、次のキー押下まで表示されない問題を修正 |
| Fix | 長い単一行の diff 遅延 | base64 文字列など非常に長い単一行を含む diff で深刻な遅延が発生する問題を修正。該当行はマーカー付きで切り詰めて表示 |
| Fix | フルスクリーンスクロール | 過去のメッセージ位置でのフルスクリーンスクロールが不安定になり、底部ジャンプが途中で停止する問題を修正 |
| Fix | バックグラウンドセッション起動失敗 | 起動ディレクトリ削除、マシンスリープ、ホストプロセス起動遅延時に 45 秒後にバックグラウンドセッションが開けなくなる問題を修正 |
| Fix | バックグラウンドセッション EACCES | 別の Claude Code プロセスが npm パッケージ再インストール中に "EACCES" で失敗する問題を修正 |
| Fix | Markdown レンダリング無効化 | メッセージの最初の 500 文字に markdown がない場合、全体のレンダリングが無効化される問題を修正。`+`/`N)` リストと setext 見出しも対応 |
| Fix | MCP tool call 中断報告 | headless/remote セッションでメッセージ到着により中断された MCP tool call が "completed with no output" として報告される問題を修正。明示的な中断エラーを返すように変更 |
| Fix | MCP tool 引数の型 | parameter schema が空 (`{}`) の場合に MCP tool 引数が JSON 文字列として送信される問題を修正。実際の型で送信 |
| Fix | 中断コマンドの表示 | 実行中に中断されたコマンドが "Ran 1 shell command" と表示され、中断の兆候がない問題を修正 |
| Fix | Dynamic workflow 再起動 | `←` 押下または `/background` 実行時に dynamic workflow の完了済みサブエージェントが再起動する問題を修正。事前に確認し、再起動数を表示 |
| Fix | エージェント起動中の停止 | `claude agents` で起動中のセッションを開くと "was stopped while the respawn was in flight" で停止する問題を修正（Windows で頻発） |
| Fix | 重複セッションリスト | `claude agents` でバックグラウンド化された名前付きセッションが二重に表示される問題を修正。再バックグラウンド化時は番号付き（例: `my-session (2)`） |
| Fix | git worktree 削除 | バックグラウンドセッションの保持期限スイープが `.claude/worktrees/` 下の手動作成 worktree を削除する問題を修正 |
| Fix | Auto mode ツール拒否 | 非常に大きなセッションで auto mode tool call が "temporarily unavailable" として拒否される問題を修正。safety-check deadline をプロンプトサイズに応じてスケール |
| Fix | プラグインキャッシュ重複 | プラグインキャッシュが同一プラグインに対し重複した SHA 名ディレクトリを作成する問題を修正 |
| Fix | プラグインスキル名の重複 | frontmatter `name` に `<plugin>:` プレフィックスが既に含まれるプラグインスキルで、スラッシュメニュー表示が重複（例: `/plugin:plugin:skill`）する問題を修正 |
| Fix | プラグイン更新の失敗 | `claude plugin update` でインストール済みプラグインの bare name 指定が失敗する問題を修正（完全修飾名のみ動作していた） |
| Fix | BOM 付き plugin.json | `plugin.json` が UTF-8 BOM 付きで保存されている場合にプラグインインストールが失敗する問題を修正 |
| Fix | プラグインスキル 0 件報告 | `skills/*/SKILL.md` でスキルを定義するプラグインで `/reload-plugins` が 0 件と報告する問題を修正 |
| Fix | フックエラーメッセージ | フックエラーメッセージで `${CLAUDE_PLUGIN_ROOT}` がリテラル表示される問題を修正。解決済みパスを表示 |
| Fix | `/rename` の border 色 | `/rename` でテーマのプロンプト border 色（カスタムテーマの `promptBorder` を含む）がデフォルトの cyan に置き換わる問題を修正 |
| Fix | カスタムテーマ diff 色 | カスタムテーマの diff 色（`diffAdded`/`diffRemoved` と dimmed 変種）が diff および `/theme` プレビューで無視される問題を修正 |
| Fix | 不明なキーバインド | `keybindings.json` で不明なアクション名のバインドがキーを無効化する問題を修正。スキップしてデフォルトバインドを維持し、`--debug` で警告 |
| Fix | `/stats` 日付ずれ | `/stats` の activity heatmap で各日のアクティビティが 1 セルずれる（日曜が月曜下に表示）問題を修正（UTC 以東のタイムゾーン） |
| Fix | `/fork` の空会話 | 既にフォークまたはバックグラウンド化されたセッションから `/fork` すると、新セッションが空の会話で開始される問題を修正 |
| Fix | `/--` で始まるプロンプト | `/--` で始まるプロンプト（例: Lean doc コメント）が不明なスラッシュコマンドとして拒否される問題を修正 |
| Fix | `@` ファイルピッカー | 入力テキストが実在パスと一致しなくなった後も `@` ファイルピッカーが開いたままになる問題を修正 |
| Fix | ステータスラインのリセット | エージェントビュー移動後にステータスラインのコストと duration がゼロにリセットされる問題を修正 |
| Fix | フルスクリーンフォーカス | フルスクリーンモードでターミナルウィンドウをクリックしてフォーカス復帰させただけで、ポインタ下のコントロールにキーボードフォーカスが移動する問題を修正 |
| Fix | パス補完の失敗 | 補完トークンまたは作業ディレクトリに null バイトが含まれる場合のパス補完失敗を修正 |
| Fix | stale セッションエントリ | Windows/macOS で headless セッションが異常終了時に `~/.claude/sessions` に残す stale エントリをクリーンアップしない問題を修正 |
| Fix | サードパーティ API の `tool_use` | サードパーティの Anthropic 互換エンドポイント（`ANTHROPIC_BASE_URL`）が `id` なしで `tool_use` をストリームした際のレンダリングエラーを修正 |
| Fix | Write ツール OOM | 非常に大きな既存ファイルを上書きした後に Write ツールが "Out of memory" を報告またはフリーズする問題を修正（ファイルは書き込み済み） |
| Fix | プラグインインストール失敗 | `claude plugin install <name>` で `~/.claude/plugins/known_marketplaces.json` が空または破損している場合に無言終了またはハングする問題を修正 |
| Fix | 再開セッションの 400 エラー | 保存履歴に Anthropic API が受け入れない tool block（通常はサードパーティ API プロキシが書き込み）が含まれる場合に再開セッションが毎ターン 400 で失敗する問題を修正 |
| Fix | インストールスクリプト Raw mode | `curl -fsSL https://claude.ai/install.sh | bash` がサーバー管理設定を持つ一部 Team/Enterprise ユーザーで "Raw mode is not supported" で失敗する問題を修正 |
| Fix | プランモード再開 | プランモードで終了したセッションが VS Code 拡張で、または `claude -p --continue`/`--resume` + 権限プロンプトツールで、プランモード外で再開される問題を修正 |
| Fix | `Notification` フック | サンドボックス "Network request outside of sandbox" 権限プロンプト待機中に `Notification` フックが発火しない問題を修正 |
| Fix | Bash 権限チェック | `&&` または `||` 演算子が末尾に残る不正なコマンドを常に承認要求するように修正 |
| Fix | `--strict-mcp-config` プロンプト | `--strict-mcp-config` セッションが読み込まないはずの `.mcp.json` サーバーの承認をプロンプトし、バックグラウンドセッションが起動時に待機する問題を修正 |
| Fix | テレメトリの API キー送信 | テレメトリとメトリクスリクエストがサードパーティゲートウェイ（`ANTHROPIC_BASE_URL`）用の API キーを Anthropic に送信する問題を修正。資格情報は自身のホストにのみ送信 |
| Fix | `apiKeyHelper` JWT リフレッシュ | `apiKeyHelper` が短命 JWT を返す場合、アイドル後の最初のプロンプトで表示される API エラーを修正。有効期限切れトークンは送信前にリフレッシュし、401/403 エラーは静かに再試行 |
| Fix | メモリ増加 | フルスクリーンと Ctrl+O transcript ビューのメモリ増加を修正。各メッセージ行が transcript 全体の tool lookup のフルコピーを保持しなくなった |
| Fix | `/ultrareview` 起動時の変更 | 同一リポジトリから同時起動された `/ultrareview` とクラウドセッション（例: 複数 worktree）が別の起動のコミットされていない変更で開始される問題を修正 |
| Fix | タスク進捗カウント | バックグラウンドクラウドセッション（例: `/autofix-pr`）のタスク進捗カウント（例: `3/5`）が時折タスクを欠く問題を修正 |
| Fix | Remote Control 名前 | Remote Control セッションが claude.ai と Claude アプリで 2 回目のプロンプトまでプレースホルダー名を保持する問題を修正。自動生成タイトルが最初のプロンプト後に表示 |
| Fix | `requiresUserInteraction` ツール | `requiresUserInteraction` マークの MCP ツールが権限プロンプトで "Yes, and don't ask again" を提供する問題を修正。オプションは allow ルールを書き込んでいたがツールは無視していた |
| Fix | セルフホストランナーの終了 | work-poll レスポンスが不正な形式（例: プロキシの HTML ページ）の際にセルフホストランナーがライブセッションを終了または exit する問題を修正。ポーリングを再試行 |
| Improvement | `/cd` の設定反映 | `/cd` で新ディレクトリのプロジェクト設定、フック、`.mcp.json` サーバー（通常の承認プロンプト経由）、スキル、エージェントが `--resume` ではなく移動直後に反映されるように改善 |
| Improvement | Bash ツールのレイテンシ | bash シェルでスナップショット関数を base64 サブシェルなしでリプレイすることで Bash ツールのレイテンシを改善 |
| Improvement | サブエージェント結果 | `maxTurns` 制限で停止したサブエージェントが完了として表示される代わりに、`SendMessage` による継続ヒント付きで部分結果としてマークされるように改善 |
| Improvement | 非対話セッションの継続 | 非対話セッション（`-p`、SDK、クラウドセッション）でサーバーエラー、接続切断、ストールによりレスポンスが中断された際、エラー終了ではなく自動継続するように改善 |
| Improvement | 使用量テレメトリの組織帰属 | workload identity federation セッション、起動時 `apiKeyHelper` 実行中のイベント送信、アイドル中のログイントークン有効期限切れ後の使用量テレメトリを組織に正しく帰属させるよう改善 |
| Change | `/code-review` の利用範囲拡大 | Claude が Bedrock、Vertex AI、Foundry、Claude アプリゲートウェイ経由、テレメトリまたは非必須トラフィック無効時でも `/code-review` を自ら開始できるように変更 |
| Change | `/goal` チェックイン制限 | アイドルセッションで長時間実行バックグラウンド作業に対し、ゴールあたり最大 3 回のチェックインを開始。次のメッセージで追加 3 回許可 |
| Change | マネージド設定同意の延期 | `claude install` と `claude update` で保留中のマネージド設定同意プロンプトを次の対話セッションまで延期するように変更 |
| Change | OpenTelemetry plugin イベント | claude.ai から同期されたプラグインの OpenTelemetry plugin イベントで、`plugin_id_hash` が実際のマーケットプレースを反映し、admin インストールプラグインの `enabled_via` が `admin-install` になるよう変更 |
| Fix | コマンドサンドボックス設定 | コマンドサンドボックスのファイルシステム設定が `--setting-sources` を尊重しない問題を修正 |

### v2.1.245

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Fix | glibc 2.44 起動クラッシュ | glibc 2.44 を搭載する Linux ディストリビューション（Arch Linux、CachyOS、Fedora Rawhide など）での起動時クラッシュを修正 |

### v2.1.243

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Loops 統計表示 | `/usage` に Loops の詳細統計（ループごとの実行回数、総トークン、1実行あたりトークン、最終実行時刻）を追加。暴走タスクの検出が容易に |
| Feature | `modelPicker` 設定 | `/model` ピッカーをカスタマイズする設定を追加。順序付き・ラベル付きモデルリスト（Vertex/Bedrock ID を含む任意の ID 形式）をビルトイン lineup に追加または置換可能 |
| Feature | `promptCacheTtl` 設定 | `promptCacheTtl` と `subagentPromptCacheTtl` 設定を追加。メイン会話を 1 時間、サブエージェントを 5 分に設定するなど、プロンプトキャッシュ TTL の細かな制御が可能 |
| Feature | `modelPricing` 設定 | 組織の契約レートと割引率を `/cost`、ステータスライン、テレメトリのコスト数値に反映する `modelPricing` マネージド設定を追加 |
| Feature | コンソールサインイン | `/login` → Anthropic Console に "Sign in with your Console account" を追加。API キー作成を許可しない組織でもサインイン可能 |
| Feature | `Skipped sources` 表示 | `/status` に `Skipped sources` 行を追加。より高優先度のマネージド設定が有効なため適用されなかったマネージド設定ソース（例: `managed-settings.json`）を一覧表示 |
| Feature | `managed` マーカー | claude.ai コネクタで組織が認証を管理しているものに `managed` マーカーを `/mcp` と `/plugins` に追加 |
| Feature | GitHub 接続ヒント | GitHub を Claude Code on the web に接続していない claude.ai ユーザー向けに `/web-setup` へのヒントを追加 |
| Feature | GitHub 接続ステータス | `/status` に Claude Code on the web（Pro/Max）の GitHub 接続状態を表示する行を追加。未接続時は `/web-setup` へ誘導 |
| Feature | サブエージェントモデル表示 | `/tasks` とエージェント詳細ダイアログに各サブエージェントが実行したモデル（と effort level）を表示 |
| Fix | リモート MCP 再接続 | 非対話（`-p`）および SDK セッションでリモート MCP サーバーが接続切断後に復旧しない問題を修正。自動再接続または失敗報告を行う |
| Fix | MCP サーバーサインイン | デスクトップアプリからの MCP サーバーサインインが client ID metadata document 対応サーバー（例: Linear）で "Invalid redirect URI" で失敗する問題を修正 |
| Fix | Auto mode 無効キャッシュ | 起動時に一時的なサーバー側 auto mode 無効がキャッシュされ、後続のフラグ取得が失敗した場合に auto mode が利用不可のままになる問題を修正 |
| Fix | Auto mode 過負荷拒否 | API が一時的に過負荷状態でクライアントに再試行を要求した後、約 1 分の待機後に auto mode tool call が "temporarily unavailable" として拒否される問題を修正 |
| Fix | `/model` Ultracode 無視 | `/model` ピッカーで Ultracode 選択が無視される問題を修正。Ultracode 選択が現在のセッションに適用される |
| Fix | `/resume` 50 件制限 | `/resume` が最新 50 セッションのみをリストする問題を修正。スクロールでさらに読み込み |
| Fix | クラウドセッション再開 | クラウドセッションがターン途中の再起動後に再開される際、保留中のフックまたはバックグラウンドタスク通知が通常の継続メッセージではなくプロンプトとして再送信される問題を修正 |
| Fix | クロスセッションメッセージング | ユーザーネームスペースと rootless コンテナ内でクロスセッションメッセージングが 2.1.232 のソケットディレクトリ強化後に無効になる問題を修正 |
| Fix | はみ出しテキスト | コンテナ外にはみ出すテキスト（例: `/login` のサインイン URL）が画面の別部分再描画時に先頭列を失う問題を修正 |
| Fix | スペルチェック絵文字 | 絵文字直後に入力したスペルミスの単語に `spellcheck` が下線を引かない問題を修正 |
| Fix | バックグラウンドサブエージェント | 最後のバックグラウンド Bash タスク完了時にバックグラウンドサブエージェントが起動しない問題を修正 |
| Fix | API レスポンスタイムアウト | Anthropic API がレスポンスを開始しない場合にセッションが 10 分以上無応答になる問題を修正。約 3 分後にタイムアウト、1 回再試行、`API Error: No response from API` を表示 |
| Fix | エラーメッセージのレンダリング | 認証、モデル可用性、その他クライアント生成エラーメッセージがモデル出力のようにレンダリングされる問題を修正。エラー行として表示 |
| Fix | Workload identity federation | CI 環境の workload identity federation で、1 ジョブ内のプロセスが交換トークンを共有せず、単一利用トークンを再交換していた問題を修正。拒否された交換はサーバーメッセージで即座に失敗 |
| Fix | サーバー管理 `companyAnnouncements` | サインインで始まるセッション（例: `/logout` 後の最初の起動）でサーバー管理 `companyAnnouncements` が起動時に表示されない問題を修正 |
| Fix | フック `if` 条件 | `Bash(cat *)` のようなフック `if` 条件が、`$()` またはバッククォートコマンド置換とその後の引数を含む無関係な Bash コマンドで発火する問題を修正 |
| Fix | プラグイン依存解決 | `marketplace` フィールドで宣言されたプラグイン依存が、両方のプラグインが `--plugin-dir` 経由で一緒にロードされた場合に解決されない問題を修正 |
| Fix | `/reload-plugins` LSP ツール | 最後の LSP プラグインが無効化された後も `/reload-plugins` が LSP ツールを保持する問題を修正。会話再読み込みを伴う LSP プラグイン変更前に警告を表示 |
| Fix | `--agents` JSON エラー | `--agents` が無効な JSON または無効なエージェント定義を無視する問題を修正。`--mcp-config` 同様、明確なエラーで exit |
| Fix | `/status` MCP エラー | `~/.claude.json` に無効な MCP サーバーエントリがある場合に `/status` が "Found invalid entries in: ." とファイル名なしで表示する問題を修正 |
| Fix | `/clear` セッション名 | 新セッションでも名前は保持されているのに、`/clear` が `/rename` で付けたセッション名をプロンプトバーから消す問題を修正 |
| Fix | 履歴の破損エントリ | `~/.claude/history.jsonl` に不正なエントリが含まれる場合に Ctrl+R 履歴検索と上矢印履歴が壊れる問題を修正 |
| Fix | Ctrl+[ と vim モード | 修飾キーをエンコードするターミナル（modifyOtherKeys / kitty protocol）で Ctrl+[ が vim の INSERT モードを抜けない問題を修正 |
| Fix | `NO_PROXY` の大文字小文字 | `localhost` が `NO_PROXY` に記載され小文字の `no_proxy` に無い場合、ローカル IDE 接続が `HTTPS_PROXY` 経由にルーティングされる（時に失敗する）問題を修正。両方の表記を尊重 |
| Fix | サンドボックス違反の詳細欠落 | ブロックされたコマンドが exit 0 で終了した場合（例: `curl` がプロキシの 403 ページを出力）に、サンドボックスのネットワーク違反詳細が Bash ツール結果から欠落する問題を修正 |
| Fix | レート制限のリセット後表示 | セッションがアイドル中にレート制限ウィンドウがリセットされた後も、ステータスラインの `rate_limits` フィールドと `/usage` がリセット前の使用率を表示する問題を修正 |
| Fix | `--teleport` の未コミット変更 | `claude --teleport <session>` が未コミット変更で終了する問題を修正。セッションピッカーと同様に stash して続行するか尋ねる |
| Fix | `/web-setup` の再ログイン要求 | `gh auth token` を持たない古い GitHub CLI が既に認証済みの場合に `/web-setup` が繰り返しログインを求める問題を修正 |
| Fix | Claude in Chrome の接続断 | 自動更新がセットアップ時のバージョンを削除した後に Claude in Chrome が Claude Code への接続を失う問題を修正。ネイティブホストは安定版の `claude` ランチャー経由で起動 |
| Fix | [VSCode] 権限モード | フィーチャーフラグ取得前に開始したセッション（例: インストール直後）が auto mode や設定済みのデフォルトモードではなくデフォルト権限モードで開く問題を修正 |
| Fix | [VSCode] Focus ビュー | 展開した Focus ビューのセクションが、サブエージェントのツール実行中に自動で折りたたまれる問題を修正 |
| Improvement | 起動時間 | サンドボックスと MCP の起動が最初のフレームをブロックしなくなり、素の起動はサブコマンド登録をスキップ。ワークフロー探索・設定・トラストストア処理も軽量化 |
| Improvement | ダウンロードサイズ | ネイティブインストールと自動更新のバイナリを zstd 圧縮に変更（Linux x64 で約 340 MB → 約 75 MB） |
| Improvement | テレメトリの組織帰属 | `ANTHROPIC_AUTH_TOKEN` で Anthropic API に直接認証するセッションの使用量テレメトリを組織に正しく帰属させ、その組織のデータ取り扱い設定が適用されるよう改善 |
| Improvement | バイナリサイズ | 同梱スキルとプロンプトテキストをよりコンパクトに格納し、ネイティブバイナリを約 2 MB 削減 |
| Improvement | ネイティブビルドのメモリ | バンドル全体を常駐させず必要に応じてコードを読み込むよう変更（セッションあたり約 40〜70 MB のメモリ削減） |
| Improvement | 長時間セッションのピークメモリ | ヒープ増加に応じてランタイムがより早くガベージコレクトするよう改善 |
| Improvement | SSH 経由の `/login` | サインイン URL が即座に表示され、`c` 押下時は常に成功と主張する代わりにコピー方法を報告。フルスクリーンでのテキスト選択方法のヒントも表示 |
| Improvement | effort のエラーメッセージ | thinking 無効時に effort `xhigh`/`max` を使った際のエラーを改善。該当レベル名、thinking を無効化している設定、対処法としての `/effort high` を明示 |
| Improvement | `/loop` の出力 | Claude に処理すべきことがない連続した wake-up を、1件ずつ出力せずターミナル上の1行にまとめるよう改善 |
| Change | サンドボックス Bash のプロンプト | サンドボックス化された Bash ツールのプロンプトが許可済みネットワークホストを列挙しないよう変更。列挙外のホストをブロック済みと決めつけず、Claude がリクエストを試行し新しいホストを承認できる |
| Change | Sonnet 5 の価格表示 | `/model` ピッカーと同梱の `claude-api` スキルで、Sonnet 5 の $2/$10 per Mtok を期間限定プロモではなく標準リスト価格として表示するよう更新 |
| Change | macOS の computer use | macOS の computer use で、デスクトップ・Dock・Finder ウィンドウのクリックに、他アプリと同様アクセスダイアログでの Finder 許可を必要とするよう変更 |
| Change | `/model`・`/fast`・`/effort` の即時実行 | Bedrock・Vertex・Foundry 上およびテレメトリ無効時にも、ターン終了までキューイングせず即座に実行するよう変更 |
| Fix | `claude remote-control` の終了 | サーバーがセッション途中で環境を落とした際に `claude remote-control` が終了し、接続中の Remote Control セッションが取り残される問題を修正。復帰するように変更 |
| Fix | Remote Control の停止・再起動 | admin/owner ロールを持たない Team・Enterprise メンバーで、`claude remote-control` が提供する Remote Control セッションが停止・再起動後に固まることがある問題を修正 |
| Change | クロスセッション受信ソケット | クロスセッションメッセージングの受信ソケットが、30 秒以内に完全な1行を送らない接続を閉じるよう変更。投稿するスクリプトはデータが揃ってから接続すること |
| Improvement | Remote Control の通知文 | Remote Control が別ターミナルに保持されている会話を再開した際の通知を改善。他マシン上のセッションはこちらから見えず、到達もできない旨を明示 |
| Improvement | [VSCode] 履歴の切り詰め | 長時間セッションで古いツール実行行から先に削除し、ユーザーのメッセージと Claude の返信が残るよう改善 |
| Improvement | [VSCode] 拡張のテレメトリ帰属 | Claude アカウントでサインインしている場合に、拡張自身の使用量テレメトリを組織に正しく帰属させ、そのデータ取り扱い設定が適用されるよう改善 |

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)