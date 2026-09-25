---
title: "【Codex CLI】rust-v0.156.1 リリースノートまとめ"
date: 2026-09-24T08:01:16+09:00
draft: false
tags: ["codex", "gpt-6-sol", "gpt-6-luna", "model-picker", "hotfix"]
categories: ["Codex CLI Updates"]
summary: "rust-v0.156.1 のCodex CLIリリースノートまとめ"
---

![](/images/codex-updates-20260924/header.png)

# Codex CLI rust-v0.156.1 リリースノート

## はじめに

OpenAI Codex CLI の **rust-v0.156.1** が 2026年9月23日（GitHub リリース日、UTC）に公開されました。rust-v0.156.0 に対する hotfix で、変更は1件です。モデルピッカーで **GPT-6 Sol** と **GPT-6 Luna** を選べるようになりました。

## 注目アップデート深掘り

### GPT-6 Sol と GPT-6 Luna をモデルピッカーに追加

リリースノートの New Features は次の1項目です。

> Choose GPT-6 Sol or GPT-6 Luna from the model picker. The rate-limit switch prompt now recommends GPT-6 Luna. (#47405)

- モデルピッカーから GPT-6 Sol と GPT-6 Luna を選択できるようになりました
- レート制限時に表示されるモデル切り替えプロンプトが、GPT-6 Luna を推奨するようになりました

この変更は PR #47405（"[hotfix 0.156.0] Add GPT-6 Sol and Luna to the model catalog"、#47332 のバックポート）として取り込まれています。両モデルの性能や料金の違いはリリースノートには書かれていないため、使い分けは OpenAI の公式ドキュメントで確認してください。

## 実用的な活用ポイント

- rust-v0.156.0 を使っていて GPT-6 Sol / Luna を使いたい場合は、0.156.1 に更新するとモデルピッカーに表示されます。
- レート制限に達したときは、切り替えプロンプトで GPT-6 Luna が推奨されます。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | GPT-6 Sol と GPT-6 Luna のサポート追加 | モデルピッカーから GPT-6 Sol と Luna を選択可能に。レート制限時の切り替えプロンプトで Luna を推奨 (#47405) |

## まとめ

rust-v0.156.1 は、GPT-6 Sol と GPT-6 Luna をモデルカタログに追加する1件だけの hotfix リリースです。レート制限時の切り替えプロンプトでは GPT-6 Luna が推奨されます。

---

## 📚 Codex CLIをもっと深く学ぶなら

- [OpenAI Codex CLI 公式リポジトリ](https://github.com/openai/codex)
- [OpenAI Platform ドキュメント](https://platform.openai.com/docs)