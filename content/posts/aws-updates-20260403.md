---
title: "【AWS】2026/04/03 のアップデートまとめ"
date: 2026-04-03T08:01:12+09:00
draft: false
tags: ["aws", "cloudwatch", "elasticache", "directconnect", "ecs", "sagemaker", "ses", "eks", "lightsail", "deadline-cloud"]
categories: ["AWS Updates"]
summary: "2026/04/03 のAWSアップデートまとめ。ElastiCache ServerlessのIPv6対応、CloudWatch OTelメトリクス、Lightsailコンピュート最適化インスタンスなど10件"
---

![](/tech-pulse/images/aws-updates-20260403/header.png)

## はじめに

2026年4月3日のAWSアップデートは10件です。ElastiCache ServerlessのIPv6・デュアルスタック対応、CloudWatchのOpenTelemetryメトリクスサポート、SageMaker Data Agentの日本・オーストラリア向け地域推論などが含まれます。Lightsailにコンピュート最適化インスタンスが追加されたのも地味に便利です。

## 注目アップデート深掘り

### Amazon ElastiCache Serverless の IPv6・デュアルスタック接続対応

![ElastiCache Serverless IPv6 移行パス](/tech-pulse/images/aws-updates-20260403/ipv6-migration.png)

ElastiCache Serverless が IPv6 およびデュアルスタック接続をサポートしました。従来の IPv4 のみという制約がなくなり、IPv6 移行を進めている環境でもキャッシュレイヤーが足枷になりません。

デュアルスタック接続では IPv4 と IPv6 の両方のエンドポイントが提供されます。レガシーシステムを維持しつつ、新しい IPv6 対応アプリケーションも同時に接続可能。段階的な移行に向いています。

```bash
# デュアルスタックでServerlessキャッシュを作成
$ aws elasticache create-serverless-cache \
  --serverless-cache-name my-dualstack-cache \
  --engine redis \
  --major-engine-version 7 \
  --cache-usage-limits DataStorage={Maximum=10,Unit=GB} \
  --subnet-ids subnet-12345678 \
  --security-group-ids sg-abcdef12 \
  --network-type dual-stack
```

IPv4 → デュアルスタック → IPv6 のように段階的に切り替えれば、ダウンタイムなしで移行できます。CloudWatch で IPv4/IPv6 それぞれのトラフィックを監視しておくと、移行の進捗が可視化できて安心です。

### SageMaker Data Agent の日本・オーストラリア向け地域推論

> **SageMaker Data Agentとは？**
> Amazon Bedrockのモデルと連携して、構造化・非構造化データに対する推論を実行するマネージドサービスです。データソースへの接続とプロンプト実行をサーバーレスで処理します。

SageMaker Data Agent が日本（ap-northeast-1）とオーストラリア向けの地域特化推論に対応しました。データが各地域内で処理され、クロスボーダーでのデータ移転を回避できます。

個人情報保護法や金融庁ガイドラインに準拠する必要がある場合、データが日本国内で処理される保証は実務上の必須要件。SageMaker コンソールまたは API でリージョン制限付きの Data Agent を作成することで、地域内処理を強制できます。ただし地域制限により利用可能なモデルや機能に制約が生じる場合があるので、導入前のパフォーマンス検証は忘れずに。

## SRE視点での活用ポイント

ElastiCache の IPv6 対応は、インフラの段階的移行に使えます。デュアルスタックにしておけば、既存の IPv4 アプリケーションを稼働させたまま新しいサービスを IPv6 で接続可能。Terraform で管理している場合は `network_type` パラメータの変更だけで切り替えられます。

SageMaker Data Agent の地域制限は、障害対応ランブックにデータ処理の地域チェックを組み込む際に有用です。ただし利用可能なモデルに制約が出る場合があるため、要件に合うかは事前に確認しておくべきです。

## 全アップデート一覧

> **AWS Deadline Cloudとは？**
> VFX、アニメーション、映画制作などのレンダリングワークロードを管理するフルマネージドサービスです。レンダーファームの構築・管理を簡素化し、必要なときだけコンピュートリソースをスケールできます。

| サービス | アップデート内容 |
|---------|------------------|
| [Amazon CloudWatch](https://aws.amazon.com/about-aws/whats-new/2026/04/cloudwatch-otel-container-insights-eks/) | OTel Container Insights for Amazon EKS (Preview) |
| [Amazon ElastiCache](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-elasticache-serverless-ipv6-dual-stack/) | Serverless で IPv6 およびデュアルスタック接続をサポート |
| [AWS Direct Connect](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-direct-connect-100g-auckland/) | オークランドで100G接続を拡張 |
| [Amazon CloudWatch](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-cloudwatch-cloudfront-enablement/) | CloudFrontログと3つのリソースタイプで自動有効化を拡張 |
| [Amazon CloudWatch](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-cloudwatch-opentelemetry-metrics/) | OpenTelemetryメトリクスをパブリックプレビューでサポート |
| [Amazon ECS](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ecs-managed-daemons/) | ECS Managed Instances向けManaged Daemonsを発表 |
| [Amazon SageMaker](https://aws.amazon.com/about-aws/whats-new/2026/03/sage-maker-da-infr-jp-au/) | Data Agent が日本・オーストラリア向け地域特化推論をサポート |
| [Amazon SES](https://aws.amazon.com/about-aws/whats-new/2026/04/ses-mail-manager-introduces-new-features/) | Mail Manager でセキュリティとメール処理の新機能を追加 |
| [Amazon Lightsail](https://aws.amazon.com/about-aws/whats-new/2026/04/lightsail-compute-optimized-instances/) | コンピュート最適化インスタンスバンドルを提供開始（最大72 vCPU、15リージョン） |
| [AWS Deadline Cloud](https://aws.amazon.com/about-aws/whats-new/2026/04/deadline-cloud-job-scheduling/) | キューのジョブスケジューリングモード（Priority FIFO / Balanced / Weighted）を設定可能に |

## まとめ

10件中、ElastiCache ServerlessのIPv6対応とSageMaker Data Agentの地域推論が実務インパクトとしては大きいです。前者はIPv6移行計画にキャッシュレイヤーを組み込めるようになった点、後者はデータ主権要件を満たしながらAI推論を使える点がポイント。Lightsailのコンピュート最適化インスタンス（最大72 vCPU）も、バッチ処理やエンコーディング用途で選択肢が広がります。
