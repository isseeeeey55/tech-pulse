---
title: "【AWS】2026/06/13 のアップデートまとめ"
date: 2026-06-13T08:02:02+09:00
draft: false
tags: ["aws", "sagemaker", "eks", "ec2", "outposts", "quick", "snowflake"]
categories: ["AWS Updates"]
summary: "2026/06/13 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260613/header.png)

# 直近の AWS アップデート情報 — SageMaker AI、EKS Outposts ほか

## はじめに

今回は、直近で発表された6件のAWSアップデートを紹介します。Amazon SageMaker AI による大規模言語モデルのサーバーレス微調整対応、Amazon EKS が AWS Outposts 上で EC2 インスタンスストアからの完全ローカル実行に対応など、機械学習とコンテナ運用の各領域で注目すべき機能拡張が行われています。また、EC2 高メモリインスタンスやストレージ最適化インスタンスのリージョン拡大、AWS GovCloud での機械学習向け容量予約機能の提供開始など、エンタープライズや規制対応環境でのワークロード実行オプションも充実してきています。本記事では、これらのアップデートの中から特に運用改善やコスト最適化に寄与する内容を深掘りし、SRE 視点での活用ポイントを整理します。

## 注目アップデート深掘り

### Amazon EKS が AWS Outposts 上で完全ローカル実行に対応

AWS は、Amazon EKS のローカルクラスター機能を AWS Outposts 環境に拡張し、**Amazon EC2 インスタンスストア** から起動する第1世代および第2世代の Outposts ラックに対応しました。これにより、Kubernetes コントロールプレーン全体が Outposts 上で動作し、AWS リージョンとのネットワーク接続に依存しない運用が可能になります。

#### データレジデンシーとネットワーク分離の要求に応える

従来の EKS on Outposts では、コントロールプレーンの一部が AWS リージョン側で実行されていたため、クラウドとの接続が一時的に途切れた場合、クラスタ操作に影響が出る可能性がありました。新しいアーキテクチャでは、etcd を含むコントロールプレーン全体が Outposts 上で稼働するため、**ネットワーク切断のリスクが軽減** されます。

金融機関や医療機関など、規制上の理由からデータをオンプレミスに保持する必要がある業界では、この完全ローカル実行が重要な要件となります。Kubernetes ワークロードを AWS のマネージドサービスとして運用しながら、データレジデンシーを満たすことができるのは大きな利点です。

#### 運用負荷の軽減と機能パリティの向上

新しいアーキテクチャでは、**AWS マネージド** による運用モデルが提供され、etcd のバックアップやログエージェントの管理が自動化されます。従来のセルフマネージド Kubernetes クラスタと比べ、運用負荷が大幅に削減されます。

さらに、EKS アドオン、**IAM Roles for Service Accounts**、**EKS Pod Identity** といったクラウド EKS で利用可能な機能が、Outposts 上でもサポートされるようになりました。これにより、クラウドとオンプレミスで一貫した運用体験が得られ、マルチ環境での Kubernetes 管理が容易になります。

#### 導入時の考慮点

Outposts は物理ラックの設置と初期構成が必要であり、クラウドリソースのような即座のプロビジョニングはできません。また、EC2 インスタンスストアを使用するため、インスタンスが停止するとデータが失われる特性を理解しておく必要があります。永続化が必要なデータは EBS ボリュームや外部ストレージを併用する設計が求められます。

パフォーマンスやコストの観点では、EC2 インスタンスストアは EBS と比べて I/O レイテンシが低く、ローカルディスクの高速アクセスが可能ですが、耐久性と可用性のトレードオフがあります。ワークロードの特性に応じて適切なストレージ構成を選択することが重要です。

## SRE視点での活用ポイント

### Outposts 上の EKS でハイブリッド環境の運用を統一

オンプレミスとクラウドのハイブリッド環境で Kubernetes を運用している場合、異なる管理ツールやワークフローが混在し、運用負荷が増大しがちです。EKS on Outposts の完全ローカル実行により、クラウドと同じ EKS API と運用モデルを Outposts 上でも利用できるため、kubectl、Helm、CI/CD パイプラインを統一できます。

IAM Roles for Service Accounts や Pod Identity が Outposts でもサポートされるため、AWS リソースへのアクセス制御をクラウドと同じ方法で実装できます。Terraform や eksctl でインフラをコード管理している場合、設定ファイルの差分を最小限に抑えて Outposts 環境をプロビジョニングできるでしょう。

ただし、Outposts は物理ハードウェアの設置とメンテナンスが必要であり、クラウドのようなスケールアップの柔軟性はありません。容量計画を慎重に行い、将来的なワークロード増加を見越したラック構成を選定することが重要です。また、ネットワーク切断時の動作確認や障害シミュレーションを事前に実施し、ランブックに組み込んでおくと、インシデント対応時の安心感が増します。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| **Amazon SageMaker AI** | Nvidia Nemotron 3 Nano モデルのサーバーレス微調整（SFT/RFT）に対応。30B パラメータモデルを独自データでカスタマイズ可能、インフラ管理不要、従量課金モデル。東京、アイルランド、米国東部・西部で提供開始。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-ft-nemotron-3/) |
| **Amazon EKS** | AWS Outposts 上で EC2 インスタンスストアから起動する完全ローカル実行に対応。コントロールプレーン全体が Outposts 上で動作し、データレジデンシー要件に対応。EKS アドオン、IAM Roles for Service Accounts、Pod Identity をサポート。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-eks-aws-outposts-ec2-instance-store/) |
| **Amazon EC2 Capacity Blocks for ML** | AWS GovCloud (US-West/US-East) で提供開始。最大8週間先まで最長6ヶ月の GPU 容量予約が可能。1～64インスタンスのクラスタサイズに対応し、AWS RAM で複数アカウント間の容量共有が可能。P6-B200/P6-B300 インスタンスで利用可能。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ec2-capacity-blocks-ml-govcloud/) |
| **Amazon EC2 U7i-8TB** | パリリージョンで高メモリインスタンス U7i-8TB が利用可能に。8TiB DDR5メモリ、448 vCPU、Intel 第4世代 Xeon Scalable プロセッサ搭載。既存 U-1 比で 45% 優れた価格性能を実現。SAP HANA、Oracle、SQL Server などに最適化。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ec2-u7i-8tb-europe-paris/) |
| **Amazon EC2 I7i** | パリリージョンでストレージ最適化インスタンス I7i が利用可能に。第5世代 Intel Xeon Processor 搭載、I4i 比で計算性能 23% 向上、価格性能比 10% 改善。最大 45TB NVMe ストレージ、I/O レイテンシ 50% 低減、Torn Write Prevention 対応。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ec2-i7i-instances-europe-paris-region/) |
| **Amazon Quick** | Snowflake Cortex AI と統合。Model Context Protocol (MCP) 経由で接続し、自然言語で Snowflake データをクエリ可能。Cortex Analyst（構造化データ）と Cortex Search（非構造化ドキュメント）に対応。Quick Flow で複数ステップのワークフロー自動化が可能。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-quick-snowflake-cortex-ai/) |

## まとめ

今回紹介したアップデートは、機械学習の民主化、ハイブリッドクラウドでのコンテナ運用統一という、SRE やプラットフォームエンジニアが直面する課題に対する具体的な解決策を提供しています。

SageMaker AI のサーバーレス微調整は、大規模言語モデルのカスタマイズを手軽にし、インフラ管理の負担を排除することで、AI 活用のハードルを下げます。EKS on Outposts の完全ローカル実行は、規制対応やデータレジデンシー要件を満たしながら、クラウドと同じ運用体験を提供します。

また、EC2 の高メモリ・ストレージ最適化インスタンスのリージョン拡大や、GovCloud での GPU 容量予約機能の提供は、エンタープライズや政府機関での大規模ワークロード実行をより柔軟にサポートします。

これらのアップデートを活用する際は、既存システムへの影響を慎重に評価し、段階的な導入やコスト・パフォーマンスの測定を行いながら、運用改善につなげていくことが重要です。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)