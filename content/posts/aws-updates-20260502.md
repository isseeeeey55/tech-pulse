---
title: "【AWS】2026/05/02 のアップデートまとめ"
date: 2026-05-02T08:02:23+09:00
draft: true
tags: ["aws", "opensearch", "cloudfront", "rds", "redshift", "iam", "eks", "bedrock", "ecs", "payment-cryptography", "quicksight"]
categories: ["AWS Updates"]
summary: "2026/05/02 のAWSアップデートまとめ"
---

# 2026年5月2日 AWS アップデート解説

## はじめに

2026年5月2日は、全11件のアップデートが発表されました。本日のハイライトは、**OpenSearch UI のクロスリージョンデータアクセス対応**と**CloudFront の VPC オリジン経由 WebSocket サポート**です。前者はグローバル分散システムの統合監視を大幅に簡素化し、後者はリアルタイムアプリケーションのセキュリティアーキテクチャに新たな選択肢を提供します。また、EKS の CloudShell 統合や RDS for SQL Server のクロスアカウントスナップショット強化など、運用効率とセキュリティを向上させる実践的なアップデートが多数含まれています。

## 注目アップデート深掘り

### OpenSearch UI のクロスリージョンデータアクセス対応

#### なぜこのアップデートが重要なのか

従来、異なるリージョンの OpenSearch ドメインにアクセスする場合、エンドポイントを手動で切り替えるか、データをレプリケーションして単一リージョンに集約する必要がありました。グローバル展開している企業では、GDPR や各国のデータレジデンシー要件により、特定のデータを特定リージョンに保管する義務があります。しかし、セキュリティ分析やコンプライアンス監査では、全リージョンのログを横断的に検索・可視化したいというニーズが常に存在していました。

今回のアップデートにより、**単一の OpenSearch UI から複数リージョン・複数アカウントのドメインに同時アクセス**できるようになり、データ主権を保ちながら統合的な分析が可能になりました。

#### クロスリージョンアクセスの設定と検証

OpenSearch UI でのクロスリージョンアクセスは、既存のクロスアカウント対応と組み合わせて動作します。基本的な設定フローは以下の通りです：

**1. 各リージョンのドメイン準備**

まず、異なるリージョンに OpenSearch ドメインを作成します。以下は AWS CLI での作成例です：

```bash
$ aws opensearch create-domain \
  --domain-name logs-us-east-1 \
  --region us-east-1 \
  --engine-version OpenSearch_2.11 \
  --cluster-config InstanceType=t3.small.search,InstanceCount=1 \
  --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=20

$ aws opensearch create-domain \
  --domain-name logs-eu-west-1 \
  --region eu-west-1 \
  --engine-version OpenSearch_2.11 \
  --cluster-config InstanceType=t3.small.search,InstanceCount=1 \
  --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=20
```

**2. IAM 認証の設定**

クロスリージョンアクセスには IAM または IAM Identity Center のいずれかを使用できます。IAM Identity Center を使用する場合、より簡潔なユーザー管理が可能です。IAM ロールでアクセスする場合の例：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/OpenSearchCrossRegionRole"
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:123456789012:domain/logs-us-east-1/*"
    }
  ]
}
```

**3. OpenSearch UI での接続**

OpenSearch UI にアクセスし、複数のドメインエンドポイントを登録します。UI 上で各ドメインの認証情報を設定すると、単一のダッシュボードから全リージョンのデータを検索・可視化できるようになります。

#### クロスクラスタレプリケーションとの組み合わせ

クロスクラスタレプリケーション（CCR）を使用している場合、プライマリドメインとレプリカドメインの両方に直接クエリを発行できます。これにより、フェイルオーバー時の動作検証や、レプリケーション遅延の監視が容易になります：

```bash
# プライマリドメインへのクエリ
$ curl -X GET "https://logs-us-east-1.region.es.amazonaws.com/_cat/indices" \
  --aws-sigv4 "aws:amz:us-east-1:es"

# レプリカドメインへの同時クエリ
$ curl -X GET "https://logs-eu-west-1.region.es.amazonaws.com/_cat/indices" \
  --aws-sigv4 "aws:amz:eu-west-1:es"
```

#### 認証方式の比較

| 項目 | IAM | IAM Identity Center |
|------|-----|---------------------|
| セットアップ複雑度 | 中（ロール・ポリシー管理） | 低（GUI ベース） |
| マルチアカウント対応 | 可（クロスアカウントロール） | 可（組織レベル統合） |
| ユーザー管理 | IAM ユーザー/ロール | SSO ユーザー |
| 監査ログ | CloudTrail | CloudTrail + Identity Center ログ |

Public と VPC の両構成で利用可能ですが、VPC 構成の場合は VPC エンドポイント経由でのアクセス制御と組み合わせることで、よりセキュアな環境を構築できます。

---

### CloudFront の VPC オリジン経由 WebSocket サポート

#### なぜこのアップデートが重要なのか

リアルタイム通信を必要とするアプリケーション（チャット、コラボレーションツール、ライブダッシュボード）では、WebSocket プロトコルが広く使用されています。従来、CloudFront を WebSocket トラフィックのフロントエンドとして使用する場合、オリジンサーバー（ALB、NLB、EC2）を**パブリックサブネットに配置**する必要がありました。これは以下のセキュリティリスクを伴います：

- パブリック IP アドレスの公開による攻撃面の拡大
- セキュリティグループや NACL による複雑なアクセス制御の必要性
- オリジンサーバーへの直接アクセスを防ぐための追加設定（カスタムヘッダー検証など）

今回のアップデートにより、WebSocket を使用するアプリケーションを**プライベートサブネット内に完全に隔離**し、CloudFront 経由でのみアクセス可能にできます。

#### VPC オリジン経由 WebSocket の動作メカニズム

CloudFront の VPC オリジン機能は、VPC Lattice を利用して CloudFront と VPC 内リソース間にプライベート接続を確立します。WebSocket 接続の確立フローは以下の通りです：

**1. WebSocket ハンドシェイク**

クライアントが CloudFront に HTTP Upgrade リクエストを送信：

```http
GET /chat HTTP/1.1
Host: example.cloudfront.net
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

**2. CloudFront から VPC オリジンへの転送**

CloudFront は VPC エンドポイント経由でプライベートサブネット内の ALB にリクエストを転送します。

**3. WebSocket 接続の維持**

ハンドシェイク成功後、CloudFront は双方向の永続的接続を維持し、クライアントとオリジン間でメッセージをプロキシします。

#### 実装例：プライベート ALB + WebSocket アプリケーション

以下は Terraform での実装例です：

```hcl
# プライベートサブネット内の ALB
resource "aws_lb" "websocket_alb" {
  name               = "websocket-private-alb"
  internal           = true  # プライベート ALB として作成
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = aws_subnet.private[*].id
}

# WebSocket アプリケーションのターゲットグループ
resource "aws_lb_target_group" "websocket_tg" {
  name     = "websocket-tg"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

# CloudFront ディストリビューション
resource "aws_cloudfront_distribution" "websocket_dist" {
  enabled = true

  origin {
    domain_name = aws_lb.websocket_alb.dns_name
    origin_id   = "websocket-vpc-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }

    # VPC オリジン設定
    origin_access_control_id = aws_cloudfront_origin_access_control.vpc_oac.id
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "websocket-vpc-origin"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = true
      headers      = ["Upgrade", "Sec-WebSocket-Key", "Sec-WebSocket-Version"]
      cookies {
        forward = "all"
      }
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# セキュリティグループ：CloudFront からのみ許可
resource "aws_security_group" "alb_sg" {
  name        = "websocket-alb-sg"
  description = "Allow WebSocket traffic from CloudFront only"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 443
    to_port         = 443
    protocol        = "tcp"
    prefix_list_ids = [data.aws_ec2_managed_prefix_list.cloudfront.id]
  }
}
```

> **Note:** VPC オリジン機能を使用する場合、セキュリティグループで CloudFront のマネージドプレフィックスリストを参照することで、CloudFront からのトラフィックのみを許可できます。

#### HTTP トラフィックとの統合

同一の CloudFront ディストリビューションで HTTP リクエストと WebSocket 接続の両方を処理できます。パスベースルーティングの例：

```hcl
ordered_cache_behavior {
  path_pattern     = "/ws/*"
  allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
  target_origin_id = "websocket-vpc-origin"

  forwarded_values {
    query_string = true
    headers      = ["Upgrade", "Sec-WebSocket-Key", "Sec-WebSocket-Version"]
    cookies {
      forward = "all"
    }
  }
}

ordered_cache_behavior {
  path_pattern     = "/api/*"
  allowed_methods  = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
  target_origin_id = "api-vpc-origin"

  forwarded_values {
    query_string = true
  }
}
```

#### セキュリティ面でのメリット

- **攻撃面の縮小**：オリジンサーバーがインターネットに直接露出しない
- **組み込み DDoS 保護**：CloudFront の AWS Shield Standard が自動的に適用される
- **統一されたアクセス制御**：CloudFront の地理的制限、WAF ルール、レート制限を WebSocket にも適用可能
- **TLS 終端の一元化**：証明書管理を CloudFront で完結できる

## SRE視点での活用ポイント

### OpenSearch クロスリージョンアクセスの運用シナリオ

グローバル展開しているサービスでは、各リージョンのログやメトリクスを統合的に監視する必要があります。従来は Elasticsearch の Kibana に複数のエンドポイントをブックマークし、リージョンごとにログインして確認する運用が一般的でした。この方法では、インシデント発生時にどのリージョンで問題が起きているかを特定するまでに時間がかかります。

OpenSearch UI のクロスリージョン対応により、単一のダッシュボードで全リージョンの異常を検知できるため、**MTTR（平均修復時間）の短縮**が期待できます。特に、以下のシナリオで有効です：

- **セキュリティインシデント対応**：不正アクセスの兆候を全リージョン横断で検索し、攻撃の規模と影響範囲を迅速に把握
- **パフォーマンス劣化の原因特定**：複数リージョンで同時発生しているエラーパターンを比較分析
- **コンプライアンス監査**：特定ユーザーのアクションログを全リージョンから抽出してレポート生成

導入時の注意点として、クロスリージョンクエリは各ドメインへの並列クエリとなるため、ドメイン数が増えるとクエリ実行時間が長くなる可能性があります。頻繁にアクセスするデータは CloudWatch Logs Insights や Athena との併用も検討すべきです。

### CloudFront VPC オリジン WebSocket の運用改善

リアルタイムダッシュボードやチャットアプリケーションでは、WebSocket 接続の安定性がユーザー体験に直結します。従来のパブリックサブネット配置では、セキュリティグループの変更や NLB のヘルスチェック設定ミスが WebSocket 切断の原因となることがありました。

VPC オリジン経由の WebSocket では、**CloudFront のグローバルエッジネットワークが接続の安定性を向上させる**ため、ネットワーク品質の改善が期待できます。また、プライベートサブネット配置により、以下のメリットが得られます：

- **変更影響範囲の縮小**：パブリック IP やセキュリティグループの変更がインターネットからのアクセスに直接影響しない
- **障害時の切り分けの明確化**：CloudFront とオリジン間のトラフィックは VPC 内に閉じているため、ネットワーク経路の切り分けが容易
- **コスト最適化の選択肢**：NAT Gateway のデータ転送コストを削減できる（CloudFront からのトラフィックは VPC Endpoint 経由のため）

ただし、VPC Lattice を利用する VPC オリジン機能には追加コストが発生するため、トラフィック量とセキュリティ要件を考慮した費用対効果の検証が必要です。また、CloudWatch メトリクスで WebSocket 接続数や接続時間を監視し、異常値を検知するアラームを設定することで、プロアクティブな運用が実現できます。

## 全アップデート一覧

| # | サービス | タイトル | 概要 |
|---|----------|----------|------|
| 1 | **OpenSearch** | [クロスリージョンデータアクセス対応](https://aws.amazon.com/about-aws/whats-new/2026/05/opensearch-ui-cross-region-data-access-domains/) | OpenSearch UI が複数リージョン・複数アカウントのドメインに単一 UI からアクセス可能に。データレジデンシー要件を満たしながら統合分析を実現 |
| 2 | **AWS Transform** | [BI 移行エージェント提供開始](https://aws.amazon.com/about-aws/whats-new/2026/05/quick-bi-migration/) | Tableau と Power BI から QuickSight への移行を数日に短縮する AI 駆動エージェントを AWS Marketplace で提供開始 |
| 3 | **CloudFront** | [VPC オリジン経由 WebSocket サポート](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-cloudfront-websockets-vpc-origins/) | プライベートサブネット内の WebSocket アプリケーションに CloudFront 経由でアクセス可能に。セキュリティと運用性が向上 |
| 4 | **RDS for SQL Server** | [追加ストレージボリュームのクロスアカウント共有](https://aws.amazon.com/about-aws/whats-new/2026/05/rds-sqlserver-cross-account-snapshot-sharing-additional-storage-volume/) | 最大256 TiB のストレージ構成を持つスナップショットをアカウント間で共有可能に。コンプライアンス対応とディザスタリカバリを強化 |
| 5 | **Redshift** | [Concurrency Scaling が auto-copy と zero-ETL に対応](https://aws.amazon.com/about-aws/whats-new/2026/03/concurrency-scaling-auto-copy-zero-ETL/) | ピーク時にコンピュート容量を自動追加し、データ取り込みを高速化。Serverless と RA3 Provisioned の両方で利用可能 |
| 6 | **IAM Roles Anywhere** | [CreateSession API に VPC エンドポイントポリシー適用](https://aws.amazon.com/about-aws/whats-new/2026/05/iam-roles-anywhere-vpc/) | VPC エンドポイント経由のアクセスに対してきめ細かい制御が可能に。セキュリティポリシーの一貫性が向上 |
| 7 | **Payment Cryptography** | [物理的鍵交換（Paper-based Key Exchange）対応](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-payment-cryptography/) | 電子鍵交換未対応のパートナーとの取引に対応。PCI PIN / P2PE 準拠の鍵セレモニーを AWS 管理ファシリティで実施 |
| 8 | **EKS** | [CloudShell 経由のワンクリッククラスタアクセス](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-eks-one-click-cluster-access/) | ローカル環境の kubectl 設定不要で、AWS Console から直接 EKS クラスタに接続可能に。オンボーディングとトラブルシューティングを簡素化 |
| 9 | **EKS** | [EFA 対応 Dynamic Resource Allocation](https://aws.amazon.com/about-aws/whats-new/2026/05/kubernetes-dra-elastic-fabric-adapter/) | AI/ML/HPC ワークロードの高性能通信を簡素化。トポロジー認識型の割り当てで GPU 間通信を最適化 |
| 10 | **Bedrock AgentCore** | [On-Behalf-Of (OBO) トークン交換対応](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-bedrock-agentcore/) | ユーザーに代わって保護リソースにアクセスするエージェントを構築可能に。複数同意フローの手間を削減 |
| 11 | **ECS** | [Managed Instances で NVIDIA GPU メトリクス対応](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ecs-mi-gpu-metrics/) | Container Insights 経由で GPU ヘルスチェック、パフォーマンス、温度などをリアルタイム監視可能に |

## まとめ

本日のアップデートは、**グローバル分散システムの運用効率化**と**セキュリティ強化**という2つのテーマが色濃く反映されています。

OpenSearch UI のクロスリージョン対応と CloudFront の VPC オリジン WebSocket サポートは、いずれも「複数の場所に分散したリソースを統合的に管理する」というニーズに応えるものです。前者はデータレジデンシー要件を満たしながらグローバルな可視性を確保し、後者はリアルタイム通信のセキュリティアーキテクチャに新たな選択肢を提供します。

EKS 関連のアップデート（CloudShell 統合、EFA DRA）は、Kubernetes の運用障壁を下げつつ、AI/ML ワークロードの高性能化を実現しています。また、RDS や Redshift のエンタープライズ機能強化により、大規模データ基盤の柔軟性が向上しています。

これらのアップデートは、単体でも有用ですが、組み合わせることでさらに強力な運用基盤を構築できます。例えば、OpenSearch でグローバルログを統合監視しつつ、CloudFront + VPC オリジンでセキュアなリアルタイムダッシュボードを提供し、EKS 上で AI 分析ワークロードを実行する、といったアーキテクチャが考えられます。各アップデートの詳細な仕様や制限事項については、公式ドキュメントを参照してください。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)