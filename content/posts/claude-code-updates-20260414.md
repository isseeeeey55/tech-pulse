---
title: "【Claude Code】v2.1.105 リリースノートまとめ"
date: 2026-04-14T08:01:10+09:00
draft: false
tags: ["claude-code", "hooks", "plugins", "mcp", "webfetch", "worktree", "doctor", "api-stream"]
categories: ["Claude Code Updates"]
summary: "v2.1.105 の変更点を解説します。PreCompact hook、plugin background monitor、EnterWorktree `path` パラメータ、API stream の non-streaming フォールバック、`/doctor` の自動修正フローなど、新機能 4 件と改善 9 件、バグ修正 20 件超のリリース内容です。"
---

![](/images/claude-code-updates-20260414/header.png)

## はじめに

Claude Code の **v2.1.105** が 2026-04-14 に、前日の **v2.1.104** と連続してリリースされました。v2.1.104 は changelog に記載がない中間版で、今回の主な変更はすべて v2.1.105 にまとめられています。

新機能は 4 件（PreCompact hook、plugin background monitor、`EnterWorktree` の `path` パラメータ、`/proactive` エイリアス）、改善が 9 件、バグ修正が 20 件以上と、体験改善寄りのリリースです。特に **PreCompact hook** と **plugin background monitor** はユーザー側で挙動をフックできる範囲を広げる変更で、使い込んでいるユーザーほど恩恵を受けます。

## 注目アップデート深掘り

### PreCompact hook — 自動圧縮をブロックできるフックが追加

![PreCompact hook の制御フロー](/images/claude-code-updates-20260414/precompact-hook.png)

Claude Code は長時間セッションで context window が逼迫したとき、会話履歴を要約して圧縮する **compaction** を自動で走らせます。これまではこの処理を止める手段がなく、「いま圧縮されると作業中の文脈が消える」といった場面でも黙って進んでいました。

v2.1.105 で追加された **PreCompact hook** は、compaction の直前にユーザー定義のフックを呼び出し、フック側から処理をブロックできます。

> **フック（Hooks）とは？**
> Claude Code の特定イベントに反応して任意のシェルコマンドを実行できる拡張機構です。`PreToolUse`、`PostToolUse`、`UserPromptSubmit` などのイベントに対して `settings.json` の `hooks` キーでコマンドを登録します。今回追加された `PreCompact` は compaction イベント用の新しいフックポイントです。

ブロック方法は 2 通りあります。

**方法1: exit code 2 で終了**

```bash
#!/bin/bash
# ~/.claude/hooks/block-compact.sh
# 作業中フラグがあれば compaction をブロック
if [ -f /tmp/claude-no-compact ]; then
  echo "Compaction blocked: work in progress" >&2
  exit 2
fi
exit 0
```

`settings.json` でフック登録:

```json
{
  "hooks": {
    "PreCompact": [
      {
        "hooks": [
          { "type": "command", "command": "~/.claude/hooks/block-compact.sh" }
        ]
      }
    ]
  }
}
```

**方法2: JSON 出力で明示的に block**

```bash
#!/bin/bash
# stdout に JSON で block を返す
echo '{"decision":"block","reason":"作業中のため圧縮をスキップ"}'
exit 0
```

使い方の一例として、`/resume` 直後や plan モード中は圧縮をスキップする、といった運用が組めます。

### Plugin background monitor — プラグインが常駐監視プロセスを持てる

![Plugin background monitor の起動フロー](/images/claude-code-updates-20260414/plugin-monitor.png)

v2.1.105 で plugin manifest に **`monitors`** というトップレベルキーが追加されました。プラグイン側でバックグラウンドで動かし続けたいプロセス（ファイル監視、外部サービスのポーリング、ログ tail 等）を宣言しておくと、セッション開始時または skill invoke 時に自動で起動されます。

manifest 記述例:

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "monitors": [
    {
      "name": "file-watcher",
      "command": "node scripts/watch.js",
      "armOn": "session-start"
    },
    {
      "name": "skill-tracer",
      "command": "tail -f /tmp/my-plugin.log",
      "armOn": "skill-invoke"
    }
  ]
}
```

`armOn` には `session-start`（セッション開始時に起動）と `skill-invoke`（当該プラグインの skill が呼ばれたときに起動）の 2 つが指定できます。プロセスは Claude Code のセッション寿命に紐づくので、セッション終了とともに停止します。

従来は「セッション開始時に bash hook で裏プロセスを spawn する」といった半裏技で実現していた常駐監視が、manifest の宣言だけで扱えるようになります。特に、自作プラグインで外部ツールと連携するタイプ（たとえばステータスラインへの情報プッシュ、別プロセスとの IPC）で書きやすくなる変更です。

## 実用的な活用ポイント

**`/doctor` に `f` キー追加**: 診断結果にステータスアイコンが付いたうえで、`f` を押すと検出された問題を Claude に修正してもらえます。環境設定やパス絡みの問題が出たときに、以前は自分で出力を読み取って対応していた部分が自動化されます。

**API stream の non-streaming フォールバック**: API ストリームが 5 分無応答になった場合、接続を中断して非ストリーミングモードでリトライします。不安定なゲートウェイ経由や低速ネットワーク環境での体感が変わる変更です。

**Network エラーメッセージの即時表示**: 接続エラー時、従来は無言のスピナーで待たされることがありましたが、リトライ中であることを即座に表示するようになりました。

**WebFetch で `<style>` / `<script>` 除去**: CSS 重いページを WebFetch するとき、スタイル・スクリプトで content budget が消費されて本文に届かないケースがありました。v2.1.105 から除去されるので、長大なドキュメントページや公式サイトの取得が安定します。

**Skill description 文字数制限引き上げ**: skill listing の上限が 250 → **1,536 文字**に。description が切り詰められている場合はセッション開始時に警告も出ます。長めのトリガー説明を書いていたスキルを見直すタイミングです。

**MCP 大量出力の truncation prompt 改善**: 大きな MCP ツール出力が切り詰められた際、JSON なら `jq`、テキストなら Read のチャンクサイズ計算など、**形式別の具体的な続き読みレシピ**が提示されるようになりました。

**`EnterWorktree` に `path` パラメータ**: 既存の worktree への切り替えが 1 ステップでできるようになります。複数 worktree を使い分ける運用で地味に効きます。

**`/proactive` = `/loop` エイリアス**: `/loop` コマンドの別名として `/proactive` が使えるようになりました。自分の運用語彙に合う方を選べます。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Added | PreCompact hook | exit 2 または `{"decision":"block"}` で自動 compaction をブロック可能 |
| Added | Plugin background monitor | manifest `monitors` キーで session-start / skill-invoke 時に監視プロセス自動起動 |
| Added | `EnterWorktree` の `path` パラメータ | 既存 worktree への切り替えをワンステップで |
| Added | `/proactive` alias | `/loop` コマンドの別名 |
| Improved | API stream フォールバック | 5分 no-data で中断 → non-streaming リトライ |
| Improved | `/doctor` の `f` キー | 検出した問題を Claude に修正させる対話フロー追加 |
| Improved | WebFetch の style/script 除去 | CSS 重いページで本文に到達できる |
| Improved | Skill description 上限 | 250 → 1,536 文字、切り詰め時に startup 警告 |
| Fixed | バグ修正 20 件超 | Ctrl+J / alt+enter の改行挿入、429 エラー表示、Bedrock モデル ID、marketplace プラグイン更新 ほか多数 |

## まとめ

v2.1.105 はユーザー拡張ポイントを広げる 2 つの新機能（PreCompact hook と plugin background monitor）が目玉で、残りはネットワーク処理やターミナル表示の地味だが効く改善と、大量のバグ修正という構成です。Claude Code をエージェント基盤として使い込んでいるチーム、特に plugins を自作しているチームは、monitors と PreCompact の組み合わせで表現できる範囲が一段広がります。`/doctor` の `f` キーや WebFetch の style 除去は、日常的な使い勝手に直接効く変更なので今日からそのまま恩恵を受けられます。
