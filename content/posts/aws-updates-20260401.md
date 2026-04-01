---
title: "【AWS】2026/04/01 のアップデートまとめ"
date: 2026-04-01T08:01:22+09:00
draft: false
tags: ["aws", "s3", "marketplace", "flink", "deadline-cloud", "aurora", "devops", "ecs", "private-ca", "security-hub", "cloudwatch", "healthomics", "iam", "vpc"]
categories: ["AWS Updates"]
summary: "2026/04/01 のAWSアップデートまとめ。CloudWatchマルチアカウントログ一元化、Aurora DSQL .NET/Rustコネクタ、DevOpsエージェントGA、Security Agentペネトレーションテストなど13件"
---

![](/tech-pulse/images/aws-updates-20260401/header.png)

## はじめに

2026年4月1日のAWSアップデートは13件。CloudWatchのマルチアカウントログ一元化とAurora DSQLの.NET/Rustコネクタが実務的に刺さる内容。DevOpsエージェントのGA、Security Agentのペネトレーションテスト機能も出揃った。

## 注目アップデート深掘り

### Amazon CloudWatch マルチアカウントログ一元化

複数アカウント・リージョンにまたがるログ管理は、各環境に個別にアクセスして確認する必要があった。この機能でデータソース名と種類に基づく自動識別が入り、CloudTrail、VPC Flow Logs、EKS Audit Logsなどを一箇所で管理できるようになる。

組織レベルでのログ集約の設定例：

```bash
$ aws logs create-log-group --log-group-name "/aws/centralized/security-logs" \
    --retention-in-days 365
$ aws logs put-destination \
    --destination-name "MultiAccountLogDestination" \
    --target-arn "arn:aws:logs:us-east-1:123456789012:log-group:/aws/centralized/security-logs" \
    --role-arn "arn:aws:iam::123456789012:role/CloudWatchLogsRole"
```

Terraformで書くとこうなる：

```hcl
resource "aws_cloudwatch_log_group" "centralized_logs" {
  name              = "/aws/centralized/multi-account-logs"
  retention_in_days = 365

  tags = {
    Environment = "production"
    Purpose     = "centralized-logging"
  }
}

resource "aws_cloudwatch_log_destination" "cross_account_destination" {
  name       = "CentralizedLogDestination"
  role_arn   = aws_iam_role.cloudwatch_logs_role.arn
  target_arn = aws_cloudwatch_log_group.centralized_logs.arn
}

resource "aws_cloudwatch_log_destination_policy" "cross_account_policy" {
  destination_name = aws_cloudwatch_log_destination.cross_account_destination.name
  access_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = ["arn:aws:iam::${var.source_account_id}:root"]
        }
        Action   = "logs:PutSubscriptionFilter"
        Resource = "arn:aws:logs:*:${data.aws_caller_identity.current.account_id}:destination:CentralizedLogDestination"
      }
    ]
  })
}
```

以前は各アカウントで個別にログ検索し、関連イベントを手動で紐付けていた。データソース識別で関連ログが自動グループ化されるので、セキュリティインシデント調査のときに効く。

### Aurora DSQL .NET・Rust コネクタ

Aurora DSQLに.NETとRust向けのコネクタが追加された。静的な認証情報を使わず、IAMベースの動的トークン生成で接続する方式。

.NETでの実装例：

```csharp
using Amazon.DSQL;
using Npgsql;

public class DSQLConnection
{
    private readonly IAmazonDSQL _dsqlClient;
    private readonly string _clusterEndpoint;
    
    public DSQLConnection(IAmazonDSQL dsqlClient, string clusterEndpoint)
    {
        _dsqlClient = dsqlClient;
        _clusterEndpoint = clusterEndpoint;
    }
    
    public async Task<NpgsqlConnection> CreateConnectionAsync()
    {
        var tokenRequest = new GenerateConnectAuthTokenRequest
        {
            ClusterEndpoint = _clusterEndpoint,
            Region = "us-east-1"
        };
        
        var tokenResponse = await _dsqlClient.GenerateConnectAuthTokenAsync(tokenRequest);
        
        var connectionString = new NpgsqlConnectionStringBuilder
        {
            Host = _clusterEndpoint,
            Database = "testdb",
            Username = tokenResponse.DbUser,
            Password = tokenResponse.AuthToken,
            SslMode = SslMode.Require
        }.ToString();
        
        return new NpgsqlConnection(connectionString);
    }
}
```

Rustでも同じパターンで書ける：

```rust
use aws_sdk_dsql::{Client, Error};
use sqlx::{PgPool, Row};
use sqlx::postgres::PgConnectOptions;

pub struct DSQLConnector {
    client: Client,
    cluster_endpoint: String,
}

impl DSQLConnector {
    pub fn new(client: Client, cluster_endpoint: String) -> Self {
        Self { client, cluster_endpoint }
    }
    
    pub async fn create_pool(&self) -> Result<PgPool, Error> {
        let token_response = self.client
            .generate_connect_auth_token()
            .cluster_endpoint(&self.cluster_endpoint)
            .region("us-east-1")
            .send()
            .await?;
            
        let options = PgConnectOptions::new()
            .host(&self.cluster_endpoint)
            .database("testdb")
            .username(&token_response.db_user().unwrap_or("default"))
            .password(&token_response.auth_token().unwrap_or(""))
            .ssl_mode(sqlx::postgres::PgSslMode::Require);
            
        Ok(PgPool::connect_with(options).await?)
    }
}
```

静的認証情報が不要になるのが最大のメリット。トークンは短時間で期限切れになり、IAMポリシーでアクセス制御を細かく設定できる。接続プーリングも最適化されている。

## SRE視点での活用ポイント

CloudWatchのログ一元化は、マルチアカウント環境でのインシデント対応に直結する。Terraformでログ集約設定をコード化しておけば、CloudWatchアラームと組み合わせて特定パターン検出時の自動エスカレーションまで持っていける。

Aurora DSQLの新コネクタは、Secrets Managerで静的認証情報を管理していた環境に効く。ローテーション作業が不要になり、IAMポリシーだけでアクセス制御が完結する。ただし移行にはアプリケーションコードの修正が必要なので、まずは新規プロジェクトから試すのがよいだろう。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| Amazon S3 | [S3 Vectors expands to 17 additional AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/03/s3-vectors-expands-17-regions/) | ベクター検索機能が17の追加リージョンで利用可能に |
| AWS Marketplace | [Sellers can now self-serve refunds and agreement cancellations](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-marketplace-seller-self-service-refund-cancel/) | 販売者向けのセルフサービス返金・契約キャンセル機能 |
| Amazon Managed Service for Apache Flink | [Now supports Apache Flink 2.2](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-managed-service-flink-2-2/) | Apache Flink 2.2サポート、Java 17対応、I/O性能向上 |
| AWS Deadline Cloud | [New fleet scaling configurations for render farms](https://aws.amazon.com/about-aws/whats-new/2026/03/deadline-cloud-fleet-scaling/) | レンダーファーム向けの新しいフリートスケーリング設定 |
| Aurora DSQL | [New .NET and Rust connectors](https://aws.amazon.com/about-aws/whats-new/2026/03/aurora-dsql-rust-npgsql-connectors/) | .NETとRust向けの新コネクタ、IAM認証の簡素化 |
| AWS DevOps Agent | [Now generally available](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-devops-agent-generally-available/) | マルチクラウド・オンプレミス対応のDevOpsエージェント |
| Amazon ECS | [Managed Instances supports EC2 instance store](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-ecs-mi-local-storage/) | マネージドインスタンスでEC2インスタンスストアをサポート |
| AWS Services | [Service Availability Updates](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-service-availability/) | 一部サービスのメンテナンスモード移行とサンセット予定 |
| AWS Private CA | [Publishes utilization metrics to CloudWatch](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-private-ca-publishes-metrics/) | 証明書利用状況メトリクスをCloudWatchに送信 |
| AWS Security Agent | [On-demand penetration testing GA](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-security-agent-ondemand-penetration/) | オンデマンドペネトレーションテスト機能が正式リリース |
| Amazon CloudWatch | [Multi-account log centralization by data source](https://aws.amazon.com/about-aws/whats-new/2026/03/cloudwatch-centralization-datasource/) | データソース別のマルチアカウントログ一元化 |
| AWS HealthOmics | [VPC-connected workflows](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-healthomics-vpc-connected-workflows/) | VPC接続ワークフロー機能、HIPAA準拠 |
| AWS Security Hub | [Available in GovCloud (US) Regions](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-security-hub-govcloud-us-regions/) | GovCloud(US)リージョンでSecurity Hubが利用可能 |

## まとめ

13件中、CloudWatchのログ一元化とAurora DSQLコネクタが実務インパクトとしては大きい。マルチアカウント環境の可観測性と、データベース認証のIAM化という、どちらも地味だが運用負荷に直結するテーマ。DevOpsエージェントGAとSecurity Agentのペネトレーションテスト機能も、自動化の選択肢が増えたという点で押さえておきたい。