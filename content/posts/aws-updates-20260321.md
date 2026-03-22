---
title: "【AWS】2026/03/21 のアップデートまとめ"
tags: ["aws", "update"]
date: "2026-03-21T08:00:00+09:00"
categories: ["AWS Updates"]
summary: "Bedrock AgentCore RuntimeへのWebRTC追加、EKS Provisioned Control Planeの99.99% SLA・8XLティア新設が目立つ6件のアップデート。"
draft: false
---

![](/images/aws-updates-20260321/header.png)

## はじめに

2026年3月21日のAWSアップデートは6件。Bedrock AgentCore RuntimeへのWebRTC追加、EKS Provisioned Control Planeの99.99% SLA・8XLティア新設が目立ちます。ほかにNeuronのDRAサポート、DataSyncのSecrets Manager対応、RedshiftのIAM Identity Center連携強化など。

## 注目アップデート深掘り

### Amazon Bedrock AgentCore RuntimeにWebRTCサポートを追加

AgentCore Runtimeに、既存のWebSocketに加えてWebRTCプロトコルが追加されました。ブラウザやモバイルアプリでの音声AIエージェント構築で、UDPベースの低レイテンシー双方向ストリーミングが使えるようになります。

![Bedrock AgentCore Runtime WebRTC構成図](/images/aws-updates-20260321/bedrock-webrtc-architecture.png)

**WebSocketとの違い**

WebSocketはTCPベースの永続接続で、テキストや音声のストリーミングには向いています。一方、リアルタイムの音声・映像通信ではUDPベースのWebRTCのほうがレイテンシーが低い。これまで音声AIエージェントを作るには独自のメディアサーバーを構成する必要がありましたが、AgentCore Runtimeが直接WebRTCをサポートしたことでその手間がなくなります。

**TURNリレーの構成オプション**

> **NAT越え（NAT Traversal）とは？**
> WebRTCは端末同士が直接通信するP2P方式ですが、ほとんどの端末はルーター（NAT）の背後にいるため、外部から直接繋がりません。この壁を越えるのがNAT越えです。
>
> まずSTUNサーバーが端末のグローバルIPを特定してP2P接続を試みます。それでもダメな場合（対称NATやファイアウォール環境）、**TURNサーバー**が中継役としてデータを仲介します。TURNを経由するとP2Pではなくなるのでレイテンシーは若干増えますが、ほぼどんなネットワーク環境でも接続できます。

NAT越えが必要な場合、3つの選択肢があります。

- **Amazon Kinesis Video Streams マネージドTURN**（推奨）: フルマネージド。AWS IAM統合済みで、TURNサーバーの自前運用が不要
- **サードパーティTURNプロバイダー**: Twilio、Xirsysなど。すでに使っていれば移行コストが低い
- **セルフホストTURN**: coturnなどをEC2上で運用。自由度は高いが、可用性やスケーリングは自分で面倒を見る必要がある

**対応リージョン**

東京を含む14リージョンで利用可能（米国3、アジア太平洋5、欧州5、カナダ1）。Amazon Nova Sonicを使った音声エージェントのサンプルや、Pipecat・LiveKit・Strands Agents SDKとの連携実装例も公開されています。

### Amazon EKS Provisioned Control Planeの99.99% SLAと8XLティア

EKS Provisioned Control PlaneのSLAが99.95%から99.99%に引き上げられました。また、8XLスケーリングティアが追加され、4XLの2倍のKubernetes APIサーバーリクエスト処理能力を持ちます。

**SLA引き上げの実際の意味**

99.95%→99.99%は、年間ダウンタイム許容量で約26分→約5分。数字としてはわずかですが、ミッションクリティカルなワークロードにとっては大きな差です。可用性は1分間隔で測定されます。

**8XLティアのユースケース**

- 超大規模AI/MLトレーニングクラスター
- ハイパフォーマンスコンピューティング（HPC）
- 大規模データ処理パイプライン
- 数千ノード規模のクラスター運用

EKS Provisioned Control Planeが提供されている全リージョンで利用可能です。

### AWS NeuronがEKSでDynamic Resource Allocation（DRA）をサポート

> **AWS Neuronとは？**
> AWSの独自AIチップ「Trainium」（学習用）と「Inferentia」（推論用）向けのSDK。コンパイラ、ランタイム、プロファイラを含み、PyTorchやTensorFlowで書かれたモデルをこれらのチップ上で動かすためのソフトウェアスタック。NVIDIAのCUDAに相当するものと考えるとわかりやすいです。

従来のKubernetesでは、GPU等の特殊ハードウェアの割り当てはDevice Pluginに依存していて、細かな制御が難しい状態でした。DRAを使うと、ハードウェアトポロジーとデバイス属性がKubernetesスケジューラに直接公開され、柔軟なリソース管理ができるようになります。

**何が変わるのか**

大規模MLワークロードでは、複数のTrainiumチップを効率的に割り当てることが性能に直結します。従来はMLエンジニアがインフラの詳細を把握して手動で設定する必要がありましたが、DRAならKubernetesネイティブなリソース要求として記述できます。

**具体的な検証手順**

まず、EKSクラスターでNeuron DRAドライバを有効化します：

```bash
# Neuron DRAドライバのインストール
kubectl apply -f https://raw.githubusercontent.com/aws-neuron/aws-neuron-eks-samples/main/dra/neuron-dra-driver.yaml

# ResourceClassの確認
kubectl get resourceclass
```

次に、ResourceClaimTemplateを定義してMLワークロードに適用します：

```yaml
# resource-claim-template.yaml
apiVersion: resource.k8s.io/v1alpha2
kind: ResourceClaimTemplate
metadata:
  name: trainiumv1-claim-template
spec:
  spec:
    resourceClassName: trainiumv1.neuron.aws
    parametersRef:
      apiVersion: resource.neuron.aws/v1alpha1
      kind: TrainiumParameters
      name: multi-chip-params
```

```yaml
# ml-workload.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: distributed-training-job
spec:
  template:
    spec:
      resourceClaims:
      - name: trainiumv1
        source:
          resourceClaimTemplateName: trainiumv1-claim-template
      containers:
      - name: training-container
        image: your-ml-image:latest
        resources:
          claims:
          - name: trainiumv1
```

**従来の方法との比較**

Device Plugin方式では、静的なリソース定義しか書けません：

```yaml
# 従来の方法
resources:
  limits:
    aws.amazon.com/neuron: 8
```

DRA方式なら、トポロジーを考慮した動的な指定が可能です：

```yaml
# DRA方式
parametersRef:
  apiVersion: resource.neuron.aws/v1alpha1
  kind: TrainiumParameters
  name: optimized-topology-params
```

**パフォーマンス測定の観点**

MLワークロードでの効果を測るには、以下のメトリクスを監視します：

```python
import boto3
import time

def measure_resource_allocation_time():
    """リソース割り当て時間の測定"""
    start_time = time.time()

    # Kubernetes APIでPodの状態を監視
    # リソース割り当て完了までの時間を測定

    allocation_time = time.time() - start_time
    return allocation_time

def compare_training_throughput():
    """学習スループットの比較"""
    # DRA使用時とDevice Plugin使用時のスループット比較
    pass
```

### AWS DataSyncでSecrets Manager対応強化

DataSyncが全ロケーションタイプでSecrets Managerに対応しました。認証情報を平文で渡す必要がなくなり、Secrets Managerで暗号化・管理できます。

**セキュリティ向上の具体例**

従来は認証情報をパラメータストアやハードコーディングで管理していました：

```bash
# 従来の方法（非推奨）
aws datasync create-location-smb \
    --server-hostname example.com \
    --user myuser \
    --password "hardcoded-password" \
    --subdirectory /data
```

Secrets Managerを使う方法：

```bash
# Secrets Managerにクレデンシャルを保存
aws secretsmanager create-secret \
    --name "datasync/smb-credentials" \
    --description "SMB server credentials for DataSync" \
    --secret-string '{"username":"myuser","password":"secure-password"}'

# DataSyncロケーション作成時にSecrets Managerを参照
aws datasync create-location-smb \
    --server-hostname example.com \
    --secrets-manager-arn "arn:aws:secretsmanager:region:account:secret:datasync/smb-credentials" \
    --subdirectory /data
```

**Terraformでの実装例**

```hcl
resource "aws_secretsmanager_secret" "datasync_credentials" {
  name = "datasync/nfs-credentials"
  description = "NFS credentials for DataSync transfer"
}

resource "aws_secretsmanager_secret_version" "datasync_credentials" {
  secret_id = aws_secretsmanager_secret.datasync_credentials.id
  secret_string = jsonencode({
    username = var.nfs_username
    password = var.nfs_password
  })
}

resource "aws_datasync_location_nfs" "source" {
  server_hostname = "nfs.example.com"
  subdirectory    = "/exports/data"

  secrets_manager_arn = aws_secretsmanager_secret.datasync_credentials.arn

  on_prem_config {
    agent_arns = [aws_datasync_agent.on_premises.arn]
  }
}
```

**コンプライアンス対応**

SOC 2やISO 27001の要件を満たしやすくなります。認証情報の自動ローテーションも設定可能です：

```python
import boto3

def setup_credential_rotation():
    """認証情報の自動ローテーション設定"""
    secrets_client = boto3.client('secretsmanager')

    response = secrets_client.rotate_secret(
        SecretId='datasync/smb-credentials',
        RotationLambdaArn='arn:aws:lambda:region:account:function:rotate-datasync-credentials',
        RotationRules={
            'AutomaticallyAfterDays': 30
        }
    )
    return response
```

## SRE視点での活用ポイント

**Neuron DRAの導入判断**

TerraformでEKSクラスターを管理しているなら、DRAの導入は検討に値します。MLエンジニアから「リソースが足りない」「配置が最適でない」という問い合わせが多い環境では、DRAで解決できるケースがあります。複数チームが同一クラスターを共有しているなら、リソース競合の軽減にも効きます。

ただし、DRAはまだ新しい機能です。本番投入前にステージング環境で検証し、既存ワークロードへの影響がないことを確認してください。

**DataSync × Secrets Managerの運用**

CloudWatchアラームと組み合わせれば、認証エラーによるデータ転送失敗を即座に検知できます。Systems Managerのメンテナンスウィンドウと連携して、ローテーション後にデータ転送タスクを自動再実行する仕組みも作れます。

障害対応のランブックには、「認証情報の期限切れによる転送失敗」のシナリオを追加しておくといいでしょう。Secrets Managerのバージョン管理機能を使えば、直前のクレデンシャルに戻すことも可能です。

## 全アップデート一覧

| サービス | アップデート内容 | 概要 |
|----------|------------------|------|
| [Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-bedrock-webrtc/) | AgentCore RuntimeにWebRTCサポート追加 | UDPベースの低レイテンシー双方向ストリーミングで音声AIエージェント構築が容易に |
| [Amazon EKS](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-eks-announces-sla-8xl-scaling-tier/) | Provisioned Control Planeの99.99% SLAと8XLティア | 年間ダウンタイム許容約5分、最大規模のスケーリングティア追加 |
| [AWS Neuron](https://aws.amazon.com/about-aws/whats-new/2026/03/neuron-eks-dra-support/) | EKSでDynamic Resource Allocation対応 | TrainiumリソースをKubernetesネイティブな方法で動的に割り当て |
| [AWS DataSync](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-datasync-secrets-manager/) | 全ロケーションタイプでSecrets Manager対応 | 認証情報をSecrets Managerで安全に管理可能に |
| [AWS Firewall Manager](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-firewall-manager-launches-ap-nz/) | アジアパシフィック（ニュージーランド）リージョン対応 | セキュリティポリシーの統一管理がニュージーランドリージョンで利用可能に |
| [Amazon Redshift](https://aws.amazon.com/about-aws/whats-new/2026/03/redshift-federated-permissions-idc-mrr/) | IAM Identity Center連携マルチリージョン対応 | 複数リージョンのRedshiftクラスターに対して統一されたアクセス管理が可能 |

## まとめ

Bedrock AgentCore RuntimeのWebRTC対応で音声AIエージェントの構築ハードルが下がり、EKSの99.99% SLAで「落ちたら困る」クラスターの選択肢が広がりました。Neuron DRAは、Trainiumを使ったMLワークロードのリソース管理をKubernetesの世界に持ち込んだ形です。DataSyncのSecrets Manager対応は地味ですが、認証情報を平文で渡していた環境には刺さるアップデートです。
