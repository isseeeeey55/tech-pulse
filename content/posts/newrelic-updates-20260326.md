---
title: "【New Relic】2026年2-3月のアップデートまとめ"
date: 2026-03-26T09:00:00+09:00
draft: false
tags: ["newrelic", "infrastructure-agent", "sre-agent", "no-code-parsing", "pipeline-control", "opentelemetry", "nrql", "dashboards", "alerts", "logs"]
categories: ["New Relic Updates"]
summary: "Infrastructure Agent 3リリース（CVE修正・nr-control統合・EOL OS削除）と、2月のプラットフォームアップデート11件（SRE Agent・No Code Parsing・Pipeline Control等）をまとめて解説。"
---

![](/images/newrelic-updates-20260326/header.png)

## はじめに

今回は2026年2月〜3月にかけてのNew Relicアップデートをまとめてお届けします。Infrastructure Agentの3リリース（v1.72.7〜v1.72.9）に加え、2月のプラットフォームアップデート11件を取り上げます。

特に注目すべきは、CVE-2026-22184のセキュリティ修正を含むInfrastructure Agent v1.72.8と、AIによる障害調査自動化を実現するSRE Agentの登場です。また、No Code Parsingによるログ解析の大幅な効率化や、Pipeline Control Gatewayによるテレメトリデータの事前処理機能など、SREの日常業務に直結するアップデートが充実しています。

## 注目アップデート深掘り

### Infrastructure Agent v1.72.8 — CVE-2026-22184 セキュリティ修正

![Infrastructure Agent v1.72.7→v1.72.9 リリースタイムライン](/images/newrelic-updates-20260326/infra-agent-timeline.png)

Infrastructure Agent v1.72.8では、[CVE-2026-22184](https://github.com/advisories/GHSA-7687-3v4j-49fr)への対応が行われました。このセキュリティ修正は、エージェントの安全な運用を維持するために早急なアップグレードが推奨されます。

**アップグレード手順**

Linux環境の場合：

```bash
# 現在のバージョン確認
$ newrelic-infra --version

# パッケージマネージャーでアップグレード（Amazon Linux / RHEL）
$ sudo yum update newrelic-infra -y

# Ubuntu / Debian
$ sudo apt-get update && sudo apt-get install newrelic-infra -y

# アップグレード後の確認
$ newrelic-infra --version
# 1.72.8 以上であることを確認

# サービス再起動
$ sudo systemctl restart newrelic-infra
```

v1.72.9（3月23日リリース）ではさらに、`nr-control` メタデータサービスとの統合が追加され、Go 1.25.8・gRPC 1.79.3へのアップデートも含まれています。セキュリティ修正と合わせて、v1.72.9への一括アップグレードを推奨します。

v1.72.7ではEOL（End of Life）OSのサポートが削除されています。古いOSで運用している環境では、アップグレード前にサポート対象OSの確認が必要です。

### SRE Agent — AIによる障害調査の自律自動化

![SRE Agent 障害対応フローの Before / After](/images/newrelic-updates-20260326/sre-agent-before-after.png)

> **SRE Agentとは？**
> New Relicが提供するAIエージェント機能で、テレメトリデータに自然言語でアクセスし、障害の根本原因分析（RCA）と復旧推奨を自動的に行います。従来は人間が手動で行っていたダッシュボード確認→ログ調査→原因特定のプロセスを、AIが数分で自律的に実行します。

SRE Agentは2月のプラットフォームアップデートで最も注目すべき機能です。障害発生時に自然言語で状況を伝えるだけで、AIがテレメトリデータを横断的に分析し、根本原因の特定と復旧手順の提案を行います。

**従来の障害対応フローとの比較**

従来：アラート受信 → ダッシュボード確認 → ログ検索 → メトリクス相関分析 → 原因特定（30分〜数時間）

SRE Agent：アラート受信 → AIに状況を伝える → 自動分析 → 原因と復旧手順の提示（数分）

さらに、インシデントレポートの自動生成機能も備えており、ポストモーテム作成の工数も削減できます。AWS環境でECS/EKSを運用しているSREにとっては、コンテナのリスタートループやメモリリーク調査など、複雑な障害対応シナリオで特に威力を発揮するでしょう。

### No Code Parsing — 正規表現不要のログ解析ルール作成

No Code Parsingは、ログの構造化を劇的に簡素化する機能です。従来は正規表現（Grok パターン）の知識が必要だったログ解析ルールの作成が、UIで抽出したいテキストを選択するだけで完了します。

**SRE業務への影響**

アプリケーションチームから「このログからエラー率を可視化したい」と依頼された際、従来は正規表現の試行錯誤に時間を取られていました。No Code Parsingなら、サンプルログを表示してフィールドを選択するだけで解析ルールが作成できます。

特にカスタムアプリケーションのログや、標準フォーマットに準拠していないログの構造化において、大幅な工数削減が期待できます。

## SRE視点での活用ポイント

**Infrastructure Agentのアップグレード戦略**

v1.72.7でEOL OSサポートが削除されているため、アップグレードパスの確認が重要です。まずステージング環境でv1.72.9を検証し、問題なければ本番環境にローリングアップデートすることを推奨します。Terraformで管理している場合は、Launch Templateのユーザーデータでエージェントバージョンを固定できます。

**Pipeline Control Gatewayの導入検討**

> **Pipeline Control Gatewayとは？**
> テレメトリデータ（ログ、メトリクス、トレース）をNew Relicに送信する前に、サンプリング・フィルタリング・データ変換を行うゲートウェイ機能です。不要なデータを事前に除外することで、データインジェストコストを最適化できます。

大量のログやメトリクスを送信している環境では、Pipeline Control Gatewayによるコスト最適化が有効です。従来はYAMLでの設定が必要でしたが、UIからの直感的なルール管理が可能になりました。

**ダッシュボード変数の活用**

ダッシュボードの変数機能が親子関係をサポートし、チャート名への変数埋め込みも可能になりました。たとえば「リージョン → クラスター → サービス」のドリルダウンビューを1つのダッシュボードで実現できます。

```
FROM SystemSample SELECT average(cpuPercent)
WHERE clusterName = {{cluster}}
FACET hostname
TIMESERIES
```

## 全アップデート一覧

| カテゴリ | バージョン/機能 | 概要 |
|---------|----------------|------|
| [Infrastructure Agent](https://github.com/newrelic/infrastructure-agent/releases/tag/1.72.9) | v1.72.9 | nr-control メタデータサービス統合、Go 1.25.8 / gRPC 1.79.3 更新 |
| [Infrastructure Agent](https://github.com/newrelic/infrastructure-agent/releases/tag/1.72.8) | v1.72.8 | CVE-2026-22184 セキュリティ修正 |
| [Infrastructure Agent](https://github.com/newrelic/infrastructure-agent/releases/tag/1.72.7) | v1.72.7 | EOL OSサポート削除、nri-flex 1.17.5 / nri-winservices 1.4.4 更新 |
| Platform | SRE Agent | AI による障害調査の自律自動化・インシデントレポート自動生成 |
| Platform | No Code Parsing | 正規表現不要のログ解析ルール作成 |
| Platform | Notebooks | データ分析と手順書を統合する次世代ドキュメント |
| Platform | Homepage | 運用情報を集約した専用ビュー |
| Platform | Workflow Automation | Azure 連携によるノーコード自動化 |
| Platform | User Management | メール認証ベースの MFA 対応 |
| Platform | Pipeline Control Gateway | テレメトリデータの事前処理（サンプリング・フィルタリング） |
| Platform | APM Rate Sampling | 分散トレーシングのレートサンプリング（Python Agent 対応追加） |
| Platform | Infra NRDOT | OpenTelemetry 移行支援・コスト最適化 UI |
| Platform | Dashboards | 変数の親子関係・チャート名への変数埋め込み |
| Platform | Infrastructure Elasticsearch | OTel Collector ベースの Elasticsearch 統合監視 |

## まとめ

今回のアップデートは「自動化」と「ノーコード化」がキーワードです。SRE Agentによる障害調査の自動化、No Code Parsingによるログ構造化の簡素化、Pipeline Control Gatewayによるデータ管理の効率化と、SREの手作業を減らす方向のアップデートが目立ちます。

Infrastructure Agentについては、CVE-2026-22184の修正が含まれるため、v1.72.9への早期アップグレードを推奨します。EOL OSサポートの削除（v1.72.7）もあるため、アップグレード前に対象環境の確認を忘れずに。

New Relicのプラットフォーム全体として、OpenTelemetryとの統合がさらに進んでおり、ベンダーロックインを避けつつNew Relicの強力な可視化・分析機能を活用できる方向に進化しています。
