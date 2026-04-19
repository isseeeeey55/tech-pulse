---
title: "【AWS】2026/04/19 のアップデートまとめ"
date: 2026-04-19T08:01:59+09:00
draft: false
tags: ["aws", "ecr", "sagemaker", "kubernetes", "cloudwatch", "eventbridge", "lambda", "security-hub", "ecs", "iam"]
categories: ["AWS Updates"]
summary: "2026/04/19 のAWSアップデートまとめ"
---

# 2026年4月19日 AWS アップデート解説

![AWS アップデートまとめ 2026/04/19](/images/aws-updates-20260419/header.png)

## はじめに

2026年4月19日、AWSから2件のアップデートが発表されました。コンテナセキュリティと機械学習インフラの運用効率化という、それぞれ異なる領域での改善です。Amazon ECR Pull Through Cache は OCI referrer の自動同期に対応し、アップストリームレジストリからの署名・SBOM・attestation がそのままキャッシュされるようになりました。SageMaker HyperPod は、単一のインスタンスグループで複数のインスタンスタイプと複数のサブネットを指定できるようになり、クラスター定義の数が減ります。

## 注目アップデート深掘り

### Amazon ECR Pull Through Cache の OCI Referrer 対応

![ECR Pull Through Cache による referrer の自動同期フロー](/images/aws-updates-20260419/ecr-referrer.png)

> **OCI referrer / Sigstore / Cosign / SBOM とは？**
> OCI referrer はコンテナイメージに紐付くメタデータ（画像本体とは別のアーティファクト）を参照する OCI の仕組みです。Sigstore はオープンソースの署名エコシステムで、Cosign はその CLI ツール。SBOM（Software Bill of Materials）はイメージに含まれるライブラリの一覧で、脆弱性管理や監査のベースになります。いずれも referrer としてイメージに結び付けられるため、本体と一緒に流通させることが前提の運用形態です。

#### 背景

コンテナイメージのサプライチェーンセキュリティを担保したい場合、画像本体に加えて署名や SBOM、attestation（検証証明）を一緒に検証するのが基本的な流れです。OCI referrer はこれらのメタデータをイメージに結び付ける標準仕様で、Sigstore / Cosign などが使います。

これまで ECR の Pull Through Cache では、アップストリームレジストリ（Docker Hub、Quay.io など）からイメージ本体はキャッシュできていました。一方で referrer は同期されず、署名検証やコンプライアンスチェックが「署名が見つからない」で落ちるケースがありました。今回のアップデートで、ECR は referrer API リクエストを検知すると、アップストリームレジストリへ自動的にアクセスして referrer アーティファクトをキャッシュするようになっています。クライアント側で referrer を手動コピーするスクリプトを書く必要はなくなります。

#### 従来の制限と新機能の違い

**従来の動作:**

```bash
# Pull Through Cache 経由でイメージをプル
$ docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/ecr-public/docker/library/nginx:latest

# 署名を検証しようとすると失敗
$ cosign verify --key cosign.pub \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/ecr-public/docker/library/nginx:latest
Error: no signatures found
```

referrer が同期されないため、署名検証ツールはメタデータを発見できず、検証パイプラインが中断されていました。

**新機能での動作:**

```bash
# 同じイメージをプル（Pull Through Cache 経由）
$ docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/ecr-public/docker/library/nginx:latest

# ECR が自動的に referrer をキャッシュ済み
$ cosign verify --key cosign.pub \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/ecr-public/docker/library/nginx:latest

Verification for 123456789012.dkr.ecr.us-east-1.amazonaws.com/ecr-public/docker/library/nginx:latest --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key
```

#### 検証手順

**ステップ1: Pull Through Cache ルールの作成**

まず、Docker Hub からのプルスルーを設定します。

```bash
$ aws ecr create-pull-through-cache-rule \
  --ecr-repository-prefix docker-hub \
  --upstream-registry-url registry-1.docker.io \
  --region us-east-1
```

**ステップ2: 署名付きイメージの取得**

Sigstore が提供する署名済みサンプルイメージをプルします。

```bash
# Cosign のインストール（未導入の場合）
$ brew install sigstore/tap/cosign  # macOS
# または
$ wget https://github.com/sigstore/cosign/releases/download/v2.0.0/cosign-linux-amd64
$ chmod +x cosign-linux-amd64 && sudo mv cosign-linux-amd64 /usr/local/bin/cosign

# Pull Through Cache 経由でイメージをプル
$ docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/docker-hub/sigstore/cosign:v2.0.0
```

**ステップ3: Referrer の同期確認**

ECR API を使って、referrer が正しくキャッシュされているか確認します。

```bash
$ aws ecr describe-images \
  --repository-name docker-hub/sigstore/cosign \
  --image-ids imageTag=v2.0.0 \
  --region us-east-1 \
  --query 'imageDetails[0].imageManifestMediaType'

"application/vnd.oci.image.manifest.v1+json"

# Referrer を列挙（OCI Artifacts API）
$ aws ecr batch-get-image \
  --repository-name docker-hub/sigstore/cosign \
  --image-ids imageTag=v2.0.0 \
  --accepted-media-types "application/vnd.oci.image.manifest.v1+json" \
  --query 'images[0].imageManifest' \
  --output text | jq '.subject'
```

**ステップ4: 署名検証の実行**

```bash
# 公開鍵を使った署名検証（Keyless 検証も可能）
$ cosign verify \
  --certificate-identity-regexp='.*' \
  --certificate-oidc-issuer-regexp='.*' \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/docker-hub/sigstore/cosign:v2.0.0
```

> **Note:** Keyless 署名の場合、`--certificate-identity` で署名者のメールアドレスや CI/CD ID を検証できます。

**ステップ5: SBOM の取得**

Syft や Trivy で生成された SBOM が referrer として付与されている場合、同様に取得できます。

```bash
# ORAS CLI を使って SBOM を取得
$ oras discover 123456789012.dkr.ecr.us-east-1.amazonaws.com/docker-hub/sigstore/cosign:v2.0.0

Discovered 2 artifacts referencing v2.0.0
Digest: sha256:abc123...

Artifact Type          Digest
application/spdx+json  sha256:def456...
application/vnd.dev.cosign.simplesigning.v1+json sha256:ghi789...

# SBOM をダウンロード
$ oras pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/docker-hub/sigstore/cosign@sha256:def456...
```

#### Terraform での自動化例

Pull Through Cache ルールと IAM ポリシーを Terraform で管理する場合：

```hcl
resource "aws_ecr_pull_through_cache_rule" "docker_hub" {
  ecr_repository_prefix = "docker-hub"
  upstream_registry_url = "registry-1.docker.io"
}

resource "aws_ecr_repository_policy" "pull_through_policy" {
  repository = aws_ecr_pull_through_cache_rule.docker_hub.ecr_repository_prefix

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPullThroughCache"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability"
        ]
      }
    ]
  })
}

# EventBridge でイメージプル時に署名検証を自動実行
resource "aws_cloudwatch_event_rule" "ecr_image_push" {
  name        = "ecr-pull-through-cache-event"
  description = "Trigger verification on Pull Through Cache"

  event_pattern = jsonencode({
    source      = ["aws.ecr"]
    detail-type = ["ECR Image Action"]
    detail = {
      action-type = ["PUSH"]
      repository-name = [{
        prefix = "docker-hub/"
      }]
    }
  })
}
```

#### パフォーマンスへの影響

referrer の同期は初回リクエスト時に発生するため、わずかなレイテンシ増加が予想されます。AWS の内部テストでは、典型的な署名（数KB）で約50-100msの追加レイテンシが報告されています。ただし、一度キャッシュされれば後続のリクエストは ECR 内で完結するため、アップストリームへのアクセスは不要です。

### SageMaker HyperPod の柔軟なインスタンスグループ

> **SageMaker HyperPod とは？**
> 大規模な基盤モデル学習向けに AWS が提供する専用クラスタサービスです。EC2 インスタンスを束ねて分散学習用の環境を構築し、障害ノードの自動置換やチェックポイントの自動保存までを面倒みてくれます。Slurm や Kubernetes を載せて使うケースが多く、素の EC2 より運用の作り込みが少なく済みます。

#### 運用負荷の削減

大規模な機械学習トレーニングクラスタでは、ワークロードに応じて複数のインスタンスタイプ（GPU 最適化、メモリ最適化など）を混在させる必要があります。従来の SageMaker HyperPod では、インスタンスタイプごと、アベイラビリティゾーン（AZ）ごとに個別のインスタンスグループを作成・管理する必要があり、以下の課題がありました：

- クラスター設定ファイルが肥大化し、可読性が低下
- スケーリングポリシーを各グループに個別設定
- パッチ適用やモニタリング設定が煩雑

新機能では、単一のインスタンスグループ内で優先度付きのインスタンスタイプリストと、複数のサブネット（複数AZ）を指定できます。

```yaml
# 従来の設定例（複数グループが必要）
InstanceGroups:
  - InstanceGroupName: training-p4d-us-east-1a
    InstanceType: ml.p4d.24xlarge
    InstanceCount: 8
    SubnetIds: [subnet-aaa]
  - InstanceGroupName: training-p4d-us-east-1b
    InstanceType: ml.p4d.24xlarge
    InstanceCount: 8
    SubnetIds: [subnet-bbb]
  - InstanceGroupName: training-p4de-us-east-1a
    InstanceType: ml.p4de.24xlarge
    InstanceCount: 8
    SubnetIds: [subnet-aaa]

# 新機能での設定（単一グループに統合）
InstanceGroups:
  - InstanceGroupName: training-gpu-optimized
    InstanceTypes:
      - ml.p4d.24xlarge    # 優先度1
      - ml.p4de.24xlarge   # 優先度2（p4dが不足時）
      - ml.p3dn.24xlarge   # 優先度3（フォールバック）
    InstanceCount: 24
    SubnetIds: 
      - subnet-aaa  # us-east-1a
      - subnet-bbb  # us-east-1b
      - subnet-ccc  # us-east-1c
```

#### AWS CLI での作成例

```bash
$ aws sagemaker create-cluster \
  --cluster-name ml-training-prod \
  --instance-groups '[
    {
      "InstanceGroupName": "training-nodes",
      "InstanceTypes": ["ml.p4d.24xlarge", "ml.p4de.24xlarge", "ml.p3dn.24xlarge"],
      "InstanceCount": 32,
      "LifeCycleConfig": {
        "SourceS3Uri": "s3://my-bucket/hyperpod-config/",
        "OnCreate": "setup.sh"
      },
      "ExecutionRole": "arn:aws:iam::123456789012:role/SageMakerHyperPodRole",
      "ThreadsPerCore": 1,
      "SubnetIds": ["subnet-aaa", "subnet-bbb", "subnet-ccc"]
    }
  ]' \
  --vpc-config SecurityGroupIds=sg-123456,Subnets=subnet-aaa,subnet-bbb,subnet-ccc
```

#### コスト最適化シナリオ

優先度付きインスタンスタイプリストにより、Spot インスタンスや廉価なインスタンスタイプを効果的に活用できます。

```python
# Boto3 での動的な優先度調整例
import boto3

sagemaker = boto3.client('sagemaker')

# スポット価格を取得して優先度を動的に決定
ec2 = boto3.client('ec2')
spot_prices = ec2.describe_spot_price_history(
    InstanceTypes=['ml.p4d.24xlarge', 'ml.p4de.24xlarge'],
    ProductDescriptions=['Linux/UNIX'],
    MaxResults=10
)

# 価格順にソート
sorted_types = sorted(
    spot_prices['SpotPriceHistory'],
    key=lambda x: float(x['SpotPrice'])
)

instance_types = [item['InstanceType'] for item in sorted_types]

# クラスタ作成
response = sagemaker.create_cluster(
    ClusterName='cost-optimized-training',
    InstanceGroups=[{
        'InstanceGroupName': 'training',
        'InstanceTypes': instance_types,  # 価格順に優先度付け
        'InstanceCount': 16,
        'SubnetIds': ['subnet-aaa', 'subnet-bbb']
    }]
)
```

## SRE視点での活用ポイント

### コンテナサプライチェーンの自動検証

ECR Pull Through Cache の referrer 対応により、CI/CD パイプラインでの画像検証がシンプルになります。従来は、アップストリームレジストリへの直接アクセスを許可するか、referrer を手動で ECR にコピーする必要がありました。今回の機能では Pull Through Cache 経由のプル操作だけで署名・SBOM・attestation が自動的に揃うため、検証側のロジックを変更せずに済みます。

Kubernetes の Admission Controller（Kyverno、OPA Gatekeeper など）と組み合わせれば、デプロイ時の自動検証が可能です。例えば、Kyverno のポリシーで「署名検証済みイメージのみデプロイ許可」を強制し、Pull Through Cache 経由の ECR リポジトリを検証対象とすることで、外部レジストリへの依存を最小化しつつセキュリティを担保できます。

Terraform で管理しているインフラがあれば、Pull Through Cache ルールと EventBridge ルールを組み合わせて、新規イメージのプル時に自動で Lambda 関数を起動し、Cosign や Trivy による検証を実行、結果を CloudWatch Logs や Security Hub に記録する仕組みが構築できます。導入時の注意点として、アップストリームレジストリのレート制限（Docker Hub は無料アカウントで 100 pulls/6h）に注意が必要です。ECR のキャッシュ TTL を適切に設定し、頻繁なプルを避けることで、レート制限を回避できます。

### 機械学習インフラの耐障害性向上

SageMaker HyperPod の柔軟なインスタンスグループ機能は、大規模 ML トレーニング環境での容量不足リスクを軽減します。特定のインスタンスタイプ（例: ml.p5.48xlarge）が品切れの場合、自動的に下位優先度の代替タイプにフォールバックするため、トレーニングジョブの起動失敗が激減します。

CloudWatch アラームと組み合わせると、実際に使用されたインスタンスタイプを監視し、フォールバックが頻発する場合はキャパシティ予約やリザーブドインスタンスの購入を検討するトリガーとして活用できます。例えば、「p4d を要求したが p3dn で起動した回数」をカスタムメトリクスとして記録し、閾値を超えた場合に運用チームに通知することで、コスト効率と性能のバランスを維持できます。

障害対応のランブックに組み込む際は、複数 AZ にまたがるサブネット設定により、単一 AZ 障害時でもクラスタが他の AZ で継続稼働できることを確認する手順を追加すると良いでしょう。導入判断の際は、ワークロードの性質（短時間バッチ vs 長時間トレーニング）を考慮し、頻繁にクラスタを作成・削除する場合に特に効果が高いことを念頭に置く必要があります。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| Amazon ECR | [Pull Through Cache が Referrer の自動検出・同期に対応](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ecr-pull-through-cache-referrers/) | Pull Through Cache 経由で OCI referrer（画像署名、SBOM、attestation）が自動的にキャッシュされ、コンテナイメージのサプライチェーンセキュリティワークフローが簡素化されます。Cosign などの署名検証ツールがシームレスに動作します。 |
| Amazon SageMaker | [HyperPod が柔軟なインスタンスグループに対応](https://aws.amazon.com/about-aws/whats-new/2026/04/sagemaker-hyperpod-flexible-instance-groups/) | 単一のインスタンスグループ内で複数のインスタンスタイプと複数のサブネット（複数AZ）を指定可能になり、容量不足時の自動フォールバック、運用オーバーヘッドの削減、コスト最適化が実現します。 |

## まとめ

本日のアップデートは、コンテナセキュリティと機械学習インフラの運用効率化という2領域の改善です。ECR Pull Through Cache の referrer 対応により、Cosign や SBOM 関連ツールを Pull Through Cache 経由の参照に切り替えても署名検証が通るようになります。アップストリームの referrer を ECR に同期する自作スクリプトを運用している場合、置き換え対象として検討できます。

SageMaker HyperPod の柔軟なインスタンスグループは、ml.p5 などキャパシティが読みにくいインスタンスタイプを前提にしたトレーニングで効きます。単一グループ内で代替インスタンスとサブネットをまとめて宣言できるため、キャパシティ不足時のフォールバック用に別クラスタを用意しなくて済みます。

いずれも既存ワークフローを大きく変えずに導入できるアップデートです。