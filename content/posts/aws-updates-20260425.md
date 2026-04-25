---
title: "【AWS】2026/04/25 のアップデートまとめ"
date: 2026-04-25T08:02:13+09:00
draft: false
tags: ["aws", "client-vpn", "transit-gateway", "sagemaker", "hyperpod", "ec2", "connect", "compute-optimizer", "rds", "marketplace", "bedrock", "amazonquick"]
categories: ["AWS Updates"]
summary: "2026/04/25 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260425/header.png)

## はじめに

2026年4月25日の AWS アップデートは 8 件。ネットワーク（Client VPN）、ML 基盤（SageMaker HyperPod）、コンタクトセンター（Connect）、最適化（Compute Optimizer）、AI 関連（Bedrock AgentCore / Amazon Quick）など分野はバラついていますが、運用負担を減らす方向の変更が中心の回です。

本記事で深掘りするのは次の 2 つ。

- **AWS Client VPN が AWS Transit Gateway とのネイティブ統合に対応** — 中間 VPC 不要、SNAT 排除、送信元 IP の End-to-End 保持
- **Amazon SageMaker HyperPod が Slurm の自動トポロジ管理に対応** — クラスタのスケーリングや置換に追従して最適トポロジを自動維持

他に Amazon Connect の AI エージェント評価メトリクス 8 種、Compute Optimizer の最新世代 EC2/RDS 対応、EC2 High Memory U7i の追加リージョン、Amazon Quick × Visier Vee 連携、AWS Marketplace の銀行口座削除 UI、Bedrock AgentCore Gateway/Identity の VPC Egress 対応などが含まれます。

## 注目アップデート深掘り

### 1. AWS Client VPN が Transit Gateway とのネイティブ統合に対応

![Client VPN × Transit Gateway 構成の変化](/images/aws-updates-20260425/client-vpn-tgw.png)

> **Transit Gateway とは？**
> 複数の VPC とオンプレミスネットワークを 1 つのハブとして相互接続できる AWS のネットワーキングサービス。各 VPC を個別に VPC ピアリングで結ぶ代わりに、Transit Gateway を中心としたハブ＆スポーク構成を取れます。

#### これまでの構成と課題

これまで Client VPN から複数の VPC やオンプレネットワークに接続する場合、**中間 VPC を作って Transit Gateway へ接続する** 構成が必要でした。公式アナウンスにあるとおり、この構成には次の 2 つの不便さがありました。

- 中間 VPC のリソース（NAT・ルートテーブル・サブネット等）を別途プロビジョニング・運用しなければならない
- Source NAT (SNAT) によりクライアントの送信元 IP が変換されるため、どのリモートユーザーがどのトラフィックを生成したかを特定しづらい（セキュリティ監査で問題になる）

#### v2026-04-25 の変更点

- Client VPN エンドポイントを **直接 Transit Gateway にアタッチ** 可能になった（中間 VPC 不要）
- **エンドユーザーの送信元 IP が End-to-End で保持** されるようになった（SNAT 排除）
- 結果として、**実クライアント IP に基づく authorization rule が書ける** ようになり、トラフィックを特定ユーザーに紐づけて追跡できる
- **Transit Gateway flow logs が、保持された送信元 IP に紐づく接続レベルの詳細を記録** する
- Client VPN が利用可能な全リージョンで提供。**追加料金なし**（Client VPN と Transit Gateway の通常料金のみ）

具体的な API パラメータ・CLI 例・コンソール手順は、公式の Client VPN 製品ページとドキュメントを参照してください。本リリースのアナウンスでは具体的な CLI 形式までは記載されていないので、本記事ではドキュメントにない構文を推測で書きません。

#### SRE が嬉しいポイント

- **インシデント調査時のユーザー特定が容易**: 中間 VPC の SNAT を経由しないため、Transit Gateway flow logs / VPC flow logs から実 IP で追える
- **コンプライアンス監査の証跡が綺麗になる**: 「誰がどこにアクセスしたか」が IP ベースで記録される
- **中間 VPC の運用が消える**: NAT・サブネット・パッチ・SG 管理など、純粋に消化していた運用タスクの削減

---

### 2. Amazon SageMaker HyperPod が Slurm の自動トポロジ管理に対応

![HyperPod 自動トポロジ管理の流れ](/images/aws-updates-20260425/hyperpod-topology.png)

> **SageMaker HyperPod とは？**
> 大規模分散学習向けに最適化された SageMaker のクラスタ機能。GPU インスタンスの集合を Slurm や Kubernetes で管理し、長時間ジョブの耐障害性（自動ノード置換、チェックポイント）や、HPC 風のスケジューリングを提供します。

> **Slurm とは？**
> HPC の世界で広く使われているジョブスケジューラ。`sbatch` でジョブを投げ、ノードを割り当てて並列実行する。SageMaker HyperPod でもクラスタオーケストレータの選択肢として提供されています。

#### 何ができるようになったか

公式アナウンスより、ポイントは以下です。

- HyperPod が **クラスタ内の GPU インスタンスタイプを自動検出** し、最適なネットワークトポロジモデルを選択する
- **Tree topology**: 階層的なインターコネクトを持つインスタンスタイプ向け。対象は `ml.p5.48xlarge` / `ml.p5e.48xlarge` / `ml.p5en.48xlarge`
- **Block topology**: 均一な高帯域幅接続を持つインスタンスタイプ向け。対象は `ml.p6e-gb200.NVL72`
- **インスタンスタイプ混在クラスタでは、両方に互換性のあるトポロジを自動選択**
- **クラスタの scale-up / scale-down / ノード置換イベントに追従** してトポロジ設定を自動更新
- **デフォルトで有効**、追加設定不要
- HyperPod が利用可能な全リージョンで提供

#### 何が嬉しいか

- スケーリングのたびに Slurm 設定ファイルを手動で更新する手間がなくなる
- ノード置換時にトポロジ再設定の作業が消えるので、**長時間学習ジョブの中断時間を短くできる**
- トポロジ最適化のためにインスタンス特性を深く理解しなくても、ML エンジニアがそのまま使える

各インスタンスタイプの具体的な GPU 数・メモリ・帯域などの仕様は、本リリースノートの範囲外なので、SageMaker / EC2 公式ドキュメントを確認してください。

#### 移行時の確認

すでに HyperPod クラスタを運用している場合、自動選択されるトポロジが手動で構成していたものと一致するかを事前に確認すると安全です。カスタム Slurm 設定がある場合の互換性は、自分の構成依存の話なので個別検証が必要です。

---

## SRE視点での活用ポイント

### Client VPN × Transit Gateway 統合の運用効果

中間 VPC の廃止と送信元 IP 保持は、実運用の 3 つのシーンに効いてきます。

**インシデント対応**: VPN クライアントから不審なアクセスがあったときに、実 IP がフローログに記録されているので、ユーザー特定が直接できる。CloudWatch Logs Insights と組み合わせれば、特定ユーザーのアクセス履歴を時系列で追える構成にできます。

**コンプライアンス監査**: 「誰がどのリソースにアクセスしたか」を IP ベースで記録できる。VPC flow logs / Transit Gateway flow logs / アプリ側のアクセスログを実 IP で結合できれば、監査要件への対応が整理しやすくなります。

**運用削減**: 中間 VPC のパッチ・セキュリティグループ・NAT ゲートウェイの可用性監視といった、純粋に消化していた運用タスクが消える。新規構築のチームほど効果が大きい一方、既存環境では中間 VPC を撤去するための切り替え作業が発生するので、実利を見ながら段階的に進めるのが現実的です。

### SageMaker HyperPod 自動トポロジ管理の運用効果

ML 基盤の運用で効くのは次の 2 軸です。

**ノード置換時の復旧時間短縮**: GPU インスタンスの障害・置換は HyperPod のような大規模クラスタでは日常的に起きる事象です。トポロジ再構成が自動化されることで、置換後のジョブ再開までの時間が短くなります。CloudWatch アラームで GPU インスタンス異常を検知 → HyperPod の自動置換 → 自動トポロジ更新、というフローを組めば、夜中のオンコールが減る方向に効きます。

**新規クラスタ構築のハードル低下**: 自動有効なので、Slurm の topology.conf を自分でメンテする必要がない状態で動かせる。ML エンジニアがクラスタ初期構築をやる場面で、トポロジ最適化を専門知識としてキャッチアップしなくてよくなる。

導入判断としては、新規クラスタなら即座に恩恵を受けられる一方、既存クラスタでカスタムの Slurm 設定を持っている場合は、自動選択されるトポロジが現行設定と整合するかを事前に検証してから移行するのが安全です。

---

## 全アップデート一覧

> **Amazon Quick とは？**
> ACL（アクセス制御リスト）対応のナレッジベースを管理できる AWS のサービス。SharePoint や Google Drive 等の外部データソースを横断検索できる。Amazon Q（生成 AI アシスタント）とは別サービス。

> **EFA (Elastic Fabric Adapter) とは？**
> EC2 インスタンスに装着できる、HPC / ML 向けの高速・低レイテンシなネットワークインターフェース。MPI や NCCL を使った大規模ノード間通信で性能を出すために使われる。

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon Bedrock AgentCore Gateway and Identity support VPC egress](https://aws.amazon.com/about-aws/whats-new/2024/04/agentcore-gateway-identity-vpc/) | Bedrock AgentCore Gateway と Identity が VPC Egress に対応 |
| 2 | [Amazon Quick now integrates with Visier's Vee agent for workforce intelligence](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-visier-vee/) | Amazon Quick が Visier の AI アシスタント Vee と統合。MCP 経由で人員分析データに自然言語アクセス、Quick Flows から Vee 呼び出しが可能 |
| 3 | [AWS Marketplace Management Portal now supports bank account deletion](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-marketplace-management-portal/) | Marketplace 販売者が Payment Settings で銀行口座 (ACH/SWIFT) を直接削除可能に。サポート連絡が不要 |
| 4 | [Amazon Connect now provides eight new metrics to measure and improve AI agent performance](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-connect-ai-agent-metrics/) | AI エージェント性能評価用に 8 つの新メトリクス（goal success rate / faithfulness score / tool selection accuracy / hallucination 検知 / カスタマーフィードバック等）。GetMetricDataV2 API と zero-ETL データレイク経由で取得可能 |
| 5 | [Amazon EC2 High Memory U7i instances now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ec2-high-memory-u7i/) | High Memory U7i インスタンスの追加リージョン提供（Stockholm、Zurich、Ohio 等） |
| 6 | [AWS Client VPN now supports native AWS Transit Gateway integration](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-client-vpn-transit-gateway/) | Client VPN が Transit Gateway にネイティブ統合。中間 VPC 不要、送信元 IP の End-to-End 保持、追加料金なし |
| 7 | [AWS Compute Optimizer supports 162 new EC2 instance types and 32 new RDS DB instance classes](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-compute-optimizer-ec2-rds/) | 最新世代 EC2 162 種（C8a/C8gb/C8i/C8i-flex/C8id/M8a/M8azn/M8gb/M8gn/M8id/R8a/R8gb/R8gn/R8id/x8i/i7i）と RDS 32 クラス（M7i/M8g/R8g/X1/Z1d）に対応 |
| 8 | [Amazon SageMaker HyperPod now supports automatic Slurm topology management](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-sagemaker-hyperpod-automatic-slurm-topology/) | HyperPod が GPU インスタンスタイプに応じて Tree topology / Block topology を自動選択。スケールやノード置換にも追従。ml.p5/p5e/p5en/p6e-gb200 対応 |

## まとめ

ネットワーク（Client VPN × Transit Gateway）と ML 基盤（HyperPod 自動トポロジ）の 2 つは、どちらも「これまで自前で組み立てていた配管が、AWS 側のマネージド側に移った」タイプの変更です。中間 VPC や Slurm topology.conf の手動管理は、本来の業務価値とは関係ない設定維持のコストだったので、この種の変更は実運用に効きます。

Amazon Connect の AI エージェント評価メトリクス、Compute Optimizer の最新世代対応、EC2 U7i の追加リージョン、Amazon Quick × Visier Vee 連携、AWS Marketplace の UI 改善、Bedrock AgentCore の VPC Egress 対応はそれぞれ用途特化の変更で、該当機能を使っているチームには直接的に効きます。

SRE の動き出しとしては、Client VPN を運用しているチームは中間 VPC の撤去計画を引きやすくなった点、SageMaker HyperPod を使っているチームはノード置換時の復旧時間短縮を CloudWatch メトリクスで追っておく価値がある点、あたりが現実的な入り口です。
