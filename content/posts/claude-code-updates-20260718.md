---
title: "【Claude Code】v2.1.212 リリースノートまとめ"
date: 2026-07-18T08:01:59+09:00
draft: true
tags: ["claude-code", "fork", "subtask", "auto-mode", "websearch", "subagent", "mcp", "resume", "plan-mode", "bash", "worktree", "hook", "sigterm", "windows", "powershell", "ultrareview", "opentelemetry", "otlp", "prompt-caching", "bedrock", "vertex", "agent-view", "enterprise", "sdk"]
categories: ["Claude Code Updates"]
summary: "v2.1.212 のClaude Codeリリースノートまとめ"
---

## はじめに

Claude Code v2.1.212 がリリースされました。本バージョンでは、セッション管理の強化とランアウェイ対策が中心となっています。`/fork` コマンドがバックグラウンドセッションへの会話コピー方式に変更され、WebSearch と subagent の各セッション上限設定、長時間実行 MCP ツールの自動背景化、`/resume` による過去セッション復帰機能が追加されました。また、plan mode におけるファイル修正 Bash コマンドの無許可実行や、worktree 作成時の symlink 追跡による範囲外ファイル作成といったセキュリティ問題が修正されています。

---

## 注目アップデート深掘り

### `/fork` コマンドの動作変更とセッション並行管理

従来の `/fork` はセッション内 subagent を起動していましたが、本バージョンから会話を新しいバックグラウンドセッション（`claude agents` の独立した行）にコピーする方式に変更されました。元のセッションでは作業を継続でき、従来の in-session subagent 起動は `/subtask` に移行しています。また、セッションにタイトルがない場合は、プロンプト内容から名前を付けるよう変更され、agent view での識別性が向上しました。

これにより、複数の会話を並列に進めながら、元のセッションの作業を中断せずに続けられるようになります。バックグラウンドセッションが完了すると、入力待ちがない場合でも `←` フッターヒントが `N done` と一瞬点滅して通知します。

### WebSearch と subagent のランアウェイループ対策

セッション全体で WebSearch ツール呼び出しに上限（デフォルト 200、環境変数 `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` で調整可能）が設定され、無限検索ループを防止します。同様に、セッション内の subagent 生成数にも上限（デフォルト 200、`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` でオーバーライド可能）が設けられ、無限委譲ループを防ぎます。`/clear` を実行すると、subagent の予算がリセットされます。

### MCP ツールの長時間実行自動背景化

MCP ツール呼び出しが 2 分を超えて実行される場合、自動的にバックグラウンドに移行し、セッションの操作性を維持します。この閾値は `CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` 環境変数で設定でき、無効化も可能です。

---

## 実用的な活用ポイント

`/fork` と `/resume` の組み合わせにより、複数の調査や開発タスクを並行して進める運用が可能になります。`/resume` は agent view で実行すると、過去のセッション一覧（削除済みセッションを含む）から選択してバックグラウンドセッションとして復帰できます。

WebSearch と subagent の上限設定は、ループによるリソース消費を防ぎ、セッションの安定性を高めます。`claude auto-mode reset` コマンドで、デフォルトの auto-mode 設定を確認プロンプト付きで復元できます（`--yes` フラグでスキップ可能）。

セキュリティ面では、plan mode でのファイル修正 Bash コマンド（`touch`、`rm` など）が許可プロンプトや SDK `canUseTool` コールバックなしに自動実行されていた問題が修正され、意図しない操作を防げるようになりました。

---

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | `/fork` の動作変更 | 会話をバックグラウンドセッションにコピーする方式に変更、in-session subagent は `/subtask` に移行 |
| Feature | `claude auto-mode reset` 追加 | デフォルト auto-mode 設定を確認プロンプト付きで復元（`--yes` でスキップ可能） |
| Feature | WebSearch ツール上限 | セッション全体で WebSearch 呼び出し上限を設定（デフォルト 200、`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION` で調整） |
| Feature | subagent 生成上限 | セッション内 subagent 生成数に上限（デフォルト 200、`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` でオーバーライド可能、`/clear` でリセット） |
| Feature | MCP ツール自動背景化 | 2 分超の MCP ツール呼び出しを自動的にバックグラウンドに移行（`CLAUDE_CODE_MCP_AUTO_BACKGROUND_MS` で調整・無効化可能） |
| Feature | `/resume` セッション復帰 | agent view で `/resume` を実行すると過去セッション（削除済み含む）を選択してバックグラウンドセッションとして復帰 |
| Fix | plan mode でのファイル修正 Bash コマンド無許可実行 | `touch`、`rm` などのファイル修正コマンドが許可プロンプトや SDK `canUseTool` コールバックなしに自動実行されていた問題を修正 |
| Fix | worktree 作成時の symlink 追跡 | `.claude/worktrees` のリポジトリコミット済み symlink を追跡してリポジトリ外にファイルを作成していた問題を修正 |
| Fix | `continue:false` hook のハルト処理 | ツール失敗・完了中にハルトが失われ、hook インフラエラーがユーザー拒否として誤報告されていた問題を修正 |
| Fix | SIGTERM 時の Bash プロセスツリー孤立 | print/SDK モード実行中の SIGTERM が Bash プロセスツリーを孤立させていた問題を修正、CLI はターン中止・ツリー終了・exit 143 を実行 |
| Fix | Windows での `/background` と `claude --bg` 失敗 | Group Policy が PowerShell 5.1 をブロックする環境で "EUNKNOWN: unknown error, uv_spawn" エラーが発生していた問題を修正、PowerShell 7 を優先使用 |
| Fix | shell mode での自動補完中のコマンド実行 | ファイルパス自動補完ポップアップ表示中に `!` でコマンドが実行されなかった問題を修正 |
| Fix | auto-mode 拒否通知の文字化け | 長い拒否理由が絵文字の途中で切り詰められて文字化けしていた問題を修正 |
| Fix | Ctrl+J での改行挿入 | 拡張キー報告を持つ端末の agent view 入力欄で Ctrl+J が改行を挿入しなかった問題を修正、`?` ヘルプに改行ショートカットを追加 |
| Fix | `/ultrareview` の PR 参照拒否 | `#123`、`PR 123`、ペーストされた PR URL を拒否していた問題を修正、エラーヒントに実際に入力したコマンド名を表示 |
| Fix | `/ultrareview <branch>` のリモート取得 | ブランチがリモートに存在する場合に取得しなかった問題を修正、タイポ時に最も近いブランチ名を提案 |
| Fix | `/ultrareview` の `/clear` 後の請求確認スキップ | 新しい会話で `/clear` 後に請求確認がスキップされていた問題を修正 |
| Fix | Claude Desktop での `/ultrareview` エラー提案 | "not a git repository" エラー時に端末コマンドではなくプロジェクトのリポジトリフォルダを提案するよう修正 |
| Fix | hosted セッションでの起動失敗 | リポジトリ設定で mTLS 証明書、追加 CA バンドル、OAuth スコープが設定されている場合に起動失敗していた問題を修正、警告付きで無視 |
| Fix | ファイル編集時のエラー | offset/limit 付きで読み取ったファイルをセッション再開後に編集すると "File has not been read yet" エラーが発生していた問題を修正 |
| Fix | `ExitWorktree` の失敗 | print/SDK モードで `--continue`/`--resume` によるセッション再開後に "no active EnterWorktree session" エラーが発生していた問題を修正 |
| Fix | workflow agent グリッドの空表示 | Remote Control クライアントが実行中にセッションに参加した際にグリッドが空のままだった問題を修正 |
| Fix | ストリーミングモード制御リクエストの完了タイミング | ハンドラ終了前にリクエストが完了扱いされ、セッション再起動時にリクエストが失われていた問題を修正 |
| Fix | `/fork` 作成バックグラウンドセッションの保護喪失 | 状態書き込み失敗後に live-parent 保護が失われていた問題を修正 |
| Fix | 停止済みバックグラウンドセッションの再開失敗 | agent view からの再開が無言で失敗していた問題を修正、再開実行または不可理由表示と強制再起動オプションを提供 |
| Fix | agent teams の重複アイドル通知 | 停止中のチームメイトがセッション内でチーム初期化が再実行された際にリーダーに重複アイドル通知を送信していた問題を修正 |
| Fix | plan 承認ダイアログフッターの分割 | ファイルパスが長い場合に "ctrl+g to edit in <editor>" が分割されていた問題を修正 |
| Fix | ウェルカムバナーのパネル幅保持 | フルスクリーンモードで幅と高さが同時にリサイズされた際に古いパネル幅が保持されていた問題を修正 |
| Fix | diff プレビューの行番号と +/- マーカー喪失 | 狭いレイアウトで行番号と +/- マーカーが失われていた問題を修正 |
| Fix | @-mention の複数問題 | 部分的なファイル読み取り後に何も添付されない、plugin uninstall が間違ったマーケットプレイスを対象にする、exit code 143 で偽の "Command timed out" が発生する問題を修正 |
| Fix | OpenTelemetry HTTP エクスポート拒否 | Azure Monitor など chunked transfer encoding を受け入れないエンドポイントで 411/400 エラーが発生していた問題を修正 |
| Fix | OTLP イベントログレコードの trace_id/span_id 欠落 | SDK/headless モードで `TRACEPARENT` が設定されている場合に欠落していた問題を修正 |
| Fix | 画像多数の会話での誤エラー | 画像が多い会話で誤って "Request too large" エラーが発生していた問題を修正、エラーメッセージで実際の原因を説明するよう改善 |
| Fix | web search と web fetch の API エラーテキスト返却 | API が過負荷の際に "API Error" テキストが検索結果やページ内容として返却されていた問題を修正 |
| Improvement | web search と web fetch の信頼性向上 | 529 エラーとレート制限リクエストを制限付きバックオフで再試行 |
| Improvement | prompt caching の改善 | mid-conversation system ブロックが LLM ゲートウェイとカスタム base URL（Bedrock、Vertex、1P）の背後で動作するよう改善 |
| Improvement | background agent attach の改善 | コールドアタッチ時に、セッション起動中の空白待ちではなく、即座にフォーマット済みトランスクリプトを表示 |
| Improvement | inter-agent メッセージングのトークン削減 | `SendMessage` 本体が再生履歴とツール結果に重複して含まれていた問題を解消 |
| Improvement | `/fork` のセッション名付け | セッションにタイトルがない場合はプロンプト内容から名前を付け、agent view で識別可能に |
| Improvement | bare `/btw` の動作変更 | 最新のやり取りで side-question パネルを再開し、過去の回答を閲覧可能に |
| Improvement | バックグラウンドエージェント完了通知 | 入力待ちがない場合でも `←` フッターヒントが `N done` と一瞬点滅 |
| Breaking | Task ツール `mode` パラメータの非推奨化 | 無視されるよう変更、subagent は親セッションの許可モードをデフォルトで継承 |
| Improvement | Enterprise `forceLoginMethod` の適用範囲拡大 | VS Code 拡張、SDK、`setup-token`、`install-github-app` ログインにも適用 |
| Improvement | セッショントランスクリプトに reasoning effort level 記録 | 各 assistant メッセージに reasoning effort level を記録 |
| Improvement | headless/SDK セッションの mid-turn モデル変更 | `set_model` 制御リクエストをターン中に適用、次のラウンドトリップから新モデルを使用 |
| Improvement | agent view / `claude agents --json` のステータス表示 | sandbox、MCP-input、managed-settings プロンプト待ちのセッションを "Working" ではなく "Needs input" と表示 |
| Improvement | 認証ステータスパネルタイトル変更 | "Cloud authentication" から "Authentication" に変更 |
| Improvement | リリースノート訂正 | 2.1.200 のリリースノートを訂正、tmux 3.6 系列まで synchronized output サポートなし、新しい tmux は自動検出 |

---

## まとめ

v2.1.212 は、セッション管理の柔軟性と安全性を大幅に強化したバージョンです。`/fork` のバックグラウンドセッション化と `/resume` による復帰機能により、複数タスクの並行実行が容易になりました。WebSearch と subagent の上限設定、MCP ツールの自動背景化は、ランアウェイループを防ぎ、セッションの安定性を向上させます。

セキュリティ面では、plan mode でのファイル修正 Bash コマンドの無許可実行や、worktree 作成時の symlink 追跡による範囲外ファイル作成といった問題が修正され、安全性が向上しています。また、Windows 環境での `/background` と `claude --bg` の失敗、`/ultrareview` の PR 参照拒否、OpenTelemetry エクスポート拒否など、多岐にわたる修正が含まれています。

prompt caching の LLM ゲートウェイ対応改善、inter-agent メッセージングのトークン削減、headless/SDK セッションの mid-turn モデル変更適用など、パフォーマンスと運用性の改善も含まれており、全体として安定性と機能性が向上した実用的なリリースとなっています。

---

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)