---
title: "【Claude Code】v2.1.112 / v2.1.111 リリースノートまとめ"
date: 2026-04-17T08:01:45+09:00
draft: false
tags: ["claude-code", "opus-4.7", "effort", "ultrareview", "less-permission-prompts", "powershell", "auto-mode", "bash", "keybinding"]
categories: ["Claude Code Updates"]
summary: "v2.1.112 / v2.1.111 の変更点を解説します。Claude Opus 4.7 xhigh と `/effort` スライダー、パラレルマルチエージェントの `/ultrareview`、`/less-permission-prompts` スキル、Windows 向け PowerShell tool、読み取り専用 bash のプロンプト省略など。"
---

![](/images/claude-code-updates-20260417/header.png)

## はじめに

Claude Code の **v2.1.111** は中〜大規模のリリースで、**Opus 4.7 xhigh** と `/effort` スライダー、**`/ultrareview`**（クラウド上でのパラレルマルチエージェント PR レビュー）、**`/less-permission-prompts`** スキル、Windows 向け **PowerShell tool** の段階展開など、新機能が多数入りました。続く **v2.1.112** は直後のホットフィックスで、`claude-opus-4-7 is temporarily unavailable` という auto mode でのエラーを修正した単発リリースです。

## 注目アップデート深掘り

### Opus 4.7 xhigh と `/effort` スライダー — 速度と知能のバランスを手元で切り替え

![/effort スライダーの効果レベル](/images/claude-code-updates-20260417/effort-slider.png)

v2.1.111 で **Claude Opus 4.7 xhigh** が使えるようになりました。公式の位置付けは **`high` と `max` の間のエフォートレベル**で、同じモデルでも推論にどれくらいエネルギーを使うかを調整する軸です。`/effort` コマンドで切り替えます。

> **`/effort` とは？**
> Claude Code でモデルの「推論エフォート（どれくらい時間・トークンをかけて考えるか）」を切り替えるコマンドです。`/effort` を引数なしで呼ぶとインタラクティブスライダーが開き、矢印キーで `low` / `medium` / `high` / `xhigh` / `max` を切り替えて Enter で確定できます。`--effort` フラグやモデルピッカーからも選択可能。Opus 4.7 以外のモデルでは `xhigh` は `high` にフォールバックします。

使い方は次のいずれか:

```bash
# インタラクティブスライダーを開く（v2.1.111 新機能）
/effort

# 直接切り替え
/effort xhigh

# 起動時に指定
$ claude --effort xhigh
```

加えて、**Max サブスクライバーは auto mode で Opus 4.7 が使えるように**なりました（v2.1.111）。これまで `--enable-auto-mode` フラグの明示が必要でしたが、それも不要化されています。auto mode はモデル選択を Claude 側に任せて、タスクの複雑さに応じて自動で上げ下げしてくれる運用モードで、Max プランで Opus 4.7 を日常使いする人の体験がここで大きく整います。

さらに v2.1.112 では、auto mode 選択時に `claude-opus-4-7 is temporarily unavailable` エラーになるケースが修正されました。v2.1.111 + 112 のセットで、Opus 4.7 周辺の「試せるけどたまに不安定」という状態が取り切れた格好です。

### `/ultrareview` — クラウド上でパラレルマルチエージェント PR レビュー

![/ultrareview の流れ](/images/claude-code-updates-20260417/ultrareview-flow.png)

`/ultrareview` は v2.1.111 で追加された新コマンドで、**クラウド上で複数エージェントを並列に走らせて包括的なコードレビューと批評を行う**機能です。公式の記述はコンパクトで、次の 2 つのモードがあります。

- **引数なし**: 現在のブランチをレビュー
- **`/ultrareview <PR#>`**: 指定 GitHub PR をフェッチしてレビュー

```bash
# 現在のブランチをレビュー
/ultrareview

# 特定の PR をレビュー
/ultrareview 123
```

公式ノートには「パラレルマルチエージェント分析と批評」とあるだけで、エージェントの具体的な分類（セキュリティ / パフォーマンス / etc.）までは明記されていません。リリース直後なので、**実際にどういう出力が返ってくるかは手元で試してから運用に組み込むのが安全**です。

面白いのはクラウド側で動く点。ローカル Claude Code セッションの文脈とは独立に、リポジトリの状態をクラウドに渡して複数エージェントが同時にレビューするので、大規模な PR でもレビュー時間がほぼスケールしません。GitHub PR 番号を直接渡せるので、レビュー用の別ブランチを切ってローカルでチェックアウトする手間が省けます。

### `/less-permission-prompts` スキル — 許可プロンプトを実績から削る

地味ですが運用では効くのが **`/less-permission-prompts`** スキルです。v2.1.111 で追加されました。

> **どういう仕組みか?**
> 過去のセッション transcript をスキャンし、よく出てくる **読み取り専用の Bash コマンド** と **MCP ツール呼び出し** を抽出して、`.claude/settings.json` の allowlist に追加する提案を優先度順に出してくれます。承認すれば、それ以降のセッションでそのコマンドは許可プロンプトなしで実行されるようになります。

要するに「毎日の作業で何十回も Yes を押しているコマンドを allowlist 化する」作業を、Claude Code 自身のログを根拠にして半自動化してくれるツールです。`claude code` を daily driver で使っていると、`git status`、`ls`、`cat`、`gh pr view` あたりが大量に出てくるはずで、そういう読み取り系を `settings.json` に詰めるだけで体験が軽くなります。

加えて v2.1.111 では、**glob パターン付きの読み取り専用コマンド（`ls *.ts` 等）と、`cd <project-dir> &&` プレフィックス付きコマンド** は設定抜きでプロンプトが出なくなりました。`/less-permission-prompts` とセットで考えると、プロンプト疲れがだいぶ減ります。

## 実用的な活用ポイント

**Windows 向け PowerShell tool の段階展開**: v2.1.111 から `CLAUDE_CODE_USE_POWERSHELL_TOOL` 環境変数で opt-in / opt-out できます。Linux / macOS でも `CLAUDE_CODE_USE_POWERSHELL_TOOL=1` で有効化可能（`pwsh` が PATH 上にあること）。Windows Server 運用で PowerShell スクリプトを扱うチームは、ローリングの対象になっていれば使える状態のはずなので、試してみる価値ありです。

**Auto (match terminal) テーマ**: `/theme` から選択すると、ターミナルの dark / light モードに自動追従します。macOS の外観モード切替 + iTerm2 のプロファイル切替と組み合わせて使うと、昼夜で Claude Code の見た目も自動で変わります。

**入力バッファ操作の強化**: `Ctrl+U` が**入力バッファ全体をクリア**する挙動に変わりました（旧: 行頭までの削除）。誤クリアしたら `Ctrl+Y` で復元できます。加えて `Ctrl+L` はフルスクリーン再描画も行うようになり、描画が崩れたときのリセットに使えます。

**`claude <word>` の typo 提案**: `claude udpate` と打つと「Did you mean `claude update`?」と候補を出してくれます。subcommand 名の綴りを覚えていないときに助かる地味な改善です。

**`Ctrl+O` / `/skills` の小改善**: Transcript view のフッターに `[`（スクロールバックに dump）と `v`（エディタで開く）が表示されるように。`/skills` メニューは `t` キーで token count ソートに切替可能。

**Bedrock / Vertex / Foundry の 429**: 以前は `status.claude.com` へのリンクが出ていましたが、これらサードパーティプロバイダでは意味がなかったので除去されました。

**v2.1.110 の non-streaming fallback cap を revert**: v2.1.110 で「リトライ上限を設けて長時間の待機を防ぐ」変更が入っていたのが、API overload 時にかえって outright failure を増やしてしまうので v2.1.111 で戻されています。動作がまた v2.1.109 以前の挙動に近づいています。

## 全変更点一覧

| カテゴリ | 変更内容 | 概要 |
|---------|---------|------|
| Added (v2.1.111) | Claude Opus 4.7 xhigh + `/effort` スライダー | `xhigh` は `high` と `max` の中間、インタラクティブスライダーで切替可能 |
| Added (v2.1.111) | `/ultrareview` コマンド | クラウド上のパラレルマルチエージェントで PR レビュー、`/ultrareview <PR#>` 対応 |
| Added (v2.1.111) | `/less-permission-prompts` スキル | transcript スキャンで allowlist 候補を提案 |
| Added (v2.1.111) | Auto mode for Max + Opus 4.7 | `--enable-auto-mode` 不要化、Max サブスクライバーで Opus 4.7 を自動選択 |
| Added (v2.1.111) | Windows 向け PowerShell tool | `CLAUDE_CODE_USE_POWERSHELL_TOOL` opt-in で段階展開 |
| Added (v2.1.111) | "Auto (match terminal)" テーマ | `/theme` からターミナルの dark/light モードに追従設定可能 |
| Improved (v2.1.111) | 読み取り専用 bash のプロンプト省略 | glob パターン (`ls *.ts`) と `cd <dir> &&` プレフィックスでプロンプト不要 |
| Improved (v2.1.111) | `Ctrl+U` で入力バッファ全クリア | `Ctrl+Y` で復元、`Ctrl+L` はフルスクリーン再描画を追加 |
| Fixed (v2.1.112) | Opus 4.7 auto mode 安定化 | `claude-opus-4-7 is temporarily unavailable` エラーを修正 |
| Fixed (v2.1.111) | 多数のバグ修正 | iTerm2+tmux 表示、LSP 診断、`/resume` tab 補完、plugin 依存、Windows 環境ファイル ほか |

## まとめ

v2.1.111 は新機能の密度が高いリリースでした。日常ユースでは **`/effort` スライダー + Opus 4.7 xhigh** が体感を変える 1 つ目、**`/less-permission-prompts`** と **読み取り専用 bash のプロンプト省略**がプロンプト疲れを取る 2 つ目の軸。**`/ultrareview`** は PR レビューワークフローの新しい選択肢として、大規模 PR を抱えるチームで試す価値があります。v2.1.112 は Opus 4.7 auto mode 周りの不安定さを取り切るためのホットフィックスで、111 と合わせて当ててしまうのが素直です。
