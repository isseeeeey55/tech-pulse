---
title: "【Claude Code】v2.1.163 リリースノートまとめ"
date: 2026-06-05T08:01:03+09:00
draft: true
tags: ["claude-code", "hooks", "skills", "bash", "edr", "bazel", "onedrive", "bedrock", "vertex", "windows"]
categories: ["Claude Code Updates"]
summary: "v2.1.163 のClaude Codeリリースノートまとめ"
---

# Claude Code v2.1.163 リリース情報

## はじめに

2026年6月5日、Claude Code v2.1.163 がリリースされました。今回のリリースでは、バージョン管理機能の追加、プラグイン一覧表示コマンドの実装、Hooks機能の拡張、Skills の$エスケープ構文対応などの機能追加が行われています。また、Bash実行時のバグ修正（EDR/Bazel対応、Windows OneDrive互換性）、Bedrock/Vertex APIキー処理の改善、バックグラウンドセッション管理の安定化といった品質改善も含まれています。

## 注目アップデート深掘り

### プラグイン一覧表示コマンドとバージョン管理機能

今回のリリースでは、プラグイン管理の利便性を向上させる機能が追加されました。プラグイン一覧表示コマンドにより、インストール済みのプラグインを簡単に確認できるようになります。また、バージョン管理機能の追加により、Claude Code本体やプラグインのバージョン情報を明示的に扱えるようになりました。これらの機能は、複数のプラグインを利用する環境や、特定バージョンでの動作を保証したい開発チームにとって有用です。

### Hooks機能の拡張とSkillsの$エスケープ構文対応

Hooks機能が拡張され、より柔軟なワークフローのカスタマイズが可能になりました。さらに、Skills機能において$エスケープ構文が新たにサポートされました。これにより、シェル変数やテンプレート記法を含むコマンドをSkills内で正しく記述できるようになり、より複雑な自動化タスクの定義が可能になります。

> **Note:** Hooksは特定のイベント発生時に任意の処理を実行する仕組み、Skillsはエージェントが利用可能な定義済み操作です。

## 実用的な活用ポイント

新しいプラグイン一覧表示コマンドを活用することで、現在の環境にどのプラグインが導入されているかを素早く確認できます。バージョン管理機能と組み合わせることで、チーム内でのプラグイン構成の統一や、トラブルシューティング時のバージョン確認が容易になります。

Bash実行に関するバグ修正は、EDRソフトウェアやBazelビルドツールを使用している環境、またはWindows環境でOneDriveと連携している場合の安定性を大幅に向上させます。これらの環境で以前にエラーが発生していた場合は、このバージョンへのアップデートが推奨されます。

Bedrock/Vertex APIキー処理の改善により、AWS BedrockやGoogle Cloud Vertexを利用している場合の認証処理がより堅牢になります。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | バージョン管理機能の追加 | Claude Codeのバージョン情報を明示的に管理できるように |
| Feature | プラグイン一覧表示コマンド | インストール済みプラグインを確認するコマンドを追加 |
| Feature | Hooks機能の拡張 | Hooksの機能が拡張され、より柔軟なカスタマイズが可能に |
| Feature | Skillsの$エスケープ構文対応 | Skills内でシェル変数などのエスケープ処理に対応 |
| Fix | Bash実行時のEDR/Bazel対応 | EDRソフトウェアやBazelツール使用時の互換性問題を修正 |
| Fix | Windows OneDrive互換性 | Windows環境でのOneDrive連携時の問題を修正 |
| Improvement | Bedrock/Vertex APIキー処理の改善 | AWS BedrockおよびGoogle Cloud VertexのAPIキー処理を改善 |
| Improvement | バックグラウンドセッション管理の安定化 | バックグラウンドで動作するセッションの管理処理を安定化 |

## まとめ

v2.1.163は、機能追加と品質改善のバランスが取れたリリースとなっています。プラグイン管理やバージョン管理といった運用面での利便性向上に加え、Hooks/Skillsの機能拡張により、より高度な自動化が可能になりました。また、Bash実行やAPI認証に関する複数のバグ修正により、特定の環境下での安定性が大幅に向上しています。EDR/Bazel/OneDriveを使用している環境、またはBedrock/Vertexを利用している場合は、早期のアップデートが推奨されます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)