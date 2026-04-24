---
title: "【AWS】2026/04/25 のアップデートまとめ"
date: 2026-04-25T08:02:13+09:00
draft: true
tags: ["aws", "client-vpn", "transit-gateway", "sagemaker", "hyperpod", "ec2", "connect", "compute-optimizer", "rds", "marketplace", "bedrock", "quick"]
categories: ["AWS Updates"]
summary: "2026/04/25 のAWSアップデートまとめ"
---

# 2024年4月25日 AWS アップデート解説

## はじめに

2024年4月25日、AWSから8件のアップデートが発表されました。本日の注目ポイントは、**AWS Client VPNのTransit Gatewayネイティブ統合**と**Amazon SageMaker HyperPodの自動トポロジ管理機能**です。特にClient VPNアップデートは、リモートアクセスアーキテクチャを根本から簡素化し、セキュリティ監査を強化する重要な機能です。また、SageMaker HyperPodの機能強化は、大規模分散学習環境の運用負荷を大幅に軽減します。その他、Amazon Connectの新メトリクス追加やEC2最新インスタンスの地域拡大など、運用改善と性能向上に貢献するアップデートが揃いました。

## 注目アップデート深掘り

### AWS Client VPN の Transit Gateway ネイティブ統合

#### なぜこのアップデートが重要なのか

従来、AWS Client VPNから複数のVPCやオンプレミスネットワークにアクセスする場合、中間VPCを構築し、そこを経由してTransit Gatewayに接続する必要がありました。このアーキテクチャには以下の課題がありました：

- **運用の複雑性**: 中間VPCの構築・維持管理が必要
- **IPアドレス変換の問題**: SNAT（Source NAT）により、クライアントの実際の送信元IPアドレスが隠蔽される
- **セキュリティ監査の困難性**: どのリモートユーザーがトラフィックを生成したか正確に特定できない

今回のアップデートにより、Client VPNが直接Transit Gatewayに接続可能となり、これらの課題が解決されます。特に重要なのは、**クライアントの送信元IPアドレスがEnd-to-Endで保持される**ようになった点です。これにより、セキュリティグループやネットワークACLでクライアントIPベースの細かいアクセス制御が可能となり、ログ分析やコンプライアンス監査が飛躍的に容易になります。

#### アーキテクチャの変化

**従来のアーキテクチャ**:

```
[Client VPN] → [中間VPC + NAT] → [Transit Gateway] → [各VPC/オンプレミス]
                     ↓
               送信元IP変換（SNAT）
```

**新しいアーキテクチャ**:

```
[Client VPN] → [Transit Gateway] → [各VPC/オンプレミス]
                     ↓
           送信元IP保持（End-to-End）
```

#### 実装手順

Transit Gateway統合を有効化するには、Client VPN エンドポイント作成時に以下のパラメータを指定します。

AWS CLI での作成例：

```bash
$ aws ec2 create-client-vpn-endpoint \
  --client-cidr-block "10.0.0.0/16" \
  --server-certificate-arn "arn:aws:acm:us-east-1:123456789012:certificate/abc123..." \
  --authentication-options Type=certificate-authentication,MutualAuthentication={ClientRootCertificateChainArn=arn:aws:acm:us-east-1:123456789012:certificate/def456...} \
  --connection-log-options Enabled=true,CloudwatchLogGroup=client-vpn-logs \
  --transport-protocol udp \
  --split-tunnel
```

既存のClient VPNエンドポイントにTransit Gatewayアタッチメントを追加：

```bash
$ aws ec2 associate-client-vpn-target-network \
  --client-vpn-endpoint-id cvpn-endpoint-0123456789abcdef0 \
  --subnet-id subnet-0123456789abcdef0 \
  --transit-gateway-id tgw-0123456789abcdef0
```

#### セキュリティグループルールの設定例

送信元IPが保持されるため、クライアントIPベースの認可が可能になります：

```bash
$ aws ec2 authorize-security-group-ingress \
  --group-id sg-0123456789abcdef0 \
  --protocol tcp \
  --port 443 \
  --cidr 10.0.0.100/32 \
  --description "Allow access from specific VPN client"
```

#### Transit Gateway フローログでの検証

送信元IPの保持を確認するため、Transit Gateway フローログを有効化します：

```bash
$ aws ec2 create-flow-logs \
  --resource-type TransitGateway \
  --resource-ids tgw-0123456789abcdef0 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /aws/transitgateway/flowlogs
```

フローログには、クライアントの実際のIPアドレスが記録され、トラフィック追跡が正確に行えます。

> **Note:** この機能は既存のClient VPN・Transit Gateway料金のみで利用でき、追加料金は発生しません。

### Amazon SageMaker HyperPod の自動 Slurm トポロジ管理

#### 分散学習における通信最適化の重要性

大規模な機械学習モデルの学習では、複数のGPUインスタンス間でモデルパラメータや勾配を頻繁に同期する必要があります。この通信パターンは、NCCL（NVIDIA Collective Communications Library）などの集約操作ライブラリによって最適化されますが、その効率はネットワークトポロジに大きく依存します。

従来、SageMaker HyperPodでSlurmクラスタを構築する際、最適なネットワークトポロジを選択・設定するには、GPUインスタンスの相互接続特性を深く理解し、手動でSlurm設定ファイルを編集する必要がありました。クラスタのスケーリングやノード置換時には、再度手動で設定を更新する必要があり、運用負荷が高い状況でした。

#### 自動トポロジ管理の仕組み

今回のアップデートにより、HyperPodは以下を自動的に実行します：

- **GPUインスタンスタイプの検出**: クラスタ内のインスタンスタイプ（ml.p5.48xlarge、ml.p5e.48xlarge、ml.p5en.48xlarge、ml.p6e-gb200.NVL72など）を識別
- **最適なトポロジの選択**: 
  - **ツリートポロジ**: 階層的な相互接続を持つインスタンス向け（多段スイッチ構成）
  - **ブロックトポロジ**: 均一な高帯域幅接続を持つインスタンス向け（フルメッシュに近い構成）
- **動的な設定更新**: スケーリングやノード置換時に自動でトポロジを再計算・適用
- **混合環境への対応**: 複数のインスタンスタイプが混在する場合、互換性のあるトポロジを自動選択

#### 技術的な背景

ツリートポロジとブロックトポロジの違いは、NCCL集約操作のアルゴリズム選択に影響します：

- **ツリートポロジ**: Ring AllReduceやTree AllReduceアルゴリズムを最適化。階層的な通信パターンで帯域幅を効率的に利用
- **ブロックトポロジ**: Double Binary Treeアルゴリズムなど、並列度の高い操作を最適化。低レイテンシ通信が可能

#### 対応インスタンスタイプ

本機能は以下のGPUインスタンスタイプに対応しています：

- **ml.p5.48xlarge**: NVIDIA H100 GPU × 8、EFA対応、インスタンス間3.2Tbps
- **ml.p5e.48xlarge**: H100 GPU × 8、高性能メモリ構成
- **ml.p5en.48xlarge**: H100 GPU × 8、強化されたネットワーク構成
- **ml.p6e-gb200.NVL72**: NVIDIA GB200 Grace Blackwell（最新世代）

#### 実装上の考慮点

デフォルトで有効化されているため、既存のHyperPodクラスタでも追加設定なしに利用できます。ただし、以下の点に注意が必要です：

- クラスタ作成時にインスタンスタイプを慎重に選択（トポロジはインスタンスタイプに基づいて決定される）
- 混合インスタンス環境では、通信性能のボトルネックが発生しないようインスタンスの組み合わせを検討
- 既存の手動Slurm設定がある場合、自動トポロジ管理との競合を確認

> **Note:** この機能は、すべてのSageMaker HyperPod対応AWSリージョンで利用可能です。

## SRE視点での活用ポイント

### Client VPN × Transit Gateway 統合の運用改善

リモートアクセス環境の運用において、この統合は以下のシナリオで大きな価値を発揮します。

**セキュリティインシデント対応の高速化**: 従来、VPNクライアントからの不審なアクセスを調査する際、中間VPCでのSNATによりログ追跡が困難でした。送信元IP保持により、Transit Gateway フローログやVPCフローログから直接クライアントを特定でき、インシデント対応時間を大幅に短縮できます。CloudWatch Logs Insightsと組み合わせれば、特定ユーザーのアクセスパターンをリアルタイムで分析可能です。

**コンプライアンス監査の自動化**: 金融機関や医療機関など、厳格な監査要件がある環境では、「誰が・いつ・どのリソースにアクセスしたか」の完全な記録が必須です。クライアントIP保持により、AWS CloudTrail、VPCフローログ、アプリケーションログを統合した監査証跡を構築できます。Terraformで管理している環境であれば、セキュリティグループルールとログ分析パイプラインを一体で管理し、変更履歴を自動追跡できます。

**マルチテナント環境でのコスト配賦**: クライアントIPベースでトラフィックを正確に分類できるため、部門別・プロジェクト別のネットワーク利用量を測定し、コスト配賦の精度を向上できます。AWS Cost and Usage Reportと組み合わせた分析基盤を構築すれば、リソース利用の可視化が容易になります。

**運用複雑性の削減**: 中間VPCの廃止により、パッチ適用、セキュリティグループ管理、NATゲートウェイの可用性監視といった運用タスクが不要になります。障害対応のランブックもシンプルになり、MTTR（平均復旧時間）の短縮が期待できます。

### SageMaker HyperPod 自動トポロジ管理の運用価値

機械学習基盤の運用では、以下の改善が見込まれます。

**スケーリング時の運用負荷軽減**: 学習ジョブの優先度や緊急性に応じてクラスタを動的にスケールする運用では、ノード追加のたびにSlurm設定を手動更新する負担が大きな課題でした。自動トポロジ管理により、Auto Scalingグループと連携した完全自動化が実現し、オンコール対応の頻度を削減できます。

**ノード障害時の自動復旧**: GPUインスタンスの障害は稀ではなく、ノード置換が発生します。従来は置換後に手動でトポロジ再設定が必要でしたが、自動管理により復旧プロセスが完全に自動化され、学習ジョブの中断時間を最小化できます。CloudWatch アラームと組み合わせてノード異常を検知し、自動置換フローを構築すれば、無人運用に近づけます。

**パフォーマンス最適化の民主化**: ネットワークトポロジの最適化には深い専門知識が必要でしたが、自動管理によりMLエンジニアがインフラの詳細を意識せずに高性能な学習環境を利用できます。これにより、SREチームは運用自動化やコスト最適化などの高付加価値業務に集中できます。

**導入時の判断基準**: 既存のHyperPod環境で手動トポロジ設定を運用している場合、移行前に自動選択されるトポロジが現在の設定と一致するか検証が必要です。特に、カスタマイズしたSlurm設定がある場合、互換性を慎重に確認してください。新規構築であれば、デフォルトで有効化されているため即座に恩恵を受けられます。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon Bedrock AgentCore Gateway and Identity support VPC egress](https://aws.amazon.com/about-aws/whats-new/2024/04/agentcore-gateway-identity-vpc/) | Bedrock AgentCore Gateway と Identity が VPC Egress に対応 |
| 2 | [Amazon Quick now integrates with Visier's Vee agent for workforce intelligence](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-visier-vee/) | Amazon Quick が Visier の AI アシスタント「Vee」と統合。MCP を通じて人員分析データにアクセス可能となり、従業員数、離職率、勤続年数などを自然言語で質問できる。Quick Flows の自動化ワークフローから Vee を呼び出し可能 |
| 3 | [AWS Marketplace Management Portal now supports bank account deletion](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-marketplace-management-portal/) | AWS Marketplace 販売者が Payment Settings ページから銀行口座（ACH/SWIFT）を直接削除可能に。カスタマーサポート連絡が不要となり、複数通貨管理や未使用口座のクリーンアップが効率化 |
| 4 | [Amazon Connect now provides eight new metrics to measure and improve AI agent performance](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-connect-ai-agent-metrics/) | AI エージェントのパフォーマンス測定用に 8 つの新メトリクスが追加。目標達成率、忠実性スコア、ツール選択精度、ハルシネーション検出、カスタマーフィードバックなどを測定可能。GetMetricDataV2 API とゼロ ETL データレイク経由でカスタムレポート作成に対応 |
| 5 | [Amazon EC2 High Memory U7i instances now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ec2-high-memory-u7i/) | 高メモリ U7i インスタンスがヨーロッパ・米国の追加リージョンで利用可能に。u7i-8tb.112xlarge（ストックホルム、チューリッヒ）、u7in-16tb.224xlarge（オハイオ）、u7in-24tb.224xlarge（ストックホルム）を提供。第4世代 Intel Xeon（Sapphire Rapids）搭載、DDR5 メモリ、最大 100 Gbps EBS 帯域幅 |
| 6 | [AWS Client VPN now supports native AWS Transit Gateway integration](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-client-vpn-transit-gateway/) | Client VPN が Transit Gateway にネイティブ統合対応。中間 VPC が不要となり、クライアント送信元 IP が End-to-End で保持される。SNAT による IP 変換が排除され、セキュリティ認可ルールの設定やトラフィック追跡、コンプライアンス監査が大幅に簡素化 |
| 7 | [AWS Compute Optimizer supports 162 new EC2 instance types and 32 new RDS DB instance classes](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-compute-optimizer-ec2-rds/) | Compute Optimizer が最新世代 EC2 インスタンスタイプ 162 種類（C8a、C8gb、C8i、C8i-flex、C8id、M8a、M8azn、M8gb、M8gn、M8id、R8a、R8gb、R8gn、R8id、x8i、i7i）と RDS DB インスタンスクラス 32 種類（M7i、M8g、R8g、X1、Z1d）に対応 |
| 8 | [Amazon SageMaker HyperPod now supports automatic Slurm topology management](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-sagemaker-hyperpod-automatic-slurm-topology/) | HyperPod が Slurm クラスタの最適なネットワークトポロジを自動選択・管理。GPU 間通信を最適化し、分散学習のパフォーマンスを向上。ツリートポロジとブロックトポロジを自動適用し、スケーリングやノード置換時に動的に適応。ml.p5/p5e/p5en/p6e-gb200 など複数の GPU インスタンスに対応 |

## まとめ

本日のアップデートは、**運用効率化**と**パフォーマンス最適化**という2つの軸で大きな進化を遂げています。

Client VPN の Transit Gateway ネイティブ統合は、リモートアクセスアーキテクチャの複雑性を根本から解消し、セキュリティとコンプライアンスの両面で実質的な改善をもたらします。送信元IP保持という一見地味な改善が、監査、インシデント対応、コスト配賦といった広範な運用シーンに波及効果を持つ点が注目です。

SageMaker HyperPod の自動トポロジ管理は、大規模分散学習環境の運用を専門知識不要で高度に最適化する方向性を示しています。機械学習基盤の民主化と運用自動化を同時に推進する重要なステップと言えるでしょう。

その他、Amazon Connect の AI エージェントメトリクス、Compute Optimizer の最新インスタンス対応、EC2 高メモリインスタンスの地域拡大など、既存サービスの着実な機能強化が目立ちます。これらは個別には小さな改善に見えますが、組み合わせることで運用品質の総合的な向上につながります。

AWSは引き続き、運用負荷の軽減と性能向上を両立させる方向でサービスを進化させており、今後のアップデートにも期待が持てます。