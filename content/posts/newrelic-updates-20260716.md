---
title: "【New Relic】2026/07/16 のアップデートまとめ"
date: 2026-07-16T08:00:55+09:00
draft: false
tags: ["newrelic", "infrastructure-agent", "logs", "windows", "observability"]
categories: ["New Relic Updates"]
summary: "2026/07/16 のNew Relicアップデートまとめ"
---

![](/images/newrelic-updates-20260716/header.png)

# 2026年7月16日 New Relic アップデート情報

## はじめに

2026年7月15日、New Relic Infrastructure Agent のバージョン 1.78.1 がリリースされました。今回のアップデートは1件のみで、内容は Windows 向けに組み込まれている New Relic fluent-bit output plugin の 3.6.0 から 3.7.0 への更新（リリースノート上は fix に分類）と、カスタムヘルスチェックポートの単体テスト追加の2点です。Windows 環境で Infrastructure Agent のログ転送を利用しているチームに関係するメンテナンスリリースです。

## 注目アップデート深掘り

### Infrastructure Agent 1.78.1 - Windows 向け fluent-bit output plugin の更新

今回のリリースに含まれる変更は、公式リリースノートによると次の2点です。

- Windows 向けに組み込まれている New Relic fluent-bit output plugin を 3.6.0 から 3.7.0 へ更新（`fix` として分類）
- カスタムヘルスチェックポートの単体テストを追加

Infrastructure Agent は内部的に fluent-bit を利用してログの収集・転送を行っており、この output plugin は fluent-bit から New Relic プラットフォームへログを送る部分を担うコンポーネントです。今回の更新は Windows 環境のログ転送経路に関わる修正という位置づけになります。なお、リリースノート本文には修正対象の具体的な不具合内容は記載されていないため、詳細が必要な場合はリリースページからたどれる変更履歴（Pull Request）を確認してください。

**なぜログ転送経路の更新に注目すべきか**

ログ監視は障害の早期発見と根本原因分析において中心的な役割を果たします。特にWindows Server上で稼働するアプリケーション（IIS、.NETアプリケーション、SQLServerなど）では、イベントログやアプリケーションログが障害対応の生命線です。ログ転送を担うコンポーネントの更新は、こうした監視パイプラインの土台に関わるため、変更内容を把握したうえで計画的に適用する価値があります。

**アップグレード判断の考え方**

本アップデートの変更範囲は Windows 向けの fluent-bit output plugin とテストコードに限定されています。したがって、Linux中心の運用環境ではアップグレードの優先度は相対的に低めです。一方、Windows Server 上で Infrastructure Agent を稼働させ、ログ転送機能を利用している場合は、次のメンテナンスサイクルでの適用を検討するとよいでしょう。

## SRE視点での活用ポイント

### ログ転送コンポーネントのバージョン把握

Infrastructure Agent のログ転送は組み込みの fluent-bit と New Relic output plugin が担っており、今回のようなコンポーネント更新は、Logs UI での検索や NRQL Alerts Conditions によるログベースアラートの土台に関わります。エージェント本体のバージョンだけでなく、内部の fluent-bit / output plugin のバージョンも変更履歴で追跡しておくと、ログ転送まわりの挙動が変化した際の切り分けがしやすくなります。

### AWS環境での運用影響

AWS上のWindows EC2インスタンス（例：ASP.NET WebアプリケーションをホストするIISサーバー）やECS on EC2のWindowsコンテナで Infrastructure Agent を稼働させている場合、今回の更新対象である Windows 向けログ転送経路を利用している可能性が高く、本アップデートの関係範囲に含まれます。CloudWatch Logs と併用している場合も、New Relic 側のエージェント更新は CloudWatch 側の収集経路とは独立しているため、影響を切り離して検証できます。

### アップグレード時の注意点

Infrastructure Agentのアップグレードは通常、既存の設定ファイル（`newrelic-infra.yml`）を維持したまま適用できますが、念のため以下の点に留意してください。

- **カスタムログ設定の確認**: `log.d/` ディレクトリ配下にカスタムログ転送設定がある場合、アップグレード後に正常動作するか検証
- **Windows環境でのサービス再起動**: アップグレード後、Infrastructure Agentサービスの再起動が必要になる場合があるため、メンテナンスウィンドウでの適用を推奨
- **ロールバック準備**: 万一問題が発生した場合に備え、旧バージョンのインストーラーをバックアップしておく

小規模なステージング環境や開発環境で先行適用し、ログ転送の正常性を確認した上で本番環境へ展開する段階的アプローチが安全です。

## 全アップデート一覧

| カテゴリ | 対象 | 概要 | リンク |
|---------|------|------|--------|
| Infrastructure | Infrastructure Agent 1.78.1 | Windows 向け組み込み fluent-bit output plugin を 3.6.0 → 3.7.0 へ更新（fix 分類）、カスタムヘルスチェックポートの単体テスト追加 | [詳細](https://github.com/newrelic/infrastructure-agent/releases/tag/1.78.1) |

## まとめ

本日取り上げたアップデートは1件のみで、内容は Windows 向け fluent-bit output plugin の更新（3.6.0 → 3.7.0）とテスト追加という、メンテナンス色の強いリリースです。ただし、ログ転送はログベースのアラートや障害調査の土台となるコンポーネントであるため、Windows Server 上で Infrastructure Agent のログ転送を利用しているチームは、変更内容を把握したうえで適用を計画する価値があります。

一方、Linux中心の運用環境では影響範囲が限定的であるため、緊急性は低めです。次回の定期メンテナンスサイクルに組み込む形での適用が現実的な選択肢となります。いずれにせよ、ログ監視基盤の安定性は可観測性戦略の根幹ですので、自環境への影響を見極めた上で計画的なアップグレードを進めましょう。

---

## 📚 New Relicをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17631627%2F%3Fl-id%3Dsearch-c-item-text-01" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">New Relic実践入門 第2版 オブザーバビリティの基礎と実現（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [New Relic 公式ドキュメント](https://docs.newrelic.com/)