---
title: "【AWS】2026/04/15 のアップデートまとめ"
date: 2026-04-15T08:01:25+09:00
draft: false
tags: ["aws", "secrets-manager", "post-quantum", "ec2", "graviton4", "ebs", "sagemaker", "redshift", "cloudwatch-logs"]
categories: ["AWS Updates"]
summary: "Secrets Manager の post-quantum TLS（ML-KEM）対応、EC2 C8gn/M8gn/R8gn の EBS 帯域 2 倍化、CloudWatch Logs Insights の parameterized saved queries など 7 件のアップデートを紹介します。"
---

![](/images/aws-updates-20260415/header.png)

## はじめに

2026年4月15日のAWSアップデートは7件です。うち5件が本日分（Secrets Manager の post-quantum TLS、AWS Transform の Kiro/VS Code 対応、EC2 C8gn/M8gn/R8gn の EBS 性能向上、SageMaker JumpStart の新モデル追加、Amazon Quick の Google Drive ドキュメントレベル ACL）、2件が前日遅れて通知された分（Redshift Top-K 最適化、CloudWatch Logs Insights の parameterized saved queries）です。目玉は **EBS 帯域 2 倍化** と **parameterized saved queries** の2つ。

## 注目アップデート深掘り

### EC2 C8gn / M8gn / R8gn — 48xlarge / metal-48xl で EBS 帯域 2 倍

![EC2 EBS 性能向上 Before/After](/images/aws-updates-20260415/ebs-perf-compare.png)

AWS Graviton4 プロセッサ搭載の C8gn / M8gn / R8gn のうち、**48xlarge** と **metal-48xl** サイズに限って EBS 最適化性能が 2 倍になりました。公式の数値は次の通りです。

| 指標 | Before | After |
|---|---|---|
| EBS 帯域幅 | 60 Gbps | **120 Gbps** |
| EBS IOPS | 240,000 | **480,000** |

この改善は AWS Nitro System の **6 世代目 Nitro カード**への更新によるもので、追加料金はありません。2026-04-14 以降に新規起動または再起動したインスタンスから自動的に適用されます。

対象インスタンスサイズ:

- **c8gn** (Compute-optimized, network-enhanced): 48xlarge, metal-48xl
- **m8gn** (General-purpose, network-enhanced): 48xlarge, metal-48xl
- **r8gn** (Memory-optimized, network-enhanced): 48xlarge, metal-48xl

> **EC2 の "gn" 系列とは？**
> Graviton (arm64) ベースインスタンスのうち、ネットワークとストレージの両方を強化したバリアントです。同じ世代の無印 (c8g / m8g / r8g) と比べて、EBS 帯域・IOPS・ネットワーク帯域の上限が広がっています。高スループット DB、高速ログ処理、大規模並列 IO を扱うワークロード向けです。

Terraform での利用例（既存の c8gn.48xlarge をそのまま使えば性能向上を受けられます）:

```hcl
resource "aws_instance" "high_io" {
  ami           = data.aws_ami.al2023_arm64.id
  instance_type = "c8gn.48xlarge"

  ebs_block_device {
    device_name = "/dev/sdf"
    volume_type = "gp3"
    volume_size = 1000
    iops        = 16000
    throughput  = 1000
  }

  tags = { Name = "high-io-workload" }
}
```

既に c8gn.48xlarge / m8gn.48xlarge / r8gn.48xlarge を運用しているチームは、**インスタンスを再起動するだけで新しい性能プロファイルに切り替わります**。アプリ側が IO バウンドなら効きが早く出る変更です。逆に CPU バウンドのワークロードでは目立った差は出ません。

### CloudWatch Logs Insights — parameterized saved queries

![CloudWatch Logs Insights Parameterized Query の実行フロー](/images/aws-updates-20260415/logs-insights-params.png)

CloudWatch Logs Insights の保存クエリ（saved queries）に **パラメータ定義** が追加されました。1 つのクエリテンプレートに対してパラメータを最大 **20 個** まで定義でき、呼び出し時に値を差し込んで実行できます。

パラメータの書き方は、クエリを保存したあとに **クエリ名の前に `$` を付けて関数呼び出し風に値を渡す** 形式です。

```
$ErrorsByService(logLevel="ERROR", serviceName="OrderEntry")
```

各パラメータにはオプションでデフォルト値も指定できます。AWS Console、AWS CLI、AWS CDK、AWS SDKs のいずれからも利用可能です（現時点では OpenSearch PPL 等、他のログ分析系との互換性は公式情報なし）。

従来は「障害レベルごと」「サービスごと」に別々のクエリを保存して運用していたところを、1 本のテンプレートに寄せられるようになります。特にオンコールのランブックで、同じクエリ構造を `logLevel` や `timeRange` だけ変えて呼び出すケースに効きます。

> **CloudWatch Logs Insights とは？**
> CloudWatch Logs に対してクエリ言語で検索・集計を実行するサービスです。`fields`、`filter`、`stats`、`sort` などの構文で SQL 風の操作ができ、ダッシュボードやアラームから呼び出せます。今回の parameterized saved queries は、その保存クエリに動的パラメータを注入できるようにした機能拡張です。

## SRE視点での活用ポイント

**EBS 性能向上** は、既に c8gn / m8gn / r8gn の最大サイズで運用しているチームにそのまま効きます。DB のバックアップ時間、ログ集約基盤の同時処理数、リアルタイム分析での I/O レイテンシなどに直結する変更で、特に 48xlarge を選んでいた時点で「EBS 帯域がボトルネック」と認識していた環境では体感差があります。逆に CPU バウンドなワークロードや、48xlarge 未満のサイズを使っている環境では恩恵なしなので、サイズダウンを検討中のチームは判断材料に。

**parameterized saved queries** は、オンコール用のランブック整備に効きます。「エラー調査クエリ」「遅延リクエスト抽出クエリ」などを 1 本のテンプレートに寄せ、パラメータで `logLevel` や `serviceName` を差し替える運用が書きやすくなります。CDK から定義できるので、IaC に載せてチーム全員で共有するのが素直です。

**Secrets Manager の post-quantum TLS** は、**ML-KEM** を使った X25519 とのハイブリッド鍵交換が導入された変更です。Secrets Manager Agent 2.0.0 以上、Lambda Extension v19 以上、Secrets Manager CSI Driver 2.0.0 以上、および対応する AWS SDK（Rust / Go / Node.js / Kotlin / Python (OpenSSL 3.5+) / Java v2 2.35.11+）では、アップグレードするだけで自動的にハイブリッド鍵交換に切り替わります。コード変更は不要（Java v2 のみ一部例外）。CloudTrail では `X25519MLKEM768` として記録されるので、本番で有効化されたかの確認はそこで取れます。

**AWS Transform の Kiro / VS Code 対応** は、レガシーコードのモダナイゼーション支援ツールが AWS Kiro（Amazon 版 IDE エージェント）と VS Code 拡張として使えるようになった変更です。既存の Transform ユーザーで Web UI から降りたかったチーム向けです。

**SageMaker JumpStart の新モデル**（Nemotron-3-Super-120B、Qwen3.5-9B、Qwen3.5-27B）は、エージェント推論と多言語コーディング用途の選択肢追加です。JumpStart から直接デプロイできるので、評価段階のチームは PoC を立てやすくなります。

**Amazon Quick の Google Drive ドキュメントレベル ACL** は、Google Drive をナレッジソースにするときに「ドキュメント単位の権限」を Google Drive 側の実権限と同期して保てるようになった変更です。インデックス済み ACL と、クエリ時の Google Drive への実時間権限確認の二重チェック方式で、権限変更が反映されない問題を避けます。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| [AWS Secrets Manager](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-secrets-manager-post-quantum-tls/) | Hybrid post-quantum TLS 対応 | ML-KEM (X25519MLKEM768) によるハイブリッド鍵交換。Agent/Extension/CSI/SDK アップグレードで自動有効化 |
| [AWS Transform](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-transform-kiro-vscode/) | Kiro および VS Code で利用可能に | レガシーコードのモダナイゼーション支援が IDE 側で動くように |
| [Amazon EC2](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-c8gn-m8gn-r8gn-ebs/) | C8gn/M8gn/R8gn 48xlarge・metal-48xl の EBS 性能 2 倍 | Graviton4 + Nitro 6世代、60→120 Gbps / 240K→480K IOPS、追加料金なし |
| [Amazon SageMaker JumpStart](https://aws.amazon.com/about-aws/whats-new/2026/04/nemotron3super-120b-qwen3.5-9b-qwen3.5-27b-on-sagemaker-jumpstart/) | Nemotron-3-Super-120B / Qwen3.5-9B / Qwen3.5-27B 追加 | エージェント推論・多言語コーディング向けの新基盤モデル 3 種 |
| [Amazon Quick](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-document-level-access-controls-google-drive/) | Google Drive ナレッジベースの document-level ACL | インデックス ACL + 実時間権限チェックで Google Drive 権限と同期 |
| [Amazon Redshift](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-redshift-topk-optimization/) | Top-K クエリ最適化 | `ORDER BY ... LIMIT N` 系クエリの内部実行効率を改善 |
| [Amazon CloudWatch Logs Insights](https://aws.amazon.com/about-aws/whats-new/2026/03/cloudwatch-logs-insights-query-params/) | parameterized saved queries | 保存クエリに最大 20 個のパラメータを定義、`$QueryName(key="value")` で呼び出し |

## まとめ

目玉は EC2 C8gn/M8gn/R8gn の EBS 性能 2 倍化と、CloudWatch Logs Insights の parameterized saved queries の 2 つです。前者は対象サイズを既に使っているチームに即効で効く無料アップグレード、後者はオンコール運用のクエリ整備を一段進められる機能追加です。Secrets Manager の post-quantum TLS は、Agent/SDK の更新だけで自動的にハイブリッド鍵交換に切り替わるので、コンプライアンス要件で量子耐性を要求される組織は次のリリースサイクルで取り込んでおくと良さそうです。
