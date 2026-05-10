---
title: "【Claude Code】v2.1.138・v2.1.137 リリースノートまとめ"
date: 2026-05-10T08:01:22+09:00
draft: false
tags: ["claude-code", "vscode", "windows"]
categories: ["Claude Code Updates"]
summary: "v2.1.138・v2.1.137 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260510/header.png)

# Claude Code v2.1.138 & v2.1.137 リリース情報

## はじめに

2026年5月9日、Claude Code の v2.1.137（2026-05-09 00:11 UTC）と v2.1.138（2026-05-09 06:33 UTC）が相次いでリリースされました。今回はいずれも修正・内部改善のみで、新機能の追加はありません。

公式リリースノートに記載されている変更点は次の 2 行のみです。

- **v2.1.137**: `[VSCode] Fixed extension failing to activate on Windows`
- **v2.1.138**: `Internal fixes`

このため本記事では、唯一具体的に内容が公開されている v2.1.137 の Windows 向け修正に絞って解説します。v2.1.138 については公式に詳細が公開されておらず、内容を推測して記載することは行いません。

## 注目アップデート深掘り

### Windows での VSCode 拡張起動問題の修正（v2.1.137）

v2.1.137 では、Windows 環境で Claude Code の VSCode 拡張が「activate」段階で失敗していた不具合が修正されました。リリースノート上の記載は次の 1 行のみです。

> [VSCode] Fixed extension failing to activate on Windows

**影響範囲**

VSCode 拡張の `activate` 失敗は、拡張機能のエントリポイントが起動しない状態を指し、起動するとコマンドパレットや UI から Claude Code を呼び出せない、もしくは Output パネルに activation エラーが表示される、といった症状が出ます。Windows のみで再現していた事象のため、macOS / Linux のユーザーには影響しません。

**該当しそうなユーザー**

- VSCode（または Cursor などの VSCode 派生 IDE）で Claude Code 拡張を Windows 上で利用しているユーザー
- 直近のバージョンで「Claude Code が VSCode 上で起動しない／反応しない」と感じていたユーザー

該当する場合は v2.1.137 以降に更新することで解消が見込めます。

### v2.1.138 の Internal fixes について

v2.1.138 のリリースノートは `Internal fixes` の 1 行のみで、対象機能・OS・回帰の有無といった具体情報は公開されていません。本記事では推測ベースの解説は行わず、**「内部修正のロールアップで、目に見える挙動変更は宣言されていない」** という事実のみ記録します。

実環境で何らかの挙動変化や副作用に気づいた場合は、公式の GitHub Releases や公式ドキュメントの更新を併せて確認することをおすすめします。

## 実用的な活用ポイント

今回のリリースは「機能を増やすアップデート」ではなく、**Windows 環境での既知の障害を取り除くアップデート**です。

- Windows + VSCode 環境で Claude Code がうまく起動しなかった場合、まずは v2.1.137 以降への更新を試す価値があります。
- macOS / Linux のみで運用している場合、急いでアップデートする理由は今回のリリースノートからは読み取れません。次回の機能リリースまで現行バージョンで利用を継続しても問題ありません。
- v2.1.138 は内部修正のみで、運用ワークフローの見直しを必要とする変更は告知されていません。

## 全変更点一覧（公式リリースノート準拠）

| バージョン | カテゴリ | 内容 |
|-----------|---------|------|
| v2.1.137 | Fix | [VSCode] Windows で拡張機能が activate に失敗する問題を修正 |
| v2.1.138 | Internal | Internal fixes（公式リリースノートに詳細記載なし） |

## まとめ

v2.1.137・v2.1.138 はいずれもメンテナンスリリースで、機能追加はありません。公開されている具体的な変更点は **Windows での VSCode 拡張 activate 失敗の修正** のみです。Windows 環境でこれまで Claude Code 拡張がうまく起動しなかった場合は、このタイミングでの更新が有効です。それ以外の環境では、急いで適用する必要のある変更は今回のリリースノート上では確認できません。

## 参考

- [Claude Code v2.1.137 release](https://github.com/anthropics/claude-code/releases/tag/v2.1.137)
- [Claude Code v2.1.138 release](https://github.com/anthropics/claude-code/releases/tag/v2.1.138)

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
