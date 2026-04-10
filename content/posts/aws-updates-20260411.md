---
title: "【AWS】2026/04/11 のアップデートまとめ"
date: 2026-04-11T08:01:26+09:00
draft: false
tags: ["aws", "cloudwatch", "bedrock", "deadline-cloud", "backup", "fsx", "billing", "cost-management", "timestream", "influxdb", "iam"]
categories: ["AWS Updates"]
summary: "2026/04/11 のAWSアップデートまとめ"
---

![](/tech-pulse/images/aws-updates-20260411/header.png)

## はじめに

2026年4月11日のAWSアップデートは7件。CloudWatch パイプラインに条件付き処理と Drop Events プロセッサが追加されたのと、Bedrock で IAM ユーザー・ロール別のコスト配分がサポートされたのが目玉です。

地味だけど Billing ダッシュボードのスケジュールメール配信や、Timestream for InfluxDB のメンテナンスウィンドウ設定も、運用面では助かるアップデートです。

## 注目アップデート深掘り

### Amazon CloudWatch パイプライン：条件付き処理とDrop Eventsプロセッサの活用

![CloudWatch パイプラインの条件付き処理によるログコスト削減](/tech-pulse/images/aws-updates-20260411/cloudwatch-pipeline.png)

CloudWatch パイプラインで、条件に基づいてプロセッサの適用を分岐できるようになりました。加えて Drop Events プロセッサが追加され、パイプライン段階で不要なログを捨てられるようになっています。従来はログが取り込まれてからフィルタリングしていたので、捨てるログにもストレージ料金がかかっていました。

**21種類のプロセッサでの条件設定パターンの検証**

まず、条件付き処理の基本的な設定方法を見てみましょう。以下はAWS CLIを使った設定例です：

```json
{
  "name": "conditional-log-pipeline",
  "processors": [
    {
      "type": "conditionalProcessor",
      "condition": "$.level == 'ERROR'",
      "processors": [
        {
          "type": "addFields",
          "fields": {
            "alert": "true",
            "priority": "high"
          }
        }
      ]
    },
    {
      "type": "dropEvents",
      "condition": "$.source == 'debug' && $.level == 'INFO'"
    }
  ]
}
```

**Drop Eventsプロセッサの具体的な実装**

新しいDrop Eventsプロセッサは、不要なログエントリを早期にフィルタリングすることでコストを削減します。Terraformでの設定例は以下の通りです：

```hcl
resource "aws_cloudwatch_log_pipeline" "security_filter" {
  name = "security-log-filter"
  
  processor {
    type = "drop_events"
    condition = jsonencode({
      and = [
        { equals = [{ var = "source" }, "security-scanner"] },
        { not = { equals = [{ var = "severity" }, "critical"] } }
      ]
    })
  }
  
  processor {
    type = "conditional"
    condition = jsonencode({
      equals = [{ var = "event_type" }, "authentication_failure"]
    })
    
    nested_processor {
      type = "add_fields"
      fields = {
        "requires_investigation" = "true"
        "escalation_level" = "2"
      }
    }
  }
}
```

**コスト削減の試算例**

例えばセキュリティログの90%が通常アクセスログ、10%が重要イベントだとします：

```bash
# 従来の方法（全ログを取り込み）
$ aws logs put-retention-policy --log-group-name /security/all-events --retention-in-days 30

# 新しい方法（重要なイベントのみ保持）
$ aws logs create-log-pipeline --pipeline-name security-critical-only \
  --processors '[{
    "type": "drop_events",
    "condition": "$.severity != \"critical\" && $.severity != \"high\""
  }]'
```

Drop Events で早期に弾ければ、取り込み量を最大90%削減できます。CloudWatch Logs の取り込み料金は $0.50/GB（東京リージョン）なので、月100GBのログなら$45/月の節約になる計算です。

### Amazon Bedrock：IAMベースのコスト配分による詳細な利用状況追跡

Bedrock の利用料を IAM ユーザー・ロール単位で分けて集計できるようになりました。これまでは AWS アカウント全体の Bedrock コストしか見えなかったので、「どのチーム/プロジェクトがどれくらい使っているか」の把握が困難でした。

**IAMプリンシパルへのタグ付けとコスト配分設定**

まず、コスト配分のためのIAMロール設定を行います：

```hcl
resource "aws_iam_role" "bedrock_project_role" {
  name = "bedrock-project-alpha"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    "Project"    = "ProjectAlpha"
    "Team"       = "AIResearch"
    "CostCenter" = "Engineering"
    "Environment" = "Production"
  }
}

resource "aws_iam_policy_attachment" "bedrock_access" {
  name       = "bedrock-project-alpha-access"
  roles      = [aws_iam_role.bedrock_project_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonBedrockFullAccess"
}
```

**Cost Explorerでの詳細分析手順**

コスト配分タグを有効化し、Cost Explorerで分析する手順は以下の通りです：

```python
import boto3

# Cost Explorerクライアントの作成
ce_client = boto3.client('ce')

# タグベースでのコスト分析
response = ce_client.get_cost_and_usage(
    TimePeriod={
        'Start': '2026-04-01',
        'End': '2026-04-30'
    },
    Granularity='DAILY',
    Metrics=['BlendedCost', 'UsageQuantity'],
    GroupBy=[
        {
            'Type': 'TAG',
            'Key': 'Project'
        },
        {
            'Type': 'TAG', 
            'Key': 'Team'
        }
    ],
    Filter={
        'Dimensions': {
            'Key': 'SERVICE',
            'Values': ['Amazon Bedrock']
        }
    }
)

# プロジェクト別コスト集計
for result in response['ResultsByTime']:
    print(f"Date: {result['TimePeriod']['Start']}")
    for group in result['Groups']:
        project = group['Keys'][0] if group['Keys'][0] != 'Project$' else 'Untagged'
        team = group['Keys'][1] if group['Keys'][1] != 'Team$' else 'Untagged'
        cost = group['Metrics']['BlendedCost']['Amount']
        print(f"  {project} ({team}): ${float(cost):.2f}")
```

**予算アラートの設定例**

プロジェクト別に予算上限を設定して、超過時にアラートを飛ばす例：

```bash
# AWS CLIでのBudget設定
$ aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "BedrockProjectAlphaBudget",
    "BudgetLimit": {
      "Amount": "1000",
      "Unit": "USD"
    },
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {
      "Service": ["Amazon Bedrock"],
      "TagKey": ["Project"],
      "TagValue": ["ProjectAlpha"]
    }
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "project-alpha-leads@company.com"
    }]
  }]'
```

> **Note:** コスト配分タグは設定後、データが反映されるまで24時間程度かかる場合があります。また、既存のリソースには遡って適用されないため、タグ付け戦略は事前に計画することが重要です。

## SRE視点での活用ポイント

CloudWatch パイプラインの条件付き処理は、ログレベルや送信元に応じてロググループを振り分けるのに使えます。例えば `ERROR` 以上だけを高コストな長期保存ロググループに送り、`DEBUG` は Drop Events で捨てる、といった構成が1つのパイプラインで実現できます。

導入時は「何を捨てるか」の判断がリスクポイント。まず Drop Events なしで条件分岐だけ試し、ログ量の内訳を可視化してから段階的に絞り込んでいくのが安全です。

Bedrock のコスト配分は、既存の IAM ロール設計にタグを足すだけで始められます。コスト配分タグの反映には24時間かかる点と、既存リソースに遡って適用されない点は覚えておいてください。組織全体で Bedrock 利用が広がっているなら、AWS Config のタグポリシーで命名規則を強制する仕組みも合わせて入れておくのがおすすめです。

## 全アップデート一覧

> **AWS Deadline Cloud とは？**
> VFX・アニメーション・映像制作向けのクラウドレンダリングサービスです。レンダーファームの構築・管理をマネージドで提供し、Autodesk Maya や SideFX Houdini などの DCCツールと連携します。

> **Amazon Timestream for InfluxDB とは？**
> InfluxDB 互換の時系列データベースをマネージドで提供するサービスです。OSS の InfluxDB を自前運用する代わりに、AWS マネージドで InfluxQL/Flux クエリが使えます。IoT データやメトリクスの蓄積に向いています。

> **Amazon FSx for NetApp ONTAP とは？**
> NetApp の ONTAP ファイルシステムを AWS 上でフルマネージド提供するサービスです。NFS/SMB/iSCSI の複数プロトコルに対応し、オンプレの NetApp ストレージからの移行先として使われます。

| サービス | アップデート内容 | リンク |
|---------|-----------------|-------|
| AWS Deadline Cloud | 複数リージョンでのモニター作成をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/deadline-cloud-monitor-creation/) |
| Amazon CloudWatch | パイプラインで条件付き処理とDrop Eventsプロセッサをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-cloudwatch-pipelines-conditional/) |
| AWS Backup | Amazon FSxサポートを5リージョンに拡大、14リージョンでクロスリージョン・アカウントコピーが利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/backup-extends-fsx-support/) |
| Amazon FSx for NetApp ONTAP | 第二世代が4つの商用リージョンとGovCloud (US)リージョンで利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/second-gen-amazon-fsx-ontap-regions/) |
| AWS Billing and Cost Management | ダッシュボードでスケジュールされたメール配信をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-billing-and-cost-management-dashboards-scheduled-email-delivery/) |
| Amazon Timestream for InfluxDB | カスタマー定義メンテナンスウィンドウをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/timestream-influxdb-maintenance-windows/) |
| Amazon Bedrock | IAMユーザーとロール別のコスト配分をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/bedrock-iam-cost-allocation/) |

## まとめ

CloudWatch パイプラインの条件付き処理は「ログコスト削減」、Bedrock の IAM コスト配分は「AI コストの可視化」と、どちらもコスト関連のアップデートが中心です。Billing ダッシュボードのスケジュールメール配信と合わせて、FinOps 周りの改善が多い日でした。

FSx for NetApp ONTAP の第二世代リージョン追加や Deadline Cloud のモニター対応拡大は、該当ワークロードがあれば確認しておいてください。