---
title: "【Claude Code】v2.1.273・v2.1.272・v2.1.271 リリースノートまとめ"
date: 2026-09-16T08:03:35+09:00
draft: true
tags: ["claude-code"]
categories: ["Claude Code Updates"]
summary: "v2.1.273・v2.1.272・v2.1.271 のClaude Codeリリースノートまとめ"
---

## はじめに

2026年9月16日、Claude Code の v2.1.273、v2.1.272、v2.1.271 が連続してリリースされました。v2.1.273 は LLM ゲートウェイ向けリクエストヘッダーの追加、MCP サーバー切断時の自動再接続通知、Remote Control セッションのフォーク機能など多岐にわたる機能追加と、権限チェック・エラーハンドリング・キャッシュ管理に関する多数の不具合修正を含みます。v2.1.272 はバグ修正と信頼性向上に焦点を当てたメンテナンスリリースです。v2.1.271 では Claude Code Remote セッションのファストモード対応、`/config` パネルへのマウス操作サポート、セルフホステッドランナーのドレインマーカーファイル機能、auto モードにおけるコマンド単位のドメイン許可制御など、セッション管理と自動化機能が大幅に強化されました。

## 注目アップデート深掘り

### LLM ゲートウェイ向けリクエストヘッダーの追加（v2.1.273）

v2.1.273 では、LLM ゲートウェイ向けに `x-claude-code-request-class`、`x-claude-code-agent-type`、`x-claude-code-prev-tool-durations`、`x-claude-code-compaction`、`x-claude-code-context-compacted` の各リクエストヘッダーが追加されました。これらのヘッダーは環境変数 `CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` を設定することでオプトインできます。

ゲートウェイ側でこれらのヘッダーを活用することで、リクエストの種類やエージェントタイプ、過去のツール実行時間、コンテキストのコンパクション状態などの情報を取得できるようになります。これにより、ゲートウェイでのルーティング最適化やロギング、課金計算などの高度な制御が可能になります。

### Claude Code Remote セッションのファストモード対応（v2.1.271）

v2.1.271 では、Claude Code Remote セッション（クラウドおよびセルフホステッドランナー）でファストモードが利用可能になりました。ホスト側のファストモード設定、またはセッション内で入力した `/fast` コマンドが、組織のポリシーで許可されている場合に適用されます。

これにより、リモートセッションでもローカルセッションと同等の応答速度改善が期待できます。特にクラウド環境やセルフホステッドランナーを利用する組織では、セッションの体感速度向上と生産性向上につながります。

### auto モードにおけるコマンド単位のドメイン許可制御（v2.1.271）

v2.1.271 では、auto モードかつサンドボックス有効時に、Bash、PowerShell、Monitor の各コマンドに対してコマンド単位で `allowed_domains` を設定できるようになりました。コマンドが必要とするホストはコマンドと一緒にレビューされ、そのコマンドに対してのみ許可されます。それ以外のホストへのアクセスは拒否されます。

この機能により、ネットワークアクセスの最小権限原則をコマンドレベルで実現でき、セキュリティリスクを大幅に低減できます。特定のコマンドが特定のドメインにのみアクセスする必要がある場合、他の潜在的に危険なホストへの意図しないアクセスを防止できます。

## 実用的な活用ポイント

v2.1.273 では、MCP サーバーが切断され自動再接続が諦めた場合に通知が表示され、`/mcp` コマンドへ誘導されるようになりました。これにより、接続障害の早期発見と対処が容易になります。また、Bedrock、Vertex、Foundry のエラーメッセージが改善され、再認証が必要な認証情報やゲートウェイ管理者への問い合わせ先が明示されるようになり、トラブルシューティングが効率化されます。

v2.1.271 では、`/config` パネルのフルスクリーンモードでマウス操作がサポートされ、設定値の変更やスクロールがより直感的になりました。また、セルフホステッドランナーに `--drain-marker-file <path>` オプションが追加され、SIGTERM によるドレイン時に指定ファイルが存在する場合、ランナーはホストドレインとして終了を報告します（テレメトリのみ）。

複数のバグ修正により、権限チェックの精度向上（Bash の `fmt`、`column`、ワイルドカード展開、複数 `cd` や `git` チェーンなど）、MCP OAuth の登録処理改善、背景コマンドの重複起動防止、設定ファイル変更の監視改善など、全体的な信頼性と安定性が向上しています。

## 全変更点一覧

### v2.1.273

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | LLM ゲートウェイ向けリクエストヘッダー追加 | `x-claude-code-request-class` など 5 種のヘッダーを追加。`CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` でオプトイン |
| Feature | MCP サーバー切断時の通知 | 自動再接続が諦めた際に通知を表示し `/mcp` へ誘導 |
| Feature | Remote Control セッションのフォーク | Claude アプリから `claude --remote-control` または `/remote-control` で開始したセッションをフォークし、バックグラウンドセッションとして実行可能に |
| Fix | Bash 権限チェッカーの回避 | `permissions.blockReadsOutsideWorkingDirectories` 下で、権限チェッカーが完全に解析できないコマンドがプロンプトをスキップしていた問題、およびサブシェルが bypass モードで危険な `rm` を隠していた問題を修正 |
| Fix | Skills の組織設定同期 | claude.ai から同期した Skills が組織で Skills オフ後も利用可能だった問題を修正。削除され回復可能なゴミ箱へ移動するように |
| Fix | MDM 設定の無視 | `allowManagedMcpServersOnly` などの MDM または `managed-settings.json` の設定が、サーバー管理設定が存在する場合に無視されていた問題を修正 |
| Fix | 認証エラーメッセージの改善 | Bedrock、Vertex、Foundry、Claude アプリゲートウェイの 401/403 エラー時に、更新すべき認証情報名またはゲートウェイ管理者への問い合わせ先を明示 |
| Fix | `/login` 等のプロンプトキャッシュ破棄 | `/login`、`/upgrade`、`/extra-usage` が会話の思考を破棄し、次リクエストで完全なプロンプトキャッシュ再書き込みを強制していた問題を修正 |
| Fix | auto モードでの Artifact ツール承認 | クラウドまたは Remote Control セッションでチャットに添付したファイルを Artifact ツールがアップロードする際に承認のため停止していた問題を修正 |
| Fix | `.git/info/exclude` の再生成 | 長時間実行セッションで `.git` ディレクトリが削除または移動された後にスタブ `.git/info/exclude` を再作成していた問題を修正 |
| Fix | シェルモードでの `!` 入力 | メインプロンプトでシェルモード中に先頭に入力した `!` が削除され、`! grep …` のような否定コマンドが入力できなかった問題を修正 |
| Fix | macOS Read の symlink エラー | macOS の Read が、ドラッグ＆ドロップしたスクリーンショットやシステムが第二パスで報告するファイルを拒否していた問題を修正 |
| Fix | `permissions.blockReadsOutsideWorkingDirectories` のメモリディレクトリ | リポジトリ設定で選択されたメモリディレクトリがプロンプトにロードされ、記憶され、インデックスされ、メモリ抽出で使用されていた問題を修正 |
| Fix | サブエージェントと背景エージェントの失敗報告 | 最終ストリーミング応答がトークン使用量を省略したりモデル ID を含まなかったりした場合に失敗と報告され、結果が配信されなかった問題を修正 |
| Fix | コンテキストメーターとコンパクションの計算 | advisor-tool ターンを実際のサイズの約 2 倍でカウントし、自動コンパクトが実際のウィンドウの約半分で発火していた問題を修正 |
| Fix | `/tui` の再起動拒否 | 既に完了してエージェントパネルに表示されなくなったエージェントチームのチームメイトがいる場合に再起動を拒否していた問題を修正 |
| Fix | スケジュールタスクのセッション混同 | `.claude/scheduled_tasks.json` が別フォルダ（新しい worktree など）にコピーされた際に誤ったセッションで実行されていた問題を修正 |
| Fix | SDK と stream-json のサブエージェント出力 | サブエージェントが実行途中でバックグラウンドに移動した際に、残りのメッセージと最終レポートがドロップされていた問題を修正 |
| Fix | `/install-github-app` のエラーメッセージ | SAML シングルサインオンブロックを「管理者権限が必要」と報告していた問題を修正 |
| Fix | Remote Control クライアントの拒否 | Claude Desktop、VS Code、JetBrains セッションに接続した Remote Control クライアントがコンテキストウィンドウ使用量を要求した際に拒否されていた問題を修正 |
| Fix | スピナーの二重省略記号 | コンパクションステータス行で省略記号が二重表示されていた問題を修正 |
| Fix | frontend-design プラグインの誤表示 | Artifact の読み取りまたは公開後に frontend-design プラグインを提案する誤ったスピナーチップを修正 |
| Fix | Bash deny ルールチェックの revert | 2.1.268 で追加された、権限チェッカーが解析できない Bash 行（`eval`、`env -C`）の Read/Edit deny ルールチェックを元に戻した。`time -p make build` などが拒否されずプロンプトが再度表示されるように |
| Improvement | 長時間セッションの応答性向上 | フック進行状況とサブエージェント活動が会話全体を再処理しないように改善 |
| Improvement | Artifact ツールのエラー改善 | Artifact が提供しないファイルタイプを含む公開時のエラーで、Claude には提供される型と代替手段を、ターミナルには 1 行のプレーンメッセージを表示 |
| Improvement | Artifact ツールのページ読み取り改善 | Artifact サービスが保持するページの機能とデータベースルールを記述するように改善 |
| Improvement | Artifact データベース書き込み改善 | 更新時にドキュメント全体を書き直す代わりに単一フィールドを削除できるように改善 |
| Improvement | Artifact 公開の信頼性向上 | 公開の接続が claude.ai 到達後にドロップした場合、失敗や重複バージョン作成の代わりに安全に再送信されるように改善 |
| Improvement | クラウドセッション GitHub エラー改善 | IP 許可リスト、一時停止されたアプリインストール、SAML シングルサインオンのエラーで、汎用インストールヒントの代わりに原因を表示 |
| Improvement | `/autofix-pr` のエラー改善 | `gh pr view` 失敗時に gh 自身のエラー（サインイン、SAML、レート制限）を表示し、GitHub webhook 配信のセットアップ失敗理由（GitHub アカウント未リンクなど）を明示 |
| Improvement | `/web-setup` エラー改善 | 拒否された GitHub トークンで理由と修正方法をリスト表示し、接続失敗でプロキシまたは TLS 証明書問題を指摘 |
| Improvement | SSL 証明書とプロキシエラー改善 | セッション内の SSL 証明書およびプロキシ接続エラーでエラーコードと修正方法（信頼されていない企業 CA 用の `NODE_EXTRA_CA_CERTS` など）を明示 |
| Improvement | クラウドセッション作成エラー改善 | Claude ログインが期限切れまたは取り消された場合、`/login` の実行を指示 |
| Improvement | MCP サーバーサインイン期限切れエラー改善 | サインインが期限切れの際に再認証方法（`/mcp`）を明示 |
| Breaking | Bedrock、Vertex、Foundry の auto モード分類器 | デフォルトでローカル分類器を使用。`CLAUDE_CODE_AUTO_MODE_SERVER=1` でプラットフォームのサーバー側分類器を使用可能 |
| Improvement | `OTEL_LOG_TOOL_DETAILS=1` の拡張 | コストとトークンメトリクスに実際のエージェント、スキル、プラグイン、MCP サーバー名を含めるように改善 |
| Breaking | Claude アカウントサインインの拡張 | claude.ai プラグインへのアクセスもリクエストするように変更 |
| Breaking | `/bug` と `/feedback` のデータ削減 | 最後の API リクエストからモデル動作パラメータ（モデル、システムプロンプト、ツール）のみを含め、リクエストメタデータと `CLAUDE_CODE_EXTRA_BODY` フィールドを省略 |
| Fix | [VSCode] "Report a problem" の表示制御 | 組織でプロダクトフィードバックが無効の場合に表示されなくなり、`/bug` / `/feedback` もレポートフォームを開かないように修正 |
| Fix | [VSCode] Windows の終了コードバナー | Windows で完了したターン後に赤い「Claude Code process exited with code 4294967295」バナーが表示されていた問題を修正 |
| Improvement | Windows UNC パスの権限チェック | `--add-dir` でマップされたネットワークドライブ追加時の UNC パスのネットワークパス権限チェックを改善 |
| Fix | [Web] ルーチンの組織コネクタアクセス喪失 | 管理者が組織コネクタを削除して再追加した後、ルーチンがアクセスを失い古いコネクタを呼び出し続けていた問題を修正 |
| Fix | [Web] セルフホステッド環境作成エラー | 組織設定からセルフホステッド環境を作成する際にサーバーエラーで失敗し、半分作成された環境が残る問題を修正 |
| Breaking | [Web] "Share cloud sessions" 設定の移動 | 管理者の "Share cloud sessions" 設定を Claude Code ページから Data and privacy に移動し、Data and privacy 管理者も管理可能に |
| Feature | [Web] ルーチンの破棄確認 | New routine ページまたは Edit routine ダイアログで、入力したルーチン名、プロンプト、編集を破棄する前に "Discard unsaved changes?" 確認を追加 |
| Breaking | [Web] デスクトップアプリダウンロード画面の削除 | Mac と Windows で、クラウド環境を持たない新規ユーザー向けのフルページデスクトップアプリダウンロード画面を削除。セットアップに直行するように変更 |
| Improvement | [Web] ルーチン詳細ページの改善 | メニューと名前変更をパンくずに、オン/オフスイッチと Run now をトップに、実行履歴をルーチン設定の横に配置 |
| Fix | [Claude Tag] Enterprise Grid 切断後のサイレント | Enterprise Grid 切断後にワークスペースが接続されたままの場合、アプリ再インストール後数分で Claude が無言になっていた問題を修正 |
| Fix | [Claude Tag] 組織共有プライベートチャネルのスケジュールタスク | 組織共有プライベート Slack チャネルで設定されたスケジュールタスクが無言で投稿されなかった問題を修正。作成されたスレッドで実行を継続するように |
| Fix | [Claude Tag] タスク中の古いスレッド返信 | Claude がタスク中に古い Slack スレッドで返信すると、まだプッシュしていない作業を失い最初から再起動することがあった問題を修正 |
| Fix | [Claude Tag] トークンリフレッシュ後の誤ったメッセージ | アカウントトークンリフレッシュ直後に誤った「環境が見つからない」通知でメッセージをドロップすることがあった問題を修正 |
| Fix | [Claude Tag] AWS リージョンレスエンドポイント拒否 | AWS 接続が Budgets、Savings Plans、WAF Classic、Import/Export などリージョンレスエンドポイントを拒否していた問題を修正。Global Accelerator リクエストが正しく署名されるように |
| Improvement | [Claude Tag] AWS 接続失敗の改善 | リクエストが署名できない場合（リージョンのないホスト名など）に理由と修正方法を Claude に伝達し、ベアエラーの代わりに詳細を提供 |
| Fix | [Claude Tag] OAuth トークンタイプの小文字対応 | 小文字のトークンタイプを返すプロバイダーで OAuth client-credentials および JWT-bearer 接続が失敗していた問題を修正。標準 Bearer スキームを送信するように |
| Fix | [Claude Tag] チャネルマネージャー追加の拒否 | Enterprise Grid 共有チャネル、Claude がまだ使用されていないチャネル、レガシープライベートチャネルでチャネルマネージャー追加が拒否されていた問題を修正 |
| Breaking | [Claude Tag] 関連パブリックチャネルの自動監視 | 会話が依存するインシデントチャネルなど、関連するパブリックチャネルを、依頼されたときではなく自動的に監視を開始するように変更 |
| Fix | [Claude Tag] 管理者メモリページのチャネル表示 | Claude が自動でセットアップしたチャネルが保存されたメモリを持つ場合でも表示されなかった問題を修正。管理者がメモリを開き、編集、削除できるように |
| Fix | [Code Review] Additional findings 後のマージレビュー | "Additional findings" をリストした以前のレビューの後にベースブランチを PR にマージすると完全な再レビューがトリガーされていた問題を修正。軽量なフォローアップレビューになるように |
| Fix | [Code Review] REVIEW.md の無視条件 | @メンション、行をまたぐコードスパン、バッククォートされた HTML タグにより REVIEW.md 全体が無視されていた問題を修正。変更ファイルにリンクする行のみ保留するように |
| Improvement | [Code Review] 修正提案の改善 | 修正時に他のコードが依存する動作が変更される場合、動作を維持すべきことを明記するように改善 |
| Improvement | [Code Review] レビューコメントの第二位置参照改善 | 第二の影響を受ける位置を指すレビューコメントで、その位置の問題を切り詰めスタブではなく完全な文で記述するように改善 |
| Fix | [Code Review] `/ultrareview --post` のコメント重複/欠落 | GitHub エラー後の再試行で findings コメントが投稿されなかったり 2 回投稿されたりしていた問題を修正。コメントにレビューされたコミットを明記するように |
| Fix | [Code Review] 大文字リポジトリ名の再レビュー | 所有者名またはリポジトリ名に大文字を含む GitHub リポジトリで、空または内容が同一のプッシュが再レビューされていた問題を修正。スキップするように |

### v2.1.272

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Fix | バグ修正と信頼性改善 | 詳細は公開されていないが、全般的なバグ修正と信頼性向上が実施された |

### v2.1.271

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Claude Code Remote のファストモード対応 | クラウドおよびセルフホステッドランナーでホスト設定または `/fast` コマンドによるファストモードが利用可能に |
| Feature | `/config` パネルのマウス操作対応 | フルスクリーンモードでマウスホイールによるスクロール、クリックによる値変更、ポインタ下の行のハイライトに対応 |
| Feature | セルフホステッドランナーのドレインマーカーファイル | `--drain-marker-file <path>` で SIGTERM ドレイン時にファイル存在時にホストドレインとして報告（テレメトリのみ） |
| Feature | コマンド単位のドメイン許可制御 | auto モードかつサンドボックス有効時、Bash、PowerShell、Monitor でコマンド単位の `allowed_domains` によるホスト許可制御 |
| Feature | サブエージェントの CLAUDE.md 除外オプション | エージェント frontmatter および `--agents` JSON に `omitClaudeMd` を追加。カスタムおよびプラグインサブエージェントがユーザー、プロジェクト、ローカル CLAUDE.md ファイルなしで実行可能に（管理ポリシーファイルは読み込み） |
| Feature | プラグインインストール時のコマンド承認 | `claude plugin install` および `claude plugin update` に `--accept-command <sha256>` オプションを追加。`-y` の代わりに前回の `--json` 実行で表示されたコマンドを正確に承認可能に |
| Feature | modelPricing の multiplier サポート | `modelPricing` 管理設定および Claude アプリゲートウェイ `pricing` ブロックで 1 以上 10 以下の `multiplier` をサポート。内部チャージバックレート用 |
| Feature | スピナーチップの改善 | Bedrock、Vertex AI、Foundry、LLM ゲートウェイユーザーに Claude デスクトップアプリを案内。claude.ai デスクトップアプリチップは `/desktop` を提案しダウンロードを提供 |
| Fix | 組織ポリシーのキャッシュ再利用 | アカウント、組織、API キー切り替え後にキャッシュされた組織ポリシーが再利用され、認証情報変更後の次回更新まで更新されなかった問題を修正 |
| Fix | 組織ポリシー変更時のツールとコマンドリスト更新 | 起動後の組織ポリシー読み込み完了時またはセッション中の変更時にツールとコマンドリストが更新されなかった問題を修正 |
| Fix | enterprise `managed-mcp.json` の読み取りエラー処理 | 読み取りまたはパース不能な `managed-mcp.json` が無視されていた問題を修正。排他的 MCP 制御を維持し起動時に警告を表示 |
| Fix | サードパーティプロキシでの組織ポリシー取得 | `ANTHROPIC_UNIX_SOCKET` 経由のサードパーティローカルプロキシで組織ポリシーが取得され拒否されていた問題を修正。他のカスタムゲートウェイと同様に扱い、Remote Control 含む |
| Fix | ワーカー再起動後のサブエージェントツール呼び出し拒否 | ワークフローまたはエージェント承認適用後にセッションワーカーが再起動した場合、すべてのサブエージェントツール呼び出しが拒否されていた問題を修正 |
| Fix | `/fast off` のメッセージ | 組織でファストモードが無効の場合、オフにする代わりに "Fast mode unavailable" と応答していた問題を修正 |
| Fix | `CLAUDE_CODE_SKIP_FAST_MODE_ORG_CHECK` でのファストモード再送 | API がファストモードを拒否した後、毎ターンファストリクエストを再送していた問題を修正。拒否が維持され理由が表示されるように |
| Fix | ファストモードの usage-credits limit フォールバック | `CLAUDE_CODE_RETRY_WATCHDOG` 下で usage-credits limit またはオーバーロード時にファストモードがターンを失敗させていた問題を修正。標準速度にフォールバックするように |
| Fix | Bash 権限チェックの認識外オプション | `fmt`、`column` などのコマンドがチェッカーが認識しないオプションの後にファイルを読み取る際に見落としていた問題を修正 |
| Fix | Bash ワイルドカードの権限チェック | コマンドのパターンまたはオプション値にワイルドカードがある場合（例: `grep -v dir/* file`）にワイルドカードが展開されるファイルをスキップしていた問題を修正 |
| Fix | Bash 変数宣言フラグの権限チェック | シェル変数宣言フラグが実行されるコマンドを誤って表示できていた問題を修正 |
| Fix | Bash の複数ディレクトリ変更の権限チェック | 2 つのディレクトリ変更、サブシェル、または `cd`+`git` チェーンを含むコマンドが、bypass および auto モードの `permissions.blockReadsOutsideWorkingDirectories` 下でプロンプトをスキップしていた問題を修正 |
| Fix | `.git/config.lock` の放置 | サンドボックスコマンド起動失敗後、古い `.git/config.lock` が残り、`git checkout -b`、`git push -u`、`git config` がセッション残り時間で失敗していた問題を修正（Linux） |
| Fix | macOS 設定ファイル変更の監視 | システムファイルイベントサービスが飽和した macOS マシンで、セッション外で行われた設定ファイル変更が見

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)