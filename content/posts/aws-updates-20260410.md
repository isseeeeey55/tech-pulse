---
title: "【AWS】2026/04/10 のアップデートまとめ"
date: 2026-04-10T08:01:13+09:00
draft: false
tags: ["aws", "rds", "opensearch", "prometheus", "s3", "marketplace", "ec2", "auto-scaling"]
categories: ["AWS Updates"]
summary: "2026/04/10 のAWSアップデートまとめ"
---

![](/tech-pulse/images/aws-updates-20260410/header.png)

## はじめに

2026年4月10日のAWSアップデートは6件。目玉は AWS Marketplace Discovery API のリリースと、EC2 Capacity Manager のタグベースディメンション対応です。Discovery API はこれまで Web UI でしか取れなかった Marketplace のカタログ情報を API で取れるようになるもの。Capacity Manager のタグ対応は、最大5つのカスタムタグキーを使ってキャパシティを集計できるようになります。

## 注目アップデート深掘り

### AWS Marketplace Discovery API

Marketplace の製品検索・比較・価格確認は、これまで Web コンソールで手動操作するしかありませんでした。Discovery API でこれが API 経由で取得できるようになります。社内の調達ワークフローや FinOps 系のツールから直接 Marketplace のカタログを参照できる、というのが主な使いどころです。

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

#### 価格監視ワークフローの例

特定カテゴリの製品価格を定期的にチェックして、変動を検知するスクリプトの例：

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

### EC2 Capacity Manager のタグベースディメンション

![EC2 Capacity Manager のタグベースディメンション](/tech-pulse/images/aws-updates-20260410/capacity-manager-tags.png)

> **EC2 Capacity Manager とは？**
> EC2 のオンデマンド・スポット・予約インスタンスのキャパシティを横断的に可視化・管理するサービスです。AWS Compute Optimizer と異なり、推奨ではなく現在の使用状況の集計とアラートに特化しています。

これまで Capacity Manager の集計軸はインスタンスタイプ・AZ・プラットフォームに限られていました。今回のアップデートで、最大5つのカスタムタグキーを集計軸として追加できるようになりました。

例えば `Environment=production` と `Team=web-platform` のリソースだけを抽出してキャパシティを見る、といった分析が可能になります。Terraform での設定例：

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

### Marketplace Discovery API

監視ツールやセキュリティソリューションの選定で「カテゴリ内の主要製品の最新価格と機能を一覧化したい」というケースは多いです。これまでは Web コンソールを開いて手動で集計していたものを、API でスクリプト化できるようになります。FinOps チームの定期レポート生成にも使えるはず。

利用時の注意点として、API の呼び出しレート制限と、価格情報の更新タイミング（リアルタイムではない場合がある）は事前に確認してください。

### EC2 Capacity Manager のタグディメンション

タグキーで集計軸を増やせるようになったので、「マイクロサービス別」「環境別」「コストセンター別」など、組織の単位に合わせた粒度でキャパシティを見られるようになります。CloudWatch アラームと組み合わせれば、特定タグを持つリソース群のキャパシティ超過を検知できます。

導入のハードルは「タグが付いていること」。タグ命名規則がチーム間でバラバラだと集計軸として機能しないので、AWS Tagging Strategies のドキュメントを参考に統一しておくと良いです。

## 全アップデート一覧

> **AWS Agent Registry とは？**
> Bedrock AgentCore 配下の新サービスで、組織内で開発・運用されている AI エージェントを中央集権的に登録・検索・ガバナンスするためのレジストリです。複数チームが似たエージェントを重複開発する状況を防ぐ目的があります。

> **Amazon Managed Service for Prometheus とは？**
> AWS が提供する Prometheus 互換のマネージドメトリクスサービスです。OSS の Prometheus サーバーを自前で運用する代わりに、PromQL クエリと Prometheus データソースをマネージドで使えます。今回 OpenSearch Service との直接統合がサポートされ、OpenSearch Dashboards から PromQL を実行可能になりました。

| タイトル | 概要 |
|---------|------|
| [Amazon RDS Blue/Green Deployments now supports Amazon RDS Proxy](https://aws.amazon.com/about-aws/whats-new/2026/04/rds-proxy-blue-green/) | RDS Blue/Green DeploymentsがRDS Proxyをサポート。データベースのメジャーバージョンアップグレードやスキーマ変更を最小限のダウンタイムで実行可能 |
| [Amazon OpenSearch Service supports Managed Prometheus and agent tracing](https://aws.amazon.com/about-aws/whats-new/2026/04/opensearch-managed-prometheus-agent-tracing/) | OpenSearchがManaged Service for Prometheusと直接統合。PromQLクエリ実行やAIエージェントトレースが可能に |
| [Amazon S3 Lifecycle pauses actions on objects that are unable to replicate](https://aws.amazon.com/about-aws/whats-new/2026/03/s3-lifecycle-pauses-actions-on-objects/) | S3 Lifecycleがレプリケーション失敗オブジェクトの処理を一時停止する機能を追加。データ保護の信頼性が向上 |
| [AWS Agent Registry for centralized agent discovery and governance is now available in Preview](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-agent-registry-in-agentcore-preview/) | AWS Agent Registryがプレビューで提供開始。企業全体のAIエージェント管理と重複開発防止を実現 |
| [AWS Marketplace announces the Discovery API for programmatic access to catalog data](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-marketplace-discovery-api/) | AWS Marketplace Discovery APIが提供開始。製品情報と価格データへのプログラマティックアクセスが可能 |
| [Amazon EC2 Capacity Manager now supports tag-based dimensions](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-capacity-manager-tag-based-dimensions/) | EC2 Capacity Managerがタグベースディメンションをサポート。最大5つのカスタムタグによる詳細なキャパシティ分析が可能 |

## まとめ

Marketplace Discovery API は調達ワークフローの自動化、Capacity Manager のタグディメンションは組織単位のキャパシティ可視化、というのが今回の目玉です。OpenSearch の Managed Prometheus 統合や RDS Proxy の Blue/Green 対応も、該当ワークロードがあるなら確認しておくと良いでしょう。

AWS Agent Registry はプレビュー段階ですが、社内で AI エージェントが乱立し始めている組織には今のうちにキャッチアップしておきたい動きです。