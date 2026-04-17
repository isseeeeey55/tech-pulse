---
title: "【Claude Code】v2.1.113 リリースノートまとめ"
date: 2026-04-18T08:01:33+09:00
draft: false
tags: ["claude-code", "native-binary", "sandbox", "denieddomains", "bash", "security", "loop", "ultrareview", "remote-control"]
categories: ["Claude Code Updates"]
summary: "v2.1.113 の変更点を解説します。CLI がネイティブバイナリに切り替わり、`sandbox.network.deniedDomains` 設定追加、Bash の exec ラッパー経由 deny ルール対応、macOS 危険パス検知、`/loop` と `/ultrareview` の体験改善など。"
---

![](/images/claude-code-updates-20260418/header.png)

## はじめに

Claude Code の **v2.1.113** は比較的大きなリリースです。目玉は **CLI がネイティブバイナリへ切り替わった**こと（platform 別の optional dependency として配布）と、**セキュリティ関連の複数改善**（`sandbox.network.deniedDomains` 追加、Bash の exec ラッパー経由 deny ルール対応、macOS 危険パス検知）。加えて `/loop` と `/ultrareview` の体験改善、Remote Control クライアントの機能拡張、長文のバグ修正リストが入っています。

## 注目アップデート深掘り

### CLI がネイティブバイナリに切り替わった

![ネイティブバイナリ化の影響](/images/claude-code-updates-20260418/native-binary.png)

v2.1.113 から、CLI は **platform 別の optional dependency として配布されるネイティブバイナリ**を spawn するように変わりました。公式の表現は「instead of bundled JavaScript」で、バンドル済み JavaScript を直接実行する従来方式からの切替です。

ユーザー側のインストール手順は変わりません（`npm install -g @anthropic-ai/claude-code` や自動更新経由）。内部的には各プラットフォーム（macOS / Linux / Windows、それぞれ x64 / arm64）向けの optional dependency がダウンロードされ、CLI ラッパーから実ネイティブバイナリが呼ばれる形です。

体感として効きやすいのは **起動時間と常駐メモリ** で、Node.js ランタイムを毎回初期化するオーバーヘッドがなくなります。CI/CD や git hook 内から短時間で claude を叩くユースケースで恩恵を受けやすい変更です。ただし具体的な速度倍率はリリースノートに記載されていないので、手元で `time claude --version` を比較してみるのが確実です。

### セキュリティ関連の 4 つの改善

v2.1.113 にはセキュリティ周りの改善が複数入りました。どれも既存の Bash / sandbox 仕組みの「細かい抜け穴」を埋める系統の変更です。

**1. `sandbox.network.deniedDomains` 設定が追加**

サンドボックス設定に **`sandbox.network.deniedDomains`** が新設されました。これは既存の `allowedDomains` でワイルドカードで許可した場合でも、**特定ドメインだけを明示的にブロック**するためのものです。

```json
{
  "sandbox": {
    "network": {
      "allowedDomains": ["*.github.com", "*.anthropic.com"],
      "deniedDomains": ["raw.githubusercontent.com/*"]
    }
  }
}
```

`*.github.com` を包括的に許可しつつ、任意のファイル取得に使われうる `raw.githubusercontent.com` だけを除外する、といった使い方ができます。社内セキュリティポリシーと Claude Code のネットワークアクセスをきめ細かく合わせたいエンタープライズ環境向けの改善です。

> **sandbox とは？**
> Claude Code のネットワーク・ファイルシステムアクセスを制限する仕組みです。`settings.json` の `sandbox` セクションで `network.allowedDomains` や `bash.denylist` などを設定すると、Claude が実行するツール呼び出しがその範囲内に制限されます。エンタープライズ配布の `managed-settings` と組み合わせることで、組織ポリシーを強制できます。

**2. Bash deny ルールが exec ラッパー経由のコマンドにも効くように**

これまで `Bash(rm:*)` のような deny ルールは、**`env` / `sudo` / `watch` / `ionice` / `setsid` などの exec ラッパーでラップされたコマンドに対して効かない**抜け穴がありました（例: `sudo rm -rf /foo` は deny されない）。v2.1.113 ではラッパー越しでもマッチするようになりました。

**3. `Bash(find:*)` allow ルールが `find -exec` / `-delete` を自動承認しない**

`find` の allow ルール経由で `find ... -exec rm -rf {} \;` のような破壊的コマンドが通ってしまう抜け穴が塞がれました。これ以降、`-exec` と `-delete` は別途パーミッション確認が走ります。

**4. macOS の `/private/{etc,var,tmp,home}` が危険パス扱いに**

macOS では `/etc` や `/var` がシンボリックリンクで `/private/etc`、`/private/var` を指しています。`Bash(rm:*)` の allow ルール下で `rm -rf /etc/...` が拒否されても、`rm -rf /private/etc/...` という実パス経由だと通っていた抜け穴を塞ぐ修正です。

**5. `Bash dangerouslyDisableSandbox` のパーミッションプロンプト忘れ修正**

サンドボックス無効化オプション `dangerouslyDisableSandbox` が、プロンプトなしで実行できてしまうバグを修正。サンドボックス外でのコマンド実行は必ずユーザー確認が走るようになりました。

## 実用的な活用ポイント

**`/loop` の UX 改善**: `/loop` 実行中に **Esc を押すと pending 状態の wakeup をキャンセル**できるようになりました。また、wakeup が走ったときの表示が `Claude resuming /loop wakeup` に統一されて「なんで今走ったんだろう」が一目で分かります。

**`/ultrareview` の高速化**: launch dialog に **diffstat** が表示され、並列化されたチェックで起動が速くなりました。加えて **animated launching state** が入り、起動待ちが分かりやすくなっています。

**Subagent のスタック検出**: subagent が mid-stream で stall した場合、**10 分でエラーを返す**ようになりました（従来は silent hang）。長時間の並列 agent 実行で進捗が分からなくなる問題が改善されます。

**キーバインド各種**:
- **Fullscreen mode の `Shift+↑/↓`**: 選択範囲を視界外まで拡張するスクロールに対応
- **`Ctrl+A` / `Ctrl+E`**: multiline 入力で readline 同様に論理行頭・行末移動
- **Windows `Ctrl+Backspace`**: 前の単語を削除
- **`Cmd-backspace` / `Ctrl+U`**: カーソルから行頭までの削除（回帰修正）

**長い URL の hyperlink 維持**: ターミナル出力や bash 出力で、長い URL が折り返しされても **OSC 8 hyperlinks 対応ターミナル**（iTerm2、WezTerm など）で clickable のまま保たれます。

**Remote Control クライアントの拡張**: `/extra-usage` と `@`-file autocomplete がモバイル/Web クライアントから使えるようになりました。加えて、Remote Control セッションで subagent transcripts がストリームされる修正と、Claude Code 終了時に Remote Control セッションが archive される修正も入っています。

**`cd <current-directory> && git ...` のパーミッションプロンプト省略**: 既に cd 済みのディレクトリに対して `cd` を重ねる no-op のケースでは、パーミッションプロンプトが出なくなりました。git 操作でよく出てくる rituals の 1 つがノイズから除去されます。

**多数のバグ修正**: MCP concurrent-call timeout の watchdog、markdown テーブル内のパイプ文字、session recap の誤発火、`/copy` のテーブル整形、`/effort auto` の表示、`/insights` Windows EBUSY、Opus 4.7 の Bedrock Application Inference Profile ARN エラーなど、広範囲の細かい修正が入っています。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---|---|---|
| Changed | CLI がネイティブバイナリを spawn | platform 別の optional dependency としてネイティブバイナリを配布 |
| Added | `sandbox.network.deniedDomains` | `allowedDomains` ワイルドカード許可下でも特定ドメインを明示ブロック |
| Improved | `/loop`: Esc で pending wakeup キャンセル | wakeup 表示も `Claude resuming /loop wakeup` に統一 |
| Improved | `/ultrareview`: diffstat + parallelized checks | launch dialog 改善、animated launching state 追加 |
| Added | Remote Control で `/extra-usage` / `@`-file autocomplete | モバイル/Web クライアントから利用可能 |
| Security | Bash deny ルールが exec ラッパー経由にマッチ | `env` / `sudo` / `watch` / `ionice` / `setsid` ラップ時も検出 |
| Security | `Bash(find:*)` allow ルールが `-exec` / `-delete` を自動承認しない | 抜け穴を閉じる |
| Security | macOS `/private/{etc,var,tmp,home}` が危険パス扱い | symlink 経由の削除を防止 |
| Improved | キーバインド各種 | `Shift+↑/↓`、`Ctrl+A/E` の readline 対応、Windows `Ctrl+Backspace` |
| Improved | 長い URL の OSC 8 hyperlink 維持 | 折り返し時も clickable |
| Improved | Subagent stall が 10 分でエラー | silent hang 回避 |
| Improved | `cd <same-dir> && git ...` のプロンプト省略 | no-op cd のノイズ削減 |
| Fixed | 多数のバグ修正 | MCP timeout、markdown table、/copy、/effort auto 表示、Bedrock ARN ほか |

## まとめ

v2.1.113 の最大の構造変化は CLI のネイティブバイナリ化で、ユーザー側は自動で恩恵を受けつつ、CI/CD の git hook など短時間の起動が多い使い方で体感が変わります。セキュリティ改善はどれも「既存の deny ルールの細かい抜け穴を塞ぐ」系統で、組織ポリシーを厳しく運用しているチームにはそのまま効きます。`/loop` と `/ultrareview` の体験改善、Remote Control の機能拡張、広範囲の細かいバグ修正も含め、全体として「作り込みを一段引き上げる」バージョンです。
