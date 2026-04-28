---
title: "【AWS】2026/04/28 のアップデートまとめ"
date: 2026-04-28T08:02:06+09:00
draft: false
tags: ["aws", "connect", "sagemaker", "redshift", "workspaces", "fsx", "ec2"]
categories: ["AWS Updates"]
summary: "2026/04/28 のAWSアップデートまとめ"
---

# 2026年4月28日 AWS アップデート解説

![](/images/aws-updates-20260428/header.png)

## はじめに

2026年4月28日は、5件のAWSアップデートが発表されました。この日のアップデートは、特にコンタクトセンターソリューション、データウェアハウス、機械学習基盤、仮想デスクトップといった幅広い領域にわたり、既存サービスの機能強化とリージョン拡大が中心となっています。

中でも注目すべきは、**Amazon Connect のファイル添付上限が20MBから100MBへ5倍に拡大**されたこと、そして **Amazon SageMaker HyperPod が G7e インスタンスをサポート**し、G6e比で最大2.3倍の推論性能向上を実現したことです。また、Amazon Redshift Serverless がメルボルンとカルガリーリージョンで利用可能になり、Amazon WorkSpaces Personal が最新のLinux OS（Rocky 9、RHEL 9、Ubuntu 24.04）に対応するなど、グローバル展開と最新技術への対応が進んでいます。

本記事では、これらのアップデートの中から特に実務への影響が大きいものを深掘りし、SRE視点での活用ポイントを解説します。

## 注目アップデート深掘り

### Amazon Connect のファイル添付上限拡大とカスタムファイル対応

Amazon Connect において、チャット、ケース、タスクにおけるファイル添付の上限が **20MBから100MBへ5倍に拡大** されました。同時に、管理者がカスタムファイル拡張子を設定できる機能も追加されています。

#### なぜこのアップデートが重要なのか

従来の20MB制限では、診断バンドル、システムログアーカイブ、医療画像、CADファイルなどの大容量ファイルを直接共有することが困難でした。このため、サポート担当者と顧客の間で以下のような非効率な運用が発生していました：

- ファイルを分割して複数回送信する手間
- 外部のファイル共有サービスへのアップロードとリンク共有
- メール添付への切り替えによる対応履歴の分断
- セキュリティリスクを伴う代替手段の利用

新しい100MB上限により、これらの課題が解消され、顧客とサポート担当者の往復回数を削減し、問題解決までの時間を短縮できます。

#### 設定方法

管理者は Amazon Connect コンソール、または API/CLI/SDK を通じて、添付ファイルの設定を有効化・カスタマイズできます。具体的な設定パラメータ名や CLI フラグはリリースノートに明示されていないため、実装にあたっては Amazon Connect Administrator Guide の「Enable Attachments」セクションと API リファレンスを参照してください。

リリースノートで具体例として挙げられている用途は、技術サポート企業の診断バンドルやログアーカイブ（最大 100 MB）の共有、および金融サービス企業向けの契約書・コンプライアンス文書をカスタム拡張子で受け付ける運用です。

#### セキュリティとコストの考慮点

ファイルサイズの拡大に伴い、以下のような運用面の検討が必要になります：

- ウイルススキャンの実装と、スキャン時間が顧客体験に与える影響の評価
- 許可するファイル拡張子のホワイトリスト化と定期的なレビュー
- 添付ファイル保管に伴うストレージコストの増加予測と監視
- アクセスログの保持期間とコンプライアンス要件の整合性確認

### Amazon SageMaker HyperPod の G7e インスタンスサポート

Amazon SageMaker HyperPod が新たに **G7e インスタンス** と **r5d.16xlarge インスタンス** をサポートしました。特に G7e は、NVIDIA RTX PRO 6000 Blackwell Server Edition GPU を搭載し、G6e 比で最大 2.3 倍の推論性能向上を実現します。

#### G7e インスタンスの技術的特徴

G7e インスタンスは以下の仕様を持ちます：

- **GPU メモリ**：最大 768 GB
- **推論性能**：G6e 比で最大 2.3 倍
- **TFLOPS**：G6e 比で最大 1.27 倍
- **GPU 間帯域幅**：G6e の 4 倍

この大容量 GPU メモリにより、大規模言語モデル（LLM）を複数同時にデプロイし、単一エンドポイントで複数モデルの推論を実行できます。また、マルチモーダル生成 AI、エージェント AI、物理 AI（ロボティクス制御）モデルなど、メモリ要件の高いモデルの本番デプロイに適しています。

#### r5d.16xlarge インスタンスの活用シーン

r5d.16xlarge インスタンスは、以下の特徴を持ちます：

- **vCPU**：64
- **メモリ**：512 GB
- **ストレージ**：5つの 600 GB NVMe SSD
- **プロセッサ**：Intel Xeon Platinum 8000 シリーズ

このインスタンスは、分散訓練のデータ前処理、大規模特徴エンジニアリング、メモリ集約的なオーケストレーションサービスに最適です。GPU コンピュートノードと連携し、Ray などのフレームワークを使用した大規模データパイプラインを効率的に実行できます。

#### 実装例：HyperPod クラスターでの G7e 利用

HyperPod クラスターで G7e インスタンスを利用する際の設定例は以下の通りです：

```bash
# HyperPod クラスターの作成（G7e インスタンスを含む）
$ aws sagemaker create-cluster \
  --cluster-name my-hyperpod-cluster \
  --instance-groups file://instance-groups.json \
  --vpc-config file://vpc-config.json
```

`instance-groups.json` の例：

```json
[
  {
    "InstanceGroupName": "inference-group",
    "InstanceType": "ml.g7e.48xlarge",
    "InstanceCount": 2,
    "LifeCycleConfig": {
      "SourceS3Uri": "s3://my-bucket/lifecycle-config.sh",
      "OnCreate": "lifecycle-config.sh"
    }
  },
  {
    "InstanceGroupName": "preprocessing-group",
    "InstanceType": "ml.r5d.16xlarge",
    "InstanceCount": 4
  }
]
```

#### G6e との性能比較の考慮ポイント

G7e を検証する際は、以下の項目を定量的に比較することが推奨されます：

- 推論レイテンシ（単一リクエスト処理時間）
- スループット（秒あたりの処理リクエスト数）
- 同時実行可能なモデル数
- GPU メモリ使用効率
- コストパフォーマンス（1推論あたりのコスト）

リリースノートでは「最大2.3倍の推論性能向上」が示されていますが、実際のワークロードでの性能は、モデルのサイズ、バッチサイズ、精度（FP16/FP32）によって変動するため、本番環境を想定したベンチマークが重要です。

## SRE視点での活用ポイント

### Amazon Connect のファイル添付拡大を運用に組み込む

サポート業務を担うSREチームにとって、100MB添付は障害対応時の情報収集プロセスを大幅に改善できます。例えば、顧客から障害発生時のログファイル一式を直接チャットで受け取れるようになり、ログ取得指示と確認の往復時間を削減できます。

ただし、導入時には以下の点を検討する必要があります：

- **ストレージコストの監視体制**：大容量ファイルが日常的にアップロードされる場合、S3 ストレージコストが増加します。CloudWatch メトリクスでファイルサイズと件数を監視し、異常な増加を検知する仕組みを構築することが推奨されます。
- **ファイル拡張子のガバナンス**：カスタムファイル拡張子を無制限に許可すると、セキュリティリスクが高まります。業界特有のファイル形式のみをホワイトリスト化し、定期的にレビューする運用が望ましいでしょう。
- **アラート設計**：100MBに近いファイルが頻繁にアップロードされる場合、ネットワーク帯域やアップロード時間の影響を考慮し、顧客体験が低下していないかモニタリングする必要があります。

Terraform で管理している Amazon Connect 環境があれば、カスタムファイル拡張子の設定をコード化し、環境間での一貫性を保つことができます。

### SageMaker HyperPod での推論基盤の選定基準

G7e インスタンスの導入を検討する際、SRE視点では以下の観点が重要です：

- **推論ワークロードの特性分析**：レイテンシ重視のリアルタイム推論か、スループット重視のバッチ推論かにより、最適なインスタンスタイプが異なります。G7e は大容量メモリを活かした複数モデル同時実行に強みがあるため、複数の LLM を統合したエージェント AI 基盤の構築に適しています。
- **コスト最適化のためのスケーリング戦略**：HyperPod は自動スケーリング機能を持ちますが、G7e のような高性能インスタンスではスケールアウト／スケールインのタイミングを慎重に設計する必要があります。CloudWatch アラームと組み合わせ、GPU メモリ使用率が一定閾値を超えた際にアラートを発火させる仕組みが有効です。
- **障害対応のランブック整備**：G7e インスタンスの障害時には、r5d.16xlarge インスタンスでデータ前処理のみ継続するなど、段階的な縮退運用を定義しておくことで、サービス全体の可用性を維持できます。

既存の機械学習基盤で GPU インスタンスを使用している場合、G7e への移行は段階的に行い、既存ワークロードとのパフォーマンス比較を定量的に評価することが推奨されます。

### Amazon WorkSpaces の OS 移行計画

Amazon Linux 2 が 2026年6月にサポート終了を迎えるため、WorkSpaces Personal を利用している組織では、Rocky 9、RHEL 9、Ubuntu 24.04 への移行計画が必要です。

移行時の判断基準として、以下を考慮すると良いでしょう：

- **既存ツールチェーンとの互換性**：開発環境として使用している場合、Python、Node.js、Javaなどのランタイムバージョンが新OSで利用可能か確認します。
- **サポートライフサイクル**：RHEL 9 や Ubuntu 24.04 の公式サポート期間を踏まえ、次回の OS 移行タイミングを見越した選択が重要です。
- **社内標準との整合性**：オンプレミスやEC2で使用しているOSと揃えることで、運用ナレッジの共有と標準化が進みます。

移行作業をランブックに組み込む際は、既存 WorkSpaces のバックアップ取得、新 OS バンドルでの WorkSpaces 起動、アプリケーション動作確認、ユーザー移行の順で段階的に実施することで、リスクを最小化できます。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon FSx for OpenZFS Single-AZ (HA) が17のリージョンで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-fsx-openzfs-single-az-ha/) | FSx for OpenZFS の Single-AZ（高可用性）ファイルシステムが、17の追加 AWS 商用リージョンおよび AWS GovCloud (US) リージョンで利用可能になりました |
| 2 | [Amazon Connect がファイル添付上限を拡大、カスタムファイルタイプに対応](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-connect-increases-attachment/) | チャット、ケース、タスクでのファイル添付上限が20MBから100MBに拡大。管理者はカスタムファイル拡張子を設定可能になり、診断バンドルやログアーカイブなどの大容量ファイルをサポート案件で直接共有できるようになりました |
| 3 | [Amazon Redshift Serverless がメルボルンとカルガリーリージョンで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-redshift-serverless-melbourne-calgary-regions/) | Redshift Serverless がオーストラリア（メルボルン）とカナダ（カルガリー）のリージョンで利用可能に。クラスター管理不要で、自動スケーリングと秒単位課金により、データ分析がより手軽に実施可能になりました |
| 4 | [Amazon SageMaker HyperPod が G7e と r5d.16xlarge インスタンスをサポート](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-sagemaker-hyperpod-g7e-r5d/) | HyperPod が新たに G7e（NVIDIA RTX PRO 6000 Blackwell搭載、G6e比最大2.3倍の推論性能）と r5d.16xlarge（64 vCPU、512 GB メモリ）をサポート。大規模言語モデルの推論や分散訓練のデータ前処理が強化されました |
| 5 | [Amazon WorkSpaces Personal が Rocky 9、RHEL 9、Ubuntu 24.04 をサポート](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-workspaces-rocky9-rhel9-ubuntu24/) | WorkSpaces Personal で Rocky Linux 9、Red Hat Enterprise Linux 9、Ubuntu 24.04 の最新 OS バンドルが利用可能に。Amazon Linux 2 の 2026年6月サポート終了に向けた移行パスが提供されました |

## まとめ

2026年4月28日のアップデートは、既存サービスの機能強化とリージョン拡大が中心でしたが、実務への影響は大きいものが含まれています。

特に **Amazon Connect のファイル添付上限5倍拡大** は、サポート業務や顧客対応の効率化に直結し、業界横断的に活用が期待されます。カスタムファイル拡張子対応により、ヘルスケア、製造、金融といった専門性の高い業界でも柔軟な運用が可能になりました。

**SageMaker HyperPod の G7e インスタンス対応** は、LLM や生成 AI の推論基盤を本番環境で運用する際の選択肢を広げます。G6e 比で最大2.3倍の性能向上と最大768GBのGPUメモリは、複数モデルの同時実行やマルチモーダル AI に大きな価値を提供します。

また、**Redshift Serverless のメルボルン・カルガリー展開** や **WorkSpaces の最新 Linux OS 対応** は、グローバル展開と長期的な運用を見据えた重要な基盤整備です。

SRE の視点では、これらのアップデートを単に「利用可能になった」で終わらせず、既存の運用プロセス、コスト構造、障害対応手順にどう組み込むかを検討することが重要です。特に Amazon Linux 2 の EOL が迫る中、WorkSpaces の OS 移行は計画的に進める必要があります。

今後も AWS の継続的な機能強化を注視し、自組織の運用改善に活かしていきましょう。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)