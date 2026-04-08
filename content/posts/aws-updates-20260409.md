---
title: "【AWS】2026/04/09 のアップデートまとめ"
date: 2026-04-09T08:01:22+09:00
draft: false
tags: ["aws", "workspaces", "ivs", "eks", "ec2", "sagemaker", "bedrock", "opensearch", "oracle", "graviton"]
categories: ["AWS Updates"]
summary: "2026/04/09 のAWSアップデートまとめ"
---

![](/tech-pulse/images/aws-updates-20260409/header.png)

## はじめに

2026年4月9日のAWSアップデートは7件。EKSマネージドノードグループのウォームプール対応と、SageMaker HyperPodのギャングスケジューリングが目玉です。どちらも「待ち時間を減らす」方向のアップデートで、EKSはノード起動の高速化、HyperPodは分散トレーニングのリソース同期にそれぞれ効きます。

## 注目アップデート深掘り

### Amazon EKSマネージドノードグループでのEC2ウォームプール対応

![EKS ウォームプールによるスケールアウト時間の比較](/tech-pulse/images/aws-updates-20260409/warm-pool-comparison.png)

EKSのオートスケーリングでは、インスタンス起動からPodスケジューリングまで3〜5分かかることがあります。初期化スクリプトが重い場合はさらに伸びる。今回のウォームプール対応で、事前に初期化済みのインスタンスをプールしておけるようになりました。

インスタンスの状態は「Stopped」と「Running」の2種類から選べます：

```bash
# ウォームプール対応のマネージドノードグループ作成例
$ eksctl create nodegroup \
  --cluster my-cluster \
  --name warm-pool-ng \
  --node-type m5.large \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 10 \
  --asg-access \
  --warm-pool-enabled \
  --warm-pool-min-size 2 \
  --warm-pool-max-prepared-capacity 5
```

Terraformでの設定例：

```hcl
resource "aws_autoscaling_group" "eks_warm_pool" {
  name                = "${var.cluster_name}-warm-pool-asg"
  vpc_zone_identifier = var.subnet_ids
  
  min_size         = 1
  max_size         = 10
  desired_capacity = 3

  launch_template {
    id      = aws_launch_template.eks_node.id
    version = "$Latest"
  }

  warm_pool {
    pool_state                  = "Stopped"
    min_size                    = 2
    max_group_prepared_capacity = 5
    
    instance_reuse_policy {
      reuse_on_scale_in = true
    }
  }

  tag {
    key                 = "kubernetes.io/cluster/${var.cluster_name}"
    value               = "owned"
    propagate_at_launch = true
  }
}
```

通常のスケールアウトが3〜5分かかるところ、ウォームプールなら30秒〜1分程度。「Stopped」状態ではEBSボリュームが保持されるのでブートが速く、EC2利用料も発生しません。「Running」状態なら即座にトラフィックを受け入れられます。

Cluster Autoscalerと組み合わせる場合、以下のような設定が参考になります：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
spec:
  template:
    spec:
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
        name: cluster-autoscaler
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/my-cluster
        - --scale-down-enabled=true
        - --scale-down-delay-after-add=1m
        - --scale-down-unneeded-time=2m
```

### SageMaker HyperPodのギャングスケジューリング機能

> **SageMaker HyperPodとは？**
> SageMakerの基盤モデルトレーニング向けマネージドクラスターサービスです。数百〜数千GPUの大規模クラスターを、ノード障害時の自動復旧やヘルスチェック付きで運用できます。通常のSageMaker Training Jobとの違いは、長時間の継続トレーニングに最適化されている点です。

分散トレーニングで8ノード使うとき、6ノードだけ先に起動して残り2ノードを待つ、という状況はよくあります。先に起動したノードはその間GPUを確保したまま何もしていない。これがリソースの無駄になります。

ギャングスケジューリングは、全ノードの準備が揃うまでジョブの実行開始を保留する仕組みです。「全員揃ってから一斉スタート」なので、部分起動による無駄がなくなります。

SageMaker HyperPodでの設定例：

```python
import boto3

sagemaker = boto3.client('sagemaker')

# HyperPodクラスター作成時のギャングスケジューリング設定
cluster_config = {
    'ClusterName': 'my-ml-cluster',
    'InstanceGroups': [
        {
            'InstanceGroupName': 'worker-group',
            'InstanceType': 'ml.p4d.24xlarge',
            'InstanceCount': 8,
            'LifeCycleConfig': {
                'SourceS3Uri': 's3://my-bucket/lifecycle-config.sh',
                'OnCreate': 'lifecycle-config.sh'
            }
        }
    ],
    'Orchestrator': {
        'Eks': {
            'ClusterArn': 'arn:aws:eks:us-west-2:123456789012:cluster/my-eks-cluster'
        }
    }
}

# ギャングスケジューリング有効化
training_job_config = {
    'RoleArn': 'arn:aws:iam::123456789012:role/SageMakerRole',
    'InputDataConfig': [{
        'ChannelName': 'training',
        'DataSource': {
            'S3DataSource': {
                'S3DataType': 'S3Prefix',
                'S3Uri': 's3://my-bucket/training-data/'
            }
        }
    }],
    'AlgorithmSpecification': {
        'TrainingImage': '763104351884.dkr.ecr.us-west-2.amazonaws.com/pytorch-training:1.12.0-gpu-py38',
        'TrainingInputMode': 'File'
    },
    'HyperParameters': {
        'gang-scheduling': 'enabled',
        'min-worker-nodes': '8',
        'coordination-timeout': '300'
    }
}
```

Kubernetesのジョブ定義では、以下のようなアノテーションでギャングスケジューリングを制御できます：

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: distributed-training-job
  annotations:
    scheduler.alpha.kubernetes.io/gang-scheduling: "true"
    scheduler.alpha.kubernetes.io/gang-min-available: "8"
spec:
  parallelism: 8
  completions: 8
  template:
    metadata:
      annotations:
        scheduler.alpha.kubernetes.io/gang-name: "distributed-training-job"
    spec:
      restartPolicy: Never
      containers:
      - name: pytorch-worker
        image: my-training-image:latest
        resources:
          requests:
            nvidia.com/gpu: 8
          limits:
            nvidia.com/gpu: 8
```

大規模なトランスフォーマーモデルの学習や、数百GPU規模の分散深層学習で特に効果が出ます。p4d.24xlargeを8台使う構成なら、1台あたり約$32/hのGPUコストが無駄にならなくなる計算です。

## SRE視点での活用ポイント

EKSウォームプールは、セール開始やイベント配信のような予測可能な負荷スパイクに向いています。Terraform管理なら `warm_pool` ブロックをそのままコード化できるのも良い。「Stopped」と「Running」の使い分けは、初期化スクリプトの実行時間で判断するのがわかりやすいです。数十秒で済むなら「Stopped」（EBS料金のみ）、数分かかるなら「Running」を検討してください。

導入前にCloudWatchでスケールアウト頻度と所要時間を計測しておくと、ウォームプールサイズの見積もりがしやすくなります。

HyperPodのギャングスケジューリングは、定期的なモデル再学習を自動化している環境で地味に効きます。部分起動→タイムアウト→再実行のループが減るので、GPUコストの無駄も小さくなる。ただし、全ノードが揃うまで実行開始しない分、クラスターのリソース利用率は下がる場合があります。ジョブの投入間隔とクラスターサイズのバランスは確認しておきましょう。

## 全アップデート一覧

> **Amazon IVS（Interactive Video Service）とは？**
> ライブ動画配信のインフラをマネージドで提供するサービスです。Twitchの配信基盤と同じ技術を使っており、低遅延のリアルタイムストリーミングとスタンダードストリーミングの2モードがあります。

> **Amazon Bedrock AgentCoreとは？**
> Bedrock上でAIエージェントの実行環境・ツール連携・メモリ管理を提供するサービスです。AgentCore Browserはその中のコンポーネントで、エージェントがWebブラウザを操作できるようにする機能です。

> **Oracle Database@AWSとは？**
> OracleデータベースをAWSのデータセンター内で直接実行できるサービスです。Oracle Exadata基盤がAWSリージョンに物理設置されており、RDSやAuroraとは異なり、Oracle純正のライセンスと機能をそのまま使えます。

> **Graviton4とは？**
> AWSが自社設計したArm系プロセッサの第4世代です。Graviton3比で最大30%のコンピュート性能向上と低消費電力が特徴。i8geインスタンスはGraviton4搭載のストレージ最適化型で、OpenSearchのようなデータ集約ワークロードに向いています。

| サービス | タイトル | 概要 |
|---------|---------|------|
| Amazon WorkSpaces | [Amazon WorkSpaces Advisor now available for AI-powered troubleshooting](https://aws.amazon.com/about-aws/whats-new/2026/04/workspaces-advisor-ai-troubleshooting/) | AI を活用した WorkSpaces のトラブルシューティング支援機能を提供 |
| Amazon IVS | [Amazon IVS Real-Time Streaming now supports redundant ingest](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ivs-real-time-streaming-redundant-ingest/) | リアルタイムストリーミングで冗長インジェスト機能をサポート、配信の可用性向上 |
| Amazon EKS | [Amazon EKS managed node groups now support EC2 Auto Scaling warm pools](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-eks-managed-node-groups-ec2-warm-pools/) | マネージドノードグループでウォームプール対応、高速スケーリングを実現 |
| SageMaker HyperPod | [SageMaker HyperPod now supports gang scheduling for distributed training workloads](https://aws.amazon.com/about-aws/whats-new/2026/04/sagemaker-hyperpod-gang-scheduling/) | 分散トレーニング向けのギャングスケジューリング機能を追加 |
| Amazon Bedrock | [Amazon Bedrock AgentCore Browser adds OS-level interaction capabilities](https://aws.amazon.com/about-aws/whats-new/2026/04/agentcore-browser-os-actions/) | AgentCore Browser で OS レベルの操作機能を強化 |
| Amazon OpenSearch | [Amazon OpenSearch Service now supports Graviton4 based i8ge instances](https://aws.amazon.com/about-aws/whats-new/2026/4/amazon-opensearch-service-supports-i8ge/) | Graviton4 搭載の i8ge インスタンス（ストレージ最適化）をサポート |
| Oracle Database@AWS | [Oracle Database@AWS is now available in twelve AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/04/oracle-database-aws-available-twelve-regions/) | Oracle Database@AWS が12のリージョンで利用可能に拡大 |

## まとめ

EKSウォームプールとHyperPodギャングスケジューリング、どちらも「待ち時間を減らす」アップデートです。ウォームプールはスケールアウトを3〜5分→30秒〜1分に、ギャングスケジューリングは部分起動による無駄なGPU課金をカットします。

OpenSearchのGraviton4対応（i8geインスタンス）やOracle Database@AWSの12リージョン展開も、検索・DB基盤を触る機会があればチェックしておくと良さそうです。