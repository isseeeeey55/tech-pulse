---
title: "【Claude Code】v2.1.152 リリースノートまとめ"
date: 2026-05-28T08:01:08+09:00
draft: false
tags: ["claude-code", "code-review", "skills", "sessionstart", "hooks", "fallback-model", "usage", "vim", "workflow", "simplify"]
categories: ["Claude Code Updates"]
summary: "v2.1.152 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260528/header.png)

# Claude Code v2.1.152 リリース情報

## はじめに

Claude Code v2.1.152 がリリースされました。今回のアップデートでは、コードレビュー機能の自動修正適用、スキル管理の強化（ホットリロード対応）、フォールバックモデル機能の改善など、開発効率と運用の堅牢性を高める機能が追加されています。特にセッション中のスキル再スキャンや、プライマリモデルが見つからない場合のフォールバック動作により、ワークフローを止めにくくする改善が入っています。

## 注目アップデート深掘り

### `/code-review --fix` による自動修正適用

コードレビュー機能に `--fix` フラグが追加され、レビュー後に見つかった指摘を working tree へ適用できるようになりました。reuse、simplification、efficiency に関する提案を反映しやすくなり、`/simplify` も `/code-review --fix` を呼び出す形に変わっています。

Terraform や CloudFormation などの IaC ファイルのレビューにおいて、よくある改善パターン（リソース命名規則、タグの統一、冗長な設定の削減など）を即座に適用可能になり、レビューサイクルが大幅に短縮されます。

### スキルのホットリロードとセッション起動フック

スキル管理が強化され、`/reload-skills` でセッション中にスキルディレクトリを再スキャンできるようになりました。また、`SessionStart` フックが `reloadSkills: true` を返すことで、フックでインストールしたスキルを同一セッション内で利用可能になります。

これにより、AWS CLI ラッパーやログ解析スキルなどを環境に応じて動的に切り替えやすくなり、開発環境・本番環境で異なるスキルセットをセッション開始時に準備するといった運用が取りやすくなります。スキルの更新時にセッションを再起動する必要が減り、開発効率が向上します。

> **Note:** Skills は Claude Code のカスタム機能拡張の仕組みで、Hooks はライフサイクルイベント（セッション開始など）でスクリプトを実行する機能です。

### `--fallback-model` によるモデル切り替え自動化

フォールバックモデル機能が改善され、プライマリモデルが見つからない場合に、設定済みの `--fallback-model` へセッションの残り時間で切り替わるようになりました。これまではリクエストごとに失敗し続ける可能性がありましたが、今回の変更で復旧動作がより明確になっています。

利用モデル名の変更、提供側の一時的な不整合、組織設定の切り替えなどでプライマリモデルが解決できない場合に、作業を継続しやすくなります。

## 実用的な活用ポイント

今回のアップデートは、インフラ運用やコードレビューの自動化シナリオで特に効果を発揮します。

- **IaC の品質向上**: `/code-review --fix` と `/simplify` を組み合わせることで、Terraform/CloudFormation ファイルや GitHub Actions ワークフロー定義の可読性・保守性を一括改善できます
- **障害調査の効率化**: `/usage` コマンドの改善により、大容量ログファイルをメモリ効率的にスキャン可能になり、メモリリークやログローテーション問題の分析が高速化します
- **Workflow 可視化の改善**: インラインの進捗表示が簡素化され、ライブの agent 数はプロンプト下の永続ステータス行に集約されます
- **運用の堅牢性向上**: フォールバックモデル機能により、モデルの一時的な利用不可状態でも作業を継続でき、運用の可用性が向上します

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Feature | `/code-review --fix` 自動修正適用 | コードレビューで提案された修正を自動適用可能に |
| Feature | `disallowed-tools` frontmatter | スキルや slash command の有効中にモデルから一部ツールを外せるように |
| Feature | スキルのホットリロード対応 | セッション中にスキルを再スキャン可能 |
| Feature | SessionStart フック | セッション起動時に業務用スキルを自動ロード |
| Feature | MessageDisplay hook event | 表示時の assistant メッセージを hook で変換または非表示にできるように |
| Feature | `--fallback-model` 追加 | モデル利用不可時に自動的に別モデルへ切り替え |
| Improvement | `/usage` の大容量ログファイル対応 | メモリ効率的にログをスキャン |
| Improvement | Vim モード改善 | （詳細はリリースノート参照） |
| Improvement | Workflow 表示の改善 | エージェント並列実行状況の表示がシンプルで追跡しやすく |
| Improvement | `/simplify` コマンド強化 | Bash/Python スクリプトの可読性・保守性を一括改善 |

## まとめ

v2.1.152 は、自動修正適用・スキル管理強化・フォールバックモデルという 3 つの柱で、開発効率と運用の堅牢性を高めるリリースとなっています。特にインフラ運用やコードレビュー自動化において、手作業削減と継続性確保の両面で効果が期待できます。

セッション中断なしでスキルを更新できる仕組みや、モデル切り替えの自動化により、よりスムーズな開発・運用フローが実現可能になりました。IaC の品質向上や障害調査の効率化など、SRE 業務での活用シーンが一層広がります。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
