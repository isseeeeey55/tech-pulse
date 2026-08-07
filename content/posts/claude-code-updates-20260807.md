---
title: "【Claude Code】v2.1.223 リリースノートまとめ"
date: 2026-08-07T08:01:20+09:00
draft: false
tags: ["claude-code", "github", "bash", "unicode", "teleport", "code-review", "modeloverrides", "managed-settings", "subagent"]
categories: ["Claude Code Updates"]
summary: "v2.1.223 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260807/header.png)

# Claude Code v2.1.223 リリース解説 — Bash 権限バイパス修正、Organization 単位のマーケットプレイス管理、1M コンテキスト制御の変更

## はじめに

Claude Code v2.1.223 がリリースされました。本バージョンでは、GitHub Organization 全体に対するマーケットプレイス管理機能の追加と、複数のセキュリティ脆弱性の修正が実施されています。特に、Bash 権限回避、タブや不可視 Unicode によるコマンド隠蔽、ワークフローサンドボックスからの動的コード実行といった重大な脆弱性が修正されており、セキュリティ面での大幅な強化が図られています。

## 注目アップデート深掘り

### GitHub Organization 単位でのマーケットプレイス管理

`strictKnownMarketplaces` および `blockedMarketplaces` の管理設定に、オーナーワイルドカードエントリ（`"owner/*"`）が追加されました。これにより、GitHub Organization 配下の全リポジトリを一括で許可またはブロックすることが可能になります。

従来は個別リポジトリごとに許可・ブロックを設定する必要がありましたが、本機能により組織単位での一元管理が可能となります。大規模な Organization において、信頼できる組織のリポジトリをまとめて許可する、あるいは特定組織のリポジトリを全面的にブロックするといった運用が簡潔に実現できます。

### Bash 権限回避の脆弱性修正

細工されたコマンドが権限チェックの一部を隠蔽できる Bash 権限回避の脆弱性が修正されました。また、タブや不可視 Unicode でパディングされたコマンドが承認ダイアログの一部を隠せる問題も同時に修正されています。

これらの脆弱性により、ユーザーが承認ダイアログで確認する内容と実際に実行されるコマンドが異なる可能性がありました。本修正により、タブや不可視 Unicode でパディングされたコマンドが承認ダイアログからコマンドの一部を隠せなくなっています。

### ワークフローサンドボックスの動的インポート実行の修正

ワークフロースクリプトが動的 `import()` を使用してワークフローサンドボックス外のコードを実行できる問題が修正されました。この脆弱性により、サンドボックスの隔離を回避してコードが実行される可能性がありましたが、本修正により動的 `import()` 経由のサンドボックス外実行が塞がれています。

## 実用的な活用ポイント

組織内で Claude Code を利用している場合、`managed-settings.json` に `"owner/*"` 形式のエントリを追加することで、信頼できる Organization のマーケットプレイスリポジトリを一括管理できます。

クラウドセッションからローカル環境への遷移には、新たに追加された `/teleport` ヒントが表示されるようになりました。`claude --teleport <session id>` コマンドを使用してセッションを継続できます。

`/review` コマンドは `/code-review` のエイリアスとなり、現在の diff または PR をレビューします。`/code-review ultra` で詳細なクラウドレビューを実行できます。また、effort level を省略した場合、前回指定したレベルが再利用されるようになりました。

`CLAUDE_CODE_DISABLE_1M_CONTEXT` の挙動が変更され、1M コンテキストウィンドウを持つすべての Claude モデルが 200K に自動圧縮されるようになりました。認識できないモデル ID のセッションも、想定されるコンテキストウィンドウ内に維持されます。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Owner wildcard entries in marketplace settings | `strictKnownMarketplaces` および `blockedMarketplaces` に `"owner/*"` 形式のエントリを追加し、GitHub Organization 全体のリポジトリを一括管理可能に |
| Feature | Subagent model restriction warning | Workflow agents、forked skills、slash commands、resumed background agents で要求された subagent モデルが制限されている場合に警告を表示 |
| Feature | `/teleport` hint in cloud sessions | クラウドセッションで `claude --teleport <session id>` を使ってローカルで継続する方法をヒント表示 |
| Fix | Bash permission bypass | 細工されたコマンドが権限チェックの一部を隠蔽できる脆弱性を修正 |
| Fix | Permission prompt Unicode hiding | タブや不可視 Unicode でパディングされたコマンドが承認ダイアログの一部を隠せる問題を修正 |
| Fix | Workflow dynamic import sandbox escape | ワークフロースクリプトが動的 `import()` でサンドボックス外のコードを実行できる問題を修正 |
| Fix | `bypassPermissions` policy gap | Agent definition の `bypassPermissions` モードが組織のバイパス無効化ポリシーを無視していた問題を修正 |
| Fix | Session resume after `/cd` | セッション途中で `/cd` した後にセッションを再開すると空になる問題を修正 |
| Fix | Gateway model discovery | `vertex_ai/claude-*` や `bedrock/anthropic.claude-*` などのプロバイダー接頭辞付き ID で登録された Claude モデルが隠されていた問題を修正 |
| Fix | `modelOverrides` keys handling | Anthropic モデル ID でない `modelOverrides` キーがセッションの正規モデル ID として扱われていた問題を修正。不明なキーは文書通り無視されるように |
| Fix | Managed settings env block | サーバー配信設定がローカル `managed-settings.json` または MDM プロファイルの env ブロックを無効化していた問題を修正。管理者 env はキー単位でマージされるように |
| Fix | Sandboxed command start on Linux | `sandbox.filesystem.denyWrite` が作業ディレクトリをカバーする場合に Linux でサンドボックスコマンドが起動失敗する問題を修正 |
| Fix | Forked background agent resume stuck | Fork の親プロンプト再構築が失敗した際に forked background agents が「already resuming」で固まる問題を修正 |
| Fix | Resumed session malformed diagnostics | 履歴に malformed diagnostics attachment が含まれる場合にセッション再開が毎ターン失敗する、または対話アプリが無応答エラー画面に留まる問題を修正 |
| Fix | `git push` output parsing hang | 異常な `git push` 出力をパースする際の稀なハングを修正 |
| Change | `CLAUDE_CODE_DISABLE_1M_CONTEXT` behavior | 固定リストではなく 1M ネイティブウィンドウを持つすべての Claude モデルを自動圧縮で 200K に保持。200K 保持されていない場合は起動時に警告表示 |
| Change | Auto-compact for unrecognized models | 認識できないモデル ID のセッションを想定コンテキストウィンドウ内に維持。以前の動作に戻すには `CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT=1` を設定 |
| Change | `/review` alias and `/code-review` の変更 | `/review` を `/code-review` のエイリアスに変更。現在の diff または PR をレビュー（`/code-review <level> <pr#>`）。`/code-review ultra` で詳細なクラウドレビューが可能 |
| Change | `/code-review` level reuse | Effort level を省略した場合、前回指定したレベルを再利用。`/code-review high` などで変更可能 |

## まとめ

v2.1.223 は、セキュリティ強化とエンタープライズ管理機能の改善を中心としたリリースです。Bash 権限回避、Unicode によるコマンド隠蔽、ワークフローサンドボックスからの動的コード実行など、複数の重大な脆弱性が修正されており、安全性が大幅に向上しています。

Organization 単位でのマーケットプレイス管理機能は、大規模な組織での運用効率を高めます。また、`/teleport` によるクラウド・ローカル間のセッション遷移や、`/code-review` の使い勝手向上など、開発者体験の改善も含まれています。セッション再開時の問題やモデル検出の修正により、全体的な信頼性も向上しています。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)