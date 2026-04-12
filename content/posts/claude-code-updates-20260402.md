---
title: "【Claude Code】v2.1.89 リリースノートまとめ"
date: 2026-04-02T08:01:09+09:00
draft: false
tags: ["claude-code", "permission-hooks", "lsp-server", "memory-leak", "headless-session"]
categories: ["Claude Code Updates"]
summary: "v2.1.89 のClaude Codeリリースノートまとめ。パーミッションフック拡張による動的アクセス制御、LSPサーバー自動復旧、ヘッドレスセッション制御強化、メモリリーク修正など7件"
---

![](/images/claude-code-updates-20260402/header.png)

## はじめに

Claude Code v2.1.89がリリースされました。パーミッションフックの拡張による動的アクセス制御、LSPサーバーの自動復旧機能が主な追加です。メモリリーク修正や異常系処理の強化など、安定性の改善も含まれています。

## 注目アップデート深掘り

### パーミッションフックの拡張

従来の静的なアクセス制御に加え、実行時の状況に応じた動的な許可判定が可能になりました。

```javascript
hooks.register('permission-check', async (context) => {
  const { resource, action, user, timestamp } = context;

  // 本番環境は業務時間のみアクセス可
  if (resource.environment === 'production') {
    const hour = new Date(timestamp).getHours();
    if (hour < 9 || hour > 18) {
      return { allowed: false, reason: 'Production access outside business hours' };
    }
  }

  // criticalタグ付きリソースの削除を禁止
  if (action === 'terminate' && resource.tags?.critical === 'true') {
    return { allowed: false, reason: 'Critical resource termination requires manual approval' };
  }

  return { allowed: true };
});
```

外部APIとの連携も可能なので、SlackやPagerDutyのオンコール状況に基づいた緊急時アクセス許可なども実装できます。

### LSPサーバー自動復旧

LSPサーバーがクラッシュした際に自動で再起動するようになりました。大規模なTerraformプロジェクトなどでLSPサーバーがメモリ不足でクラッシュするケースがありましたが、手動再起動が不要になります。

v2.1.88以前：
```
[ERROR] Terraform LSP server crashed
[INFO] Code analysis stopped
→ 手動で claude-code lsp restart terraform が必要
```

v2.1.89以降：
```
[ERROR] Terraform LSP server crashed
[INFO] Attempting automatic recovery (1/3)
[INFO] LSP server successfully restarted
[INFO] Code analysis resumed
```

CIパイプラインでのコード品質チェックがより安定します。

## 実用的な活用ポイント

パーミッションフックは、まずは開発環境で時間ベースの制御から試すのがよいでしょう。いきなり複雑なポリシーを入れるよりも、段階的に制御を追加していく方が運用しやすいです。

メモリリーク修正は、大規模なJSONデータを扱う運用スクリプトや、長時間稼働するモニタリングツールで効果を感じられます。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | パーミッションフック拡張 | 動的なアクセス制御ロジックの実装が可能に |
| Feature | ヘッドレスセッション制御 | 自動モードでのコマンド拒否時通知機能を追加 |
| Improvement | 環境変数サポート拡張 | CLIツールの安定性と使用感を向上 |
| Improvement | LSPサーバー自動復旧 | サーバークラッシュ時の自動復旧機能 |
| Fix | メモリリーク修正 | 大規模JSONデータ処理時のメモリ使用量を改善 |
| Fix | パフォーマンス改善 | 長時間稼働ツールの安定性を向上 |
| Fix | 異常系処理強化 | エラー検知と対応の効率化 |

## まとめ

v2.1.89はパーミッションフック拡張とLSPサーバー自動復旧が2つの柱です。前者は複雑化するクラウド環境でのアクセス制御、後者はIaCを扱う開発者の作業中断削減に効きます。メモリリーク修正も含め、安定性寄りのリリースです。
