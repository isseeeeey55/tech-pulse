---
title: "【Claude Code】v2.1.141 リリースノートまとめ"
date: 2026-05-15T08:01:02+09:00
draft: false
tags: ["claude-code", "hooks", "plugins", "agent", "windows"]
categories: ["Claude Code Updates"]
summary: "v2.1.141 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260515/header.png)

# Claude Code v2.1.141 リリース情報

## はじめに

Claude Code v2.1.141 が 2026年5月13日（UTC）にリリースされました。フック・プラグイン・エージェント運用まわりに新しい設定ポイントが複数追加され、あわせて Windows・MCP・バックグラウンドエージェントまわりのバグ修正が多数入った、機能追加と品質改善のバランスが取れたリリースです。本記事では、4 つの新機能（`terminalSequence` フック出力、プラグインの HTTPS クローン、`ANTHROPIC_WORKSPACE_ID`、「Summarize up to here」）と、運用に効く改善・修正を中心に取り上げます。

## 注目アップデート深掘り

### `terminalSequence` — フックからデスクトップ通知を出せるように

フックの JSON 出力に `terminalSequence` フィールドが追加されました。これにより、制御端末を持たないフックでも、デスクトップ通知・ウィンドウタイトルの変更・ベル音を発行できます。

従来、フックから通知系の端末シーケンスを出すには制御端末が必要で、バックグラウンドで実行されるフックやデーモン経由のフックでは通知を出せませんでした。`terminalSequence` を使えば、フックが「出したい通知」を JSON で宣言し、Claude Code 側がそれを端末へ反映します。長時間タスクの完了通知やイベント通知をフックで組んでいる場合に、通知が確実に届くようになります。

### 「Summarize up to here」— Rewind メニューからコンテキストを圧縮

Rewind メニューに「Summarize up to here」が追加されました。直近のターンはそのまま残しつつ、それより前のコンテキストだけを要約・圧縮できます。

長いセッションで履歴が膨らんだとき、これまでは全体をまとめて圧縮するか、セッションを切り直すしかありませんでした。この機能では「ここまで」を指定して前半だけを要約に置き換えられるため、直近の作業文脈を失わずにトークン使用量を抑えられます。

## 実用的な活用ポイント

今回のリリースで追加された設定ポイントは、いずれも CI／エンタープライズ環境での運用を意識したものです。

- **プラグインソースの HTTPS クローン**: 環境変数 `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` を設定すると、GitHub 上のプラグインソースを SSH ではなく HTTPS でクローンします。GitHub の SSH 鍵を持たない CI 環境やコンテナで、プラグインの取得に失敗しなくなります（対象はプラグインソースの取得で、通常のリポジトリ操作には影響しません）。
- **ワークロード ID フェデレーションのワークスペース指定**: 新しい環境変数 `ANTHROPIC_WORKSPACE_ID` で、ワークロード ID フェデレーションが発行するトークンを特定のワークスペースにスコープできます。フェデレーションルールが複数のワークスペースをカバーしている場合に、どのワークスペースを使うかを明示できるようになりました。
- **背景エージェントの権限モード保持**: `/bg` や `←←` で起動したバックグラウンドエージェントが、これまで既定モードに戻っていたのを、起動時の権限モードをそのまま引き継ぐようになりました。
- **Windows のデーモン診断**: `claude daemon status` と `/doctor` が、Windows でデーモンのパイプキーファイルがロック／読み取り不可のときに不可解なエラーで落ちていた問題を修正。原因となっているエラーがそのまま表示されるようになりました。

このほか、MCP サーバー（403／401 の扱い、`.mcp.json` 由来のサーバー表示、リモート MCP の再接続）やバックグラウンドエージェント表示まわりの修正が多数入っています。

## 主な変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | `terminalSequence` フック出力 | フックの JSON 出力に `terminalSequence` を追加。制御端末がなくてもデスクトップ通知・ウィンドウタイトル・ベルを発行可能に |
| Feature | プラグインの HTTPS クローン | `CLAUDE_CODE_PLUGIN_PREFER_HTTPS` で GitHub プラグインソースを SSH ではなく HTTPS でクローン。SSH 鍵のない環境向け |
| Feature | `ANTHROPIC_WORKSPACE_ID` | ワークロード ID フェデレーションで発行するトークンを特定ワークスペースにスコープする環境変数を追加 |
| Feature | Summarize up to here | Rewind メニューに追加。直近ターンを残しつつ、それ以前のコンテキストを要約・圧縮 |
| Improvement | 背景エージェントの権限モード保持 | `/bg`・`←←` で起動した背景エージェントが既定モードに戻らず、起動時の権限モードを維持 |
| Fix | Windows デーモン診断 | `claude daemon status`・`/doctor` が Windows でパイプキーファイルのロック時に不可解に落ちる問題を修正。原因エラーを表示 |

## まとめ

v2.1.141 は、フック（`terminalSequence`）・プラグイン（HTTPS クローン）・ワークロード ID フェデレーション（`ANTHROPIC_WORKSPACE_ID`）といった「組織で配布・運用するときに効く」設定ポイントを追加しつつ、Windows・MCP・バックグラウンドエージェントまわりのバグ修正を多数まとめたリリースです。新機能はいずれもオプトインの設定で、既存のワークフローを壊さずに必要な環境だけ有効化できます。CI／エンタープライズ環境で Claude Code を運用しているなら、HTTPS クローンとワークスペース指定は確認しておく価値があります。

- 公式リリースノート: <https://github.com/anthropics/claude-code/releases/tag/v2.1.141>
- 公開日時: 2026-05-13 23:19 UTC

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
