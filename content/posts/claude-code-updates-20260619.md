---
title: "【Claude Code】v2.1.183 リリースノートまとめ"
date: 2026-06-19T11:01:00+09:00
draft: false
tags: ["claude-code", "auto-mode", "config", "mcp", "tmux", "subagent"]
categories: ["Claude Code Updates"]
summary: "v2.1.183 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260619/header.png)

# Claude Code v2.1.183 リリース情報

## はじめに

**Claude Code v2.1.183** がリリースされました。auto mode における破壊的コマンドのブロック強化を目玉に、非推奨モデルの警告表示や `/config` の使い勝手改善といった機能の追加・改善に加え、11件の不具合修正を含むリリースです。

## 注目アップデート深掘り

### auto mode の安全性強化 — 破壊的な git / IaC コマンドのブロック

今回のリリースで最も重要な変更が、auto mode における安全性の強化です。ユーザーがローカルの作業内容を破棄する指示を出していない場合、破壊的な git コマンド（`git reset --hard`、`git checkout -- .`、`git clean -fd`、`git stash drop`）がブロックされるようになりました。また、`git commit --amend` は、対象のコミットがそのセッション中にエージェントによって作成されたものでない場合にブロックされます。

さらに IaC ツールに対しても、`terraform destroy` / `pulumi destroy` / `cdk destroy` は、ユーザーが特定のスタックに対して明示的に依頼した場合を除いてブロックされるようになりました。

auto mode はエージェントが自律的に操作を進めるモードであるため、意図しない破壊的操作が実行されるリスクが懸念点でした。今回の変更により、明示的な指示がない限りこれらのコマンドが実行されなくなり、誤操作による作業内容やインフラの損失を防げます。

### 非推奨モデル・自動更新モデルの警告表示

リクエストしたモデルが非推奨（deprecated）になっている、または自動的に新しいモデルへ更新された場合に、警告が表示されるようになりました。この警告は print モード（`-p`）では stderr に出力され、さらにエージェントの frontmatter で指定されたモデルもカバーするようになっています。

モデルの指定が古くなっていることに気づかないまま利用を続けるケースを防ぎ、意図したモデルで実行できているかを把握しやすくなります。

## 実用的な活用ポイント

設定まわりでは、`/config key=value` のショートハンドキー一覧を表示する `/config --help` が追加されました。あわせて `/config` のトグル挙動が変更され、Enter と Space のどちらでも選択中の設定を変更でき、Esc はこれまでの「変更を取り消して閉じる」から「保存して閉じる」に変わりました。

また、コミットや PR に付与される claude.ai のセッションリンクを省略するための `attribution.sessionUrl` 設定が追加されました。Web およびリモートコントロールのセッションが対象です。ロゴ下に表示されていた起動時の "setup issues" 行は削除され、設定上の問題は `/doctor` または `--debug` で確認する形に変わっています。

不具合修正も多数含まれます。サブエージェントでの WebSearch が空の結果を返す問題、Windows Terminal での深いサブエージェント負荷時のフルスクリーン TUI 崩れ、tmux teammate ペインの起動失敗、認証が必要な MCP サーバーが headless / SDK モードで auth-stub ツールをモデルに露出してしまう問題などが修正されています。

## 全変更点一覧

| カテゴリ | 内容 |
| --- | --- |
| Improvement | auto mode の安全性強化：未指示時の破壊的 git コマンド（`git reset --hard` など）と `terraform destroy` / `pulumi destroy` / `cdk destroy`、エージェント作成外コミットへの `git commit --amend` をブロック |
| Feature | 非推奨・自動更新されたモデルの警告を print モード（`-p`）と agent frontmatter で表示 |
| Feature | コミット / PR から claude.ai セッションリンクを省く `attribution.sessionUrl` 設定を追加 |
| Feature | `/config key=value` のショートハンドキー一覧を表示する `/config --help` を追加 |
| Improvement | `/config` のトグル挙動を変更：Enter / Space で変更、Esc は保存して閉じる |
| Change | ロゴ下の起動時 "setup issues" 行を削除（`/doctor` または `--debug` で確認） |
| Fix | サブエージェント生成・セッションタイトル生成時の `thinking.disabled.display: Extra inputs are not permitted` 400 エラーを修正 |
| Fix | サブエージェントで WebSearch が空の結果を返す問題を修正 |
| Fix | ネイティブカーソル有効時の vim モードで履歴移動後にターミナルカーソルがプロンプト上部に取り残される問題を修正 |
| Fix | Windows Terminal の深くネストしたサブエージェント高負荷時のフルスクリーン TUI 崩れ（statusline の画面中央表示・スピナー行の重複・テキスト結合）を修正 |
| Fix | モデルが thinking ブロックのみを返した際にターン出力が表示されず無音で完了する問題を修正（1回だけ再プロンプト） |
| Fix | 複数プラグイン有効時にユーザーレベルのスキルがスラッシュコマンド補完で重複表示される問題を修正 |
| Fix | 認証が必要な MCP サーバーが headless / SDK モードで auth-stub ツールをモデルに露出する問題を修正 |
| Fix | シェルの rc ファイル初期化が遅い場合に tmux teammate ペインの起動が失敗し、エージェント生成中に入力した文字が leader プロンプトではなく新しい tmux ペインへ漏れる問題を修正 |
| Fix | teammate が開始したバックグラウンドタスクが、その teammate のターン終了時に kill される問題を修正 |
| Fix | スケジュールタスクおよび webhook トリガーの配信がキーボード入力として扱われていた問題を修正（タスク通知として分類され、auto mode で保留中のアクションを承認したりセッションタイトルを設定したりしなくなった） |
| Fix | フォーカスモードで各応答の下に "Ran N PostToolUse hooks" のタイミング行が表示される問題を修正 |

## まとめ

v2.1.183 は、auto mode の安全性強化を中心に、モデル非推奨の警告や `/config` の改善といった実用的な機能追加と、多数の不具合修正をまとめたリリースです。特に auto mode で破壊的な git / IaC コマンドが既定でブロックされるようになった点は、エージェントによる自律操作を安心して使ううえで重要な変更です。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
