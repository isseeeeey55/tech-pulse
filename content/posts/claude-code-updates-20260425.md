---
title: "【Claude Code】v2.1.119 リリースノートまとめ"
date: 2026-04-25T08:01:27+09:00
draft: false
tags: ["claude-code", "settings", "gitlab", "bitbucket", "github-enterprise", "powershell", "hooks", "mcp", "opentelemetry", "permission-mode", "vim", "skills"]
categories: ["Claude Code Updates"]
summary: "v2.1.119 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260425/header.png)

## はじめに

2026年4月25日、Claude Code v2.1.119 がリリースされました。Fix の量がかなり多い回で、加えて `/config` の永続化、`--from-pr` のマルチプラットフォーム対応、PowerShell の auto-approve 対応、Hooks への `duration_ms` 追加、OpenTelemetry の属性追加など、運用に効く小〜中粒の改善が並んでいます。

本記事で深掘りするのは次の 2 つ。

- **`/config` の設定が `~/.claude/settings.json` に永続化** — theme / editor mode / verbose 等の設定が project/local/policy override の precedence に乗る
- **`--from-pr` が GitLab MR / Bitbucket PR / GHE PR URL に対応** — GitHub.com 以外の組織でも PR コンテキスト読み込みが使える

Fix は 30 件超で、`/skills` の Enter キー挙動、async `PostToolUse` フックの空エントリ、`/usage` プログレスバー被り、MCP OAuth の細かい修正など、日常で踏みやすかった箇所が広く潰されています。

## 注目アップデート深掘り

### 1. `/config` の設定が settings.json に永続化

![/config の永続化と override precedence](/images/claude-code-updates-20260425/config-persistence.png)

公式リリースノートより（原文）:

> `/config` settings (theme, editor mode, verbose, etc.) now persist to `~/.claude/settings.json` and participate in project/local/policy override precedence

#### 何が変わるか

これまで `/config` で変更した theme / editor mode / verbose 等の設定はセッション内でのみ有効で、再起動するとデフォルトに戻っていました。v2.1.119 からは **`~/.claude/settings.json` に書き出されて永続化** され、かつ既存の **project / local / policy override の precedence** に乗ります。

> **policy override precedence とは？**
> Claude Code の設定の解決順序。一般的に「policy（管理者配布）> local（ローカル `.claude/settings.local.json`）> project（リポジトリの `.claude/settings.json`）> user（`~/.claude/settings.json`）」のような優先順位で評価されます。`/config` で変更した値が user スコープに記録されるので、project / policy 側の同じキーがあればそちらが勝ちます。

#### 実用面での効き方

- 個人用途で毎回 `/config` で `verbose` をトグルしていた人は、もう手間が省ける
- 組織で managed-settings を policy 側に配布している場合、ユーザーが `/config` で書き換えても **policy 側が precedence で勝つ** ので、統制が崩れない
- 関連 Fix で「**verbose 設定が再起動後に persist しない**」問題も解消されている（`Fixed verbose output setting not persisting after restart`）

なお、`permissionMode` の意味的な「組織ポリシーで制限」のような話は今回のリリースには含まれていません。settings.json の階層 override 自体は以前から存在する仕組みです。

---

### 2. `--from-pr` が GitLab / Bitbucket / GHE に対応

![--from-pr のマルチプラットフォーム対応](/images/claude-code-updates-20260425/from-pr-multi.png)

公式リリースノートより（原文）:

> `--from-pr` now accepts GitLab merge-request, Bitbucket pull-request, and GitHub Enterprise PR URLs

これまで `--from-pr` は github.com の PR URL のみが対象でした。v2.1.119 からは **GitLab の merge-request URL、Bitbucket の pull-request URL、GitHub Enterprise の PR URL** が受け付けられるようになります。

#### 想定される URL 形式

```bash
# GitHub.com (従来通り)
$ claude --from-pr https://github.com/owner/repo/pull/123

# GitLab (新規対応)
$ claude --from-pr https://gitlab.example.com/group/project/-/merge_requests/45

# Bitbucket (新規対応)
$ claude --from-pr https://bitbucket.example.com/projects/PROJ/repos/repo/pull-requests/12

# GitHub Enterprise (新規対応)
$ claude --from-pr https://github.enterprise.example.com/owner/repo/pull/67
```

詳細な認証方法（GitLab トークン、Bitbucket app password、GHE PAT など）は公式ドキュメントを参照してください。本記事ではドキュメントにない認証方式までは推測で書きません。

#### 関連: `prUrlTemplate` 設定の追加

同じ v2.1.119 で `prUrlTemplate` 設定が追加され、フッターの PR バッジが向く先を github.com 以外のレビューシステムに置き換えられるようになりました。GitLab/Bitbucket/GHE 中心の組織は、`prUrlTemplate` と `--from-pr` をセットで使うと、Claude Code を GitHub.com 前提から開放する整理ができます。

#### `owner/repo#N` ショートハンドも対応強化

これも関連改善で、出力中の `owner/repo#123` 形式のショートハンドリンクが、**git remote のホスト**を使ってリンクされるようになりました（従来は常に github.com を指していた）。GHE / GitLab セルフホスト環境のチームには地味に効きます。

---

## 実用的な活用ポイント

### Hooks: `PostToolUse` / `PostToolUseFailure` に `duration_ms`

公式リリースノートより:

> Hooks: `PostToolUse` and `PostToolUseFailure` hook inputs now include `duration_ms` (tool execution time, excluding permission prompts and PreToolUse hooks)

`PostToolUse` だけでなく **`PostToolUseFailure`** にも `duration_ms` が来ます。permission prompt 待ち時間と PreToolUse フックの時間は除外された、純粋なツール実行時間。OpenTelemetry や独自の集計に流せば、ツール別の実行時間分布がフックレベルで取れます。

### PowerShell の auto-approve

> PowerShell tool commands can now be auto-approved in permission mode, matching Bash behavior

これまで Bash 限定だった auto-approval が PowerShell でも効くようになりました。Windows メインの開発者が、Bash 利用者と同じ auto mode 体験を得られるようになります。

### `--print` / `--agent` の挙動改善

- `--print` モードが、エージェント frontmatter の `tools:` と `disallowedTools:` を honor するようになった（インタラクティブモードと挙動を揃える）
- `--agent <name>` が、built-in agents の `permissionMode` を honor するようになった

スクリプトや CI 経由で `--print` / `--agent` を使っているチームには、**意図したツール制限が一貫して効く**ようになる修正です。

### MCP の並列再接続

> Subagent and SDK MCP server reconfiguration now connects servers in parallel instead of serially

Subagent や SDK 経由で MCP サーバを再構成する場面で、サーバ接続が直列から並列に変わりました。v2.1.118 で入った「ローカル + claude.ai MCP の並列接続が既定」とは別の場所での並列化です。

### OpenTelemetry の属性拡張

> OpenTelemetry: `tool_result` and `tool_decision` events now include `tool_use_id`; `tool_result` also includes `tool_input_size_bytes`

`tool_result` / `tool_decision` イベントで **特定のツール呼び出しを `tool_use_id` で追跡可能**になり、`tool_result` には **入力サイズ (`tool_input_size_bytes`)** も付くようになりました。「どのツール呼び出しが何バイトの入力を受けて何 ms で終わったか」が、ID 紐付けで追える形。

### Vim モードの細かい改善

INSERT モードで Esc を押したときに、queued message が input に戻る挙動を停止。**Esc をもう一度押すと中断**になる。Vim ユーザの操作感が他モードと近づきます。

### Status line への `effort.level` / `thinking.enabled`

ステータスライン用の stdin JSON に `effort.level` と `thinking.enabled` が含まれるようになりました。カスタムステータスラインで現在の effort や thinking 状態を表示できます。

---

## 全変更点一覧

| カテゴリ | 変更内容 |
|---|---|
| **Feature** | `/config` 設定 (theme, editor mode, verbose 等) を `~/.claude/settings.json` に永続化、project/local/policy override precedence 対応 |
| **Feature** | `prUrlTemplate` 設定追加。フッターの PR バッジを GitHub.com 以外の URL に向けられる |
| **Feature** | `CLAUDE_CODE_HIDE_CWD` 環境変数追加。起動ロゴで cwd を非表示化 |
| **Feature** | `--from-pr` が GitLab MR / Bitbucket PR / GitHub Enterprise PR URL に対応 |
| **Feature** | `--print` モードが agent frontmatter の `tools:` / `disallowedTools:` を honor |
| **Feature** | `--agent <name>` が built-in agents の `permissionMode` を honor |
| **Feature** | PowerShell ツールコマンドが permission mode で auto-approve 対象に（Bash と同様） |
| **Feature** | Hooks: `PostToolUse` / `PostToolUseFailure` に `duration_ms` 追加（permission prompt と PreToolUse 除外） |
| **Improvement** | Subagent / SDK MCP server の reconfiguration が並列接続化 |
| **Improvement** | プラグインが他プラグインの version 制約で pin されたとき、満たす最新の git tag に auto-update |
| **Improvement** | Vim mode: INSERT で Esc が queued message を戻さず、再押下で中断に |
| **Improvement** | スラッシュコマンド候補がクエリにマッチした文字をハイライト |
| **Improvement** | スラッシュコマンドピッカーが長い説明を切り捨てず 2 行に折り返し |
| **Improvement** | `owner/repo#N` ショートハンドリンクが git remote のホストを使用（github.com 固定でなくなる） |
| **Improvement** | `blockedMarketplaces` の `hostPattern` / `pathPattern` エントリが正しく強制されるように |
| **Improvement** | OpenTelemetry: `tool_result` / `tool_decision` に `tool_use_id` 追加、`tool_result` に `tool_input_size_bytes` 追加 |
| **Improvement** | ステータスライン stdin JSON に `effort.level` / `thinking.enabled` 追加 |
| **Improvement** | Tool search が Vertex AI でデフォルト無効化（unsupported beta header 回避、`ENABLE_TOOL_SEARCH` で opt-in 可） |
| **Fix** | CRLF コンテンツ (Windows clipboard、Xcode console) の貼り付けで余計な空行が入る |
| **Fix** | kitty keyboard protocol の bracketed paste で複数行貼り付けの改行が消える |
| **Fix** | macOS/Linux ネイティブビルドで Bash tool が deny されると Glob/Grep ツールも消える |
| **Fix** | フルスクリーンモードで上スクロール後、ツール完了のたびに底に戻る |
| **Fix** | MCP HTTP 接続で OAuth discovery が non-JSON を返すと "Invalid OAuth error response" で失敗 |
| **Fix** | Rewind オーバーレイが画像添付メッセージで "(no prompt)" と表示 |
| **Fix** | auto mode が plan mode の "Execute immediately" 指示で plan mode を上書きする |
| **Fix** | レスポンスペイロードを返さない非同期 `PostToolUse` フックがセッショントランスクリプトに空エントリを書く |
| **Fix** | サブエージェントタスク通知がキューに孤立した状態でスピナーが回り続ける |
| **Fix** | スラッシュコマンド内で絶対パスを使った場合、`@`-file の Tab 補完がプロンプト全体を置換 |
| **Fix** | macOS Terminal.app で Docker / SSH 経由起動時に起動プロンプトに余分な `p` 文字 |
| **Fix** | HTTP/SSE/WebSocket MCP サーバの `headers` 内の `${ENV_VAR}` プレースホルダがリクエスト前に置換されない |
| **Fix** | `--client-secret` で保存した MCP OAuth client secret が `client_secret_post` 必須サーバとのトークン交換時に送られない |
| **Fix** | `/skills` で Enter キーがダイアログを閉じてしまい、`/<skill-name>` がプロンプトに pre-fill されない |
| **Fix** | `/agents` 詳細ビューがサブエージェント未使用な built-in tool を "Unrecognized" と誤表示 |
| **Fix** | プラグイン由来の MCP サーバが、プラグインキャッシュが不完全な状態の Windows で起動しない |
| **Fix** | `/export` が会話で実際に使われたモデルではなく、現在のデフォルトモデルを表示 |
| **Fix** | verbose output 設定が再起動後に persist しない |
| **Fix** | `/usage` プログレスバーが "Resets …" ラベルと重なる |
| **Fix** | プラグイン MCP サーバが `${user_config.*}` 参照先のオプションフィールドが空のとき失敗 |
| **Fix** | リスト項目の文末数字が単独で次行に折り返される |
| **Fix** | `/plan` / `/plan open` が plan mode 入室時に既存プランに作用しない |
| **Fix** | auto-compaction 前に呼ばれた skill が、次のユーザーメッセージに対して再実行される |
| **Fix** | `/reload-plugins` / `/doctor` が無効化されたプラグインのロードエラーを報告 |
| **Fix** | Agent ツールの `isolation: "worktree"` が前セッションの古い worktree を再利用 |
| **Fix** | 無効化された MCP サーバが `/status` で "failed" と表示 |
| **Fix** | `TaskList` がタスクをファイルシステム順で返し、ID 順ソートされていない |
| **Fix** | `gh` 出力に "rate limit" を含む PR タイトルがあると "GitHub API rate limit exceeded" を誤表示 |
| **Fix** | SDK/bridge `read_file` が成長中のファイルでサイズ上限を正しく強制しない |
| **Fix** | git worktree で動作時、PR がセッションにリンクされない |
| **Fix** | `/doctor` が、より高い precedence のスコープで上書きされた MCP サーバエントリに対して警告 |
| **Fix** | Windows: 偽陽性の "Windows requires 'cmd /c' wrapper" MCP 設定警告を削除 |
| **Fix** | [VSCode] macOS でマイク許可プロンプト中に音声ディクテーションの初回録音が無音 |

## まとめ

v2.1.119 は Fix の量で見ると 2026-04 の中でも特に多い回で、特に MCP OAuth まわり、Hooks の細かい挙動、フルスクリーン UI、`/skills` / `/agents` / `/export` / `/usage` 系のスラッシュコマンドなど、日常的に踏みうる箇所が広く修正されています。

機能追加では、`--from-pr` のマルチプラットフォーム対応がチーム単位での導入のしやすさに直結する変更です。GitLab セルフホストや GHE 中心の組織で、これまで「PR コンテキストを CLI で食わせる」運用が GitHub.com 前提でしか組めなかった部分を、本来の Git ホスティングに合わせられるようになります。`prUrlTemplate` と `owner/repo#N` の git remote 対応も含めて、Claude Code を GitHub.com 前提から外す方向の整理が今回のリリースの裏テーマと言えそうです。

`/config` の永続化は地味ですが、毎回 `verbose` を切り替えていた人や、組織で managed-settings を配っているチームには日常的に効きます。Hooks の `duration_ms` と OpenTelemetry の `tool_use_id` / `tool_input_size_bytes` も合わせて、observability まわりが一段強化されたリリースです。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
