---
title: "【Claude Code】v2.1.280 リリースノートまとめ"
date: 2026-09-23T08:02:46+09:00
draft: true
tags: ["claude-code", "claude-opus-5-5", "MCP", "CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH", "hook_execution_complete", "OpenTelemetry", "claude-agents", "keybindings.json", "UserPromptSubmit", "VSCode", "claude-tag", "ultrareview", "autocompact"]
categories: ["Claude Code Updates"]
summary: "v2.1.280 のClaude Codeリリースノートまとめ"
---

## Claude Code v2.1.280 リリースノート

## はじめに

Claude Code v2.1.280 は、Claude Opus 5.5 の追加とデフォルトモデル変更を筆頭に、UI・操作性・安定性にわたる大規模なアップデートです。バグ修正だけでも 50 件以上に及び、VSCode 拡張・Web・Slack（Claude Tag）・Code Review など各プラットフォーム向けの改善も同時に含まれています。

---

## 注目アップデート深掘り

### Claude Opus 5.5 追加とデフォルトモデル変更

`claude-opus-5-5` が追加され、Opus シリーズの新たなデフォルトモデルとなりました。1M コンテキストに対応し、価格は入力 $4/Mtok・出力 $20/Mtok、キャッシュ読み込みは $0.20/Mtok です。

あわせて、Pro および Team Standard プランにおけるデフォルトモデルが Sonnet から Opus に変更されました（Max・Team Premium・Enterprise はすでに Opus がデフォルトでした）。

また、Opus 4.7・Opus 4.8・Fable 5 については、`/effort` や `-p`・Agent SDK・プロジェクト設定・`--settings` の `effortLevel`・モデル別レベルで保存されていた起動時デフォルト effort の固定が解除されました。さらに、`/effort` 導入以前に保存された effort レベルは、Opus 5.5 のような新モデルには適用されなくなり、各モデルのデフォルト値から始まります。

> **Note:** `effortLevel` は Claude Code の `/effort` コマンドで設定できる、モデルの推論労力を制御するパラメータです。

---

### `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` の追加

セッション内のすべての MCP サーバーに対するツール説明およびサーバー命令の文字数上限（デフォルト 2,048 文字）を変更するための環境変数 `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` が追加されました。

> **Note:** MCP（Model Context Protocol）は、外部ツールやサーバーを Claude Code に接続するためのプロトコルです。

MCP ツールの説明が長い場合にデフォルト上限で切り捨てられていた状況に対して、この環境変数で上限を調整できます。

---

## 実用的な活用ポイント

- **デフォルトモデルの変更に注意**: Pro / Team Standard プランのユーザーはモデルが自動的に Opus に切り替わります。コスト感覚が変わる可能性があるため、現在のプランと利用状況を確認することを推奨します。
- **MCP ツール説明の上限調整**: `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` を設定することで、説明が長い MCP サーバーを使う際の文字数制限を変更できます。
- **キーバインド変更の確認**: ダイアログで `y`/`n` がそれぞれ確認・キャンセルとして機能していた挙動が修正されました。以前の動作に戻す場合は `keybindings.json` に `y`/`n` を `confirm:yes`/`confirm:no` としてバインドする必要があります。
- **`ctrl+l` / `cmd+k` の挙動変更**: 2.1.260 で追加されたフルスクリーンモードでのトランスクリプトクリア機能がリバートされ、画面の再描画に戻りました。

---

## 全変更点一覧

| カテゴリ | 内容 |
|----------|------|
| Feature | Claude Opus 5.5（`claude-opus-5-5`）を追加、Opus デフォルトモデルに。1M context、$4/$20/Mtok、キャッシュ読み込み $0.20/Mtok |
| Feature | フルスクリーンモードの `/skills` リストでマウスホイールスクロール、`/plugin` のスキル状態オプションをクリック可能に |
| Feature | `CLAUDE_CODE_MAX_MCP_DESCRIPTION_LENGTH` 環境変数を追加（MCP ツール説明・サーバー命令の文字数上限を変更可能） |
| Feature | `hook_execution_complete` OpenTelemetry イベントにフック出力サイズとファイル保存された超過出力数を追加 |
| Fix | シンボリックリンク経由の書き込みがツリー内のパス名で判定されていた問題を修正（`acceptEdits`・許可ルール・auto mode が対象外の場所を承認しなくなった） |
| Fix | auto mode がセーフティチェックで拒否されたアクションを無限リトライする問題を修正（1 回拒否後、リトライ不要と通知） |
| Fix | auto mode がセーフティチェックから無回答時に休止なくアクションを拒否し続ける問題を修正（バックオフ後、10 回連続で停止） |
| Fix | モデルが `path`・`file_text`・`file_content`・`description` を送信した際に Write 呼び出しのバリデーションが失敗する問題を修正 |
| Fix | 各種ダイアログで Ctrl+C / Ctrl+D を 2 回押すと Claude Code が終了していた問題を修正（ダイアログを閉じるだけになった） |
| Fix | ウィンドウをフォーカスするクリックがポインタ下のアイテムもトリガーしていた問題を修正 |
| Fix | 誤った `n` がダイアログを閉じ、`y` が確認していた問題を修正（Enter/Esc に変更。旧動作は `keybindings.json` で復元可能） |
| Fix | ダイアログのテキストフィールドで入力した文字がキーバインドに奪われる問題を修正 |
| Fix | Windows 端末で Enter 後にプロンプト行が乱れていた問題を修正（送信前のテキストを正確に表示するよう再描画） |
| Fix | 不可視文字クリーンアップがペルシャ語・アラビア語テキストで使われるゼロ幅非接合子を誤って除去していた問題を修正 |
| Fix | 音声ディクテーションが Ctrl+C で停止しない、Esc でキャンセルできない、Space 長押しがトランスクリプトビューや vim NORMAL モードからディクテーションを開始する問題を修正 |
| Fix | Claude 動作中にホストアプリ（Claude Desktop・VS Code・SDK）からモデル切り替えを行うと次のプロンプトでプロンプトキャッシュミスが発生する問題を修正 |
| Fix | 再開されたフォークサブエージェントがツールリストを再構築してしまいプロンプトキャッシングが壊れる問題を修正 |
| Fix | サブエージェントの手戻りメッセージが verbose モード外で展開すると内部 provenance プリアンブルが表示される問題を修正 |
| Fix | GitHub リポジトリや git URL からプラグインを更新した際に `installed_plugins.json` がインストール時のコミットを保持し続ける問題を修正 |
| Fix | `~/.claude/skills/` のスキルが同フォルダの `manifest.json` にその名前が列挙されていると `.trash/` に移動される問題を修正 |
| Fix | セッションフィードバックサーベイがライト・ANSI テーマでホバーハイライトを表示しない問題を修正 |
| Fix | `/workflows` が唯一の実行を開く前に 1 行リストを一瞬表示する問題を修正 |
| Fix | フルスクリーンモードで隠しオプションがある選択リスト（`/model`・`/permissions` 等）のマウスホイールスクロールが効かない問題を修正 |
| Fix | `/plugin` / `/skills` でオフのスキルがロード失敗プラグインと同じ赤 ✘ を表示していた問題を修正（オフは暗い ◯ に変更） |
| Fix | マルチセレクトのオプション説明がラベルではなくオプション番号の下にインデントされていた問題を修正 |
| Fix | `/plugin`・`/skills`・`/mcp` の検索ボックスがフルスクリーンモードで右ボーダーを失う問題を修正 |
| Fix | `/mcp` のサーバーリストと詳細ビューで警告アイコンが異なる（△ と ⚠）問題を修正（すべて ⚠ に統一） |
| Fix | `/config` 設定リストと `/model`・`/memory`・権限プロンプト等の選択リストで Home・End キーが機能しない問題を修正 |
| Fix | `/skills` メニューで PgUp/PgDn が先頭・末尾を超えてラップしていた問題を修正 |
| Fix | `/config` リストで Tab が選択中の設定値を無音で変更していた問題を修正（何もしないよう変更） |
| Fix | "role 'system' must precede an 'assistant' message" API エラーで毎ターン会話が失敗する問題を修正 |
| Fix | プロキシ・ゲートウェイ経由で advisor タグ非対応の環境において advisor との会話が API Error 400 で毎ターン失敗する問題を修正（タグなしで再試行） |
| Fix | ロードできない MCP ツールについての不正な通知が保存履歴に含まれているとセッションが毎ターン失敗する問題を修正 |
| Fix | 保存トランスクリプトに不正なシステムメッセージやファイルリストなしのメモリ保存通知が含まれるとセッション再開時にクラッシュする問題を修正 |
| Fix | 長時間フルスクリーンセッションが "unrecoverable interface error" で終了する原因のひとつを修正（破損メッセージリストを再構築） |
| Fix | 設定ファイルが読み込み中に名前付きパイプに差し替えられると Claude Code がハングする問題を修正 |
| Fix | `~/.claude.json` に移行済み設定の `null` や `"false"` 等の値が残っていると `/config` がクラッシュし一部設定が誤読される問題を修正 |
| Fix | 未完了のバックグラウンドエージェント・シェル・ワークフローがあるセッションを再開すると入力前にモデルターンが自動開始される問題を修正 |
| Fix | ヘッドレス・SDK セッションでサブエージェントのターン終了時にバックグラウンドサブエージェントへのメッセージがサイレントに失われる問題を修正 |
| Fix | 完了済みサブエージェントのレポートが読み込まれる前に会話がコンパクトされるとレポートが失われる問題を修正 |
| Fix | LSP プラグイン有効時にバックグラウンドサブエージェントが LSP ツールを使用できない問題を修正 |
| Fix | バックグラウンドシェルタスクが grep のマッチなし等の良性の非ゼロ終了を失敗として報告する問題を修正 |
| Fix | バックグラウンドセッション（`claude --bg`）で NUL 文字を含む環境変数があると git・hooks・plugins 等が実行できない問題を修正 |
| Fix | バックグラウンドサブエージェント実行中に Ctrl+C を 3〜4 回押さないと終了できない問題を修正（2 回で終了） |
| Fix | Esc でプロンプトを編集する・巻き戻す・スタートアップフック実行中に Esc を押すなどの操作で IDE 選択が失われる問題を修正 |
| Fix | Ctrl+S でスタッシュした `!` シェルモードプロンプトが復元時に通常プロンプトになる問題、スタッシュ直後に `/` がファイルパスを表示する問題を修正 |
| Fix | temp ディレクトリが満杯・書き込み不可・他ユーザー所有の場合に `claude agents` が空白のまま反応しない問題を修正（エラー表示に変更） |
| Fix | `claude mcp remove` 後に同名で再追加した MCP サーバーが認証必要状態のまま再接続しない問題を修正 |
| Fix | バックグラウンドプラグインマーケットプレイス自動更新が git credential helper を無視し、プライベートリポジトリマーケットプレイスが毎回 re-clone または更新されない問題を修正 |
| Fix | 公式マーケットプレイスのスナップショットファイルがシンボリックリンクまたは大きすぎる場合に `claude plugin update` がプラグインのコミット記録を消去しバージョンが "unknown" になる問題を修正 |
| Fix | 組織ポリシーがロードできない場合（例：Web プロキシ経由）に Artifact ツールがサイレントに消える問題を修正（ブロック原因をメッセージで通知） |
| Fix | アーティファクト再パブリッシュ時に保存済みデータベースアクセスルールやビュアープロファイルスコープがサイレントにリセット・欠落する問題を修正（能力なしで再送された場合は拒否） |
| Fix | `/ultrareview` がクラウドレビューの停止を完了またはリトライ可能エラーとして誤報告し、セッション削除やアカウント変更後にタイムアウトまで待機する問題を修正 |
| Fix | Claude アプリが Remote Control・クラウドセッションで `/compact` / `/clear` 直後にコンテキスト使用量を欠落・古い値で表示する問題を修正 |
| Fix | Claude アプリの Remote Control・クラウドセッション向け diff ビューで未コミット変更と並行してブランチのコミット済みファイルが欠落する問題を修正 |
| Fix | クラウド・セルフホストランナーセッションでアクセストークンのローテーション中に長時間の過負荷を経ると "Authentication failed" で失敗する問題を修正 |
| Fix | Cowork セッションでのメモリ書き込み競合時に 10,800 文字超のメモリファイルの中間部分が欠落する問題を修正 |
| Fix | Self-hosted runner: `--configure-git` でライフサイクルフックのコミット署名が失敗する問題を修正 |
| Fix | Windows: バックグラウンドクリーンアップが `~/.claude/` 配下のディレクトリシンボリックリンクまたはジャンクションを誤って削除する問題を修正 |
| Fix | Self-hosted runner: `--retire-at` リリース直前にターンが終了すると終了シグナルが失われる問題を修正 |
| Improvement | `ctrl+l` / `cmd+k` のフルスクリーンモードでのトランスクリプトクリアを 2.1.260 からリバート（画面再描画に戻す） |
| Improvement | `/permissions`: ルールの表示・追加・削除後にフォーカスがルールリストに戻るよう改善。削除・ディレクトリ削除確認のデフォルトを No に変更 |
| Improvement | `/permissions` タブナビゲーション: ルールリスト内の ←/→ と Tab がタブバーにフォーカスを移さずタブを切り替えるよう改善 |
| Improvement | `/cost` のキャッシュミス原因表示に thinking モードおよび thinking 表示変更を追記 |
| Improvement | Artifact ツール: Claude がアーティファクトリンクを読み込めない場合、継続前にユーザーへ通知するよう改善 |
| Improvement | `/install-github-app`: GitHub CLI チェックとリポジトリ選択ステップに "Esc to cancel" を表示 |
| Improvement | `/artifacts` と `/workflows` リストにスクロールバーを追加 |
| Improvement | ワークフロー進捗ツリー: 実行中のエージェント・フェーズが ⟳ から暗い点（dim dot）で表示されるよう改善 |
| Improvement | `/plugin` の Add Marketplace フォーム（フルスクリーン）のレイアウト改善 |
| Improvement | `/workflows` 詳細ビュー（フルスクリーン）の二重水平ルール削除 |
| Improvement | 言語名のないコードブロックをインラインコードと同様の色付けに変更 |
| Improvement | `/btw` がツール実行中に使用された場合、そのコールを失敗扱いではなく進行中として認識するよう改善 |
| Improvement | `UserPromptSubmit` フックのタイムアウト通知とデバッグログにタイムアウトしたフックコマンド名を表示 |
| Improvement | `@` ファイルサジェスト: ファイル名にクエリを含むファイルをフォルダ名のみでマッチするファイルより上位にランク付け |
| Improvement | アーティファクトページの改善（印刷ボタン非表示、連絡先情報のテキスト表示、フォームコントロール・スクロールバーへのダークモード対応等） |
| Improvement | `/ultrareview` アップロード: `id_rsa copy` や `kubeconfig (1).yaml` などのキーファイルの名前変更コピーもローカルに保持 |
| Improvement | クロスセッションメッセージングの起動警告に `--debug-file` の説明を追加 |
| Improvement | `@` ファイルサジェスト改善（再掲） |
| Feature | Pro / Team Standard プランのデフォルトモデルを Sonnet から Opus に変更 |
| Feature | `/effort` 導入以前に保存された effort レベルを Opus 5.5 等の新モデルに適用しないよう変更 |
| Feature | Opus 4.7・Opus 4.8・Fable 5 の起動時 effort 固定を解除 |
| Improvement | `/autocompact` のフッターヒントに ←/→ キーを明記 |
| Improvement | `/fast` のフッターに Space トグルキーを明記 |
| Feature | Self-hosted runner: ライフサイクルフックの git がランナー共有 git ファイルに列挙されたフックフォルダ・プログラムを無視するよう変更。ローカルパス・`git://` リモートには `GIT_ALLOW_PROTOCOL` が必要 |
| Feature | 予約済みマーケットプレイス名を模倣したプラグインマーケットプレイスの追加拒否・ロード停止 |
| Feature | `PermissionRequest` フック: エージェント型フックが実行されなくなり、コマンド・http フックを指定するエラーを表示 |
| Feature | [VSCode] `/status` コマンドでセッションのバージョン・アカウント・モデル・サーバー詳細を表示する Status ダイアログを追加 |
| Feature | [VSCode] `/sandbox` でサンドボックスモード・フォールバック・除外コマンドを表示する Sandbox ダイアログを追加 |
| Feature | [VSCode] `/chrome` で Chrome 拡張のステータス・インストール・再接続・権限ページ等を表示する Claude in Chrome ダイアログを追加 |
| Feature | [VSCode] `/export` で会話をプレーンテキストとしてコピー・保存する Export conversation 機能を追加 |
| Feature | [VSCode] `/skills` でスキルのソース・トークン推定・オン/オフ状態を Slash commands ダイアログに表示、クリックで状態変更可能 |
| Feature | [VSCode] `/plan` でプランモードへの切り替え・最初の計画プロンプト送信・セッションプランの表示が可能 |
| Improvement | [VSCode] チャットボックスのペーストテキスト処理改善（800 文字または 2 行超のペーストをマーク） |
| Improvement | [VSCode] チャットボックスのプロンプト処理改善（ペーストテキストから不可視 Unicode フォーマット・タグ文字を除去） |
| Improvement | [VSCode] "Open in New Tab" が最後のグループの後ではなく作業中のエディターグループの隣に開くよう変更 |
| Fix | [VSCode] effort チップが実行中のレベルではなく古い保存済み effort レベルを表示する問題を修正 |
| Fix | [VSCode] Python 拡張のアクティベーションハング時に Claude Code が起動しない問題を修正（60 秒後に Python 環境なしで起動） |
| Fix | [VSCode] プラン承認カードに auto mode が提示されない問題を修正（"Yes, and use auto mode" を最初の選択肢に） |
| Fix | [VSCode] セッションリストで archive/unarchive 後にキーボードによる矢印キーナビゲーションが停止する問題を修正 |
| Fix | [VSCode] セッション再オープン後にペーストマーカー行が自分のメッセージに表示される問題を修正 |
| Feature | [Claude Code on the web] 管理者向け Routines オン/オフ設定を Admin settings → Capabilities → Remote sessions に移動 |
| Fix | [Claude Code on the web] GitHub Enterprise Server リポジトリのクラウドセッションで `gh` および GitHub API 呼び出しが約 8 時間後に失敗する問題を修正（トークン自動更新） |
| Fix | [Claude Code on the web] スケジュール実行直前に編集されたルーティンが古いプロンプト・名前で実行される問題を修正 |
| Fix | [Claude Code on the web] クラウドセッションのトランスクリプト内でセッションの作業ディレクトリ外を指すファイルリンクのファイルカードが永続的にロード中になる問題を修正（無効化して理由を表示） |
| Fix | [Claude Code on the web] 期限切れまたは新しいメッセージで上書きされた承認プロンプトが拒否として記録され auto mode がツール呼び出しを再試行しない問題を修正 |
| Improvement | [Claude Code on the web] Claude アプリでのクラウドセッション閲覧時に、ユーザー向けファイルをアプリが開けるパスに保存するよう改善 |
| Improvement | [Claude Code on the web] 管理者が GitHub をオフにした組織でセルフホスト環境のセッション開始時に空のリポジトリピッカーが表示されていた問題を修正（非表示に変更） |
| Feature | [Claude Tag] Slack のネイティブ Working インジケーター・Stop ボタン・スレッドタイトルを Claude のスレッドに追加 |
| Feature | [Claude Tag] ゲストの参加・退出で Claude の応答方法が変わる場合に Slack チャンネルへの通知を追加 |
| Fix | [Claude Tag] Enterprise Grid 参加前に接続した Slack ワークスペースでスケジュールルーティンがサイレントに失敗する問題を修正 |
| Fix | [Claude Tag] ファイルスキャンの一時的な障害時に Claude がファイルの再アップロードを要求する問題を修正（スキャン再試行・スキャナーダウン通知） |
| Fix | [Claude Tag] テキストが `+`・`-`・`*` で始まる箇条書きが空の箇条書きと余分なネストアイテムとして表示される問題を修正 |
| Fix | [Claude Tag] クラウド環境のセットアップスクリプト失敗通知が汎用メッセージになる問題を修正（スクリプト名と修正指示を表示） |
| Improvement | [Claude Tag] Claude Tag 管理設定の GitHub バナーに未接続理由（未サインイン・アプリ未リンク・SSO 未認証等）を表示するよう改善 |
| Improvement | [Code Review] Code Review チェックランが REVIEW.md 指示のカットまたは省略時にファイル名・上限とともにその旨を通知するよう改善 |

---

## まとめ

v2.1.280 は Claude Opus 5.5 の追加と Pro/Team Standard プランへのデフォルトモデル変更という大きな変化を含みつつ、50 件超のバグ修正と多数の UI 改善が含まれた大規模リリースです。フルスクリーン UI・ダイアログ操作・バックグラウンドエージェント・MCP・プラグイン管理など広範な領域で既知の問題が修正されており、安定性向上を重視したリリースとなっています。VSCode・Web・Claude Tag・Code Review の各プラットフォームにも独自の機能追加と修正が施されています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)