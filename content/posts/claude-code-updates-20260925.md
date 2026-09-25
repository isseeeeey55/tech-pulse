---
title: "【Claude Code】v2.1.282 リリースノートまとめ"
date: 2026-09-25T08:02:16+09:00
draft: false
tags: ["claude-code", "maxProseWidth", "claude-doctor", "allowClaudeInChromeWithManagedMcp", "managed-mcp.json", "CLAUDE_CODE_AUTO_MODE_SERVER", "CLAUDE_CODE_ENABLE_TELEMETRY", "OTEL_LOG", "allowManagedPermissionRulesOnly", "allowUnsandboxedCommands", "allowManagedDomainsOnly", "anthropic-skills", "claude-ai", "Amazon Bedrock", "Vertex AI", "MCP", "claude-api", "ant apply", "SessionStart"]
categories: ["Claude Code Updates"]
summary: "v2.1.282 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260925/header.png)

# Claude Code v2.1.282 リリースノート

## はじめに

Claude Code v2.1.282 は、大量のバグ修正と細かな改善が集積されたメンテナンス色の強いリリースです。公式 CHANGELOG には 86 件の変更が記録されており、主な領域は以下の通りです。

- **新設定・新機能**: `maxProseWidth` 設定、無視されたテレメトリ変数の通知、Chrome 連携のマネージド設定追加など
- **バグ修正（多数）**: web 検索結果を含む会話での 400 エラー、セッション再開時のメッセージ重複、extended thinking の欠落、vim モードの挙動など幅広い領域
- **Claude Tag（Slack 連携）向け修正**: Enterprise Grid 対応、コスト表示の誤りなど複数の不具合修正
- **VSCode 拡張向け修正**: 長い応答のレンダリング遅延、リモートコントロールセッションの開き方など

---

## 注目アップデート深掘り

### `maxProseWidth` 設定の追加

ワイドターミナルでは Claude の回答が横幅いっぱいに広がり、長い行が読みにくくなることがありました。新しく追加された `maxProseWidth` 設定は、Claude が出力する **散文（プレーンテキスト）の幅に上限** を設けるものです。テーブルとコードブロックはこの設定の影響を受けず、引き続き端末の全幅を使用します。

CHANGELOG の原文は次の通りです。

> "Added a `maxProseWidth` setting that caps the width of Claude's prose in wide terminals while tables and code blocks keep the full width"

設定値の形式は CHANGELOG には書かれていないため、指定方法は公式ドキュメントの設定リファレンスを確認してください。

---

### プロジェクト設定のテレメトリ変数の扱いの変更と通知

今回、プロジェクト設定とローカル設定では、テレメトリのエクスポートを有効化する・エンドポイントを設定する・コンテンツをキャプチャする OpenTelemetry 変数（`CLAUDE_CODE_ENABLE_TELEMETRY`、`OTEL_LOG_*` など）が**無視される**ように変更されました。

これに合わせて、プロジェクトの設定ファイル内で **無視された** テレメトリ変数や **テレメトリをオフにした** テレメトリ変数を列挙する起動時の通知が追加され、`/status` と `claude doctor` にも同じ内容の項目が加わりました。これらの変数をプロジェクト設定に書いている場合は、起動時の通知や `claude doctor` で該当する変数を確認できます。

---

## 実用的な活用ポイント

- **セッション再開の信頼性向上**: `--continue` / `--resume` 利用時にメッセージが変化した形で再送信されるケースが追加修正されました。また、`--tools` リストから組み込みツールを除外した状態で再開したとき extended thinking が失われる問題も修正されています。
- **コンパクション失敗時のリカバリ**: 要約リクエストが拒否されてコンパクションが失敗する問題が修正され、フォールバックモデルでリトライするようになりました。
- **マネージド設定の堅牢化**: boolean ロックキーの値の誤りや、ネストされた値が 1 つ不正な場合にブロック全体が無視される問題が複数修正されました。組織ポリシーとして `managed-settings.json` を運用している場合は特に注目の変更です。
- **Vertex AI での web 検索**: Claude Code がまだ認識していない（新規リリース直後などの）モデルで web 検索が提示されない問題が修正されています。

---

## 全変更点一覧

| カテゴリ | 内容 |
|---|---|
| Feature | `maxProseWidth` 設定の追加（ワイドターミナルでの散文幅上限） |
| Feature | スタートアップ通知・`/status`・`claude doctor` にテレメトリ変数一覧を追加 |
| Feature | `allowClaudeInChromeWithManagedMcp` マネージド設定の追加（`claude --chrome` と exclusive `managed-mcp.json` の共存） |
| Feature | Claude apps gateway に `store.readiness_grace_seconds` を追加（`/readyz` のフェイルオーバー耐性） |
| Feature | `/feedback` の下書きリストにスクロールバーを追加（フルスクリーンモード） |
| Fix | web 検索結果を含む会話履歴で全リクエストが 400 エラーになる問題を修正 |
| Fix | `--continue` / `--resume` 時に以前のメッセージが変化した形で再送信される問題を追加修正 |
| Fix | `/model`・`/rename`・`/artifacts` 等のスラッシュコマンド使用時に extended thinking が失われる問題を修正 |
| Fix | `--tools` リストから組み込みツールを除いた状態での再開時に extended thinking が失われる問題を修正 |
| Fix | `redacted_thinking` ブロックの "Invalid `data`" API エラーでセッションが毎ターン失敗する問題を修正（thinking ブロックを削除して 1 回リトライ） |
| Fix | コンパクション失敗時（要約拒否）にフォールバックモデルでリトライするよう修正 |
| Fix | thinking オフ・effort high 超のセッションでの安全関連のモデル切り替え後に "Effort 'xhigh' isn't available" エラーが出る問題を修正 |
| Fix | Fable usage-credits プロンプトが未応答のままモデルが切り替わる問題（SDK ホストセッション）を修正 |
| Fix | フル Fable モデル ID での `/model` が usage-credits プロンプトを開かず API エラーで止まる問題を修正 |
| Fix | 他プロセスがログインリフレッシュ中に閉じられた後、最大 1 分間ログインエラーになる問題を修正 |
| Fix | 別の Claude Code ウィンドウがサインインをリフレッシュ中に開始したセッションが組織ポリシー取得をリトライしない問題を修正 |
| Fix | リポジトリシンリンク経由での CLAUDE.md / rules 読み込みが macOS の `/Network` や `/.vol` パスに到達する問題を修正 |
| Fix | 設定ファイルの Bash 権限ルールで中間パターン `:*` が `--allowedTools` では有効なのにスキップされる問題を修正 |
| Fix | 復元されたパーミッションプロンプトで承認済みコマンドがリモートセッションのワーカー再起動時に 2 度実行される問題を修正 |
| Fix | マネージド設定で `disableClaudeAiConnectors` 等の boolean ロックキーの値が誤字だった場合に無視される問題を修正 |
| Fix | マネージド `permissions`・`autoMode`・`worktree`・`attribution` 設定でネストされた値が 1 つ不正な場合にブロック全体が無視される問題を修正 |
| Fix | マネージド `allowManagedPermissionRulesOnly` 配下でリポジトリ・ユーザー・`--add-dir` のスキル等が自ツールを事前承認できる問題を修正 |
| Fix | Amazon Bedrock / Bedrock Mantle のセーフガードブロックメッセージにリクエスト ID が表示されない問題を修正（メッセージ ID も表示） |
| Fix | Vertex AI で未認識モデルに web 検索が提示されない問題を修正 |
| Fix | Bash / PowerShell でディスククォータ超過が "Exit code 1" に隠れ大きな出力ファイルが temp に残る問題を修正 |
| Fix | ツール入力バリデーションエラーで最初の不正パラメーターしか表示されない問題を修正 |
| Fix | セッション中に bracketed paste mode がリセットされた後、貼り付けた複数行テキストが 1 行ずつ送信される問題を修正 |
| Fix | `SessionStart` フック付きプロジェクトでプロンプトのサンプルテキストが起動時に点滅して消える問題を修正 |
| Fix | フルスクリーンモード開始時に最初のフレームの前に白紙画面が一瞬表示される問題を修正 |
| Fix | ターミナルが縮小した際の非フルスクリーンレンダラーでの行ズレ問題を修正 |
| Fix | diff 再描画時に CJK 文字・絵文字が折り返した際に末尾に文字が残る問題を修正 |
| Fix | 履歴から呼び出したプロンプトにタブが含まれているとカーソル位置がずれる問題を修正 |
| Fix | Windows Terminal 1.25 未満で ctrl+enter を送信するターミナルでの "send-now" ヒントを修正（ctrl+x ctrl+s を表示） |
| Fix | `claude remote-control --debug` が "Unknown argument: --debug" で失敗する問題を修正 |
| Fix | `/install-github-app` でキャンセルしても branch push と API key シークレット保存が続行される問題を修正 |
| Fix | Bedrock / Vertex 等のサードパーティプロバイダーで `/feedback`・`/bug`・`/share` の保存中にキャンセルしてもレポートファイルが保存される問題を修正 |
| Fix | プラグインアンインストール時に設定ファイルが有効な状態だと成功と報告してオプションを削除してしまう問題を修正 |
| Fix | プラグインアンインストール後にインストール済みプラグイン一覧が読めない場合に保存オプション・シークレットが削除される問題を修正 |
| Fix | `/skills` で `/` 直後のキー入力がスキルリストを移動してしまう問題を修正 |
| Fix | `/skills` 検索ボックス入力中にカーソルがスキルリストにジャンプする問題（IME 入力の誤配置）を修正 |
| Fix | `/skills`・`/mcp` 等スクロールバー付きリストが非フルスクリーンで 2 列分狭くなる問題を修正 |
| Fix | エージェントパネルフッターが長いキーバインドで 2 行に折り返す問題と "Esc to collapse" ヒントが再バインドキーを無視する問題を修正 |
| Fix | `/tasks` ダイアログフッターで stop-all-agents ショートカットが未バインドの場合に `·` セパレーターが二重になる問題を修正 |
| Fix | アーティファクト公開時にバージョンラベルが 60 文字超だと失敗する問題を修正（ラベルを短縮） |
| Fix | スクリーンリーダーモード・引用リスト等でコードブロックの先頭空行が欠落する問題を修正 |
| Fix | PDF ページ読み取りエラーメッセージでアクセント文字・非ラテン文字パスが文字化けし、ディレクトリ名による誤原因表示が起きる問題を修正 |
| Fix | vim モードの `>>` が空行をインデント、`r` がカウント指定時に誤動作、`2J` が 1 行多く結合、末尾行でのカウント操作が誤動作する問題を修正 |
| Fix | vim モードのカーソル位置: `dd`・`dj`・`dG`・行全体の `p`/`P` 後の位置、`yy` による移動、絵文字後の Esc の問題を修正 |
| Fix | vim モードで `.` 前のカウントが無視される問題、行折り返し時の行全体操作が誤行に作用する問題を修正 |
| Fix | vim モードで履歴から呼び出したプロンプトや normal モードでカーソルが行末を超える問題を修正 |
| Improvement | 大規模セッション（未コンパクトを含む）の再開時間を改善 |
| Improvement | Windows でのトランスクリプトファイル読み取りエラー (EBADF) 時のエラーメッセージを改善 |
| Improvement | Claude Desktop での未知モデルエラーに別モデルへの切り替え提案を追加 |
| Improvement | パーミッションプロンプトでの特殊 Unicode のレンダリングを改善 |
| Improvement | `/artifacts`: タイトルの列揃え、詳細の単語途中切り捨て防止、PgUp/PgDn・Home/End・マウスホイール・クリック対応 |
| Improvement | `claude-api` スキル更新: 出力前拒否の課金リンク追加、ミッドストリーム拒否の課金説明、レート制限カウントの明記 |
| Improvement | `claude-api` スキル更新: Managed Agents リソースのバージョン管理に `ant apply` を推奨 |
| Change | auto モードが直接 Anthropic API 接続かつテレメトリオフ時にサーバーサイド分類器をデフォルトで使用するよう変更（`CLAUDE_CODE_AUTO_MODE_SERVER=0` でオプトアウト） |
| Change | `sandbox.excludedCommands` がマネージド設定や `--settings` で `allowUnsandboxedCommands: false` 等が設定されている場合にプロジェクト・ローカル設定を無視するよう変更 |
| Change | プロジェクト・ローカル設定で OpenTelemetry エクスポート有効化・エンドポイント・コンテンツキャプチャ変数を無視するよう変更 |
| Change | Windows/WSL のマネージド設定で管理者ポリシーが無効・読み取り不能な場合にユーザー書き込み可能な HKCU と WSL `/etc/claude-code` を適用しないよう変更 |
| Change | `Skill(anthropic-skills:*)` と `Skill(claude-ai:*)` の許可ルールを claude.ai から同期されたスキルのみに限定 |
| Change | `anthropic-skills` / `claude-ai` 名前空間のスキルフォルダ・コマンドファイル・ワークフローコマンドをロードしないよう変更 |
| Change | `anthropic-skills` / `claude-ai` 名前で設定された MCP サーバーのスキル・プロンプトをリストしないよう変更 |
| Change | `ultracode` ビジュアル（`/effort` とプロンプト入力）をプレーンスタイルに変更し dynamic-workflows スピナーヒントを削除 |
| Change | Clawd マスコットの足の位置調整 |
| Fix | [VSCode] 長い応答でパネルが毎更新に全返答を再パースする問題を修正 |
| Fix | [VSCode] ディクテーションマイクボタンがメッセージ入力のスクロールバーを覆う問題を修正 |
| Fix | [VSCode] リモートコントロールセッションが Web エントリから開けない問題を修正 |
| Fix | [VSCode] エディタータブのサインイン画面がエクステンションホスト再起動後にハングする問題を修正 |
| Feature | [Cloud sessions] Settings › Connectors › GitHub に Claude GitHub App ステータス表示を追加 |
| Feature | [Cloud sessions] GitHub 以外の Git サーバーのリポジトリに "Open repository" / "Open compare page" リンクを追加 |
| Feature | [Cloud sessions] 実行中クラウドセッションに別 GitHub オーナー（fork の upstream 等）のリポジトリを追加アタッチ可能に |
| Fix | [Cloud sessions] 半時間オフセットタイムゾーン（インド等）で時間ルーティンの次回実行時刻が 30 分ずれる問題を修正 |
| Improvement | [Cloud sessions] Routines ページとサイドバーの Scheduled リストの読み込み速度を改善 |
| Fix | [Claude Tag] Enterprise Grid のワークスペースをまたいだチャンネルパターン自動参加が無視される問題を修正 |
| Fix | [Claude Tag] Enterprise Grid で 2 ワークスペース共有チャンネルで Claude が応答しない問題を修正 |
| Fix | [Claude Tag] GitHub Enterprise Server リポジトリのプログレスカードの表示・Create PR ボタンの動作を修正 |
| Fix | [Claude Tag] 廃止モデルのスレッドが毎回フォールバックを繰り返す問題を修正（スレッドを動作するモデルに移行） |
| Fix | [Claude Tag] テーブルを含むキャプション付きファイルアップロードが失敗する問題を修正 |
| Fix | [Claude Tag] Agents & tools ビューでのスレッド表示名が最初のメッセージになる問題を修正（リネーム後も更新） |
| Fix | [Claude Tag] GitHub 組織の grant 削除が接続解除後に保存失敗する問題を修正 |
| Fix | [Claude Tag] 追加されていない Grid ワークスペース共有チャンネルでの "Couldn't check this channel" メッセージを改善 |
| Fix | [Claude Tag] セッションのクラウドワーカー再起動後にコスト・トークン合計が大幅に過大表示される問題を修正 |
| Change | [Claude Tag] Slack 返信のボーダーカードをデフォルトでワイド表示に変更 |
| Change | [Claude Tag] 新規接続 Slack ワークスペースが接続時点のデフォルトモデルではなく現在のデフォルトモデルに従うよう変更 |

---

## まとめ

v2.1.282 は新機能よりも **修正と安定性向上に重点を置いたリリース** です。セッション再開・extended thinking の欠落・マネージド設定の誤動作など、信頼性に直結する修正が多数含まれています。vim モードの挙動修正やレンダリング修正も多数含まれます。また、`anthropic-skills` / `claude-ai` 名前空間のスキル・MCP サーバーの扱いや、プロジェクト設定のテレメトリ変数の扱いなど、既存の設定に影響しうる変更（Change）もあるため、該当する設定を使っている場合は全変更点一覧を確認してください。VSCode 拡張、Cloud sessions、Claude Tag（Slack 連携）向けの項目も含まれています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)