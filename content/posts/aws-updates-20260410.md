---
title: "【AWS】2026/04/10 のアップデートまとめ"
date: 2026-04-10T08:01:13+09:00
draft: true
tags: ["aws", "rds", "opensearch", "prometheus", "s3", "marketplace", "ec2", "auto-scaling"]
categories: ["AWS Updates"]
summary: "2026/04/10 のAWSアップデートまとめ"
---

## はじめに

2026年4月10日は、AWSから6件のアップデートが発表されました。今回の目玉は、AWS Marketplace Discovery APIとEC2 Capacity Managerのタグベース機能拡張です。特にMarketplace Discovery APIは、AWS Marketplaceの製品情報にプログラムでアクセスできる新しいAPIとして、調達プロセスの自動化に大きな可能性を秘めています。また、EC2 Capacity Managerのタグベースディメンション対応により、より細かい粒度でのリソース管理が可能になっています。

## 注目アップデート深掘り

### AWS Marketplace Discovery API: プログラマティック調達の新時代

AWS Marketplace Discovery APIの登場は、企業の調達プロセスに革命をもたらす可能性があります。このAPIにより、従来は手動で行っていたMarketplace製品の検索・比較・価格確認が、すべてプログラムで自動化できるようになりました。

#### APIの基本的な使用方法

まず、必要なIAM権限を設定する必要があります。Discovery APIを使用するには、`aws-marketplace:DescribeEntity`権限が必要です：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:DescribeEntity",
        "aws-marketplace:ListEntities"
      ],
      "Resource": "*"
    }
  ]
}
```

基本的なAPIコールの例を見てみましょう：

```bash
$ aws marketplace-catalog list-entities \
    --catalog "AWSMarketplace" \
    --entity-type "SaaSProduct" \
    --filter-list Name="ProductTitle",ValueList="analytics" \
    --region us-east-1
```

Python SDKを使用した場合の例：

```python
import boto3

client = boto3.client('marketplace-catalog', region_name='us-east-1')

response = client.list_entities(
    Catalog='AWSMarketplace',
    EntityType='SaaSProduct',
    FilterList=[
        {
            'Name': 'ProductTitle',
            'ValueList': ['analytics', 'monitoring']
        }
    ]
)

for entity in response['EntitySummaryList']:
    print(f"Product: {entity['Name']}")
    print(f"Entity ID: {entity['EntityId']}")
```

#### 実践的な活用シナリオ：社内調達システムとの統合

このAPIの真価は、既存の調達システムやワークフローとの統合にあります。例えば、定期的に特定カテゴリの製品価格を監視し、価格変動を検知するシステムを構築できます：

```python
import boto3
import json
from datetime import datetime

def monitor_marketplace_prices(product_categories):
    client = boto3.client('marketplace-catalog')
    results = []
    
    for category in product_categories:
        entities = client.list_entities(
            Catalog='AWSMarketplace',
            EntityType='SaaSProduct',
            FilterList=[{'Name': 'Category', 'ValueList': [category]}]
        )
        
        for entity in entities['EntitySummaryList']:
            # 詳細情報と価格情報を取得
            details = client.describe_entity(
                Catalog='AWSMarketplace',
                EntityId=entity['EntityId']
            )
            
            results.append({
                'timestamp': datetime.now().isoformat(),
                'category': category,
                'product_name': entity['Name'],
                'pricing_details': details['Details']
            })
    
    return results
```

### EC2 Capacity Manager: タグベース管理で運用効率を向上

EC2 Capacity Managerのタグベースディメンション対応により、従来のインスタンスタイプやAZベースの管理から、ビジネス要件に基づいた管理への転換が可能になりました。

#### カスタムタグディメンションの設定

最大5つのカスタムタグキーを有効化できる新機能を活用し、環境別・チーム別の詳細な分析が可能です。Terraformを使用した設定例：

```hcl
resource "aws_ec2_capacity_reservation" "web_tier_reservation" {
  instance_type     = "m7i.large"
  instance_platform = "Linux/UNIX"
  availability_zone = "us-west-2a"
  instance_count    = 10

  tags = {
    Environment = "production"
    Team        = "web-platform"
    CostCenter  = "engineering"
    Project     = "user-portal"
    Owner       = "platform-team"
  }
}

resource "aws_instance" "web_servers" {
  count         = 3
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "m7i.large"
  
  tags = {
    Environment = "production"
    Team        = "web-platform"
    CostCenter  = "engineering"
    Project     = "user-portal"
    Owner       = "platform-team"
  }
}
```

#### 分析ワークフローの実装

タグベースの分析を行うスクリプト例：

```bash
# 環境別キャパシティ使用状況の確認
$ aws ec2 describe-capacity-reservations \
    --filters "Name=tag:Environment,Values=production" \
    --query 'CapacityReservations[*].{InstanceType:InstanceType,Count:TotalInstanceCount,Available:AvailableInstanceCount,Environment:Tags[?Key==`Environment`].Value|[0]}'

# コストセンター別の詳細分析
$ aws ec2 describe-instances \
    --filters "Name=instance-state-name,Values=running" "Name=tag:CostCenter,Values=engineering" \
    --query 'Reservations[*].Instances[*].{InstanceId:InstanceId,Type:InstanceType,Team:Tags[?Key==`Team`].Value|[0],Project:Tags[?Key==`Project`].Value|[0]}'
```

> **Note:** M7iインスタンス（汎用コンピューティング最適化、第4世代Intel Xeonスケーラブルプロセッサ搭載）は、バランスの取れたパフォーマンスを提供し、Webアプリケーションや中規模データベースに適しています。

## SRE視点での活用ポイント

### Marketplace Discovery APIの運用活用

SREチームにとって、AWS Marketplace Discovery APIは調達プロセスの自動化だけでなく、監視ツールやセキュリティソリューションの選定プロセスを大幅に効率化する可能性があります。例えば、新しい監視要件が発生した際に、適切なソリューションを自動で検索・比較するワークフローを構築できます。

Terraformで管理しているインフラがあれば、必要なツールの選定から調達までのプロセスをコード化し、インフラの変更に合わせて自動的に必要なソフトウェアを特定できます。ただし、APIの利用制限や価格情報の更新頻度について事前に確認し、過度な頻度での呼び出しを避ける設計が必要です。

### EC2 Capacity Managerの戦略的活用

タグベースディメンションの導入により、SRE業務における容量計画がより精密になります。従来の「全体のキャパシティ使用率」ではなく、「マイクロサービス別」「環境別」「重要度別」といった細かい粒度での分析が可能になります。

CloudWatchアラームと組み合わせることで、特定のタグを持つリソース群のキャパシティが閾値を超えた際に自動的に通知し、さらにはAuto Scalingグループの設定を動的に調整することも考えられます。導入時は、既存のタギング戦略の見直しと、チーム間でのタグ命名規則の統一が重要なポイントとなります。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [Amazon RDS Blue/Green Deployments now supports Amazon RDS Proxy](https://aws.amazon.com/about-aws/whats-new/2026/04/rds-proxy-blue-green/) | RDS Blue/Green DeploymentsがRDS Proxyをサポート。データベースのメジャーバージョンアップグレードやスキーマ変更を最小限のダウンタイムで実行可能 |
| [Amazon OpenSearch Service supports Managed Prometheus and agent tracing](https://aws.amazon.com/about-aws/whats-new/2026/04/opensearch-managed-prometheus-agent-tracing/) | OpenSearchがManaged Service for Prometheusと直接統合。PromQLクエリ実行やAIエージェントトレースが可能に |
| [Amazon S3 Lifecycle pauses actions on objects that are unable to replicate](https://aws.amazon.com/about-aws/whats-new/2026/03/s3-lifecycle-pauses-actions-on-objects/) | S3 Lifecycleがレプリケーション失敗オブジェクトの処理を一時停止する機能を追加。データ保護の信頼性が向上 |
| [AWS Agent Registry for centralized agent discovery and governance is now available in Preview](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-agent-registry-in-agentcore-preview/) | AWS Agent Registryがプレビューで提供開始。企業全体のAIエージェント管理と重複開発防止を実現 |
| [AWS Marketplace announces the Discovery API for programmatic access to catalog data](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-marketplace-discovery-api/) | AWS Marketplace Discovery APIが提供開始。製品情報と価格データへのプログラマティックアクセスが可能 |
| [Amazon EC2 Capacity Manager now supports tag-based dimensions](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-capacity-manager-tag-based-dimensions/) | EC2 Capacity Managerがタグベースディメンションをサポート。最大5つのカスタムタグによる詳細なキャパシティ分析が可能 |

## まとめ

今回のアップデートは、AWS利用における「自動化」と「詳細な可視化」の両面を強化する内容となっています。特にMarketplace Discovery APIは、クラウド調達プロセスのデジタル変革を促進し、EC2 Capacity Managerのタグ対応は、より戦略的なリソース管理を可能にします。

これらの機能は単体でも価値がありますが、既存のワークフローや監視システムと統合することで、その真価を発揮します。SREチームにとっては、運用の自動化と精密な監視の両立を実現する重要なツールとなるでしょう。