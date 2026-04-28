---
title: "【AWS】2026/04/26 のアップデートまとめ"
date: 2026-04-26T08:01:32+09:00
draft: false
tags: ["aws", "lambda", "kafka", "msk", "cloudwatch", "cloudformation"]
categories: ["AWS Updates"]
summary: "2026/04/26 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260426/header.png)

## はじめに

2026年4月26日の AWS アップデートは 1 件。AWS Lambda の Kafka イベントソースマッピング（ESM）に対する「プロビジョニングモード」が、アジア太平洋（台北）、AWS GovCloud（US-East）、AWS GovCloud（US-West）の 3 リージョンに展開されました。

> **Kafka ESM（イベントソースマッピング）とは？**
> Lambda が Kafka トピックからメッセージを取得してハンドラ関数に渡す仕組みです。Lambda 側がポーリングを担当し、メッセージをバッチでまとめて受け取ります。Amazon MSK（マネージド Kafka サービス）と自社ホスティングの Kafka クラスタの両方に対応しています。

プロビジョニングモードは、イベントポーラーの最小数・最大数を事前設定してリソースを確保する機能です。ピーク時間帯が読めるワークロードかどうかがオンデマンドモードとの使い分けの基準になります。

## 注目アップデート深掘り

### Lambda Kafka ESM プロビジョニングモード：トラフィック急増対応の新手法

#### オンデマンドモードとプロビジョニングモードの違い

従来のオンデマンドモードでは、Kafkaからのイベント取得に必要なポーリングリソースが動的に割り当てられるため、予測不可能なトラフィック急増時に遅延が発生する可能性がありました。市場開場時の金融取引データ、特定イベント時のアクセス集中、IoTセンサーの一斉データ送信など、ビジネスクリティカルなシナリオでは、このような遅延は深刻な影響を及ぼします。

プロビジョニングモードでは、イベントポーラーの最小数と最大数を事前に設定することで、必要なリソースを確保し、高いレスポンス性能と拡張性を実現します。これにより、トラフィックのピークに対して確実に対応できる予測可能な処理能力が得られます。

#### イベントポーラー数の設定とスループット制御

> **EPU（Event Poller Unit）とは？**
> Lambda の Kafka ESM でイベントを取得する並列処理ユニット。Provisioned Mode で導入された課金・管理の単位で、最小値と最大値を設定することでポーリングリソースの確保量をコントロールできます。

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
    --scaling-config '{"MaximumConcurrency":10}' \
    --provisioned-poller-config '{"MinimumPollers":2,"MaximumPollers":10}'
```

この設定により、常時2つのイベントポーラーが起動し、負荷に応じて最大10まで自動拡張されます。`MaximumConcurrency` は Lambda 関数の同時実行数の上限、`MinimumPollers`/`MaximumPollers` はイベント取得のためのポーリングリソース数を制御します。

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

> **Amazon MSK（Managed Streaming for Apache Kafka）とは？**
> AWS が提供するフルマネージドの Kafka クラスタサービス。Kafka ブローカーのインフラ管理が不要で、クラスタの ARN を指定するだけで Lambda ESM から接続できます。

このプロビジョニングモードは、Amazon MSK だけでなく、自社でホスティングするKafkaクラスタにも対応しています。これにより、既存のKafkaインフラをそのまま活用しながら、Lambdaによる処理のスループット最適化が実現できます。

自社管理Kafkaの場合、VPC設定やセキュリティグループの構成が適切に行われていることが前提となります。MSKを使用する場合は、クラスタのARNを指定するだけで簡単に設定できます。

#### 新リージョンでの利用価値

今回対応が追加された台北リージョンは、日本を含むアジア太平洋地域での低レイテンシアクセスが求められるアプリケーションに有効です。また、GovCloudリージョンは、米国政府機関や規制の厳しい業界でのコンプライアンス要件を満たすシステム構築に不可欠です。これらのリージョンでプロビジョニングモードが利用可能になったことで、地理的要件とパフォーマンス要件を同時に満たすアーキテクチャが実現できます。

## SRE視点での活用ポイント

プロビジョニングモードはリソースを常時確保する設計なので、事前にトラフィックパターンを把握しておかないと、コストを払っても効果が出ない設定になりがちです。

**トラフィックパターンの把握と EPU 設定：** CloudWatch Metrics で Kafka ESM の受信イベント数・処理レイテンシ・スロットリングエラーを確認し、ピーク時間帯の規模を掴んでから最小 EPU を設定するのが基本です。営業時間帯の明確なピークや月末バッチ処理のような予測可能な集中であれば、プロビジョニングモードが向いています。最大 EPU に達した状態が続くなら設定値の見直しサインで、Consumer Lag メトリクスと合わせて監視するとコスト超過前に気付けます。

**コストと IaC 管理：** EPU 単位の課金が発生するため、Cost Explorer でオンデマンドとの比較を定期的にやっておくと判断しやすくなります。Terraform で Lambda ESM を管理している場合、`provisioned_poller_config` ブロックを追加するだけで設定できます。ステージング環境で負荷テストをしてから本番に適用する流れが安全です。

**リスクと注意点：** トラフィックが少ない時間帯でも最小 EPU 分のコストが発生します。最大 EPU の上限が低すぎるとスロットリングが残るため、初期設定後の数日間はメトリクスを確認し、閾値を調整してください。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Lambda Provisioned Mode for Kafka event source mappings (ESMs) now available in AWS Asia Pacific (Taipei) and AWS GovCloud (US) Regions](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-Lambda-provisioned-esm-region-expansion/) | Lambda の Kafka ESM プロビジョニングモードが台北、GovCloud US-East、US-West リージョンで利用可能に。イベントポーラーの最小数・最大数を設定してスループットを事前確保し、トラフィック急増に対応。MSK・自社管理 Kafka の両方をサポートし、Event Poller Unit (EPU) で課金。 |

## まとめ

機能の新設ではなく、既存のプロビジョニングモードが台北・GovCloud US-East/US-West の 3 リージョンに展開されたアップデートです。

プロビジョニングモードを選ぶ基準はトラフィックパターンの予測可能性です。ピーク時間帯が読めるワークロードなら EPU を事前確保することで遅延を抑えられますが、不規則なトラフィックにはオンデマンドの方がコスト効率が良くなります。

台北リージョンはアジア太平洋向けの低レイテンシ要件の案件、GovCloud は米国政府機関・規制業界の案件で対象になるリージョンです。Terraform / CloudFormation での設定変更は `ProvisionedPollerConfig` ブロックの追加で済むため、IaC 管理済みなら切り替えコストは低いです。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)