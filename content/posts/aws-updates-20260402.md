---
title: "【AWS】2026/04/02 のアップデートまとめ"
date: 2026-04-02T08:01:35+09:00
draft: false
tags: ["aws", "vpc", "oracle", "rds", "cloudfront", "microsoft-ad", "opensearch", "cloudwatch", "security-hub", "organizations", "sagemaker", "glue", "iam", "sustainability"]
categories: ["AWS Updates"]
summary: "2026/04/02 のAWSアップデートまとめ。VPC暗号化コントロールGovCloud対応、OpenSearchエージェント型AIログ分析、CloudFront SHA-256署名URL、Sustainabilityコンソールなど11件"
---

![](/images/aws-updates-20260402/header.png)

## はじめに

2026年4月2日のAWSアップデートは11件です。VPC暗号化コントロールのGovCloud対応とOpenSearch Serviceのエージェント型AIログ分析が目を引きます。CloudFrontのSHA-256署名URLやSustainabilityコンソールなど、セキュリティと運用周りの機能追加が中心です。

## 注目アップデート深掘り

### AWS VPC 暗号化コントロールが GovCloud（US）で利用開始

GovCloud（US）リージョンでVPC暗号化コントロールが使えるようになりました。VPC内外のトラフィック暗号化を自動的に監視・強制する機能です。

従来はサービスごとに個別で暗号化設定が必要でしたが、VPCレベルで包括的に制御できるようになります。HIPAA、PCI DSS、FedRAMP、FIPS 140-2などのコンプライアンス要件を持つ環境に向いています。ただし、今回の対象はGovCloud（US）リージョン限定なので、米国政府機関や関連する規制対象組織以外では直接的な影響は少ないです。通常の商用リージョンへの展開が今後あるかは要ウォッチです。

```bash
# VPC の暗号化ポリシーを作成
$ aws ec2 create-vpc-encryption-policy \
  --vpc-id vpc-12345678 \
  --encryption-requirement "required" \
  --region us-gov-west-1
```

Terraformでの設定例：

```hcl
resource "aws_vpc_encryption_control" "secure_vpc" {
  vpc_id = aws_vpc.main.id

  encryption_policy {
    enforce_encryption   = true
    encryption_algorithm = "AES-256"

    exceptions {
      service = "ec2-instance-connect"
      reason  = "Administrative access"
    }
  }

  compliance_standards = [
    "FIPS-140-2",
    "FedRAMP-High"
  ]
}
```

ハードウェアベースのAES-256暗号化なので、パフォーマンスへの影響は通常5%未満とされています。

### Amazon OpenSearch Service エージェント型 AI ログ分析

OpenSearch Serviceに自然言語での対話型ログ分析機能が追加されました。追加コストなし（トークンベースの制限あり）で利用できます。

従来のElasticsearch DSLクエリ：

```json
{
  "query": {
    "bool": {
      "must": [
        {"range": {"@timestamp": {"gte": "now-1h"}}},
        {"match": {"log_level": "ERROR"}},
        {"wildcard": {"message": "*database*connection*"}}
      ]
    }
  },
  "aggs": {
    "error_trends": {
      "date_histogram": {
        "field": "@timestamp",
        "interval": "5m"
      }
    }
  }
}
```

これが自然言語で問い合わせ可能になります：

```python
response = opensearch_client.query_with_ai_agent(
    domain_name='production-logs',
    query="過去1時間のデータベース接続エラーを表示し、根本原因を特定して"
)
```

DSLの書き方を知らないメンバーでもログ分析ができるようになるので、オンコール対応の属人化解消に使えます。ただしAI分析結果は必ず人間が検証するフローを組んでおくべきです。

## SRE視点での活用ポイント

VPC暗号化コントロールは、Terraformテンプレートに組み込んでおけば新規環境でも暗号化設定が漏れません。CloudWatchアラームと連携させて、暗号化されていないトラフィックの検出→自動通知まで構築できます。導入は開発環境から段階的に進めるのがよいでしょう。

OpenSearchのAIログ分析は、ランブックに「AIエージェントへの質問例」を整備しておくと、障害対応の標準化に使えます。「14:30の5xxスパイクの原因は？」「タイムアウトエラーが多いマイクロサービスは？」のような定型質問をテンプレート化しておくと効率的です。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| AWS VPC | [Encryption controls now available in GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-vpc-encryption-controls/) | VPC内外トラフィック暗号化の自動監視・強制 |
| Oracle Database@AWS | [High performance networking](https://aws.amazon.com/about-aws/whats-new/2026/04/oracle-database-aws-launches-high-performance-networking/) | サブミリ秒ネットワークレイテンシ対応 |
| Amazon RDS for Oracle | [Cross-account snapshot sharing with additional storage](https://aws.amazon.com/about-aws/whats-new/2026/04/rds-oracle-cross-account-snapshot-sharing-additional-storage-volume/) | 追加ストレージボリュームでのクロスアカウント共有 |
| Amazon CloudFront | [SHA-256 signed URLs and cookies](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-cloudfront-sha-256-signed-urls/) | 署名付きURL/CookieでSHA-256をサポート |
| AWS Managed Microsoft AD | [Multi-region replication in opt-in regions](https://aws.amazon.com/about-aws/whats-new/2026/04/multi-region-opt-in-aws-microsoft-ad/) | Opt-Inリージョンでのマルチリージョンレプリケーション |
| Amazon OpenSearch Service | [Agentic AI log analytics](https://aws.amazon.com/about-aws/whats-new/2026/03/opensearch-agentic-ai-log-analytics-observability/) | 自然言語での対話型ログ分析 |
| Amazon CloudWatch | [Security Hub CSPM findings ingestion](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-cloudwatch-securityhub-findings/) | Security Hub調査結果の組織全体取り込み |
| AWS Organizations | [Path information in API responses](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-organizations-paths-api-responses/) | APIレスポンスで組織パス情報を提供 |
| Amazon SageMaker Unified Studio | [CloudWatch metrics for Glue jobs](https://aws.amazon.com/about-aws/whats-new/2026/03/sagemaker-unified-studio-metrics/) | GlueジョブのCloudWatchメトリクス統合 |
| AWS IAM Identity Center | [European Sovereign Cloud (Germany)](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-iam-identity-center-european-sovereign-cloud-germany-region/) | 欧州ソブリンクラウド（ドイツ）で利用開始 |
| AWS Sustainability | [Carbon emissions tracking console](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-launches-sustainability-console/) | 炭素排出量追跡コンソール |

## まとめ

11件中、VPC暗号化コントロールとOpenSearchのAIログ分析が実務インパクトとしては大きいです。前者はコンプライアンス対応のコード化、後者はログ分析の属人化解消に効きます。CloudFrontのSHA-256対応も、署名付きURLを使っている環境では早めに移行を検討しておくとよいでしょう。
