---
title: "【AWS】2026/03/28 のアップデートまとめ"
date: 2026-03-28T08:01:26+09:00
draft: true
tags: ["aws", "gamelift", "ec2", "step-functions", "bedrock", "lambda", "management-console", "healthimaging", "ecs"]
categories: ["AWS Updates"]
summary: "2026/03/28 のAWSアップデートまとめ"
---

## はじめに

2026年3月28日、AWSから7件のアップデートが発表されました。今回は特にセキュリティとアクセス制御に関する改善が目立ち、AWS Management Consoleでのサービス・リージョン可視性制御機能の追加と、AWS HealthImagingでの研究レベル細粒度アクセス制御が注目ポイントです。また、Lambda Managed Instancesが最大32GBメモリ・16vCPUに拡張されるなど、パフォーマンス面での大幅な向上も見られます。

## 注目アップデート深掘り

### AWS Management Consoleのサービス・リージョン可視性制御機能

### なぜこのアップデートが重要なのか

大規模な組織やマルチアカウント環境において、ユーザーに対して必要最小限のサービスやリージョンのみを表示することは、セキュリティとユーザビリティの両面で重要な要件でした。従来は、IAMポリシーによる権限制御でアクセスを制限できても、Management Console上では利用不可能なサービスも表示されるため、混乱やミスオペレーションのリスクがありました。この新機能により、表示レベルでの制御が可能となり、よりクリーンで安全な管理環境を構築できるようになります。

### 具体的な設定手順

まず、AWS Management Consoleの「Unified Settings」から設定を行います：

```bash
# AWS CLIを使用した設定例
$ aws account put-alternate-contact \
    --alternate-contact-type OPERATIONS \
    --name "Operations Team" \
    --title "Cloud Operations" \
    --email-address "ops@example.com" \
    --phone-number "+1-555-0123"

# サービス可視性の設定（CLI）
$ aws organizations create-policy \
    --name "ServiceVisibilityPolicy" \
    --description "Control service visibility in console" \
    --type "SERVICE_CONTROL_POLICY" \
    --content '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Deny",
                "Action": [
                    "sagemaker:*",
                    "databrew:*"
                ],
                "Resource": "*",
                "Condition": {
                    "StringNotEquals": {
                        "aws:RequestedRegion": ["us-east-1", "ap-northeast-1"]
                    }
                }
            }
        ]
    }'
```

Terraformを使用した場合の設定例：

```hcl
# Terraform設定例
resource "aws_organizations_policy" "console_visibility" {
  name        = "console-visibility-policy"
  description = "Controls console service and region visibility"
  type        = "SERVICE_CONTROL_POLICY"

  content = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:*",
          "s3:*",
          "cloudwatch:*",
          "lambda:*"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "aws:RequestedRegion" = ["us-east-1", "ap-northeast-1", "eu-west-1"]
          }
        }
      }
    ]
  })
}

resource "aws_organizations_policy_attachment" "console_visibility" {
  policy_id = aws_organizations_policy.console_visibility.id
  target_id = var.organizational_unit_id
}
```

### 従来の方法との比較

**従来のアプローチ（IAMポリシーのみ）：**
- アクセス権限はないが、サービス一覧には表示される
- ユーザーが誤って制限されたサービスにアクセスしようとしてエラーが発生
- 新人教育時に混乱を招く可能性

**新機能を使用したアプローチ：**
- 許可されたサービス・リージョンのみが表示される
- ユーザーインターフェースがすっきりし、操作ミスが減少
- 部門や役割に応じたカスタマイズされたコンソール体験を提供

Python SDKを使用した動的な設定変更例：

```python
import boto3

def update_console_visibility(account_id, allowed_services, allowed_regions):
    """
    コンソールの可視性設定を動的に更新
    """
    client = boto3.client('organizations')
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [f"{service}:*" for service in allowed_services],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "aws:RequestedRegion": allowed_regions
                    }
                }
            }
        ]
    }
    
    try:
        response = client.create_policy(
            Name=f"console-visibility-{account_id}",
            Description="Dynamic console visibility policy",
            Type="SERVICE_CONTROL_POLICY",
            Content=json.dumps(policy_document)
        )
        return response['Policy']['PolicySummary']['Id']
    except Exception as e:
        print(f"Error creating policy: {e}")
        return None

# 使用例
allowed_services = ['ec2', 's3', 'lambda', 'cloudwatch']
allowed_regions = ['us-east-1', 'ap-northeast-1']
policy_id = update_console_visibility('123456789012', allowed_services, allowed_regions)
```

### AWS Lambda Managed Instancesの大幅な性能向上

### 拡張された性能仕様の意義

今回のアップデートで、Lambda Managed Instancesが最大32GBメモリと16vCPUまで拡張されました。これまでLambdaは軽量なワークロード向けとされていましたが、この大幅な性能向上により、従来はEC2やFargateでしか実行できなかった重い処理もサーバーレスアーキテクチャで実現できるようになります。

### 性能比較と適用シナリオ

**従来のLambda制限：**
- メモリ：最大10,240MB（10GB）
- vCPU：メモリに比例して最大6vCPU相当

**新しい制限：**
- メモリ：最大32,768MB（32GB）
- vCPU：最大16vCPU

具体的な設定例：

```python
# AWS CDKを使用した高性能Lambda関数の定義
from aws_cdk import (
    aws_lambda as _lambda,
    Duration,
    Stack
)

class HighPerformanceLambdaStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # 32GB メモリ、16 vCPU のLambda関数
        high_memory_function = _lambda.Function(
            self, "HighMemoryFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=_lambda.Code.from_asset("lambda"),
            memory_size=32768,  # 32GB
            timeout=Duration.minutes(15),
            environment={
                'PYTHONPATH': '/var/task',
                'MEMORY_SIZE': '32768'
            }
        )
```

Terraformでの設定例：

```hcl
resource "aws_lambda_function" "high_performance" {
  filename         = "lambda_function.zip"
  function_name    = "high-performance-processor"
  role            = aws_iam_role.lambda_role.arn
  handler         = "index.handler"
  runtime         = "python3.11"
  
  # 最大性能設定
  memory_size = 32768  # 32GB
  timeout     = 900    # 15分
  
  environment {
    variables = {
      MEMORY_SIZE = "32768"
      CPU_COUNT   = "16"
    }
  }
}
```

### 実際のパフォーマンステスト例

```python
import time
import psutil
import numpy as np

def handler(event, context):
    """
    高メモリ・高CPU要求ワークロードのテスト
    """
    print(f"Available memory: {context.memory_limit_in_mb}MB")
    print(f"CPU count: {psutil.cpu_count()}")
    
    # 大規模データ処理のシミュレーション
    start_time = time.time()
    
    # 20GB のデータを処理（従来のLambdaでは不可能）
    large_array = np.random.rand(2500000000)  # 約20GBの配列
    
    # 並列計算処理
    result = np.mean(large_array)
    
    processing_time = time.time() - start_time
    
    return {
        'statusCode': 200,
        'body': {
            'result': result,
            'processing_time': processing_time,
            'memory_used': psutil.virtual_memory().used / (1024**3),
            'cpu_utilization': psutil.cpu_percent(interval=1)
        }
    }
```

> **Note:** 高メモリ設定を使用する際は、コストが大幅に増加する可能性があります。必要な場面でのみ使用し、適切なタイムアウト設定でコストを制御することが重要です。

## SRE視点での活用ポイント

今回のアップデートは、SREの日常的な運用改善に直接的なインパクトをもたらします。

**AWS Management Consoleの可視性制御**は、特にマルチチーム環境での運用標準化に有効です。Terraformでインフラを管理している場合、組織のポリシーとして各チームのアクセス範囲を明確に定義し、それをコンソール表示レベルまで一貫して適用できます。障害対応時の混乱を避けるため、インシデント対応チーム向けには必要最小限のサービス（CloudWatch、EC2、RDS等）のみを表示する設定にすることで、迅速な問題特定が可能になります。

一方、導入時は段階的なアプローチが重要です。いきなり大幅な制限をかけると、既存の運用フローに支障をきたす可能性があります。まずは非本番環境で設定をテストし、チームのフィードバックを収集してから本番適用するのが安全です。

**Lambda の高性能化**については、これまでバッチジョブでECS Fargateを使用していたようなワークロードの一部をサーバーレス化できる可能性があります。特に、不定期に発生する重い処理（レポート生成、データ変換等）では、常時起動が不要なLambdaの方がコスト効率が良い場合があります。ただし、実行時間が15分を超える処理や、頻繁に実行される処理については、依然としてFargateやEC2の方が適している可能性が高いため、ワークロードの特性を十分に分析した上で判断することが重要です。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|----------|----------|------|
| Amazon GameLift | [EC2次世代インスタンスファミリーサポート拡張](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-gamelift-servers-expands-instance-support/) | EC2第5～8世代インスタンス（M、C、Rシリーズ）に対応、Intel/AMD/Gravitonプロセッサをサポート |
| AWS Step Functions | [28の新サービス統合追加](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-step-functions-sdk-integrations/) | Amazon Bedrock AgentCoreを含む28の新サービス統合により、AIワークフローの自動化を強化 |
| AWS Management Console | [サービス・リージョン可視性制御機能](https://aws.amazon.com/about-aws/whats-new/2026/03/account-customizations-console/) | アカウント設定でサービスとリージョンの表示を制御、組織的なアクセス管理を改善 |
| AWS Lambda | [32GB メモリ・16vCPU サポート](https://aws.amazon.com/about-aws/whats-new/2026/03/lambda-32-gb-memory-16-vcpus/) | Managed Instancesで大幅な性能向上、重いワークロードのサーバーレス実行が可能 |
| AWS HealthImaging | [研究レベル細粒度アクセス制御](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-healthimaging-study-level-access-control/) | DICOM研究レベルでの詳細なアクセス制御をサポート、医療データのセキュリティを強化 |
| Amazon EC2 | [U7i インスタンス欧州ミラノ展開](https://aws.amazon.com/about-aws/whats-new/2026/03/ec2-u7i-europe-milan/) | 高メモリU7i（メモリ最適化・Intel搭載）インスタンスが欧州ミラノリージョンで利用可能 |
| Amazon ECS | [GovCloud での FIPS 認定ワークロード対応](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-ecs-mi-supports-fips-graviron-gpu/) | Managed InstancesがGravitone（ARM系高性能）とGPUアクセラレーテッドインスタンスでFIPS認定ワークロードをサポート |

## まとめ

今回のアップデートは、セキュリティとパフォーマンスの両軸で大きな進歩を見せています。Management Consoleの可視性制御機能は、大規模組織でのガバナンス強化に直結し、Lambdaの高性能化はサーバーレスアーキテクチャの適用範囲を大幅に拡大します。特に、これまでサーバーレスでは難しかった重い処理が実現できるようになったことで、アーキテクチャ設計の選択肢が豊富になりました。

医療・政府機関向けのコンプライアンス対応強化も顕著で、AWS HealthImagingやECS GovCloudでのFIPS対応など、厳格な規制要件を満たすソリューションが充実してきています。これらの機能は、従来は導入が困難だった分野でのクラウド採用を後押しするものと考えられます。