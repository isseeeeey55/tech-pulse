---
title: "【AWS】2026/04/23 のアップデートまとめ"
date: 2026-04-23T08:02:36+09:00
draft: true
tags: ["aws", "ec2", "eks", "lambda", "ecs", "workspaces", "bedrock", "sagemaker", "opensearch", "cloudwatch", "corretto", "network-firewall", "secrets-manager", "ebs", "eni", "terraform", "kubernetes", "confluent", "mongodb"]
categories: ["AWS Updates"]
summary: "2026/04/23 のAWSアップデートまとめ"
---

# 2026年4月23日 AWS アップデート情報

## はじめに

2026年4月23日、AWSから14件のアップデートが発表されました。今回のアップデートでは、**マネージドリソースの可視性制御**や**ハイブリッドKubernetes環境のネットワーク自動化**、**生成AIを活用した運用自動化**など、運用の複雑性を軽減する機能が多数登場しています。特に注目すべきは、Amazon EC2のマネージドリソース可視性設定、Amazon EKS Hybrid Nodes gateway、そしてCloudWatch pipelinesのAI支援設定機能です。これらは共通して「運用負荷の削減」と「責任範囲の明確化」というテーマを持っており、SREチームにとって実用的な改善をもたらします。

## 注目アップデート深掘り

### Amazon EC2 マネージドリソース可視性設定

#### 背景と重要性

これまで、EKS、ECS、Lambda、WorkSpacesなどのマネージドサービスが自動的にプロビジョニングするEC2リソース（インスタンス、EBSボリューム、ENIなど）は、ユーザーが直接管理するリソースと区別なくEC2コンソールやAPI応答に表示されていました。これにより、「管理すべきリソース」と「AWSが管理するリソース」が混在し、リソース棚卸しやコスト分析、自動化スクリプトの精度に影響を与えていました。

今回のアップデートでは、**共有責任モデルとの整合性**を重視し、新規のマネージドリソースはデフォルトで非表示になります。これにより、運用チームは自分たちが責任を持つリソースに集中でき、誤操作のリスクも低減されます。

#### 実装と検証手順

まず、現在の設定状態を確認します。

```bash
$ aws ec2 get-managed-resource-visibility-settings --region us-east-1
```

デフォルトでは、新規マネージドリソースは非表示（`hidden`）に設定されています。既存のマネージドリソースの表示状態を変更する場合は、以下のコマンドを実行します。

```bash
$ aws ec2 put-managed-resource-visibility-settings \
    --region us-east-1 \
    --visibility-setting HIDDEN \
    --resource-types "instance" "volume" "snapshot" "network-interface"
```

設定前後での`describe-instances`の出力を比較してみましょう。

**設定前（マネージドリソース表示）：**

```bash
$ aws ec2 describe-instances --region us-east-1 --output table
# EKSノード、Lambdaの実行環境、自己管理インスタンスがすべて混在して表示される
```

**設定後（マネージドリソース非表示）：**

```bash
$ aws ec2 describe-instances --region us-east-1 --output table
# 自己管理インスタンスのみが表示される
```

タグベースでフィルタリングしている既存スクリプトへの影響も検証が必要です。例えば、Cost Explorerやリソースタグベースのレポート生成スクリプトは、マネージドリソースが非表示になっても引き続き正しく動作するかを確認しましょう。

```python
import boto3

ec2 = boto3.client('ec2', region_name='us-east-1')

# 自己管理インスタンスのみを取得
response = ec2.describe_instances(
    Filters=[
        {'Name': 'tag:Environment', 'Values': ['production']},
        {'Name': 'tag:ManagedBy', 'Values': ['terraform']}
    ]
)

for reservation in response['Reservations']:
    for instance in reservation['Instances']:
        print(f"Instance ID: {instance['InstanceId']}, State: {instance['State']['Name']}")
```

#### ユースケース別の推奨設定

| ユースケース | 推奨設定 | 理由 |
|------------|---------|------|
| EKS/ECS中心の環境 | `HIDDEN` | ノードは自動スケーリングされるため、EC2コンソールでの管理は不要 |
| Lambda中心の環境 | `HIDDEN` | Lambda実行環境のEC2リソースはAWS完全管理 |
| ハイブリッド環境 | `VISIBLE` | 一時的に可視化してリソース棚卸しを実施後、`HIDDEN`に切り替え |
| セキュリティ監査 | `VISIBLE` | すべてのリソースを可視化して包括的な監査を実施 |

> **Note:** 設定変更は既存のマネージドリソースには遡及的に適用されません。新規プロビジョニングされるリソースからのみ適用されます。

---

### Amazon EKS Hybrid Nodes Gateway

#### ハイブリッドKubernetesの課題

オンプレミスとAWSクラウドにまたがるKubernetes環境では、Pod間通信のために複雑なネットワーク設定が必要でした。従来は以下のような手作業が発生していました：

- VPCルートテーブルの手動更新
- オンプレミスルーターでの静的ルート設定
- IPアドレス範囲の競合回避
- Pod動的スケーリング時のルート再設定

Amazon EKS Hybrid Nodes Gatewayは、これらをHelm chartで自動化します。

#### デプロイと動作検証

まず、EKS Hybrid Nodes環境をセットアップします。

```bash
# EKSクラスターのコンテキストを設定
$ kubectl config use-context my-eks-cluster

# Helmリポジトリを追加
$ helm repo add eks-hybrid-nodes https://aws.github.io/eks-hybrid-nodes
$ helm repo update

# ゲートウェイをデプロイ
$ helm install eks-hybrid-gateway eks-hybrid-nodes/hybrid-nodes-gateway \
    --namespace kube-system \
    --set vpc.id=vpc-0123456789abcdef \
    --set subnet.id=subnet-0123456789abcdef \
    --set onpremises.cidr=10.0.0.0/16
```

デプロイ後、VPCルートテーブルが自動的に更新されていることを確認します。

```bash
$ aws ec2 describe-route-tables --route-table-ids rtb-0123456789abcdef --query 'RouteTables[0].Routes'
```

オンプレミスからAWS VPC内のPodへの疎通確認：

```bash
# オンプレミスノードから実行
$ kubectl run test-pod --image=nginx --restart=Never
$ kubectl get pod test-pod -o wide
# PodのIPアドレスを確認

$ curl http://<pod-ip>:80
# nginxのデフォルトページが返ってくることを確認
```

#### アーキテクチャと通信フロー

EKS Hybrid Nodes Gatewayは、EC2インスタンス上で動作する軽量なルーティングコンポーネントです。以下のような役割を担います：

1. **ルート自動検出**: Kubernetesクラスター内のPod CIDR範囲を自動検出
2. **VPC統合**: AWS VPCのルートテーブルを自動更新
3. **動的スケーリング対応**: Pod数が増減しても、ルートテーブルを自動的に調整
4. **ヘルスチェック**: ゲートウェイ自身の健全性を監視し、障害時は自動フェイルオーバー

Terraformでのデプロイ例：

```hcl
resource "aws_instance" "hybrid_gateway" {
  ami           = data.aws_ami.amazon_linux_2023.id
  instance_type = "t3.medium"
  subnet_id     = aws_subnet.public.id

  user_data = <<-EOF
    #!/bin/bash
    # Helmとkubectlをインストール
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    
    # EKSクラスターに接続
    aws eks update-kubeconfig --name ${var.cluster_name} --region ${var.region}
    
    # Hybrid Nodes Gatewayをデプロイ
    helm install eks-hybrid-gateway eks-hybrid-nodes/hybrid-nodes-gateway \
      --namespace kube-system \
      --set vpc.id=${var.vpc_id} \
      --set onpremises.cidr=${var.onpremises_cidr}
  EOF

  tags = {
    Name = "eks-hybrid-gateway"
    Role = "kubernetes-networking"
  }
}
```

> **Note:** ゲートウェイはオープンソースで公開されており、GitHubリポジトリでカスタマイズやコントリビュートが可能です。追加料金は不要で、基盤となるEC2インスタンスとデータ転送料のみが課金対象です。

---

### CloudWatch Pipelines AI支援設定機能

#### ログパイプライン設定の課題

従来、CloudWatch Logsでログを加工・変換するには、複雑なプロセッサ設定（Grokパターン、JSON解析、フィールド抽出、データ型変換など）を手動で組み合わせる必要がありました。特に非標準フォーマットのログや、ネストされたJSONフィールドの解析は試行錯誤が必要で、設定ミスによるログ欠損のリスクもありました。

今回のAI支援機能により、**自然言語でやりたいことを説明するだけ**で、AIが適切なプロセッサ構成を自動生成します。

#### 実装例

CloudWatchコンソールでパイプライン作成時に「AI assist」を有効化し、以下のようなプロンプトを入力します：

**プロンプト例1：**
```
Parse Nginx access logs in combined format, extract timestamp, status code, 
request path, and client IP. Convert status code to integer and mask the last 
octet of IP addresses for privacy.
```

AIが生成する設定例（YAML形式）：

```yaml
processors:
  - grok:
      match_patterns:
        - '%{COMBINEDAPACHELOG}'
  - parse_json:
      field: message
  - convert:
      fields:
        - field: status
          type: integer
  - mutate:
      gsub:
        - field: client_ip
          pattern: '\.\d+$'
          replacement: '.XXX'
  - add_fields:
      fields:
        pipeline_version: "1.0"
        processed_at: "%{@timestamp}"
```

**プロンプト例2：**
```
Extract error level, error code, and message from application logs in format:
[2026-04-23T10:30:45Z] ERROR code=5001 message="Database connection failed"
```

生成される設定：

```yaml
processors:
  - grok:
      match_patterns:
        - '\[%{TIMESTAMP_ISO8601:timestamp}\] %{LOGLEVEL:level} code=%{NUMBER:error_code} message="%{GREEDYDATA:error_message}"'
  - date:
      match:
        - timestamp
        - ISO8601
  - convert:
      fields:
        - field: error_code
          type: integer
```

#### サンプルログでの事前検証

AI生成後、デプロイ前にサンプルログで動作確認が可能です。

```bash
# サンプルログをテスト
$ aws logs test-pipeline-configuration \
    --pipeline-name test-nginx-pipeline \
    --pipeline-configuration file://pipeline-config.yaml \
    --sample-logs file://sample-nginx-logs.txt
```

サンプル出力（JSON形式）：

```json
{
  "ProcessedLogs": [
    {
      "timestamp": "2026-04-23T10:30:45Z",
      "status": 200,
      "request_path": "/api/users",
      "client_ip": "192.168.1.XXX",
      "pipeline_version": "1.0"
    }
  ],
  "Errors": []
}
```

#### Python SDKでの自動化

```python
import boto3

logs_client = boto3.client('logs')

# AI支援でパイプライン設定を生成
response = logs_client.create_pipeline_with_ai_assist(
    pipelineName='application-log-pipeline',
    description='Parse application logs in custom format and extract error information',
    naturalLanguagePrompt='''
    Extract timestamp, log level, error code, and error message from logs.
    Mask any email addresses found in the message for privacy.
    Add a field indicating the pipeline processing time.
    ''',
    sampleLogs=[
        '[2026-04-23T10:30:45Z] ERROR code=5001 message="User user@example.com login failed"',
        '[2026-04-23T10:31:20Z] WARN code=2003 message="Cache miss for key abc123"'
    ]
)

# 生成された設定を確認
print(response['GeneratedConfiguration'])

# テスト実行
test_response = logs_client.test_pipeline_configuration(
    pipelineName='application-log-pipeline',
    configuration=response['GeneratedConfiguration'],
    sampleLogs=response['SampleLogs']
)

print(f"Test passed: {test_response['Success']}")
print(f"Processed logs: {test_response['ProcessedLogs']}")
```

> **Note:** AI生成された設定は、必ず本番投入前にサンプルログでテストしてください。特殊なエッジケース（タイムゾーン、特殊文字、エスケープシーケンス）には追加調整が必要な場合があります。

---

## SRE視点での活用ポイント

### マネージドリソース可視性設定の活用

Terraformやインフラ自動化を行っているチームでは、`aws_instance`リソースのdata sourceクエリに影響が出る可能性があります。例えば、「すべてのEC2インスタンスにタグを適用する」といった処理を行っている場合、マネージドリソースを除外する明示的なフィルタリングを追加することで、意図しないリソースへの操作を防げます。

CloudWatch Alarmsやコスト監視ダッシュボードでは、マネージドリソースが非表示になっても、実際のコストとメトリクスは正確に集計されるため、Cost Explorerとの整合性は保たれます。ただし、リソースタグベースのレポーティングを行っている場合は、マネージドリソースのタグ付けルールをAWS側で標準化されているかを確認しておくと良いでしょう。

障害対応のランブックでは、「EC2コンソールで異常なインスタンスを特定する」といった手順がある場合、設定変更後は自己管理インスタンスのみが表示されるため、調査範囲が明確になり、MTTR（平均修復時間）の短縮が期待できます。

### EKS Hybrid Nodes Gatewayの運用改善

ハイブリッドKubernetes環境を運用する際の大きな課題は、ネットワークチームとアプリケーションチームの調整コストです。Pod追加のたびにルート変更依頼を出すのは非効率的で、自動化の妨げになります。EKS Hybrid Nodes Gatewayを導入すると、DevOpsチームがKubernetesマニフェストをデプロイするだけで、ネットワーク設定が自動的に追従します。

注意点として、オンプレミス側のファイアウォールルールやセキュリティグループは、引き続き手動設定が必要です。特に、ゲートウェイEC2インスタンスへの通信許可（通常はTCP/443、UDP/500など）を事前に確認しておきましょう。また、ゲートウェイインスタンスはSingle Point of Failureになり得るため、Auto Scaling GroupやMulti-AZ配置を検討することが推奨されます。

災害復旧シナリオでは、オンプレミス側で障害が発生した場合、AWS側のPodは影響を受けずに稼働し続けられます。逆に、AWS側で障害が発生した場合も、オンプレミスのワークロードは独立して動作します。このような部分的な冗長性を活かした障害対応手順を整備しておくと、ハイブリッド環境のレジリエンスが向上します。

### CloudWatch Pipelines AI支援の実践的利用

マイクロサービスアーキテクチャでは、各サービスが異なるログフォーマットを出力することが一般的です。これまでは、サービスごとにログパイプライン設定を個別に作成・メンテナンスする必要がありましたが、AI支援機能により、新サービス追加時のセットアップ時間を大幅に削減できます。

ログフォーマットが変更された場合も、自然言語で新しい要件を説明するだけで、設定を再生成できます。これにより、「ログフォーマット変更 → パイプライン設定更新 → 動作確認」のサイクルを高速化でき、アプリケーションのイテレーション速度向上に寄与します。

セキュリティとコンプライアンスの観点では、PII（個人識別情報）マスキングを自然言語で指定できるため、GDPR、CCPA、個人情報保護法などの規制対応が容易になります。「email addresses, credit card numbers, and phone numbers should be masked」といった指示で、適切なマスキングパターンが自動生成されます。

コスト最適化の面では、ログの前処理（フィルタリング、集約）をパイプライン段階で行うことで、ログストレージとクエリコストを削減できます。AI支援機能を使えば、「keep only ERROR and CRITICAL logs, drop DEBUG and INFO」といった指示で、効率的なフィルタリング設定が生成されます。

## 全アップデート一覧

| # | サービス | タイトル | 概要 |
|---|---------|---------|------|
| 1 | EC2 | [Managed resource visibility settings](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-managed-resource-visibility/) | マネージドサービスがプロビジョニングしたEC2リソースの表示/非表示を制御可能に |
| 2 | EC2 | [C8i instances in Ireland and New Zealand](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-ec2-c8i-instances-europe-ireland-asia-pacific-new-zealand-regions/) | Intel Xeon 6搭載の計算最適化インスタンスC8iが新リージョンで利用可能 |
| 3 | EC2 | [C8i-flex instances in Europe and New Zealand](https://aws.amazon.com/about-aws/whats-new/2026/02/amazon-ec2-c8i-flex-instances-europe-ireland-europe-london-asia-pacific-new-zealand-regions/) | C8i-flexインスタンスが3つの新リージョンで利用開始 |
| 4 | Bedrock | [AgentCore new features](https://aws.amazon.com/about-aws/whats-new/2026/04/agentcore-new-features-to-build-agents-faster/) | マネージドハーネス、CLI、スキルなどエージェント構築を加速する新機能 |
| 5 | SageMaker | [Serverless fine-tuning for Qwen3.5](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-sagemaker-ft-qwen3-5/) | Qwen3.5モデルのサーバーレス微調整をサポート |
| 6 | OpenSearch | [Rollback for service software updates](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-opensearch-service-now-supports-rollback-for-service-software-updates/) | サービスソフトウェアアップデートのロールバック機能を追加 |
| 7 | Corretto | [April 2026 Quarterly Updates](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-corretto-april-2026-quarterly-updates/) | Corretto全バージョンの四半期セキュリティアップデート |
| 8 | EC2 | [SQL Server HA health notifications](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-sql-ha-health-notifications/) | SQL Server HAのヘルス通知機能をAWS Health Dashboardで提供 |
| 9 | Network Firewall | [Marketplace managed rules enhancements](https://aws.amazon.com/about-aws/whats-new/2026/04/marketplace-managed-rules-enhancements/) | パートナー提供のマネージドルールが最大1,000万ドメイン、100万IPに対応 |
| 10 | SageMaker | [Generative AI inference recommendations](https://aws.amazon.com/about-aws/whats-new/2026/04/sagemaker-ai-inference-rec/) | 生成AIモデルの推論最適化を自動提案する機能 |
| 11 | Secrets Manager | [MongoDB Atlas and Confluent Cloud support](https://aws.amazon.com/about-aws/whats-new/2026/04/secrets-manager-managed-external-secrets-mongodb-confluent/) | MongoDB AtlasとConfluent Cloudの管理対象外部シークレット機能 |
| 12 | SageMaker | [Five new Qwen models in JumpStart](https://aws.amazon.com/about-aws/whats-new/2026/04/qwen-models-on-sagemaker-jumpstart/) | コーディングエージェントと推論に特化した5つのQwenモデル |
| 13 | EKS | [Hybrid Nodes gateway](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-eks-hybrid-nodes-gateway/) | ハイブリッドKubernetes環境のネットワーキングを自動化するゲートウェイ |
| 14 | CloudWatch | [AI-assisted pipeline configuration](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-cloudwatch-pipelines-ai-configuration/) | 自然言語でログパイプラインのプロセッサ設定を自動生成 |

## まとめ

2026年4月23日のアップデートは、**運用自動化とハイブリッド環境の統合**という2つの大きなテーマが目立ちました。EC2のマネージドリソース可視性制御は、共有責任モデルの明確化により、運用チームの認知負荷を軽減します。EKS Hybrid Nodes Gatewayは、オンプレミスとクラウドのシームレスな統合を実現し、ハイブリッドKubernetesの複雑なネットワーク設定を自動化します。CloudWatch PipelinesのAI支援機能は、ログ処理パイプラインの構築を劇的に簡素化し、マイクロサービス環境での迅速なログ統合を可能にします。

また、生成AI関連のアップデート（Bedrock AgentCore、SageMaker Qwen対応、推論最適化）も充実しており、エンタープライズでのAI活用が加速する基盤が整いつつあります。特にサーバーレス微調整とAI支援設定機能は、機械学習エンジニアやMLOpsチームの生産性向上に直結します。

セキュリティ面では、Secrets Managerの外部シークレット統合拡張、Network FirewallのMarketplaceルール強化など、マルチクラウド・ハイブリッド環境におけるセキュリティ管理の効率化が進んでいます。

今後も、こうした運用自動化と生成AI活用の流れは加速すると予想され、SREチームは新機能を積極的に検証し、既存の運用プロセスに組み込んでいくことが求められます。