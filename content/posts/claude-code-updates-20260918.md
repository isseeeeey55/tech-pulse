---
title: "【Claude Code】v2.1.274 リリースノートまとめ"
date: 2026-09-18T08:03:25+09:00
draft: false
tags: ["claude-code"]
categories: ["Claude Code Updates"]
summary: "v2.1.274 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260918/header.png)

# Claude Code v2.1.274 リリースノートまとめ

## はじめに

2026年9月17日、Claude Code v2.1.274 がリリースされました。本バージョンでは、メモリ不足時の可視化警告、MCP サーバー接続タイムアウトの制御機能、OpenTelemetry トレース情報の拡張、Postgres 接続設定の改善など、運用安定性とデバッグ性を高める多数の修正・改善が含まれています。加えて、セッション内のエラー自動修復機能、HTTP+SSE MCP サーバー接続の修正、VS Code 拡張と Claude Tag（Slack）における UI/UX 改善、Code Review の出力品質向上など、幅広い領域にわたる修正が行われています。

## 注目アップデート深掘り

### メモリ不足警告の可視化とセッションエラーの自動修復

本リリースでは、メモリ使用量がクリティカルな状態に達した際に明確な警告が表示され、メモリ解放または安全な再起動の手順が提示されるようになりました。これにより、ユーザーはセッションがクラッシュする前に適切な対応を取ることができます。

また、セッションが "unexpected tool_use_id" エラーで無限リトライに陥る問題が修正されました。破損したトランスクリプトは可能な範囲で自己修復され、修復できない場合は `/rewind` を提示する明確なエラーメッセージでループを終了します。これにより、セッションが回復不能な状態に陥ることなく、ユーザーは適切な次のステップを把握できるようになりました。

### MCP サーバー接続の柔軟な制御

新たに `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` 環境変数が追加され、最初の非インタラクティブターンが MCP サーバーの接続を待つ時間を制御できるようになりました。`0` を設定すると待機をスキップでき、MCP サーバーの接続遅延がセッション開始をブロックしない運用が可能になります。

さらに、HTTP+SSE で動作する MCP サーバーが 422 や他の 4xx エラーを返した際に接続が失敗する問題が修正され、Streamable HTTP MCP のツール呼び出しが約5分でタイムアウトする制限が、サーバーごとの `timeout` 設定を尊重するよう修正されました。これにより、長時間実行されるツール呼び出しや外部 API 統合が安定して動作します。

## 実用的な活用ポイント

本リリースの改善により、以下のような実用的なメリットが得られます。

- **セッションの安定性向上**: エラー自動修復機能とメモリ警告により、長時間のセッションや複雑なタスクでも中断のリスクが減少します。
- **MCP サーバー統合の信頼性向上**: 接続タイムアウト制御と HTTP+SSE 対応の修正により、外部ツールやデータソースとの統合がより堅牢になります。
- **デバッグ効率の改善**: OpenTelemetry に `effort` 属性や `claude_code.managed_settings_resolved` イベントが追加され、トレース情報が充実しました。Postgres 接続エラー時のメッセージも改善され、トラブルシューティングが容易になります。
- **VS Code / Claude Tag / Code Review の UX 改善**: VS Code でのメモリ・インストラクション管理の追加、Claude Tag での Slack 検索修正やゲスト設定の柔軟化、Code Review の出力品質向上により、日常的な操作がよりスムーズになります。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | メモリ不足警告の可視化 | クリティカルなメモリ使用量に達した際に警告とメモリ解放・再起動手順を表示 |
| Feature | `CLAUDE_CODE_MCP_STARTUP_WAIT_MS` 追加 | 最初の非インタラクティブターンでの MCP サーバー接続待機時間を制御（`0` で待機スキップ） |
| Feature | OpenTelemetry `effort` 属性追加 | `claude_code.llm_request` トレーススパンに `api_request` イベントに一致する `effort` 属性を追加 |
| Feature | `claude_code.managed_settings_resolved` OTel イベント追加 | マネージド設定のソースとポリシーヘルパー状態を記録、`OTEL_LOG_MANAGED_SETTINGS=1` で設定内容とダイジェストを出力 |
| Feature | `store.connect_timeout_seconds` 追加 | Claude apps gateway 設定に Postgres 接続タイムアウト設定を追加（デフォルト5秒）、データベース到達不能時のエラーメッセージ改善 |
| Feature | テレメトリに `enduser.sub` 追加 | Claude Desktop と Cowork が Claude apps gateway 経由で送信するテレメトリに IdP subject を追加 |
| Feature | Claude apps gateway リクエスト数警告 | レプリカが上流に送信可能な 256 件を超えるリクエストを保持している場合に警告、起動時にその制限をログ出力 |
| Feature | フルスクリーンモードでのメッセージ展開 | チームメイトやエージェントの折りたたまれたメッセージをクリックで展開可能に |
| Feature | [VSCode] リロード後の継続機能 | ウィンドウリロードで中断したステップの継続機能を追加、設定で無効化可能 |
| Feature | [VSCode] メモリとインストラクションのメニュー追加 | Customize メニューに Memory（自動メモリトグル、保存済みメモリ、フォルダ表示）と Instructions（CLAUDE.md 編集）を追加 |
| Feature | [VSCode] `claudeCode.lockEditorGroups` 設定追加 | Claude がエディタグループをロックしないようにする設定を追加 |
| Feature | [Claude Code on the web] ブランチ比較ピッカー追加 | クラウドセッションの diff ビューで比較対象ブランチを選択可能に（ベースブランチ以外とも比較可能） |
| Feature | [Claude Tag] Add channel/workspace フォームにゲスト設定追加 | 管理設定でチャンネル・ワークスペース追加時にゲスト設定（Inherit / Allow / Channel only / Restrict）を事前選択可能に |
| Fix | セッションエラーの自動修復 | "unexpected tool_use_id" 400 エラーで無限リトライする問題を修正、破損トランスクリプトを自己修復または明確なエラーで終了 |
| Fix | HTTP+SSE MCP サーバー接続修正 | `http` 設定の MCP サーバーが 422 や他の 4xx エラーを返した際の接続失敗を修正 |
| Fix | Streamable HTTP MCP タイムアウト修正 | ツール呼び出しが約5分でタイムアウトする問題を修正、サーバーごとの `timeout` 設定を尊重 |
| Fix | MCP prompts/resources の更新通知修正 | サーバーが `listChanged` を宣言せずに list-changed 通知を送った場合の更新失敗を修正 |
| Fix | MCP ツール 403 エラーの報告修正 | 403 insufficient_scope エラーが期限切れサインインとして報告される問題を修正、不足権限を明示し `/mcp` 再認証を案内 |
| Fix | フック駆動セッションのコンパクション修正 | アクティブな `/goal` などのセッションでコンテキストオーバーフロー後に "Prompt is too long" で終了する問題を修正 |
| Fix | `/goal` レジューム時の消失修正 | コンパクション後にセッションをレジュームした際にアクティブな `/goal` が失われる問題を修正 |
| Fix | `claude agents` フラグ消失修正 | 自動更新の再起動後に `--model`, `--effort`, `--permission-mode`, `--allow-dangerously-skip-permissions`, `--agent` が失われる問題を修正 |
| Fix | 言語サーバーの診断処理改善 | 数千ファイルのプロジェクト全体診断公開時のターンごとの遅延を修正 |
| Fix | サブエージェントモデル選択修正 | Bedrock / Vertex / Foundry で `model: "opus"` のサブエージェントがセッションモデルを維持しない問題を修正（`ANTHROPIC_DEFAULT_OPUS_MODEL` 未設定時） |
| Fix | セルフホストランナーのトークンリフレッシュ修正 | 数回のトークンリフレッシュ失敗後に 401 で全ターンが失敗する問題を修正、401 後も新トークン取得を継続 |
| Fix | ローカルファイルパスのリンク修正 | VS Code などの `file://` URI を要求するターミナルでローカルファイルパスのリンクが機能しない問題を修正 |
| Fix | トランスクリプトの順序付きリスト番号修正 | 自分のメッセージ内で "3. 2. 1." が "3. 4. 5." と表示される問題を修正、入力通りに表示 |
| Fix | AskUserQuestion プレビューノート位置修正 | プレビューノートが選択中のオプションではなく以前のオプションに付与される問題を修正 |
| Fix | AskUserQuestion プレビューモード送信修正 | Enter でノート送信時にハイライトオプションがドロップされる問題を修正 |
| Fix | バックグラウンドエージェントのツールバッチ修正 | レジューム時に中断されたツールバッチの半分が保持される問題を修正 |
| Fix | ローカルセッションのバックグラウンドタスク報告修正 | `CLAUDE_CODE_RESUME_INTERRUPTED_TURN` 付きでレジュームした際に前プロセスの未完了タスクが報告されない問題を修正 |
| Fix | クラウドセッション初回ターンのツール不足修正 | SDK ホスト MCP サーバーがまだ接続中の場合に初回ターンでツールが不足する問題を修正 |
| Fix | バックグラウンドエージェント通知修正 | 自身のバックグラウンドタスク待機中に「ライブ作業なし」と通知される問題を修正 |
| Fix | Claude Desktop エラーヒント修正 | CLI フラグではなく `/usage-credits` などのスラッシュコマンドを提案するよう修正 |
| Fix | `/schedule` ルーチン保存修正 | Claude が返すルーチン形式でメッセージロールなしで保存される問題を修正 |
| Fix | `/status` の `apiKeyHelper` 失敗表示修正 | エラーバナーが確認を指示した `apiKeyHelper` 失敗が表示されない問題を修正 |
| Fix | `/fast on` 非インタラクティブセッション修正 | 組織のマネージドポリシー下で `/fast on` が報告後に無効化される問題を修正、無効化されている旨を通知 |
| Fix | Artifact ツールの承認後拒否修正 | 最新バージョンを読んでいない状態でアーティファクト更新を承認後に拒否される問題を修正 |
| Fix | Cowork / claude.ai クラウドセッションのアーティファクト読み取り修正 | ネットワークアクセス有効時にチームメイトのアーティファクト読み取りをネットワークアクセス無効として扱う問題を修正 |
| Fix | プラグイン・マーケットプレイスディレクトリのバージョン修正 | 自身の git リポジトリを持たない場合に親の git リポジトリからバージョンを取得する問題を修正 |
| Fix | `--strict-mcp-config` と空の `--mcp-config` 修正 | 偶発的な MCP サーバー待機で最大 `MCP_TIMEOUT` まで初回ターンが保留される問題を修正 |
| Fix | Stop プロンプトフックの再送信修正 | 会話の各ブロックで全プロンプトを再送信する問題を修正、リピートブロックは500文字のラベルで条件を識別 |
| Fix | Wayland での空エディタウィンドウ修正 | Cursor / VS Code ターミナル内で起動時に余分な空エディタウィンドウが開く問題を修正 |
| Fix | Claude apps gateway のプロミス拒否修正 | Postgres が支出チェック中に接続をドロップした際の未処理プロミス拒否を修正 |
| Fix | Claude apps gateway SIGTERM 時のストリーム切断修正 | SIGTERM 時に全ストリームを即座に切断する問題を修正、最大25秒間進行中リクエストを完了（`CLAUDE_GATEWAY_DRAIN_TIMEOUT_MS`） |
| Fix | `installed_plugins.json` 頻繁書き換え修正 | リモートマネージド設定からプラグインポリシーが来る場合に起動ごとに書き換えられる問題を修正、Claude Desktop セッションの不要なリロードを削減 |
| Fix | ヘッドレス/SDK セッションのバックグラウンドタスク修正 | 完了した各バックグラウンドタスクごとに別々のモデル呼び出しを行う問題を修正、キュー済みの完了を1回の呼び出しで処理 |
| Fix | Bash ツールのプロファイル再読み込み修正 | プラグインリロードごとにシェルプロファイルを再読み込みする問題を修正、プラグインの `bin/` ディレクトリ変更時のみ再読み込み |
| Fix | `hooks/hooks.json` の `$schema` 通知修正 | トップレベルの `$schema` が "unknown key" と通知される問題を修正 |
| Fix | MCP 接続エラーでのシークレット露出修正 | MCP 設定の `${VAR}` プレースホルダーから解決されたシークレットが接続エラーやログインツール説明に表示される問題を修正 |
| Fix | Bash 権限チェックのシェル変数ループ修正 | 特定の特殊シェル変数のループや代入を含むコマンドの権限チェックを修正、権限を求めるように変更 |
| Fix | ワークツリー分離セッションのシェル展開修正 | 特定のネストされたシェル展開を含む Bash コマンドを受け入れる問題を修正、拒否するように変更 |
| Fix | Edit 権限プロンプトプレビュー修正 | マルチバイト文字を含むファイルでプレビュー位置と承認後の編集位置が異なる問題を修正 |
| Fix | バックグラウンドコマンドの早期停止修正 | 軽度のメモリ圧力下で30分のアイドル後に停止される問題を修正、クリティカル低メモリ時のみ停止し理由をデバッグログに記録 |
| Fix | サブエージェントメッセージの再起動後消失修正 | サブエージェントがメインセッションに送信したメッセージが Claude Desktop 再起動後にトランスクリプトから消える問題を修正 |
| Fix | `.zip` プラグインのリロード修正 | 複数回のリロード後に古い展開から提供される問題を修正 |
| Fix | サブエージェントの進捗サマリー置換修正 | 複数段落の冗長な返信に置き換えられる問題を修正 |
| Fix | [VSCode] `/btw` 履歴混同修正 | 新しい会話の開始直後に別セッションのサイドクエスチョン履歴が表示される問題を修正 |
| Fix | [VSCode] グローバル gitignore 参照時のフリーズ修正 | 拡張機能が初めてグローバル gitignore ファイルを参照する際の短時間フリーズを修正 |
| Fix | [VSCode] リロード後のメッセージ消失修正 | Claude がツール実行中に送信されたメッセージがリロード後に会話から消える問題を修正 |
| Fix | [VSCode] プラグイン管理・MCP サーバー UI のキーボード操作修正 | Manage Plugins の有効化トグルと MCP サーバーダイアログ行がキーボードから到達不能だった問題を修正 |
| Fix | [VSCode] `CLAUDE_CONFIG_DIR` 変更のサインイン反映修正 | Environment Variables 設定で `CLAUDE_CONFIG_DIR` 変更後、ターミナルでのサインイン/アウトがリロードまで反映されない問題を修正 |
| Fix | [VSCode] チャット内 Edit diff の切れ修正 | 特定のパネル幅や長い折り返し行で diff ボックスが下部で切れる問題を修正、表示行数に合わせてフィット |
| Fix | [VSCode] 設定書き込みの衝突修正 | 拡張機能からの重複設定書き込みが `~/.claude/settings.json` をパース不能にしたり設定をドロップする問題を修正 |
| Fix | [VSCode] Open in New Tab のフォーカス修正 | Ctrl/Cmd+Shift+Esc でメッセージボックスがフォーカスされず、クリックまで入力できない問題を修正 |
| Fix | [VSCode] Claude タブのエディタレイアウト分割修正 | ロックされたグループに別の Claude タブとファイルがある状態で閉じた Claude タブを再度開くとレイアウトが分割される問題を修正 |
| Fix | [VSCode] New session のエディタグループ追加修正 | Claude タブとファイルタブが同じグループにある場合に New session が別のロックされたエディタグループを開く問題を修正 |
| Fix | [VSCode] セッションピッカーでの名前移動修正 | 検索クエリ入力中にセッション名が横にシフトする問題を修正 |
| Fix | [VSCode] プランレビューカードの切れ修正 | 複数のコメントがある計画で Send feedback ボタンと理由フィールドが切れる問題を修正、コメントリストがスクロール可能に |
| Fix | [VSCode] High Contrast テーマでのコード可読性修正 | High Contrast テーマ下でチャット返信のインラインコードとコードブロックが読めない問題を修正 |
| Fix | [Claude Code on the web] GitHub トークン更新エラーハンドリング修正 | GitHub のトークン更新が一時的にエラーした際に git 操作が "service unavailable" で失敗する問題を修正 |
| Fix | [Claude Code on the web] ルーチン編集の二重起動修正 | ルーチン編集が二重起動したり一時停止したルーチンが再有効化される問題を修正 |
| Fix | [Claude Code on the web] クラウドセッションコミットの署名エラー修正 | セッションの認証情報更新後数分間コミットが署名エラーで失敗する問題を修正 |
| Fix | [Claude Code on the web] ルーチン保存後のトースト修正 | GitHub トリガーがリンクできなかった際に理由（リポジトリごとのトリガー上限など）を表示、"edit to retry" のみでなく詳細を提示 |
| Fix | [Claude Code on the web] セッションの未読復帰修正 | 既読マーク直後にセッションが未読に戻る問題を修正 |
| Fix | [Claude Tag] 他アプリからの @mention 応答修正 | 別の Slack アプリ/ボットが @mention した際に Claude が応答しない問題を修正、タグが返信を受け取り、数日の非アクティブ後のチャンネルでも起動 |
| Fix | [Claude Tag] 新チャンネルでの @Claude タグ配信修正 | 新しい Slack チャンネル作成直後に別アプリが @Claude をタグ付けしたメッセージが届かない問題を修正、Claude 参加後に配信 |
| Fix | [Claude Tag] フォローアップメッセージの通知修正 | Claude の最終メッセージから数分後のフォローアップがサイレント編集として統合される問題を修正、ブロッカーなどの遅延更新は新しい返信として投稿し通知 |
| Fix | [Claude Tag] Slack 検索のチャンネル内検索エラー修正 | 単一チャンネル内検索でエラーが発生する問題を修正、マッチしたメッセージを返すように修正 |
| Fix | [Claude Tag] セーフティフィルター停止時のコンテキストリセット修正 | 誰も待機していない状態でのセーフティフィルター停止が Slack スレッドのコンテキストをサイレントリセットする問題を修正、常に通知しバックグラウンド作業もキャンセルしないように変更 |
| Fix | [Claude Tag] Slack 返信のメールアドレス表示修正 | メールアドレスに `mailto:` プレフィックスが表示される問題を修正、クリック可能なアドレスのみを表示 |
| Fix | [Claude Tag] Enterprise Grid の組織全体チャンネル監視修正 | グリッドの別ワークスペースから組織全体共有チャンネルの監視を拒否する問題を修正 |
| Fix | [Claude Tag] 管理設定の Environment ピッカー表示修正 | アーカイブ済みまたはアプリ作成の環境が環境名ではなく生の ID で表示される問題を修正 |
| Fix | [Code Review] 修正済み指摘スレッドのクローズ修正 | 再レビューで修正済み指摘のスレッドが、新レビューで低重要度のノートが同じスレッド下に提出された際に開いたままになる問題を修正 |
| Fix | [Code Review] レビュー起動時の一時的エラー修正 | GitHub や内部サービスが起動時に一時的に失敗した際にレビューが "Code review encountered an error" で終了する問題を修正、待機とリトライを実行 |
| Improvement | `--input-format stream-json` 起動改善 | 初回ターンがツール検索を延期する MCP サーバー接続を最大2秒待機しなくなり、後のターンで到着 |
| Improvement | Monitor ツール通知改善 | スクリプトの最終出力と終了を1通知で送信、モデルターンを節約 |
| Improvement | Artifact ツールエラー改善 | claude.ai にサインインしていない場合は初回試行時にターミナルで通知、拒否された呼び出しのリトライを早期停止 |
| Improvement | アーティファクト公開改善 | 古いバージョンに基づく公開を送信前に停止、マージすべき新しいページを提示 |
| Improvement | エージェントワークツリー削除の安全性チェック改善 | サブモジュールチェックアウトを含むワークツリー削除前の安全性チェックを改善 |
| Improvement | `OTEL_LOG_RAW_API_BODIES=file:<dir>` 出力改善 | 新しい `index.jsonl` と `request_body_id` / `message.id` イベント属性により各応答をリクエストファイルとトランスクリプトメッセージにリンク |
| Improvement | Claude apps gateway 起動改善 | 初回 Postgres 接続を最大3回まで試行、数秒遅れて到達可能なデータベースでも起動失敗しないように改善 |
| Improvement | Claude apps gateway 支出制限チェック改善 | 負荷時の支出制限チェックをデータベース往復1回に削減（以前は4回）、タイムアウトの減少 |
| Improvement | Claude apps gateway サインインレート制限エラー改善 | `/login` が拒否理由を説明し、ゲートウェイログが制限項目と変更すべき設定を記録 |
| Improvement | [VSCode] スクリーンリーダーの会話ナビゲーション改善 | 各メッセージを "You" または "Claude" として通知、ツールステップにはツール名を含む |
| Improvement | [Claude Tag] Slack 進捗チェックリスト改善 | 2,000文字にキャップ、ビジースレッドで最大15分ごとに再投稿、古い "Latest task list" リンクを更新 |
| Improvement | [Code Review] 指摘文言の改善 | 各指摘を短く明確な文章で記載、影響を受ける対象・コードの問題点・修正方法を冒頭で提示 |
| Improvement | [Code Review] 組織制限によるレビュースキップ時のメッセージ改善 | チェックランカードと PR コメントに各原因の修正につながる管理ページへのリンクを追加 |
| Change | v2 MCP クライアントのデフォルト化 | Bedrock / Vertex / Foundry / テレメトリ無効インストールでも v2 MCP クライアントと MCP 2026-07-28 ネゴシエーションをデフォルト使用（オプトアウト: `MCP_SDK_GENERATION=v1` / `MCP_PROTOCOL_NEGOTIATION=legacy`） |
| Change | `/code-review` のインラインレビュープロンプト使用 | チューニング済み設定を持たないモデルでは多数のレビューサブエージェント生成ではなく軽量なインラインレビュープロンプトを使用 |
| Change | `"type": "sdk"` MCP エントリのスキップ | `.mcp.json` / 設定 / プラグイン / エージェントファイルの `"type": "sdk"` エントリを警告付きでスキップ、SDK ホストアプリケーションのみが登録可能 |
| Change | ローカルセッションでのアーティファクト監視変更 | 他の場所で公開された新バージョンがターンを開始しなくなり、Claude は後の Artifact ツール結果で新バージョンを認識 |
| Change | プラグイン・マーケットプレイスクローンの Git LFS 変更 | Git LFS ファイルをポインターのままにし、チェックアウトで `git lfs pull` を実行して取得 |
| Change | セルフホストランナーの読み取り専用リポジトリ変更 | git ホストがアクセスチェックで拒否する読み取り専用リポジトリを、セッション開始を失敗させるのではなくスキップするよう変更 |
| Change | `/status` と関連メッセージの表記変更 | `/status` の GitHub 行を "Cloud sessions" に変更、`/web-setup`・`/ultrareview`・teleport のメッセージを "Claude Code on the web" ではなく "cloud session" と表記 |
| Change | [VSCode] グローバル gitignore の既定パス変更 | `XDG_CONFIG_HOME` が絶対パスの場合、既定のグローバル gitignore ファイルを `$XDG_CONFIG_HOME/git/ignore` に変更 |
| Change | [Claude Code on the web] GitHub 接続欠落時のルーチン挙動変更 | オーナーの GitHub 接続が無い場合、最初のチェック失敗でルーチンを無効化せず、実行をスキップして最大72時間リトライするよう変更 |
| Change | [Claude Code on the web] 保留中ルーチンの通知変更 | サブスクリプション一時停止時の保留通知が、自動再開を約束せず、ユーザー自身でルーチンを再度オンにするよう案内 |
| Removed | [Claude Tag] Slack canvas のゲスト帰属注記を削除 | "Channel only" のゲスト設定を使うチャンネルで、canvas を編集するたびに追記していた帰属注記を削除 |

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)