---
title: "【AWS】2026/06/06 のアップデートまとめ"
date: 2026-06-06T08:02:06+09:00
draft: false
tags: ["aws", "ecs", "fargate", "eks", "sagemaker", "s3", "glue", "athena", "emr", "redshift", "cloudwatch", "lambda", "kubernetes", "ack", "argocd", "deadline-cloud"]
categories: ["AWS Updates"]
summary: "2026/06/06 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260606/header.png)

# 2026年6月6日 AWS アップデート解説

## はじめに

2026年6月6日、AWSから6件のアップデートが発表されました。本日の注目ポイントは、**ECS Fargateの大幅な計算能力拡張**と**EKS Capabilitiesの運用可視化強化**です。Fargateが32vCPUまで対応したことで、機械学習推論や大規模データ処理といった高負荷ワークロードがサーバーレスで実行可能になりました。一方、EKS Capabilitiesのログ配信機能により、Argo CDやACKなどマネージドコントローラーの動作が透過的に監視できるようになり、Kubernetes運用の信頼性が向上します。

その他にも、SageMaker Data Agentによるビジネス用語でのデータ発見、AWS MCPサーバーのクロスアカウント対応、Deadline Cloudのプラグイン自動同期など、開発者・運用者双方の生産性を高めるアップデートが揃いました。

## 注目アップデート深掘り

### Amazon ECS with AWS Fargate 32vCPU対応：サーバーレスの新境地

#### なぜこのアップデートが重要なのか

これまでFargateの最大構成は16vCPUでしたが、今回の32vCPU対応により**EC2インスタンスへの移行を検討していた高負荷ワークロードがサーバーレスで継続できる**ようになりました。機械学習モデルの推論API、リアルタイム動画処理、大規模なバッチ分析など、従来はEC2やEKS on EC2でしか実現できなかったユースケースが、インフラ管理不要のFargateで実行可能です。

32vCPUタスクには**60GiB、120GiB、244GiB**の3つのメモリオプションが用意され、x86とARM（Graviton）の両アーキテクチャをサポートしています。既存のCompute Savings Plansが自動適用されるため、コスト最適化も容易です。

#### タスク定義の実装例

AWS CLIでの32vCPUタスク定義の登録例を示します。

```bash
$ aws ecs register-task-definition \
  --family high-performance-task \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 32768 \
  --memory 122880 \
  --container-definitions '[
    {
      "name": "ml-inference-container",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-model:latest",
      "cpu": 32768,
      "memory": 122880,
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/high-performance-task",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]'
```

Terraformでの実装例：

```hcl
resource "aws_ecs_task_definition" "high_performance" {
  family                   = "high-performance-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "32768"  # 32 vCPU
  memory                   = "122880" # 120 GiB

  container_definitions = jsonencode([
    {
      name      = "ml-inference-container"
      image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/ml-model:latest"
      cpu       = 32768
      memory    = 122880
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/high-performance-task"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}
```

#### CPU・メモリ構成の選択肢

32vCPUタスクで利用可能なメモリ構成は以下の通りです：

| vCPU | メモリオプション |
|------|-----------------|
| 32   | 60GiB          |
| 32   | 120GiB         |
| 32   | 244GiB         |

メモリ集約型ワークロード（インメモリ分析、キャッシュサーバー）では244GiB構成、CPU集約型（動画エンコーディング、暗号処理）では60GiB構成を選択することで、コストを最適化できます。

#### 従来構成との比較

16vCPU × 2タスク構成と32vCPU × 1タスク構成を比較すると、以下の違いがあります：

**16vCPU × 2タスクの場合**
- タスク間通信のオーバーヘッドが発生
- ロードバランサーでのセッション管理が必要
- 各タスクにメモリを分散配置

**32vCPU × 1タスクの場合**
- 単一プロセス内で全リソースを活用
- 共有メモリによる効率的なデータアクセス
- シンプルなアーキテクチャで運用負荷低減

特に機械学習推論のように、大きなモデルをメモリにロードして複数リクエストを並行処理するケースでは、32vCPU単一タスクの方が効率的です。

### Amazon EKS Capabilities の CloudWatch Vended Logs 対応：マネージドコントローラーの可視化

#### 背景と課題

EKS Capabilitiesは、Argo CD（GitOps継続的デリバリー）、ACK（AWS Controllers for Kubernetes）、kro（リソースオーケストレーション）といった**AWS管理のKubernetesコントローラー**を提供する機能です。これらはユーザーのクラスター内ではなく、AWS管理のインフラ上で動作するため、従来は`kubectl logs`でログを取得できませんでした。

このため、Argo CDでのデプロイメント失敗やACKでのAWSリソース作成エラーが発生しても、**原因調査に必要なログが手元になく、トラブルシューティングが困難**でした。今回のCloudWatch Vended Logs対応により、この課題が解決されます。

#### ログ配信の有効化と分析

公式アナウンスによると、各 capability のログは **CloudWatch API または AWS マネジメントコンソールから「CloudWatch Vended Logs の配信ソース（delivery source）」として有効化**します。配信先は CloudWatch Logs・Amazon S3・Amazon Kinesis Data Firehose の3つから選択でき、EKS 側の追加料金は発生せず、配信先に応じた標準の CloudWatch Vended Logs 料金が適用されます。

CloudWatch Logs に配信したログは CloudWatch Logs Insights でクエリ・集計でき、Argo CD の sync 失敗や ACK のリソース作成エラーを時系列で調査できます。具体的な設定手順・ログのスキーマ・ロググループ名は[Amazon EKS の公式ドキュメント](https://docs.aws.amazon.com/eks/)を参照してください（公式アナウンスは `aws eks update-addon` 等の具体的なコマンド体系やロググループ名は明示していません）。

#### 配信先別の活用シナリオ

| 配信先 | 主な用途 | メリット |
|--------|----------|----------|
| CloudWatch Logs | リアルタイム監視、Insights分析 | アラート設定、ダッシュボード統合 |
| Amazon S3 | 長期保存、コンプライアンス対応 | 低コスト、Athenaでのクエリ可能 |
| Kinesis Data Firehose | 外部SIEM連携、カスタム処理 | Splunk/Datadog等への統合 |

> **Note:** CloudWatch Logsへの配信は即座に開始されますが、S3への配信はバッファリングにより数分の遅延が発生します。リアルタイム監視にはCloudWatch Logsを、監査ログ保管にはS3を併用する構成が推奨されます。

## SRE視点での活用ポイント

### Fargate 32vCPU：スケーリング戦略の再設計

32vCPUという大容量タスクが利用可能になったことで、**水平スケーリングと垂直スケーリングのトレードオフ**を再検討する価値があります。従来は「小さいタスクを多数起動」が基本戦略でしたが、機械学習推論のようにモデルロード時間が支配的なワークロードでは、「大容量タスクで並行処理数を増やす」方がコールドスタートを削減できます。

Auto Scalingポリシーでは、CPU使用率だけでなく**リクエストキューの深さやレイテンシ**をメトリクスに含めることで、より適切なスケールアウトタイミングを設定できます。Savings Plansを活用している環境では、32vCPUタスクの予約容量を計画的に購入することで、突発的な負荷にも対応しつつコストを抑制できます。

Fargate Spotとの組み合わせも有効です。32vCPU 構成は標準 Fargate と Fargate Spot の両方で利用できるため、バッチ処理やCI/CDパイプラインのように中断耐性のあるワークロードでは、32vCPU を Fargate Spot で実行することでコストを抑制できます。

### EKS Capabilities ログ：障害対応ランブックへの組み込み

EKS Capabilitiesのログが取得可能になったことで、**GitOpsやIaCによる自動化の障害対応が大幅に効率化**されます。例えば、Argo CDのsync失敗時に以下のような対応フローをランブックに組み込めます：

1. CloudWatch アラームでsync失敗を検知
2. Lambda関数がCloudWatch Logsから該当時刻のログを抽出
3. エラーメッセージをSlackに通知（Kubernetesマニフェストの構文エラー、権限不足などを特定）
4. 必要に応じてロールバック実行

ACKコントローラーのログ監視では、AWSリソースの作成失敗パターン（IAMポリシー不足、リソース制限超過）を事前に収集し、**自動修復スクリプト**を準備しておくことで、手動介入を最小化できます。

S3への長期保存を有効化している場合、Athenaで過去のデプロイメント失敗傾向を分析し、問題の多いマニフェストや時間帯を特定することで、予防的な改善が可能になります。

### データ発見とクロスアカウント運用の統合

SageMaker Data AgentとAWS MCP Serverの2つのアップデートは、**データ分析基盤の運用効率化**という共通テーマを持ちます。複数アカウントに分散したデータレイクをMCPサーバーで横断的に管理しつつ、Data Agentでビジネスユーザーが直接データ発見できる環境を構築すれば、データエンジニアへの問い合わせを削減できます。

Terraformでクロスアカウントアクセスを管理している場合、AWS MCPサーバーの認証情報をAWS Secrets Managerに集約し、IAMロールのAssumeRoleチェーンを適切に設計することで、セキュリティと利便性を両立できます。最小権限の原則に基づき、各プロファイルに必要な権限のみを付与し、CloudTrailで操作ログを記録する運用が推奨されます。

## 全アップデート一覧

| # | タイトル | 概要 | リンク |
|---|---------|------|--------|
| 1 | **S3 Tables と Iceberg のシンプルな権限管理が GovCloud で利用可能に** | AWS Glue Data Catalog が S3 Tables と Iceberg マテリアライズドビューに対して IAM ベースの認可機能をサポート。単一IAMポリシーで複数の分析サービス（Athena、EMR、Redshift等）の権限を一元管理可能に。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/gdc-s3tables-simplified-permissions-in-aws-govcloud/) |
| 2 | **Amazon ECS with Fargate が 32vCPU 構成に対応** | Fargate で最大 32vCPU（メモリ 60/120/244GiB）が利用可能に。機械学習推論、大規模データ処理、HPC ワークロードなど高負荷ユースケースをサーバーレスで実行可能。x86 と ARM（Graviton）の両方をサポート。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ecs-fargate-32vcpu) |
| 3 | **AWS MCP Server がクロスアカウント・クロスロールアクセスに対応** | Claude Code や Kiro などの AI コーディングエージェントが、セッション再起動なしに複数の AWS アカウントと IAM ロールを同時利用可能に。コマンドごとにプロファイル指定でシームレスに切り替え。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-mcp-server/) |
| 4 | **AWS Deadline Cloud がサービス管理型フリートでプラグイン自動同期をサポート** | Blender、Maya 等の DCC アプリケーションプラグインを S3 にアップロードするだけで、ジョブ開始時にワーカーへ自動配信。カスタムスクリプト不要でプラグイン管理が簡素化。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/deadline-cloud/plugin-sync) |
| 5 | **Amazon SageMaker Data Agent がビジネスコンテキストと統合** | SageMaker Catalog のビジネス用語、用語集、メタデータを活用し、技術的なテーブル名ではなくビジネス言語でデータ発見と SQL/Python コード生成が可能に。Collibra、Atlan、Alation 等のカタログをサポート。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-sagemaker-data-agent-bdc/) |
| 6 | **Amazon EKS Capabilities が CloudWatch Vended Logs に対応** | Argo CD、ACK、kro などマネージドコントローラーのログを CloudWatch Logs、S3、Kinesis Data Firehose に配信可能に。マネージド環境の監視とトラブルシューティングが容易に。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-eks-capabilities-logging) |

## まとめ

本日のアップデートは、**コンピュート能力の拡張**（Fargate 32vCPU）、**運用可視性の向上**（EKS Capabilitiesログ）、**開発者体験の改善**（MCPサーバー、Data Agent、Deadline Cloud）という3つの軸で進化が見られました。

特にFargateの32vCPU対応は、サーバーレスコンテナの適用範囲を大きく広げるものであり、これまでEC2への移行を検討していた高負荷ワークロードが再検討に値します。EKS Capabilitiesのログ配信は、Kubernetes運用のブラックボックス部分を解消し、GitOpsによる自動化の信頼性を高めます。

また、AI支援開発ツールの進化（MCPサーバー、Data Agent）は、マルチアカウント運用やデータ分析の生産性を大幅に向上させる可能性を示しています。各組織の環境に応じて、これらの新機能を段階的に検証・導入することで、運用効率とコスト最適化の両立が期待できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)