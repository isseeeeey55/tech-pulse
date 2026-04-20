---
title: "【Claude Code】v2.1.116 リリースノートまとめ"
date: 2026-04-21T08:02:01+09:00
draft: false
tags: ["claude-code", "mcp", "resume", "hooks"]
categories: ["Claude Code Updates"]
summary: "v2.1.116 の `/resume` 大規模セッション高速化、MCP stdio 起動の最適化、sandbox の dangerous-path ガード修正などを解説"
---

![Claude Code v2.1.116 リリースノートまとめ](/images/claude-code-updates-20260421/header.png)

## はじめに

Claude Code v2.1.116 がリリースされました。目立つ変更は `/resume` の大規模セッション高速化（40MB 超で最大 67%）と、MCP stdio サーバーの起動時間短縮です。そのほか、thinking スピナー、`/config` 検索、`/doctor` の応答中実行、plugin の依存関係自動インストールといった UX 系の改善と、`rm`/`rmdir` の dangerous-path チェックが sandbox auto-allow でバイパスされていた問題の修正が入っています。

バグ修正の割合がやや多く、機能追加というより既存機能の整備・安全性向上に寄ったリリースです。

## 注目アップデート深掘り

### `/resume` の大規模セッション高速化

![/resume の40MB+セッション高速化と dead-fork 処理改善](/images/claude-code-updates-20260421/resume-speedup.png)

`/resume` で過去のセッションを再開するとき、40MB を超えるような大規模セッションで最大 67% 高速化しました。同時に、過去の会話履歴に含まれる dead-fork エントリ（途中で分岐して放棄された会話ブランチの痕跡）の処理効率も改善されています。

実際に重たくなる場面は、長時間作業した日の会話を後日 `/resume` するとき、あるいは Terraform 全面改修のような大きなリポジトリで複数ターンを重ねた後です。以前はロードに数秒〜数十秒かかっていた規模でも、体感でストレスが減るレベルになっています。

関連して、`/resume` が大きなセッションファイルで無言のまま空の会話を表示する不具合（ロードエラーを報告しない）も修正されました。これまで「`/resume` したのに何も出てこない」状態に遭遇していた場合、今回の更新で原因が表示されるようになります。

また、`/branch` が 50MB 超のトランスクリプトを拒否していた問題も解消されています。

### MCP stdio サーバー起動の最適化

複数の stdio ベースの MCP サーバーを設定している環境で、起動が速くなりました。仕組みとしては、起動時に一律で実行していた `resources/templates/list` の呼び出しを、最初の `@`-mention が発生するタイミングまで遅延する形に変更されています。

```jsonc
// .mcp.json で複数サーバーを登録している例
{
  "mcpServers": {
    "github": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"] },
    "filesystem": { "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"] },
    "fetch": { "command": "uvx", "args": ["mcp-server-fetch"] }
  }
}
```

このように 3 つ以上の stdio サーバーを使っているプロジェクトでは起動時の待ち時間が目に見えて短くなります。templates リストは `@` で参照するまで取得されないため、普段 resources を使わない運用なら実質コストゼロです。

> **MCP stdio サーバーとは？**
> MCP (Model Context Protocol) のトランスポートの一つで、標準入出力でプロセス間通信する方式です。`npx` や `uvx` で起動するローカルコマンド型 MCP サーバーの大半はこれに該当します。対して SSE / HTTP 型は常駐する HTTP サーバーに接続する方式です。

### sandbox auto-allow の dangerous-path チェック修正

セキュリティ関連の修正です。sandbox 下で `Bash` ツールの auto-allow が有効な場合に、`rm` / `rmdir` の dangerous-path safety check がバイパスされていた不具合が直りました。

対象となる "dangerous path" は以下です。

- `/`（ルート）
- `$HOME`（ホームディレクトリ）
- その他のクリティカルなシステムディレクトリ

これまでも Claude Code 本体にはこのガードがありましたが、sandbox auto-allow 経路では prompt なしで通過する実装パスが存在していました。今回の修正で、auto-allow でもガードは外れず、必ずプロンプトが出るか拒否されるようになります。

sandbox + auto-allow でエージェントを長時間走らせる運用（夜間バッチ的な使い方）をしていた場合、このパッチを当てるまでは未確認の `rm` が通る可能性が僅かに残っていたことになります。`claude --version` で 2.1.116 以上になっているか確認しておくのが安全です。

### Bash ツールが `gh` の GitHub API rate limit を検知

Bash ツールが、`gh` コマンドが GitHub API のレート制限に当たったことを検知してヒントを出すようになりました。エージェントがリトライループに入る代わりに、バックオフなどの対処を選びやすくなります。

```bash
$ gh api repos/org/big-monorepo/issues?state=all --paginate
# ... 中略 ...
gh: API rate limit exceeded for user ID xxxxxxxx
```

このようなエラーが返ったとき、Claude Code 側で「rate limit に当たっている」とメタ情報として取り込まれ、次のアクションをリトライではなく待機や別アプローチに切り替える判断材料になります。対象は現状 `gh` コマンドで、一般的な HTTP 429 すべてを拾う機能ではない点に注意してください。

## 実用的な活用ポイント

### すぐに効く改善

- **`/doctor` が Claude の応答中でも開けるように**: 何か長めのタスクを投げている最中でも、別ウィンドウや別セッションに切り替えずに `/doctor` を打てます。トラブル調査時のターン待ちが消えます。
- **`/config` 検索がオプション値にもマッチ**: 設定名だけでなく値でも検索できるので、「vim」と打てば Editor mode の設定が出ます。「どのキーだっけ」を探す時間が減ります。
- **thinking スピナーのインライン進捗表示**: 「still thinking」「thinking more」「almost done thinking」が 1 行内で更新される形に変わり、画面のスクロール量が減ります。
- **VS Code / Cursor / Windsurf のフルスクリーンスクロール**: `/terminal-setup` を流すとエディタ側の scroll sensitivity も設定してくれます。スクロールのもたつきが消える環境があります。

### Plugin 使いへの地味に嬉しい変更

`/reload-plugins` とバックグラウンドでの plugin auto-update が、追加済みマーケットプレイスから欠けている依存関係を自動で取りにいくようになりました。これまでは plugin を差し替えたときに依存が足りず、手で `marketplace install` し直していたケースで、その手間がなくなります。

### Agent 主役運用への影響

Agent frontmatter の `hooks:` が、`--agent` で main-thread agent として走らせたときにも発火するようになりました。以前はサブエージェント経由でしか効かなかったので、`claude --agent my-agent` を日常的なエントリポイントにしている人にとっては挙動が揃います。

## 全変更点一覧

| カテゴリ | 変更内容 |
|---------|---------|
| Performance | `/resume` が 40MB 超の大規模セッションで最大 67% 高速化、dead-fork エントリの処理も効率化 |
| Performance | 複数 stdio MCP サーバー設定時の起動高速化（`resources/templates/list` を `@`-mention 時まで遅延） |
| Improvement | VS Code / Cursor / Windsurf でフルスクリーンスクロールを改善。`/terminal-setup` がエディタ側の scroll sensitivity も設定 |
| Improvement | thinking スピナーがインラインで進捗表示（"still thinking" / "thinking more" / "almost done thinking"） |
| Improvement | `/config` 検索がオプション値にもマッチ（例: "vim" で Editor mode 設定がヒット） |
| Improvement | `/doctor` が Claude の応答中でも開けるように |
| Improvement | `/reload-plugins` とバックグラウンド plugin auto-update で、追加済みマーケットプレイスから欠けている依存を自動インストール |
| Feature | Bash ツールが `gh` の GitHub API rate limit 到達を検知し、エージェントがバックオフできるようヒントを表示 |
| Improvement | Settings の Usage タブが 5 時間枠と週単位の使用量を即時表示、usage エンドポイントが rate-limited でも動作 |
| Feature | Agent frontmatter の `hooks:` が `--agent` 経由の main-thread agent 実行時にも発火 |
| Improvement | Slash command メニューで絞り込み結果 0 件のとき "No commands match" を表示（以前はメニューが消えていた） |
| Security | sandbox auto-allow が `rm` / `rmdir` の `/`, `$HOME`, クリティカルシステムディレクトリ向け dangerous-path チェックをバイパスしないよう修正 |
| Fix | Devanagari やその他 Indic scripts がターミナル UI で列幅ずれしていた問題を修正 |
| Fix | Kitty keyboard protocol 対応ターミナル（iTerm2, Ghostty, kitty, WezTerm, Windows Terminal）で Ctrl+- が undo にならなかった問題を修正 |
| Fix | Kitty keyboard protocol 利用時（Warp fullscreen, kitty, Ghostty, WezTerm）で Cmd+Left/Right が行頭/行末に飛ばなかった問題を修正 |
| Fix | `npx`, `bun run` などラッパー経由で Claude Code を起動したとき Ctrl+Z でターミナルがハングする問題を修正 |
| Fix | inline モードでのスクロールバック重複（ターミナルリサイズや大量出力で過去の会話履歴が繰り返されていた）を修正 |
| Fix | モーダル検索ダイアログが短い画面高でオーバーフローし、検索ボックスやキーボードヒントが隠れる問題を修正 |
| Fix | VS Code 統合ターミナルのスクロール中に空白セルが散ったり composer chrome が消えていた問題を修正 |
| Fix | リクエスト準備中に並列リクエストが完了した際、cache control TTL の順序起因で発生していた 400 エラーを修正 |
| Fix | `/branch` が 50MB 超のトランスクリプトを拒否していた問題を修正 |
| Fix | `/resume` が大規模セッションファイルでロードエラーを出さず空の会話を表示していた問題を修正 |
| Fix | `/plugin` の Installed タブで、Needs attention / Favorites にも載っている項目が二重表示されていた問題を修正 |
| Fix | ワークツリーに入るセッション中に `/update` と `/tui` が動かなくなる問題を修正 |

## まとめ

今回の焦点は「既存機能の重さを削る」方向です。`/resume` の 40MB+ 高速化と MCP stdio 起動の遅延ロード化は、日常のリズムにそのまま効きます。小さめのセッションしか扱わない環境ではあまり変化を感じませんが、長時間走らせた会話を翌日に持ち越す使い方をしているなら、`/resume` の待ち時間が明確に縮みます。

セキュリティ面では、sandbox auto-allow での dangerous-path バイパスが塞がれたのが地味に重要です。auto-allow を前提にエージェントを夜間走らせている構成なら、2.1.116 まで上げておくのが安全側の選択です。

機能追加はほぼなく、バグ修正が大半を占めるリリースなので、様子見する理由もあまりないタイプの更新です。
