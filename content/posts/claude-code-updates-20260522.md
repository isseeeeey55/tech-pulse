---
title: "【Claude Code】v2.1.147・v2.1.146 リリースノートまとめ"
date: 2026-05-22T08:01:05+09:00
draft: false
tags: ["claude-code", "code-review", "mcp", "github", "windows", "powershell"]
categories: ["Claude Code Updates"]
summary: "v2.1.147・v2.1.146 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260522/header.png)

# Claude Code v2.1.147 & v2.1.146 リリース情報

## はじめに

Claude Code の v2.1.146 が5月21日、v2.1.147 が5月22日にリリースされた。2バージョンの内容は連続しており、主な変更は3つ。`/simplify` コマンドの `/code-review` への刷新、ピン留めしたバックグラウンドセッションの常駐対応、そして Windows PowerShell と MCP まわりを中心としたバグ修正である。

## 注目アップデート深掘り

### `/simplify` から `/code-review` への刷新

v2.1.146 で `/simplify` コマンドが `/code-review` にリネームされ、v2.1.147 でさらに機能が加わった。

単なる改名ではない。旧 `/simplify` が持っていた「コードを整理して修正する」挙動は廃止され、`/code-review` は正確性のバグ（correctness bugs）を指摘するコマンドに変わった。レビューの深さは努力レベルで指定する。

```
/code-review high
```

v2.1.147 では `--comment` フラグが追加された。これを付けると、レビューで見つかった指摘を GitHub PR のインラインコメントとして直接投稿できる。

```
/code-review high --comment
```

ローカルでレビューを完結させるか、PR にコメントを残してチームのレビューフローに乗せるか。コマンド一つで切り替えられる。

### ピン留めしたバックグラウンドセッションの常駐

`claude agents` の画面で `Ctrl+T` を押すと、バックグラウンドセッションをピン留めできる。v2.1.147 では、このピン留めセッションの扱いが変わった。

- アイドル状態が続いても終了されない
- Claude Code 本体のアップデートが来たときは、その場で再起動して新バージョンを適用する
- メモリ逼迫時には、ピン留めしていないセッションが先に破棄され、ピン留めセッションは最後まで残る

長時間かけて進めるタスクや、何度も戻って参照したいセッションを、明示的に「残す」と指定できるようになった。

## そのほかの修正

### Windows・MCP まわり

v2.1.146 は v2.1.124 のリグレッション修正を含む。winget または Microsoft Store 経由で `pwsh` をインストールしている Windows 環境で、PowerShell ツールが「command line is invalid」で失敗していた不具合が直った。v2.1.147 ではさらに、フック条件 `PowerShell(git push*)` が一致しない問題や、PowerShell ツールがデフォルトフォーマッタ依存のコマンドで出力を落とす問題なども修正されている。

MCP では、ページネーションに対応したサーバーで `resources/list`・`resources/templates/list`・`prompts/list` が2ページ目以降の項目を取りこぼしていた。大量のリソースやプロンプトを公開する MCP サーバーを使っている場合、これまで一部が見えていなかったことになる。

### 自動アップデーターとパフォーマンス

自動アップデーターは、ネットワークの一時的な失敗をリトライするようになった。失敗時にはエラーの種別と OS のエラーコードを表示し、現在のバージョンも示す。原因の切り分けがしやすくなる。

大きいファイルを編集したときの差分描画パフォーマンスも改善された。プロンプト履歴は、連続する重複エントリを記録しなくなった。↑キーで同じプロンプトを呼び出して再送しても、履歴に同じものが積み重ならない。

### エンタープライズ向けの修正

マネージド設定の `forceLoginOrgUUID` と `forceLoginMethod` が、サードパーティプロバイダや API キーのセッションに対して適用されていなかった。ログイン制限を組織ポリシーとして敷いている場合、この経路が抜け穴になっていたことになる。v2.1.146 と v2.1.147 の両方で修正されている。

## 全変更点一覧

| カテゴリ | バージョン | 内容 |
|---------|-----------|------|
| Feature | v2.1.147 | `/code-review` に `--comment` を追加（GitHub PR へのインラインコメント投稿に対応） |
| Feature | v2.1.147 | ピン留めしたバックグラウンドセッションがアイドル時も常駐、更新時はその場で再起動 |
| Improvement | v2.1.147 | 自動アップデーターの改善（一時的なネットワーク失敗のリトライ、エラー種別・OSエラーコードの表示） |
| Improvement | v2.1.147 | プロンプト履歴で連続する重複エントリを記録しないように変更 |
| Improvement | v2.1.147 | 大きいファイル編集時の差分描画パフォーマンス改善 |
| Fix | v2.1.147 | MCP サーバーのページネーションでリソース・テンプレート・プロンプトを取りこぼす不具合を修正 |
| Fix | v2.1.147 | PowerShell 関連の複数の不具合（フック条件の不一致、出力欠落など）を修正 |
| Feature | v2.1.146 | `/simplify` を `/code-review` にリネーム、努力レベル指定に対応 |
| Fix | v2.1.146 | winget / Microsoft Store 版 pwsh で PowerShell ツールが失敗する不具合を修正（v2.1.124 のリグレッション） |
| Fix | v2.1.146 | MCP の resources/list・templates/list・prompts/list が2ページ目以降を取りこぼす不具合を修正 |
| Fix | v2.1.146 / v2.1.147 | forceLoginOrgUUID・forceLoginMethod がサードパーティ／APIキーのセッションに適用されない不具合を修正 |

## まとめ

v2.1.146 と v2.1.147 で目立つのは、`/code-review` への刷新だ。`/simplify` のクリーンアップ機能が、努力レベル指定と GitHub PR コメント投稿を備えたレビューコマンドに置き換わった。旧挙動が削除されている点には注意が必要だが、コードレビューを Claude Code のワークフローに組み込みやすくなった。

バックグラウンドセッションのピン留め常駐は、長時間タスクを扱う使い方を後押しする変更だ。残りは Windows PowerShell や MCP ページネーションといった環境依存の不具合修正が中心で、特定の環境で詰まっていた人には効く内容になっている。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
