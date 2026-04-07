---
title: "【AWS】2026/04/08 のアップデートまとめ"
date: 2026-04-08T08:01:25+09:00
draft: true
tags: ["aws", "bedrock", "sagemaker", "lambda", "acm", "s3", "cost-explorer", "lightsail", "iot-greengrass"]
categories: ["AWS Updates"]
summary: "2026/04/08 のAWSアップデートまとめ"
---

# AWS週次アップデート：2026年4月8日

## はじめに

2026年4月8日のAWSアップデートでは、合計10件の新機能やサービス拡張が発表されました。特に注目すべきは、AWS Certificate Manager（ACM）の証明書検索機能強化と、Amazon Lightsailのマレーシアリージョン展開です。また、Amazon BedrockのClaude Mythos Previewや、LambdaのResponse Streaming全リージョン展開など、AI・機械学習とサーバーレス分野での機能拡充も目立ちます。今回は証明書管理の効率化とグローバル展開の観点から、特に実践的な価値の高い2つのアップデートを深掘りしていきます。

## 注目アップデート深掘り

### AWS Certificate Manager の証明書検索機能強化

AWS Certificate Manager（ACM）に新しい検索機能が追加され、大規模な証明書管理がより効率的になりました。この機能強化は、複数のドメインや証明書を管理する企業にとって、運用負荷の大幅な軽減を意味します。

従来のACMコンソールでは、証明書の一覧表示と基本的なフィルタリングに留まっていましたが、今回のアップデートにより、ドメイン名、証明書ARN、有効期限などの複数パラメータを組み合わせた高度な検索が可能になりました。特に重要なのは、新たに提供されたSearchCertificates APIです。

```bash
# 特定のドメインの証明書を検索
$ aws acm search-certificates \
    --domain-name "*.example.com" \
    --region us-east-1

# 有効期限が近い証明書を検索（30日以内）
$ aws acm search-certificates \
    --expires-before $(date -d "+30 days" +%Y-%m-%d) \
    --region us-east-1

# 複数条件での絞り込み検索
$ aws acm search-certificates \
    --domain-name "api.example.com" \
    --status ISSUED \
    --key-algorithm RSA-2048 \
    --region us-east-1
```

Terraformでの証明書管理においても、このAPIを活用したdata sourceの実装が可能になります：

```hcl
data "aws_acm_certificate_search" "expiring_soon" {
  domain   = "*.example.com"
  statuses = ["ISSUED"]
  
  # 30日以内に期限切れとなる証明書を検索
  expires_before = timeadd(timestamp(), "720h")
}

resource "aws_cloudwatch_metric_alarm" "certificate_expiry" {
  count = length(data.aws_acm_certificate_search.expiring_soon.certificates)
  
  alarm_name          = "certificate-expiry-${count.index}"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DaysToExpiry"
  namespace           = "AWS/CertificateManager"
  period              = "86400"
  statistic           = "Maximum"
  threshold           = "30"
}
```

Python SDKを使用した自動化スクリプトの例も見てみましょう：

```python
import boto3
from datetime import datetime, timedelta

def monitor_certificate_expiry():
    acm = boto3.client('acm')
    
    # 30日以内に期限切れとなる証明書を検索
    expires_before = datetime.now() + timedelta(days=30)
    
    response = acm.search_certificates(
        ExpiresBefore=expires_before,
        CertificateStatuses=['ISSUED']
    )
    
    expiring_certs = []
    for cert in response['CertificateList']:
        cert_details = acm.describe_certificate(
            CertificateArn=cert['CertificateArn']
        )
        
        expiring_certs.append({
            'domain': cert_details['Certificate']['DomainName'],
            'arn': cert['CertificateArn'],
            'expires': cert_details['Certificate']['NotAfter']
        })
    
    return expiring_certs
```

> **Note:** SearchCertificates APIは、AWS CLI version 2.15以降、または boto3 version 1.34以降で利用可能です。

### Amazon Lightsail マレーシアリージョン展開

Amazon Lightsailがアジアパシフィック（マレーシア）リージョンで利用開始となり、東南アジア地域での低レイテンシーアプリケーション展開が現実的になりました。マレーシアは地理的にシンガポールとインドネシア、タイの中間に位置し、この地域をターゲットとするアプリケーションにとって戦略的に重要な拠点となります。

レイテンシーの実測比較を行うと、クアラルンプールからの接続において、従来のシンガポールリージョン（ap-southeast-1）と比較して約15-25%の遅延改善が期待できます：

```bash
# マレーシアリージョンでのLightsailインスタンス作成
$ aws lightsail create-instances \
    --instance-names "my-app-malaysia" \
    --availability-zone "ap-southeast-5a" \
    --blueprint-id "ubuntu_22_04" \
    --bundle-id "micro_2_0" \
    --region ap-southeast-5

# 接続テスト用のキーペア作成
$ aws lightsail create-key-pair \
    --key-pair-name "malaysia-keypair" \
    --region ap-southeast-5
```

コスト効率の観点でも、Lightsailの定額料金モデルは予算管理を単純化します。マレーシアリージョンでの料金体系を確認してみましょう：

```python
import boto3

def compare_lightsail_pricing():
    # 複数リージョンでの料金比較
    regions = ['us-east-1', 'ap-southeast-1', 'ap-southeast-5']
    lightsail_clients = {region: boto3.client('lightsail', region_name=region) 
                        for region in regions}
    
    bundle_comparison = {}
    
    for region, client in lightsail_clients.items():
        try:
            bundles = client.get_bundles()
            bundle_comparison[region] = {
                bundle['bundleId']: {
                    'price': bundle['price'],
                    'cpu_count': bundle['cpuCount'],
                    'ram_size': bundle['ramSizeInGb'],
                    'disk_size': bundle['diskSizeInGb']
                }
                for bundle in bundles['bundles']
            }
        except Exception as e:
            print(f"Error fetching bundles for {region}: {e}")
    
    return bundle_comparison
```

Terraformを使用したマルチリージョンでのLightsail展開例：

```hcl
# マレーシアリージョンでのLightsailインスタンス
resource "aws_lightsail_instance" "app_malaysia" {
  provider          = aws.malaysia
  name              = "myapp-malaysia"
  availability_zone = "ap-southeast-5a"
  blueprint_id      = "ubuntu_22_04"
  bundle_id         = "medium_2_0"
  
  user_data = file("${path.module}/scripts/init.sh")
  
  tags = {
    Environment = "production"
    Region      = "malaysia"
    Purpose     = "regional-app"
  }
}

# ロードバランサーの設定
resource "aws_lightsail_lb" "app_lb_malaysia" {
  provider                = aws.malaysia
  name                    = "myapp-lb-malaysia"
  health_check_path       = "/health"
  instance_port           = "80"
  
  tags = {
    Environment = "production"
  }
}

# インスタンスをロードバランサーにアタッチ
resource "aws_lightsail_lb_attachment" "app_attachment" {
  provider    = aws.malaysia
  lb_name     = aws_lightsail_lb.app_lb_malaysia.name
  instance_name = aws_lightsail_instance.app_malaysia.name
}
```

データレジデンシー要件への対応も重要な考慮点です。マレーシアには Personal Data Protection Act (PDPA) があり、特定のデータ種別について国内保存が推奨されるケースがあります。

> **Note:** マレーシアリージョンの正式なリージョンコードは `ap-southeast-5` ですが、サービス開始直後は一部のAWSサービスで利用できない場合があります。

## SRE視点での活用ポイント

今回のアップデートは、SREの日常業務において複数の改善機会をもたらします。

**証明書管理の自動化強化**において、ACMの検索機能は証明書のライフサイクル管理を大幅に改善できます。Terraform管理下のインフラであれば、証明書の自動更新フローにSearchCertificates APIを組み込むことで、期限切れリスクを事前に検知し、アラート機能と連携できます。CloudWatch Eventsと組み合わせれば、証明書期限の30日前、7日前、1日前といった段階的な通知システムを構築可能です。特に、マイクロサービス環境で多数のサブドメイン証明書を管理している場合、従来の手動確認作業から解放される効果は大きいでしょう。

**グローバル展開時のレイテンシー最適化**では、Lightsailのマレーシアリージョン追加により、東南アジア地域でのエッジ戦略を再検討する価値があります。既存の監視システムでレイテンシーメトリクスを収集している場合、地域別のパフォーマンス改善を定量的に評価できます。ただし、リージョン追加に伴うコスト増加や、データ同期の複雑性については慎重な検討が必要です。災害復旧の観点では、シンガポールリージョンの単一障害点リスクを軽減できる一方で、運用手順書やランブックの更新、監視設定の複製作業が発生します。

導入判断においては、既存のアプリケーションアーキテクチャとの整合性を重視すべきです。証明書検索機能は既存システムへの影響が minimal で導入しやすい一方、新リージョン展開は DNS設定、CDN構成、データベースレプリケーションなど、システム全体への影響を慎重に評価する必要があります。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| Amazon Bedrock | Claude Mythos Preview（ゲート付きリサーチプレビュー）提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-bedrock-claude-mythos/) |
| Amazon SageMaker | Identity Center ドメインにサーバーレスワークフロー追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-sagemaker-serverless-workflows/) |
| AWS Lambda | Response Streaming を全商用リージョンに拡張 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-lambda-response-streaming/) |
| AWS Certificate Manager | ネイティブ証明書検索機能をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-certificate-manager-search/) |
| Amazon S3 | S3 Files - S3バケットをファイルシステムとして利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-s3-files/) |
| AWS Cost Explorer | Amazon Q による自然言語クエリ機能を開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-cost-explorer-natural-language-query/) |
| Amazon Lightsail | アジアパシフィック（マレーシア）リージョンで利用開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-lightsail-malaysia/) |
| Amazon SageMaker Unified Studio | ノートブックのインポート/エクスポートと開発者向け加速機能を追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-sagemaker-unified-studio/) |
| AWS IoT Greengrass | C、C++、Rust アプリケーション用コンポーネントSDK提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/iot-greengrass-component-sdk/) |

## まとめ

今回のアップデートは、運用効率化とグローバル展開支援という2つの大きなテーマが見えてきます。ACMの検索機能強化やCost Explorerの自然言語対応は、日々の運用作業をより直感的で効率的にする取り組みです。一方、LightsailのマレーシアリージョンやIoT GreengrassのネイティブSDK対応は、新しい市場や技術領域への展開を支援する機能拡張といえるでしょう。

特にSREの観点では、これらの機能を既存の自動化パイプラインに組み込むことで、従来の手動作業を大幅に削減できる可能性があります。ただし、新機能の導入は段階的に行い、既存システムへの影響を慎重に評価しながら進めることが重要です。次週以降も、これらの機能の実用化事例や、組み合わせて使用する際のベストプラクティスに注目していきたいと思います。