---
title: "【Claude Code】v2.1.283 リリースノートまとめ"
date: 2026-09-26T08:02:34+09:00
draft: true
tags: ["claude-code", "MCP", "OpenTelemetry", "availableModelsMatch", "deniedModels", "CLAUDE_CODE_GATEWAY_HINT_HEADERS", "OTEL_LOG_TOOL_CONTENT", "DISABLE_TELEMETRY", "DO_NOT_TRACK", "ANTHROPIC_DEFAULT_HAIKU_MODEL", "DISABLE_PROMPT_CACHING_HAIKU", "VSCode", "Claude Tag", "Code Review"]
categories: ["Claude Code Updates"]
summary: "v2.1.283 のClaude Codeリリースノートまとめ"
---

## Claude Code v2.1.283 リリースノート

## はじめに

Claude Code v2.1.283 がリリースされました。本バージョンは非常に広範囲にわたるアップデートで、新機能の追加から多数のバグ修正まで含まれています。主な変更点として、LLM ゲートウェイ向けのリクエスト追跡機能、モデル管理設定の強化、`/doctor prompt-audit` コマンドの追加、MCP 関連の複数の安定性改善、プラグイン管理のバグ修正多数、UI・操作性の改善、VSCode / クラウドセッション / Claude Tag / Code Review 向けの個別修正などが挙げられます。

---

## 注目アップデート深掘り

### 1. LLM ゲートウェイ向けリクエストグルーピング機能

`x-claude-code-prompt-id` をゲートウェイヒントヘッダーに追加する機能が実装されました。`CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` を設定することでオプトインでき、1 つのユーザープロンプトが発生させる複数の LLM リクエストをゲートウェイ側でまとめて把握できるようになります。

また、同時に `load_test_mode` ブロックが Claude apps ゲートウェイ設定にオプトインで追加されました。このモードではリクエストが構築・署名されるものの上流には送信されず、クライアントは固定の応答を受け取ります。これによりデプロイ環境のロードテストが実施可能になります。

さらに Amazon Bedrock の Mantle エンドポイント向けの `mantle` アップストリームプロバイダーが Claude apps ゲートウェイに追加されました。

### 2. モデル管理設定の強化（`availableModelsMatch` / `deniedModels`）

マネージド設定に 2 つの新しい項目が追加されました。

- `availableModelsMatch`: `"exact"` を指定すると、`availableModels` に列挙されたモデルのバージョンのみを厳密に許可します。新しいモデルリリースが自動的に有効にならず、明示的にリストへ追加するまでブロックされます。
- `deniedModels`: `availableModels` で許可されているモデルであっても、特定モデルをブロックできます。

この 2 つの設定により、組織のモデル利用ポリシーをより細かく管理できるようになります。

---

## 実用的な活用ポイント

- **`/doctor prompt-audit`（`/checkup prompt-audit`）**: CLAUDE.md ファイル、スキル、エージェント、コマンドを対象に、古いモデル向けに書かれたプロンプトパターンを監査します。レポートでは古いパス・コマンド・矛盾する指示ファイルが先頭に表示されます。
- **OpenTelemetry 拡張**: `OTEL_LOG_TOOL_CONTENT=1` 設定時、MCP ツール・WebFetch・WebSearch の出力が `tool.output` OpenTelemetry スパンイベントに追加されるようになりました。
- **起動速度の改善**: `claude -p` および Claude Code Remote はインタラクティブ UI を読み込まなくなりました。また、自動モード分類器のルールと Artifact ツールは起動時ではなく初回使用時に読み込まれます。さらにパターンコンパイルステップがレスポンスのストリーミング中に実行されるようになり、初回返答のレイテンシが改善されています。

---

## 全変更点一覧

| カテゴリ | 内容 |
|---|---|
| Feature | `x-claude-code-prompt-id` をゲートウェイヒントヘッダーに追加（`CLAUDE_CODE_GATEWAY_HINT_HEADERS=1` でオプトイン） |
| Feature | `availableModelsMatch` マネージド設定を追加（`"exact"` でモデルバージョンを厳密に制限） |
| Feature | `deniedModels` マネージド設定を追加（`availableModels` で許可済みのモデルもブロック可能） |
| Feature | MCP ツール・WebFetch・WebSearch の出力を `tool.output` OTel スパンイベントに追加（`OTEL_LOG_TOOL_CONTENT=1` 時） |
| Feature | `/doctor prompt-audit`（`/checkup prompt-audit`）コマンドを追加 |
| Feature | フルスクリーンモードで他セッションの切り詰められたメッセージをクリックで展開できるように |
| Feature | `--plugin-dir` の読み込み失敗エントリに `path` を追加 |
| Feature | Claude apps ゲートウェイ設定にオプトインの `load_test_mode` ブロックを追加 |
| Feature | Claude apps ゲートウェイに Amazon Bedrock の Mantle エンドポイント向け `mantle` アップストリームプロバイダーを追加 |
| Fix | SDK セッションでターンが早期終了した際に遅延ツールコールや完了済みツール結果が失われる問題を修正 |
| Fix | 長時間実行のツールコールがバックグラウンドに移行後に MCP 進捗通知が破棄される問題を修正 |
| Fix | セッション終了時に起動中の stdio MCP サーバーが残り続ける問題を修正 |
| Fix | ステートレスリモート MCP サーバーからの一時的な HTTP 404 でそのサーバーがセッション中使用不能になる問題を修正 |
| Fix | 有効な URL を持たない MCP サーバーへのサインインが不明瞭な SDK エラーで失敗する問題を修正（`/mcp` でそのようなサーバーに Authenticate を表示しないように変更） |
| Fix | テレメトリ無効時に週次 Fable 上限が `/usage` および VS Code 使用量メーターに表示されない問題を修正 |
| Fix | `/model` が ID に日付や `-v1:0` サフィックスを持つ Sonnet 4.6 または Sonnet 5 を `[1m]` 付きで受け付けない問題を修正 |
| Fix | `ANTHROPIC_DEFAULT_HAIKU_MODEL` で別モデルを指定している場合に `/model` ピッカーがハードコードされた Haiku バージョンと価格を表示する問題を修正 |
| Fix | モデルフォールバック中に開始された動的ワークフローがすべてのエージェントをフォールバックモデルで実行する問題を修正 |
| Fix | Haiku がメインモデルの場合に `DISABLE_PROMPT_CACHING_HAIKU` が効果を持たない問題を修正 |
| Fix | `claude plugin validate` がインストールできないプラグイン名やマーケットプレイス名を受け入れると誤って表示する問題を修正 |
| Fix | `claude plugin validate` で `outputStyles`・`themes`・`monitors`・`lspServers` のパスが存在しないまたはプラグインディレクトリ外を指す場合でも通過する問題を修正 |
| Fix | `claude plugin details` がプラグインの MCP サーバー数を 0 と表示する問題を修正 |
| Fix | `claude plugin marketplace remove` がアンインストールしたプラグインを表示しない問題を修正 |
| Fix | `claude plugin uninstall` が ID の大文字小文字のみ異なる 2 つのプラグインのうち指定していない方を削除する問題を修正 |
| Fix | バージョン未宣言のプラグインがキャッシュ不在時にインストール済みのコミットではなく最新コミットから復元される問題を修正 |
| Fix | ホームまたは設定ディレクトリの移動後（bind-mount devcontainer など）にユーザーインストール済みプラグインとマーケットプレイスが "cache-miss" で読み込めない問題を修正 |
| Fix | `installed_plugins.json` が無効なプラグイン ID のレコードを持つ場合にプラグインが表示されない問題を修正 |
| Fix | `installed_plugins.json` が現バージョンで読めないレコードを持つ場合に書き換えられレコードが失われる問題を修正 |
| Fix | スクリーンリーダーモードでパーミッションダイアログの引用コマンド・パスがダイアログ自体のテキストとして読まれる問題を修正 |
| Fix | `/context` が MCP サーバーの指示をカウントしない問題を修正 |
| Fix | Warp ターミナルで Markdown リンクがクリッカブルなハイパーリンクではなくプレーンテキストとして表示される問題を修正 |
| Fix | `claude mcp add`・`add-json`・`remove` がコンフィグファイルへの書き込み失敗時でも成功と報告する問題を修正 |
| Fix | クラウドセッションで返答の最初の単語がストリーミングされず遅れて表示される問題を修正 |
| Fix | Claude の組み込みキーバインドガイドでコードのタイムアウトを 1 秒と記載していた問題を修正（正しくは 3 秒）、および `cmd` を `meta` のエイリアスと表記していた問題を修正 |
| Fix | `keybindings.json` でタイプミスのある修飾キー（例: `ctl+k`）が警告なく受け入れられる問題を修正 |
| Fix | `footer:openSelected` をリバインドまたはアンバインドした後もフッターヒントが "Enter to view" と表示され続ける問題を修正 |
| Fix | 素早く連続入力したキー（タイプアヘッド・キーリピート・SSH/tmux 経由のバースト）が古いステートに対して処理される問題を修正 |
| Fix | `GIT_CONFIG_COUNT` 環境変数で CA 証明書を渡している場合にワークツリーチェックアウトが証明書検証に失敗する問題を修正 |
| Fix | サンドボックス化された `git` がサンドボックスプロキシのログインを認証情報ヘルパーに保存しようとして "failed to store" が表示される問題を修正 |
| Fix | マネージド `sandbox` 設定でネストされた値が 1 つでも無効な場合にブロック全体が無視される問題を修正 |
| Fix | git リポジトリのサブディレクトリで起動した場合に Claude の自動メモ編集がセンシティブファイル書き込みとしてブロックされる問題を修正 |
| Fix | `DISABLE_TELEMETRY` または `DO_NOT_TRACK` でテレメトリを無効にした有料プランで Remote Control が使用できない問題を修正 |
| Fix | 狭いターミナルで `/remote-control` メニューの QR コードヒントが途中で切れる問題を修正 |
| Fix | vim モードで `.` が Shift+Enter の改行を落とす・カーソルがアクセント文字内に残る・`3J` や Visual モード `J` の後に古い変更が繰り返される問題を修正 |
| Fix | vim モードで 10,000 文字超のプロンプトを normal モードでリコールした際にカーソルが末尾を超える問題、および `V` + `p` 後のカーソル位置の問題を修正 |
| Fix | vim モードで `J` の行結合スペース処理が Vim と異なる問題、`3J` や Visual モード `J` での最終行カーソル移動が Vim と異なる問題を修正 |
| Fix | Windows: PowerShell ツールで `cmd /c rd`・`rmdir`・`del`・`erase` がドライブルートやホームフォルダを削除できる問題を修正 |
| Improvement | `/mcp` ツールリストの表示改善（より多くのツールを一覧表示、ページキー・マウスでスクロール、組織がブロックしたツールに警告アイコン表示） |
| Improvement | MCP ツールの結果改善：MCP ツールが返す画像をファイルにも保存し、Bash・Read などのツールから参照できるように |
| Improvement | `/tasks` の表示改善（ステータスアイコン・名前・詳細の表示、多数タスク時のタイトル固定表示、ページキー・マウスホイール・クリック対応） |
| Improvement | `/help`・`/hooks`・`/copy`・`/chrome`・`/memory`・`/ide`・`/release-notes`・`/rewind`・`/diff`・`/remote-env`・`/plugin` 等のリストにページキー・マウスホイール・クリックを追加 |
| Improvement | 検索ボックス付きリスト（`/skills`・`/artifacts` 等）で検索ボックスにフォーカス中はリストのポインターを薄く表示 |
| Improvement | コンパクションスピナーの改善：タイマーをコンパクション開始時点から計測し、サマリーのトークン数をストリーミングしながらカウント表示（パーセントバーを置き換え） |
| Improvement | MCP サーバーサインイン後のブラウザページを改善（中央揃えレイアウト、ダークモード、新しいアートワーク） |
| Improvement | ロードに失敗したプラグインに属するスキルの Skill ツール応答を改善（スキル未インストールではなくプラグインのロード失敗を通知） |
| Improvement | `prompt-audit` の Claude Code 設定向け改善（古いパス・コマンド・矛盾指示ファイルを先頭に表示、Claude Code ドキュメント記載の thinking キーワードを保持） |
| Improvement | 読み込めない `installed_plugins.json` からの回復改善（内容を別ファイルに保存してから再構築、`claude plugin list` でファイル名を表示） |
| Improvement | アーティファクト DB 読み取りの改善（フルページを返す順序付きクエリが 1 ページ分であることと残りの読み方を通知） |
| Improvement | 初回返答レイテンシの改善（セッション最初の返答末尾に実行されていたパターンコンパイルをストリーミング中に並行実行） |
| Improvement | 初回リクエストレイテンシの改善（事前接続済み API コネクションを再利用） |
| Improvement | 起動速度の改善（`claude -p` と Claude Code Remote がインタラクティブ UI を読み込まないように、自動モード分類器と Artifact ツールを起動時ではなく初回使用時に読み込み） |
| Improvement | claude.ai アカウントで Artifact ツール機能が未判明の場合の起動改善（初回プロンプトが最大 1.5 秒待機しないように） |
| Change | テレメトリ無効またはサードパーティプロバイダー使用のインタラクティブセッションで、`permissions.defaultMode` 未設定時に自動モードで起動するよう変更 |
| Change | `/ultrareview` 起動ダイアログにローカルブランチのレビューで未コミット変更がアップロードされる可能性の注意書きを追加 |
| Change | Opus が既に 1M コンテキストウィンドウを持つ場合、`/model` ピッカーの Opus 行とデフォルトモデル名から "(1M context)" を削除 |
| Change | ターミナルのプロンプト候補が 20 回連続で未使用の場合に表示頻度を下げるように変更（使用すると頻度が戻る） |
| Change | `--system-prompt` と `--append-system-prompt` でテキスト形式と `-file` 形式を同時に受け付けるよう変更（ファイルの内容が先頭に来る） |
| Change | `Skill(anthropic-skills:<name>)` の拒否ルールが Claude Desktop からプラグインとして届く場合も対象に、`Skill(skill:<name>)` の拒否ルールがスキルのエイリアスと表示名にも一致するよう変更 |
| Change | `/rewind` と `/diff` リストのキーバインドを他のリストと統一（`select:*` アクション）、`messageSelector:*`/`diff:*` のリバインドは引き続き機能 |
| Change | `/workflows` 実行リストのサイジングを他のリストに合わせて変更 |
| Change | `claude plugin eval` で git がインストールされている場合に git 2.31 以降を要求するよう変更 |
| Change | アーティファクト監視の変更：自動でアームされたウォッチはアクティビティなし 3.5 時間後に終了 |
| Change | セルフホストランナー: ライフサイクルフックの git が Git LFS `pre-push` フックをスキップ、書き込み可能なシステム `core.hooksPath` を無視、`--configure-git` なしではコミット署名を行わないよう変更 |
| Change | セルフホストランナー: Anthropic 管理 git 配下での `GIT_SSL_CAINFO` と `GIT_SSL_NO_VERIFY` の適用範囲を整理、ランナー自身の git は Anthropic の git ルートを常に検証 |
| Change | 2.1.282 での `claude-ai` 名前の予約をリバート：当該名のスキル・コマンド・ワークフロー・MCP サーバーが再び読み込まれ、`Skill(claude-ai:*)` ルールが通常のプレフィックスルールとして機能 |
| Fix | [VSCode] パーミッションモード自動切り替えが失敗した後もセッションが auto または bypass モードで動作し続けてインジケーターが Default を表示する問題を修正 |
| Fix | [VSCode] Web からテレポートされたセッションで Claude 作業中に送信したメッセージが失われる問題を修正 |
| Fix | [VSCode] Web セッションがセッションリストから非表示になり空のチャットが代わりに開く問題を修正 |
| Fix | [VSCode] 再オープンしたセッションでターン途中に受信したメッセージ（自動継続など）でターンが分割される問題を修正 |
| Fix | [VSCode] リロードしたセッションで rewind 済みのターンや compaction 前の行のみが表示される問題を修正 |
| Fix | [VSCode] 狭いパネルでフッターのエージェントピルのアイコンがオフセンター・ステータスドットが端に寄る問題を修正 |
| Fix | [VSCode] 長いプロンプトに改行で終わる行をペーストした後、チャット入力のテキストがカーソル・選択範囲よりわずかに下に表示される問題を修正 |
| Improvement | [Cloud sessions] 実行中のクラウドセッションへのリポジトリ追加改善：GitHub アカウントが読み取り可能だが push できないプライベートリポジトリも読み取り専用でアタッチ可能に |
| Fix | [Cloud sessions] サーバーサイド再起動からの回復後に完了済みのステップ（コメント投稿やプッシュの重複など）が再実行される問題を修正 |
| Change | [Cloud sessions] 新規ルーティンスケジュールのデフォルトを毎時数分後に変更（正時設定のルーティンは数分遅延する可能性の注記あり） |
| Feature | [Claude Tag] Claude が検索できる Slack チャンネルを組織・ワークスペース・チャンネル単位で制限する "Channels Claude can search" 管理設定を追加 |
| Feature | [Claude Tag] Claude アカウント接続後のページに "Back to Slack" ボタンを追加 |
| Fix | [Claude Tag] アタッチルール経由でアクセスバンドルを受け取るチャンネルの設定ページにコネクターやプラグインが表示されない問題を修正 |
| Fix | [Claude Tag] GitHub App のリポジトリ選択が大量のリポジトリに限定されている場合にリポジトリ検索が一部欠ける問題を修正 |
| Fix | [Claude Tag] 新メッセージが返答中に割り込んだ際に同じ返答が 2 回投稿される問題を修正 |
| Fix | [Claude Tag] Slack Connect 共有などで Slack チャンネル ID が変更された古いプライベートチャンネルでチャンネルルーティンが停止する問題を修正 |
| Fix | [Claude Tag] "Channel only" に設定されたチャンネルで非ゲストメンバー参加時に Slack のメンバーシップ確認が遅れた場合に全会話が終了する問題を修正 |
| Fix | [Code Review] GitHub がプルリクエストを返さなかった場合に "@claude review" リクエストが無音で失敗する問題を修正（1 回リトライ、失敗時はコメントで通知） |
| Fix | [Code Review] 時間制限で未検証のまま停止したレビューへの課金問題を修正（incomplete 表示、課金なし、1 回リトライ） |

---

## まとめ

v2.1.283 は機能追加・バグ修正・改善が広範囲にわたる大型リリースです。LLM ゲートウェイ連携の強化（リクエスト追跡・ロードテストモード）、組織のモデル利用ポリシー管理の細粒度化（`availableModelsMatch`・`deniedModels`）、`/doctor prompt-audit` によるプロンプト監査機能の追加が新機能として加わりました。一方で、プラグイン管理・MCP・vim モード・VSCode 統合・クラウドセッション・Claude Tag・Code Review にわたる多数のバグが修正されており、安定性向上への注力も見られます。起動レイテンシや初回返答レイテンシの改善も複数含まれており、全体的に品質改善とオペレーション機能の拡充を中心としたリリースと言えます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)