---
title: "【AWS】2026/03/26 のアップデートまとめ"
date: 2026-03-26T08:01:24+09:00
draft: false
tags: ["aws", "sagemaker", "bedrock", "route53", "batch", "backup", "documentdb", "hyperpod", "ec2", "timestream", "iam", "eventbridge", "cloudwatch"]
categories: ["AWS Updates"]
summary: "2026/03/26 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260326/header.png)

# 2026年3月26日 AWS アップデート情報まとめ

## はじめに

本日は11件のAWSアップデートが発表されました。特に注目すべきは、Amazon SageMaker Unified StudioがCursor IDEからのリモート接続をサポート開始したことと、Amazon Bedrock AgentCoreがChromeエンタープライズポリシーとカスタムルート証明書に対応したことです。これらのアップデートは、MLエンジニアの開発体験向上とエンタープライズ環境でのAIエージェント運用の安全性強化を実現します。また、EC2 I7ieインスタンスの新リージョン展開やAWS BackupのDocumentDBサポート拡大など、インフラストラクチャとデータ保護分野でも重要な進展がありました。

## 注目アップデート深掘り

### Amazon SageMaker Unified StudioのCursor IDE連携で変わるML開発体験

![SageMaker Unified Studio — Cursor IDE リモート接続アーキテクチャ](/images/aws-updates-20260326/sagemaker-cursor-architecture.png)

Amazon SageMaker Unified StudioがCursor IDEからのリモート接続をサポートしたことで、機械学習開発のワークフローが大きく変わります。Cursor IDEのAIアシスト機能を活用しながら、クラウドの強力なコンピューティングリソースにシームレスにアクセスできるこの機能は、特にローカル環境のリソース制約に悩むデータサイエンティストにとって画期的です。

**AWS Toolkitの設定手順**

まず、Cursor IDEにAWS Toolkitをインストールし、SageMaker Unified Studioへの接続を設定します：

```bash
# AWS CLIでの認証情報設定
$ aws configure
AWS Access Key ID [None]: YOUR_ACCESS_KEY
AWS Secret Access Key [None]: YOUR_SECRET_KEY
Default region name [None]: us-east-1
Default output format [None]: json

# SageMaker Unified Studioへの接続テスト
$ aws sagemaker list-domains
```

Cursor IDEからの接続では、IAM認証を通じてセキュアにリモートリソースにアクセスできます。従来のローカル開発では、大容量データセットの処理やGPUを要する訓練時にリソース不足が発生しがちでしたが、この機能により、ローカルのコード補完機能を享受しながらクラウドの拡張性を活用できます。

**開発ワークフローの変化**

リモート接続により、以下のような開発体験の向上が期待されます：

```python
# Cursor IDEのAIアシストを使いながら、SageMakerのリソースで実行
import sagemaker
from sagemaker.sklearn import SKLearn

# ローカルで快適にコーディング、実行はクラウドで
estimator = SKLearn(
    entry_point='train.py',
    instance_type='ml.m5.large',
    framework_version='0.23-1'
)

estimator.fit({'train': 's3://your-bucket/train-data'})
```

この統合により、コード補完の恩恵を受けながら、メモリ集約的なデータ前処理や長時間の訓練をクラウド上で効率的に実行できるようになります。

### Amazon Bedrock AgentCoreがエンタープライズ環境で本格運用可能に

![Bedrock AgentCore — エンタープライズ環境でのAIエージェント運用](/images/aws-updates-20260326/agentcore-enterprise.png)

> **Amazon Bedrock AgentCoreとは？**
> Bedrock上でAIエージェントを構築・実行するためのマネージドランタイム環境です。LLMにツール呼び出しやブラウザ操作などの「行動」能力を持たせ、複雑なタスクを自律的に実行するエージェントをデプロイできます。従来のBedrock APIが「問いに答える」だけだったのに対し、AgentCoreは「実際に操作する」AIを実現するサービスです。

Amazon Bedrock AgentCoreのChromeエンタープライズポリシーとカスタムルート証明書サポートは、セキュリティ要件の厳しい企業環境でのAIエージェント導入を現実的なものにします。従来、AIエージェントの企業導入では、ネットワークセキュリティやアクセス制御の制約が大きな障壁となっていましたが、この機能により企業のセキュリティポリシーに準拠した運用が可能になります。

**エンタープライズポリシーの実装**

Chrome エンタープライズポリシーの設定により、AIエージェントの動作を組織のセキュリティ方針に合わせて制御できます：

```json
{
  "BlockedDomains": ["*.social-media.com", "*.file-sharing.com"],
  "AllowedDomains": ["*.company.com", "*.trusted-partner.com"],
  "SecurityLevel": "high",
  "DownloadRestrictions": {
    "BlockDangerousDownloads": true,
    "PromptForDownload": true
  }
}
```

**カスタムルート証明書の設定**

社内のプライベート証明書局（CA）を使用している環境では、以下のような設定でAgentCoreが社内システムに安全にアクセスできます：

```bash
# カスタムCA証明書のアップロード
$ aws bedrock put-agent-runtime-config \
    --agent-id "your-agent-id" \
    --custom-ca-certificates file://company-root-ca.pem \
    --chrome-policies file://enterprise-policies.json
```

この機能により、金融機関や医療機関など、高度なセキュリティ要件を持つ業界でも、AIエージェントを活用した業務自動化が実現できます。従来のWebスクレイピングやブラウザ自動化ツールでは困難だった、企業のセキュリティポリシーに完全準拠したAIエージェント運用が可能になります。

## SRE視点での活用ポイント

今回のアップデートをSREの観点から見ると、特に運用の自動化と信頼性向上に寄与する要素が多く含まれています。

**Bedrock AgentCoreのエンタープライズ対応**は、AIを活用した障害対応の自動化において重要な意味を持ちます。例えば、社内の監視ダッシュボードや運用ツールにアクセスするAIエージェントを構築する際、カスタム証明書とポリシー制御により、セキュリティ要件を満たしながら自動化を実現できます。Terraformでインフラを管理している環境では、以下のような設定でAgentCoreを組み込めます：

```hcl
resource "aws_bedrock_agent" "ops_assistant" {
  agent_name = "ops-assistant"
  
  runtime_config {
    custom_ca_certificates = var.company_ca_certificates
    chrome_policies       = jsonencode(var.enterprise_policies)
  }
}
```

**AWS BatchのAMI状態管理とHealth Events連携**は、バッチワークロードの安定運用に直接的な改善をもたらします。CloudWatch アラームと組み合わせることで、古いAMIを使用しているコンピューティング環境を事前に検知し、計画的なメンテナンス窓での更新を自動化できます。Amazon EventBridge経由でSlackやPagerDutyに通知を送ることで、インシデント化する前の予防的対応が可能になります。

**EC2 I7ieインスタンスの新リージョン展開**は、レイテンシセンシティブなワークロードの地理的分散に活用できます。特に大容量のローカルストレージを活用するログ解析基盤やリアルタイム分析システムにおいて、ユーザーに近いリージョンでの高性能処理が可能になります。ただし、新しいインスタンスタイプの導入時は、既存のモニタリング設定や自動スケーリングポリシーの見直しが必要になる点に注意が必要です。

導入判断においては、セキュリティ要件とのバランス、既存システムへの影響範囲、そして段階的な移行計画の策定が重要になります。

## 全アップデート一覧

> **Amazon SageMaker HyperPodとは？**
> 大規模MLモデルの分散トレーニングに特化したマネージドクラスター環境です。SlurmやEKSをオーケストレーターとして使い、数百〜数千GPUの学習ジョブを自動復旧・ヘルスチェック付きで実行できます。自前でGPUクラスターを構築・運用する手間を大幅に削減するサービスです。

> **Amazon Timestream for InfluxDBとは？**
> オープンソースの時系列DB「InfluxDB」をAWSがフルマネージドで提供するサービスです。IoTセンサーデータやアプリケーションメトリクスの収集・分析に適しており、既存のInfluxDB互換クライアントやクエリ（Flux、InfluxQL）がそのまま使えます。

| サービス | アップデート内容 | 概要 |
|----------|------------------|------|
| [Amazon SageMaker Unified Studio](https://aws.amazon.com/about-aws/whats-new/2026/03/sagemaker-unified-studio-cursor-ide/) | Cursor IDEからのリモート接続サポート | AWS ツールキット拡張機能を通じて、ローカルIDEからクラウドリソースに直接アクセス可能 |
| [Amazon SageMaker AI](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-sagemaker-ai-serverless-additional-models/) | 12モデルのサーバーレス強化学習ファインチューニング対応 | インフラ管理不要で、SFT、DPO、RFTによる高度なモデル調整が可能 |
| [Amazon Route 53 Profiles](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-route-53-profiles-granular-iam/) | 詳細なIAM権限のサポート | リソースとVPCアソシエーションに対する細かなアクセス制御が可能 |
| [Amazon Bedrock AgentCore](https://aws.amazon.com/about-aws/whats-new/2026/03/agentcore-browser-policies-root-ca/) | Chromeポリシーとカスタムルート証明書サポート | エンタープライズ環境でのセキュアなAIエージェント運用を実現 |
| [AWS Batch](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-batch-ami-status-aws-health/) | AMI状態とAWS Health連携 | AMIのライフサイクル管理と計画的なメンテナンス対応を強化 |
| [AWS Batch](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-batch-quota-management-preemption-sagemaker/) | SageMakerジョブのクォータ管理とプリエンプション | 柔軟なリソース管理と優先度制御による効率化を実現 |
| [Amazon Bedrock AgentCore Runtime](https://aws.amazon.com/about-aws/whats-new/2026/03/bedrock-agentcore-runtime-session-storage/) | 永続化セッションストレージ (プレビュー) | ファイルシステム状態の永続化による継続的な開発作業をサポート |
| [AWS Backup](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-backup-amazon-documentdb-regions/) | DocumentDBサポートを12リージョンに拡大 | グローバル展開でのポリシーベースデータ保護を強化 |
| [Amazon SageMaker HyperPod](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-sagemaker-hyperpod-continuous-provisioning/) | Slurmクラスターの継続プロビジョニング | 大規模MLトレーニングでのリソース可用性を改善 |
| [Amazon EC2 I7ie](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-ec2-i7ie-instances-additional-aws-regions/) | 7リージョンで新規利用開始 | ストレージ最適化インスタンス（Intel Xeon第5世代、最大120TB NVMe）の地理的展開 |
| [Amazon Timestream for InfluxDB](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-timestream-influxdb-mexico-osaka-sao-paulo/) | 3リージョンで新規サポート | 時系列データベースサービスの地理的可用性を拡大 |

## まとめ

本日のアップデートは、AI/ML開発の生産性向上とエンタープライズ環境での実用性強化に重点が置かれています。SageMaker Unified StudioのCursor IDE連携は開発者体験を大幅に改善し、Bedrock AgentCoreのエンタープライズ機能は企業でのAI活用の障壁を取り除きます。

また、AWS BatchのAMI管理強化やEC2インスタンスの地理的展開など、インフラ運用の信頼性と効率性を高めるアップデートも充実しています。これらの機能を適切に組み合わせることで、よりロバストで自動化された運用環境の構築が可能になるでしょう。

特に注目すべきは、AIと従来のクラウドサービスの境界がますます曖昧になり、統合された開発・運用体験が提供され始めていることです。今後もこの傾向は続くと予想され、SREやDevOpsエンジニアにとってAI活用スキルの重要性がさらに高まっていくと考えられます。