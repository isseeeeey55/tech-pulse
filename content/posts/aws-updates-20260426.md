---
title: "【AWS】2026/04/26 のアップデートまとめ"
date: 2026-04-26T08:01:32+09:00
draft: true
tags: ["aws", "lambda", "kafka", "msk", "cloudwatch", "cloudformation"]
categories: ["AWS Updates"]
summary: "2026/04/26 のAWSアップデートまとめ"
---

# AWS Lambda Provisioned Mode for Kafka ESMの詳細解説

## はじめに

2026年4月26日のAWSアップデートでは、AWS Lambda の Kafka イベントソースマッピング（ESM）に対する「プロビジョニングモード」が、アジア太平洋（台北）、AWS GovCloud（US-East）、AWS GovCloud（US-West）の3つのリージョンで新たに利用可能になりました。

このアップデートは、Kafkaと連携したイベント駆動型アプリケーションにおいて、トラフィック急増時のスループット最適化を実現する重要な機能拡張です。本記事では、プロビジョニングモードの技術的詳細と、SRE視点での活用シナリオを詳しく解説します。

## 注目アップデート深掘り

### Lambda Kafka ESM プロビジョニングモード：トラフィック急増対応の新手法

#### なぜこのアップデートが重要なのか

従来のオンデマンドモードでは、Kafkaからのイベント取得に必要なポーリングリソースが動的に割り当てられるため、予測不可能なトラフィック急増時に遅延が発生する可能性がありました。市場開場時の金融取引データ、特定イベント時のアクセス集中、IoTセンサーの一斉データ送信など、ビジネスクリティカルなシナリオでは、このような遅延は深刻な影響を及ぼします。

プロビジョニングモードでは、イベントポーラーの最小数と最大数を事前に設定することで、必要なリソースを確保し、高いレスポンス性能と拡張性を実現します。これにより、トラフィックのピークに対して確実に対応できる予測可能な処理能力が得られます。

#### イベントポーラー数の設定とスループット制御

プロビジョニングモードの核心は、**Event Poller Unit (EPU)** という新しい課金単位を用いたリソース管理です。EPUはKafkaからイベントを取得する並列処理ユニットを表し、最小値と最大値を指定することで、以下のような細かいスループット制御が可能になります。

**設定の考え方：**

- **最小EPU**: 常時確保しておくポーリングリソース数。トラフィックがない時間帯でも維持されるため、瞬時にイベント処理を開始できる
- **最大EPU**: トラフィック急増時にスケールアウトできる上限。コスト制御とパフォーマンスのバランスを取るための設定

例えば、通常時は最小EPU=2で待機し、ピーク時には最大EPU=10まで自動拡張することで、コストを抑えながら急激な負荷増にも対応できます。

#### 設定方法の実例

AWS CLI を使用した Kafka ESM のプロビジョニングモード設定例：

```bash
$ aws lambda create-event-source-mapping \
    --function-name my-kafka-processor \
    --event-source-arn arn:aws:kafka:ap-northeast-1:123456789012:cluster/my-msk-cluster/abcd1234-5678-90ab-cdef-EXAMPLE11111 \
    --topics my-topic \
    --starting-position LATEST \
    --scaling-config '{"MaximumConcurrency":10,"MinimumConcurrency":2}' \
    --provisioned-poller-config '{"MinimumPollers":2,"MaximumPollers":10}'
```

この設定により、常時2つのイベントポーラーが起動し、負荷に応じて最大10まで自動拡張されます。`MaximumConcurrency` は Lambda 関数の同時実行数、`MinimumPollers`/`MaximumPollers` はイベント取得のためのポーリングリソース数を制御します。

CloudFormation での定義例：

```yaml
MyKafkaEventSourceMapping:
  Type: AWS::Lambda::EventSourceMapping
  Properties:
    FunctionName: !Ref MyLambdaFunction
    EventSourceArn: !Ref MyMSKCluster
    Topics:
      - my-topic
    StartingPosition: LATEST
    ScalingConfig:
      MaximumConcurrency: 10
      MinimumConcurrency: 2
    ProvisionedPollerConfig:
      MinimumPollers: 2
      MaximumPollers: 10
```

#### オンデマンドモードとの比較

**オンデマンドモード：**
- イベントポーラーが動的に割り当てられる
- 初回起動時やトラフィック急増時にコールドスタートに近い遅延が発生する可能性
- 低トラフィック時はコスト効率が良い
- 予測不可能な負荷パターンに対して柔軟に対応

**プロビジョニングモード：**
- 最小EPUが常時確保されるため、即座にイベント処理を開始可能
- トラフィック急増時でも事前確保されたリソースで迅速に対応
- EPU単位で利用量に応じた課金が発生
- 予測可能なピーク時間帯を持つワークロードに最適

#### MSKと自社管理Kafkaの両対応

このプロビジョニングモードは、Amazon MSK（Managed Streaming for Apache Kafka）だけでなく、自社でホスティングするKafkaクラスタにも対応しています。これにより、既存のKafkaインフラをそのまま活用しながら、Lambdaによる処理のスループット最適化が実現できます。

自社管理Kafkaの場合、VPC設定やセキュリティグループの構成が適切に行われていることが前提となります。MSKを使用する場合は、クラスタのARNを指定するだけで簡単に設定できます。

#### 新リージョンでの利用価値

今回対応が追加された台北リージョンは、日本を含むアジア太平洋地域での低レイテンシアクセスが求められるアプリケーションに有効です。また、GovCloudリージョンは、米国政府機関や規制の厳しい業界でのコンプライアンス要件を満たすシステム構築に不可欠です。これらのリージョンでプロビジョニングモードが利用可能になったことで、地理的要件とパフォーマンス要件を同時に満たすアーキテクチャが実現できます。

## SRE視点での活用ポイント

プロビジョニングモードは、SREが直面する「予測可能なピーク対応」と「コスト最適化」のバランスを取るための有効なツールとなります。

**トラフィックパターンの可視化が前提：** まず、CloudWatch Metrics を活用して Kafka ESM のメトリクス（受信イベント数、処理レイテンシ、スロットリングエラー）を継続的に監視し、トラフィックのパターンを把握することが重要です。例えば、営業時間帯に明確なピークが存在する場合や、月末・月初に処理量が増加するパターンが見られる場合、プロビジョニングモードの最小EPUをそのピーク時間帯の需要に合わせて設定することで、遅延を防ぎつつ無駄なリソース確保を避けられます。

**アラート設計との連携：** CloudWatch アラームで EPU の使用率や Lambda の同時実行数、エラー率を監視し、最大EPUに達している状態が続く場合は設定値の見直しをトリガーするようなランブックを整備しておくと、継続的な改善サイクルが回ります。また、Kafka のコンシューマーラグ（Consumer Lag）メトリクスと組み合わせることで、イベント処理の遅延を早期に検知できます。

**コスト管理の観点：** EPU単位での課金が発生するため、Cost Explorer や Budgets を用いてプロビジョニングモードのコストを可視化し、オンデマンドモードとの比較を定期的に行うことが推奨されます。トラフィックが安定している場合や、ピーク時間が短い場合は、最小EPUを低めに設定し、オンデマンドモードとのハイブリッド運用も検討できます。

**Terraformでのインフラコード化：** Terraform で Lambda ESM を管理している場合、`provisioned_poller_config` ブロックを追加することで、プロビジョニングモードの設定を Infrastructure as Code として管理できます。これにより、環境ごとの設定差分を明確にし、本番環境への適用前にステージング環境でのパフォーマンステストを実施するといった、堅牢なデプロイフローが構築できます。

**リスクと注意点：** プロビジョニングモードは常時リソースを確保するため、トラフィックが極端に少ない時間帯でもコストが発生します。また、最大EPUの設定が不適切だと、スロットリングが発生してイベント処理が遅延する可能性があるため、初期設定後も継続的なモニタリングとチューニングが必要です。負荷テストツールを用いて、実際のピーク時を模擬した検証を行い、適切な閾値を見極めることが成功の鍵となります。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Lambda Provisioned Mode for Kafka event source mappings (ESMs) now available in AWS Asia Pacific (Taipei) and AWS GovCloud (US) Regions](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-Lambda-provisioned-esm-region-expansion/) | Lambda の Kafka ESM プロビジョニングモードが台北、GovCloud US-East、US-West リージョンで利用可能に。イベントポーラーの最小数・最大数を設定してスループットを事前確保し、トラフィック急増に対応。MSK・自社管理 Kafka の両方をサポートし、Event Poller Unit (EPU) で課金。 |

## まとめ

今回のアップデートは、Kafkaを活用したイベント駆動型アーキテクチャにおいて、パフォーマンスとコストのバランスを細かく制御できる選択肢を提供するものです。特に、予測可能なトラフィックパターンを持つシステムや、レイテンシ要件が厳しいビジネスクリティカルなワークロードにおいて、プロビジョニングモードは大きな価値を発揮します。

新たに対応した台北およびGovCloudリージョンでの利用により、地理的要件やコンプライアンス要件を満たしながら、高いパフォーマンスを実現できるようになりました。SREとしては、既存のモニタリング・アラート基盤と連携させながら、継続的な改善サイクルの中でこの機能を活用していくことが重要です。

CloudFormationやTerraformを用いたインフラコード化により、設定の再現性と可視性を確保しつつ、実際のトラフィックパターンに基づいたチューニングを行うことで、信頼性とコスト効率の両立が実現できるでしょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)