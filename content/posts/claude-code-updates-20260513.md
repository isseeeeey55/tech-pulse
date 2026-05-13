---
title: "【Claude Code】v2.1.140 リリースノートまとめ"
date: 2026-05-13T08:01:03+09:00
draft: false
tags: ["claude-code", "agent", "windows", "plugins", "hooks"]
categories: ["Claude Code Updates"]
summary: "v2.1.140 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260513/header.png)

# Claude Code v2.1.140 リリース情報

## はじめに

Claude Code v2.1.140 が 2026年5月12日（UTC）にリリースされました。新機能の追加は最小限に抑えられ、Agent ツールの呼び出し精度向上、設定ホットリロード・バックグラウンドサービス・Windows 上での安定性に関する複数のバグ修正、マネージド設定まわりの挙動修正を中心とした、運用品質を底上げするメンテナンスリリースです。

## 注目アップデート深掘り

### Agent ツールの `subagent_type` マッチングが大文字・区切り文字を許容

`Agent` ツールに渡す `subagent_type` の値が、大文字小文字および区切り文字（スペース・ハイフン）の違いを吸収して解決されるようになりました。例えば `"Code Reviewer"` を指定しても、内部で `code-reviewer` エージェントにマッピングされます。

これにより、ユーザーが手で書いた `Agent({subagent_type: "Code Reviewer", ...})` のような呼び出しが、わずかな表記揺れで失敗することがなくなり、ツール経由の自動化と人間が書く呼び出しの両方で扱いやすくなりました。

### `/goal` がフック制限下でハングしなくなった

`disableAllHooks` または `allowManagedHooksOnly` が有効な環境で `/goal` を実行したとき、これまで進捗インジケータが回り続けたまま無言で固まる挙動がありました。v2.1.140 では、明示的にメッセージが表示されるようになり、フック設定によって `/goal` が利用できないことがすぐ分かります。

### マネージド／エンタープライズ運用まわりの修正

エンタープライズ環境向けの安定性修正がまとまっています。

- **エンドポイントセキュリティとの相性**: バックグラウンドサービスの起動が、エンドポイントセキュリティ製品の介入で時間を要するマシン上でも完了するよう、起動タイムアウトを拡張。
- **マネージド設定の 401 リトライ**: リモートのマネージド設定取得で 401 が返った場合、トークンを強制リフレッシュして 1 度だけリトライするように修正。期限切れトークンに起因する不可解な失敗が解消されました。
- **`extraKnownMarketplaces` の永続化**: マネージドの `extraKnownMarketplaces` 自動更新ポリシーが `known_marketplaces.json` に書き戻されていなかった問題を修正。

これらは個別には小粒な修正ですが、組織配布された Claude Code が「最初は動くがある時間以降は動かない／更新が反映されない」といった、サポート問い合わせの温床になるパターンを解消する内容です。

### 設定ホットリロード（シンボリックリンク）

Dotfiles 管理などで `settings.json` をシンボリックリンクにしているケースで、ファイル変更イベントが誤ったパスに紐付き、`ConfigChange` フックがスプリアスに発火するリグレッションを修正しました。

> **Note:** `ConfigChange` フックを使って自前のリロード処理を組んでいる場合、これまで余計に走っていた処理が止まる方向の変更です。挙動を観察した上で、不要なガードを削除する余地が出てきます。

### Windows での event-loop ストール修正

`PATH` 上に存在しない実行ファイル（例: `gh` 未インストール）に対するチェックが、Windows 上で毎回 `where.exe` を同期 spawn し直し、event loop を断続的に止める問題が修正されました。CLI 起動直後の反応が良くなる類の修正です。

### `Read` ツールの `offset` バリデーション緩和

`Read` ツールの `offset` パラメータに、空白でパディングされた文字列や `+` プレフィックス付きの文字列を渡したときにバリデーションが失敗していた問題を修正。Bash で生成した行番号文字列をそのまま渡すケースで詰まらなくなります。

### `/loop` のバックグラウンドタスク待機

`/loop` が、完了時に自分から通知するバックグラウンドタスクを対象に、冗長な wakeup スケジュールを積んでいた挙動を修正。これにより通知駆動の `/loop` 利用で、不要なポーリング起動が減ります。

### Plugins のサイレント無視を可視化

`plugin.json` で `commands` などのキーを明示している場合に、同名のデフォルトフォルダ（`commands/`）が黙って無視されていた挙動について、警告を出すようにしました。警告は `/doctor`、`claude plugin list`、`/plugin` で確認できます。

### `claude --bg` の "connection dropped mid-request" 修正

バックグラウンドサービスがアイドル終了する直前に `claude --bg` を呼び出すと "connection dropped mid-request" で失敗するレースを修正。常駐させずに `--bg` を都度叩く使い方をしているスクリプトでの再現性のある失敗が解消されます。

### ネイティブターミナルのカーソル位置

ターミナルがフォーカスを失った際に、入力キャレットからカーソルがずれる表示上の問題を修正しました。

### Agent カラーパレットの更新

ビジュアル面の変更として、Agent のカラーパレットが更新されました。

## 実用的な活用ポイント

- **エンタープライズ展開のサポート負荷低減**: 起動タイムアウト・401 リトライ・`known_marketplaces.json` 永続化の 3 点は、組織配布した端末で「初日は動いたのに翌週から動かない」系の問い合わせを直接減らすため、社内向けの "v2.1.140 以降にアップデート" の周知価値が高いリリースです。
- **`/goal` の運用**: `disableAllHooks` / `allowManagedHooksOnly` を強制しているテナントでは、これまで `/goal` がハングしてユーザーが原因に気付けませんでした。今後はエラーメッセージから設定起因と分かるため、ヘルプ動線が短くなります。
- **`subagent_type` の柔軟マッチ**: 自前の slash command やドキュメントで `subagent_type` を文字列で書いている箇所は、表記揺れを許容できるようになったため、ドキュメント更新ほどの大規模対応は不要になりました。
- **`/loop` × 通知駆動タスク**: 完了通知付きのバックグラウンドジョブを `/loop` から待つパターンは、無駄な wakeup が減ることでコストにも有利です。

## 全変更点一覧

| カテゴリ | 内容 |
|---------|------|
| Improvement | Agent ツールの `subagent_type` を大文字・区切り文字非依存でマッチ |
| Improvement | Agent カラーパレットを更新 |
| Fix | `/goal` が `disableAllHooks` / `allowManagedHooksOnly` 下で無言ハングしていた問題を修正（メッセージ表示） |
| Fix | シンボリックリンクされた設定ファイルでホットリロードのイベントが誤帰属し、`ConfigChange` フックが余分に走るリグレッションを修正 |
| Fix | `claude --bg` がアイドル終了直前に "connection dropped mid-request" で失敗するレースを修正 |
| Fix | エンドポイントセキュリティ介入下で起動が失敗するケースを、起動タイムアウト延長で修正 |
| Fix | リモートのマネージド設定取得で 401 が返ったとき、トークンを強制リフレッシュして 1 回リトライ |
| Fix | マネージドの `extraKnownMarketplaces` 自動更新ポリシーが `known_marketplaces.json` に永続化されていなかった問題を修正 |
| Fix | `/loop` が通知駆動のバックグラウンドタスクに対して冗長な wakeup を積んでいた挙動を修正 |
| Fix | Windows で `gh` などが PATH 上にないとき、`where.exe` の同期再 spawn が event loop を止める問題を修正 |
| Fix | `Read` ツールの `offset` で、空白パディングや `+` プレフィックス付き文字列がバリデーション失敗していた問題を修正 |
| Fix | ネイティブターミナルでフォーカス喪失時に入力キャレットからカーソルがずれる問題を修正 |
| Improvement | `plugin.json` で同名キーを設定したことで `commands/` などのデフォルトフォルダが silent に無視されているとき、`/doctor`・`claude plugin list`・`/plugin` で警告 |

## まとめ

v2.1.140 は派手な新機能こそ無いものの、エンタープライズ配布まわりの "サポートに上がりやすいバグ" を 3 点（起動タイムアウト、401 リトライ、マネージドポリシー永続化）まとめて潰しており、組織配布している環境ほど更新価値が大きいリリースです。加えて、Windows での event-loop ストール、`/goal` の無言ハング、`/loop` の冗長 wakeup など、毎日触っていると地味に効く品質改善が並びます。

- 公式リリースノート: <https://github.com/anthropics/claude-code/releases/tag/v2.1.140>
- 公開日時: 2026-05-12 21:09 UTC

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
