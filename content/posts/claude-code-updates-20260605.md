---
title: "【Claude Code】v2.1.163 リリースノートまとめ"
date: 2026-06-05T08:01:03+09:00
draft: false
tags: ["claude-code", "hooks", "skills", "bash", "edr", "bazel", "onedrive", "bedrock", "vertex", "windows"]
categories: ["Claude Code Updates"]
summary: "v2.1.163 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260605/header.png)

# Claude Code v2.1.163 リリース情報

## はじめに

2026年6月5日、Claude Code v2.1.163 がリリースされました。今回のリリースでは、バージョン範囲を強制する管理設定（`requiredMinimumVersion`/`requiredMaximumVersion`）の追加、`/plugin list` コマンドの実装、Hooks 機能の拡張、Skills の `\$` エスケープ構文対応などの機能追加が行われています。また、Bash 実行時のバグ修正（EDR/Bazel 対応、Windows OneDrive 互換性）、CI 環境での Bedrock/Vertex/Foundry 認証バグの修正、バックグラウンドセッション管理の安定化といった品質改善も含まれています。

## 注目アップデート深掘り

### プラグイン一覧表示コマンドとバージョン範囲の強制

今回のリリースでは、プラグイン管理とバージョン統制の機能が追加されました。`/plugin list` コマンド（`--enabled`/`--disabled` フィルタ対応）により、インストール済みのプラグインを一覧確認できます。また、`requiredMinimumVersion` / `requiredMaximumVersion` という管理設定（managed settings）が追加され、Claude Code のバージョンが許可された範囲外の場合は起動を拒否し、承認済みバージョンへ誘導します。組織で利用バージョンを統制したい開発チームにとって有用です。

### Hooks機能の拡張とSkillsの$エスケープ構文対応

Hooks 機能が拡張され、Stop / SubagentStop フックが `hookSpecificOutput.additionalContext` を返して、フックエラー扱いにせず Claude にフィードバックを与えたままターンを継続できるようになりました。さらに Skills では、コマンド本体で数字の前にリテラルの `$` を記述するための `\$` エスケープ構文がサポートされました。

> **Note:** Hooksは特定のイベント発生時に任意の処理を実行する仕組み、Skillsはエージェントが利用可能な定義済み操作です。

## 実用的な活用ポイント

新しいプラグイン一覧表示コマンドを活用することで、現在の環境にどのプラグインが導入されているかを素早く確認できます。バージョン管理機能と組み合わせることで、チーム内でのプラグイン構成の統一や、トラブルシューティング時のバージョン確認が容易になります。

Bash実行に関するバグ修正は、EDRソフトウェアやBazelビルドツールを使用している環境、またはWindows環境でOneDriveと連携している場合の安定性を大幅に向上させます。これらの環境で以前にエラーが発生していた場合は、このバージョンへのアップデートが推奨されます。

また、`CI=true` かつ Anthropic API キー未設定の状況で `claude -p` が Bedrock/Vertex/Foundry 利用時に「ANTHROPIC_API_KEY required」で誤って失敗する問題が修正され、CI 環境での実行が安定します。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | バージョン範囲の強制（managed settings） | `requiredMinimumVersion`/`requiredMaximumVersion` で許可範囲外なら起動拒否 |
| Feature | `/plugin list` コマンド | インストール済みプラグインを一覧表示（`--enabled`/`--disabled` フィルタ対応） |
| Feature | Hooks機能の拡張 | Stop/SubagentStop フックが `additionalContext` を返してターン継続可能に |
| Feature | Skills の `\$` エスケープ構文 | コマンド本体で数字の前にリテラル `$` を置く `\$` に対応 |
| Fix | Bash実行時のEDR/Bazel対応 | EDRソフトウェアやBazelツール使用時の互換性問題を修正 |
| Fix | Windows OneDrive互換性 | Windows環境でのOneDrive連携時の問題を修正 |
| Fix | CI での Bedrock/Vertex 認証 | `CI=true`・APIキー未設定時に `claude -p` が失敗する問題を修正 |
| Improvement | バックグラウンドセッション管理の安定化 | バックグラウンドで動作するセッションの管理処理を安定化 |

## まとめ

v2.1.163は、機能追加と品質改善のバランスが取れたリリースとなっています。プラグイン管理やバージョン管理といった運用面での利便性向上に加え、Hooks/Skillsの機能拡張により、より高度な自動化が可能になりました。また、Bash実行やAPI認証に関する複数のバグ修正により、特定の環境下での安定性が大幅に向上しています。EDR/Bazel/OneDriveを使用している環境、またはBedrock/Vertexを利用している場合は、早期のアップデートが推奨されます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)