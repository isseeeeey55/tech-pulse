---
title: "【AWS】2026/04/09 のアップデートまとめ"
date: 2026-04-09T08:01:22+09:00
draft: true
tags: ["aws", "workspaces", "ivs", "eks", "ec2", "sagemaker", "bedrock", "opensearch", "oracle", "graviton"]
categories: ["AWS Updates"]
summary: "2026/04/09 のAWSアップデートまとめ"
---

## はじめに

2026年4月9日のAWSアップデートでは、7件の新機能・改善が発表されました。特に注目すべきは、Amazon EKSマネージドノードグループでのEC2 Auto Scalingウォームプール対応と、SageMaker HyperPodのギャングスケジューリング機能です。これらのアップデートは、コンテナワークロードの高速スケーリングと機械学習の分散トレーニング効率化という、現代的なクラウド運用の中核的な課題に対するソリューションを提供しています。

## 注目アップデート深掘り

### Amazon EKSマネージドノードグループでのEC2ウォームプール対応

このアップデートは、EKSクラスターの運用において長年の課題となっていた「コールドスタート問題」に対する画期的なソリューションです。従来のオートスケーリングでは、需要増加に対してインスタンスの起動からPodのスケジューリングまで数分を要することが珍しくありませんでした。特に、複雑な初期化スクリプトやコンテナイメージのプルが必要なワークロードでは、この遅延が致命的な影響を与える場合もありました。

ウォームプールは、事前に初期化されたEC2インスタンスをプールとして保持する仕組みです。これらのインスタンスは2つの状態で管理できます：

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

Terraformでの実装例も確認してみましょう：

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

検証では、通常のスケールアウトが平均3-5分かかるのに対し、ウォームプール利用時は30秒-1分程度に短縮されることが期待されます。特に「Stopped」状態のウォームプールは、EBSボリュームが保持されるためブート時間が大幅に短縮され、「Running」状態では即座にトラフィックを受け入れ可能です。

Cluster Autoscalerとの統合についても重要な検証ポイントです。Cluster Autoscalerの設定を以下のように調整することで、ウォームプール対応を最適化できます：

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

機械学習の分散トレーニングにおいて、複数ノードでの協調実行は複雑な課題を抱えていました。従来のスケジューリングでは、一部のPodが先に起動し、他のPodの準備を待つ状況が発生し、結果として計算リソースの無駄やデッドロックが生じることがありました。

ギャングスケジューリングは、分散ジョブの全コンポーネント（Podやワーカー）が同時に利用可能になるまで実行を遅延させる仕組みです。これにより、部分的なジョブ実行によるリソース浪費を防ぎ、より効率的な分散トレーニングが実現されます。

実装例として、SageMaker HyperPodでのギャングスケジューリング設定を確認してみましょう：

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

この機能の効果は、特に大規模なトランスフォーマーモデルや分散深層学習において顕著に現れます。従来の実行では、8ノード中6ノードが起動済みの状態で残り2ノードを待つ間、計算リソースが無駄になっていました。ギャングスケジューリングにより、全ノードが準備完了してから一斉に実行開始することで、リソース効率性が大幅に向上します。

## SRE視点での活用ポイント

これらのアップデートは、SREチームが日常的に直面する運用課題に対して実用的なソリューションを提供します。

EKSのウォームプール機能は、特にトラフィックが急激に変動するサービスの運用で威力を発揮します。例えば、eコマースサイトのセール開始時やゲーム配信でのイベント開始時など、予測可能な負荷スパイクに対して事前準備が可能になります。Terraformでインフラを管理している環境であれば、ウォームプールの設定をコード化し、アプリケーションの特性に応じて「Stopped」と「Running」のどちらが適切かを検討できます。コスト最適化の観点では、「Stopped」状態はEBS料金のみでEC2利用料は発生しないため、待機コストを抑制しながら高速スケーリングを実現できます。

一方で、導入時にはワークロードの初期化時間やスケーリングパターンを詳細に分析する必要があります。CloudWatch メトリクスでスケールアウト頻度や所要時間を計測し、ウォームプールサイズの適切な設定値を決定することが重要です。

SageMaker HyperPodのギャングスケジューリングは、MLOpsパイプラインの信頼性向上に寄与します。分散トレーニングジョブの失敗率低減により、モデル学習の再実行コストを削減でき、開発サイクルの予測可能性が向上します。特に、定期的なモデル再学習を自動化している環境では、ジョブの成功率向上により運用負荷が軽減されます。

ただし、ギャングスケジューリング有効化により、リソース待機時間が延長される可能性もあるため、クラスターのリソース利用率とジョブ実行スケジュールのバランスを慎重に設計する必要があります。アラート設定やメトリクス監視を通じて、リソース効率性の変化を継続的に監視することが推奨されます。

## 全アップデート一覧

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

今回のアップデートは、運用効率性とパフォーマンス最適化に焦点を当てた内容が中心となりました。EKSのウォームプール対応とSageMaker HyperPodのギャングスケジューリングは、いずれも「待機時間の最小化」という共通テーマを持ち、現代的なクラウドネイティブアプリケーションと機械学習ワークロードの要求に応えるものです。

また、Amazon OpenSearch ServiceでのGraviton4インスタンス対応や、Oracle Database@AWSのリージョン拡大など、基盤サービスの強化も着実に進んでいることが確認できます。これらのアップデートは、企業がAWSでより高度で効率的なシステムを構築するための選択肢を広げ、運用コストの最適化にも寄与するでしょう。