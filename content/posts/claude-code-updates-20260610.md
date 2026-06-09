---
title: "【Claude Code】v2.1.170 リリースノートまとめ"
date: 2026-06-10T08:02:07+09:00
draft: false
tags: ["claude-code", "claude-fable-5", "mythos", "vs-code"]
categories: ["Claude Code Updates"]
summary: "v2.1.170 のClaude Codeリリースノートまとめ"
---

![](/images/claude-code-updates-20260610/header.png)

# Claude Code v2.1.170 リリース情報

## はじめに

2026年6月10日、Claude Code **v2.1.170** がリリースされました。本バージョンでは、新しいMythos級モデル「Claude Fable 5」が利用可能になりました。リリースノートによれば、その能力はこれまで一般提供されてきたどのモデルをも上回ります。加えて、VS Code統合ターミナルなどから起動した際にセッションのトランスクリプトが保存されないバグの修正が行われています。

## 注目アップデート深掘り

### Claude Fable 5（Mythos級モデル）の一般提供開始

今回のリリースで、Claude Fable 5が利用可能になりました。リリースノートには「Fableの能力は、これまで一般提供してきたどのモデルをも上回る（Fable's capabilities exceed those of any model we've ever made generally available）」とあり、安全性を確保した上で一般提供された（made safe for general use）モデルであることが強調されています。

Mythosクラスは、[Anthropicの公式発表](https://www.anthropic.com/news/claude-fable-5-mythos-5)によればOpusクラスの上位に位置する能力階級です。公式発表では、ソフトウェアエンジニアリングや知識作業、長時間の推論といった分野での性能が紹介されています。

v2.1.170へのアップデートを実施することで、この新モデルにアクセスできるようになります。

## 実用的な活用ポイント

Claude Fable 5は、公式発表でソフトウェアエンジニアリングや知識作業、長時間の推論といった分野での性能が紹介されており、より高い推論能力が求められる場面での活用が期待できます。

また、VS Code統合ターミナルや、Claude Codeの環境変数を引き継いだシェルから起動した場合に、セッションのトランスクリプトが保存されず `--resume` の一覧にも表示されない問題が解消されました。

## 全変更点一覧

| カテゴリ | 内容 | 概要 |
|---------|------|------|
| Feature | Claude Fable 5（Mythos級モデル）の一般提供 | これまで一般提供されてきたどのモデルをも上回る能力を、安全性を確保した上で提供 |
| Fix | セッションのトランスクリプト保存バグ修正 | VS Code統合ターミナルや環境変数を引き継いだシェルから起動した際に、トランスクリプトが保存されず`--resume`に表示されない問題を解消 |

## まとめ

本リリースでは、新しいMythos級モデルClaude Fable 5の提供開始という大きな機能追加と、VS Code統合ターミナルなどからの起動時の不具合修正が行われました。新モデルによる能力向上と、開発環境統合時の信頼性改善の両面で、Claude Codeの実用性が高まったリリースと言えます。

---

## 📚 Claude Codeをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F18439208%2F%3Fl-id%3Dsearch-c-item-text-02" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">実践Claude Code入門ー現場で活用するためのAIコーディングの思考法（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [Claude Code 公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)