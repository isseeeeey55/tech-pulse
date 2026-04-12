---
title: "【AWS】2026/04/08 のアップデートまとめ"
date: 2026-04-08T08:01:25+09:00
draft: false
tags: ["aws", "bedrock", "sagemaker", "lambda", "acm", "s3", "cost-explorer", "lightsail", "iot-greengrass"]
categories: ["AWS Updates"]
summary: "2026/04/08 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260408/header.png)

# AWS週次アップデート：2026年4月8日

## はじめに

2026年4月8日のAWSアップデートは9件です。ACMへのSearchCertificates API追加、S3バケットをファイルシステムとしてマウントできるAmazon S3 Files、LambdaのResponse Streaming全商用リージョン展開など、運用改善系の更新が中心でした。今回はACMの検索機能とLightsailのマレーシアリージョン展開を深掘りします。

## 注目アップデート深掘り

### AWS Certificate Manager の証明書検索機能強化

![ACM証明書検索ワークフロー比較](/images/aws-updates-20260408/acm-search-workflow.png)

AWS Certificate Manager（ACM）にSearchCertificates APIが追加されました。ドメイン名・ARN・有効期限で証明書を絞り込めます。数百枚の証明書を管理している環境だと、期限切れの見落とし防止に直結する機能です。

従来はコンソールでの一覧表示と基本フィルタリングしかなく、CLIやスクリプトから特定条件の証明書を探すには `list-certificates` の結果を自前でフィルタリングする必要がありました。

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

boto3での活用例として、期限切れが近い証明書を検索するスクリプトを見てみます：

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

> **Note:** SearchCertificates APIはすべてのパブリックAWSリージョン、AWS China、AWS GovCloudリージョンで利用可能です。CLIやSDKのバージョンが古い場合はアップデートしてください。

### Amazon Lightsail マレーシアリージョン展開

Amazon Lightsailが ap-southeast-5（マレーシア）で利用可能になりました。シンガポール（ap-southeast-1）に加えて、東南アジア向けアプリケーションのデプロイ先が増えた形です。

Lightsailは定額料金なので、リージョナルなステージング環境や小規模サービスには使いやすい選択肢です。マレーシアリージョンでのインスタンス作成例を見てみましょう：

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

リージョンごとの料金差を確認するスクリプト例です：

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

マレーシアにはPersonal Data Protection Act（PDPA）があるため、データレジデンシー要件がある場合にもこのリージョンが選択肢に入ります。ただし、サービス開始直後は一部のAWSサービスが未対応の場合があるので、利用予定のサービスの対応状況は事前に確認してください。

## 活用ポイント

**証明書の棚卸し自動化**: SearchCertificates APIをCloudWatch Events（EventBridge）と組み合わせれば、「期限切れ30日前の証明書一覧」を定期的にSlackへ通知する仕組みが作れます。マイクロサービスでサブドメインごとに証明書を発行している環境では、手動の棚卸しから解放されるのが地味に効きます。既存システムへの影響もないので、すぐに試せる類のアップデートです。

**マレーシアリージョンの使いどころ**: Lightsailは定額モデルなので、まずはステージング環境やリージョナルなヘルスチェック用エンドポイントから試すのが手軽です。本番ワークロードを移すなら、DNS・CDN・データ同期の設計変更が必要になるので、段階的に進めるのがよいでしょう。

## 全アップデート一覧

> **Amazon S3 Filesとは？**
> Amazon EFSをベースに、S3バケットをファイルシステムとしてマウントできる新機能です。数千のコンピュートリソースから同時に同じS3データへアクセスでき、コード変更なしで既存のファイルベースツールがそのまま使えます。

> **AWS IoT Greengrassとは？**
> エッジデバイス上でAWS Lambdaやコンテナを実行するためのIoTランタイムです。今回、C/C++/Rust向けのコンポーネントSDKが追加され、リソース制約の厳しいデバイスでもネイティブ言語でGreengrassコンポーネントを開発できるようになりました。

> **Claude Mythosとは？**
> Anthropicの研究段階の新モデルで、サイバーセキュリティや大規模コードベースの脆弱性検出に特化しています。現在はゲート付きリサーチプレビューで、ホワイトリスト登録された組織のみ利用可能です。

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

ACMのSearchCertificates APIは、証明書管理のスクリプト化・自動化を一段楽にしてくれるアップデートです。S3 Filesも、EFSベースでS3バケットをファイルシステムとしてマウントできるという、データパイプライン周りで気になる新機能でした。Cost Explorerの自然言語クエリ（Amazon Q連携）やBedrockのClaude Mythos Previewなど、AI系の更新も地道に進んでいます。