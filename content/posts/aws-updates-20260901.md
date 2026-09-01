---
title: "【AWS】2026/09/01 のアップデートまとめ"
date: 2026-09-01T08:02:26+09:00
draft: false
tags: ["aws", "redshift", "lambda", "ec2", "timestream", "cognito", "beanstalk", "opensearch", "iam", "s3", "sqs", "sns", "guardduty", "inspector", "macie", "security-hub"]
categories: ["AWS Updates"]
summary: "2026/09/01 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260901/header.png)

# 今回発表されたAWSアップデート11件を徹底解説

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。Amazon Redshiftの強化VPCルーティング対応IAM Identity Center認証、Lambda再帰ループ検出の全リージョン展開、Graviton5プロセッサ搭載のR9g/R9gdインスタンスといった注目機能のほか、マルチクラウド接続を実現するAWS Interconnect、AIエージェント管理のためのAWS Agent Registry、そしてセキュリティ自動修復やCognitoのマシン間認証機能など、運用効率とセキュリティを底上げするアップデートが含まれています。

特に注目したいのは、ネットワーク分離とガバナンスを重視した機能強化です。Redshift EVRとIAM Identity Centerの統合は、分析用途でパブリックインターネットへの egress を許可できないデータレジデンシー・規制・ネットワーク分離の要件下でも、データをVPC内に留めたまま企業SSOを実現します。また、Lambda再帰ループ検出は、設定ミスやコードバグによる予期しないコスト急増を自動的に防止する重要な安全装置となります。

## 注目アップデート深掘り

### Amazon Redshift の IAM Identity Center 認証と強化VPCルーティング対応

Amazon Redshiftが、強化VPCルーティング（EVR）環境下でAWS IAM Identity Center認証をサポートするようになりました。これは、データの居場所や規制要件によりパブリックインターネットへのアクセスを許可できない企業にとって、極めて価値の高いアップデートです。

**なぜこのアップデートが重要なのか**

従来、Redshiftで企業のシングルサインオン（SSO）を利用する場合、認証トークンの検証と交換の過程で、パブリックインターネット経由の通信が発生する可能性がありました。データレジデンシー要件、規制要件、ネットワーク分離要件により、分析用途でのパブリックインターネットへの egress を認められない組織があります。

今回のアップデートでは、IAM Identity Centerのトークン検証・交換がAWS PrivateLinkインターフェースエンドポイント経由で行われるため、認証フロー全体がVPC内で完結します。これにより、すべてのRedshiftトラフィックと同じ管理されたネットワークパス上で認証が行われ、セキュリティグループ、ネットワークACL、エンドポイントポリシーによる統制、さらにVPC Flow Logsによる可視化が可能になります。

**ネットワーク分離のメカニズム**

強化VPCルーティング（EVR）が有効化されたRedshiftでは、Redshiftウェアハウスと他のAWSサービス間のすべてのトラフィックがVPCを経由します。今回の機能追加により、IAM Identity Centerとの認証通信も同じくVPC内に閉じ込められます。具体的には以下の流れになります。

1. ユーザーがRedshiftへの接続を開始し、IAM Identity Centerの認証情報を提示
2. RedshiftはVPC内のPrivateLinkインターフェースエンドポイント経由でIAM Identity Centerと通信
3. トークンの検証と交換が完全にVPC内で完了
4. 認証成功後、ユーザーはRedshiftクラスタへのアクセスを許可される

この構成では、セキュリティグループで特定のエンドポイントへのアクセスのみを許可し、ネットワークACLでサブネットレベルの制御を行い、VPC Flow Logsですべての通信をログに記録できます。監査要件が厳しい環境でも、誰がいつどのような経路でRedshiftにアクセスしたかを完全に追跡可能です。

**マルチリージョン対応の意義**

IAM Identity Centerのマルチリージョンレプリケーション機能にも対応しているため、グローバルに展開する企業でも、各リージョンのRedshiftクラスタに対して一貫した認証基盤を構築できます。これにより、地理的に分散したデータ分析環境において、統一されたアクセス管理とガバナンスを実現できます。

### AWS Lambda 再帰ループ検出の全リージョン展開

AWS Lambda再帰ループ検出機能が、すべての商用AWSリージョンで利用可能になりました。この機能はデフォルトで有効化されており、Lambda関数と他のサポート対象サービス間の再帰呼び出しを自動的に検出・停止します。

**再帰ループの危険性**

Amazon S3、Amazon SQS、Amazon SNSなどのイベントソースからLambda関数をトリガーする構成は非常に一般的です。しかし、設定ミスやコードの欠陥により、Lambda関数が処理したイベントを元のソースに送り返してしまうと、無限ループが発生します。

例えば、S3バケットへのファイルアップロードをトリガーにLambda関数が実行され、その関数内で同じバケットにファイルを書き込むと、新たなイベントが発生し、再びLambda関数がトリガーされます。このサイクルが止まらなくなると、意図しない実行が積み上がり、予期しない請求につながります。

**自動検出と停止のメカニズム**

Lambda再帰ループ検出は、Lambda関数とサポート対象サービスの間で発生した再帰ループを検出します。ループが検出されると、Lambdaはイベント処理を自動的に停止し、トラブルシューティング手順を含むAWS Health Dashboard通知を送信します。

この機能はサポート対象のSDKバージョンを使用している場合に自動的に動作するため、既存のLambda関数に対する変更は不要です。ただし、意図的に再帰処理を行う必要がある場合（例：再帰的なツリー構造の処理）は、PutFunctionRecursionConfig APIを使用して検出機能を無効化できます。

**運用上の安全性向上**

このアップデートにより、開発環境での検証が不十分なコードが本番環境にデプロイされた場合でも、暴走を自動的に防止できます。特に、複数のチームが並行して開発を進める大規模な環境では、意図しない設定の組み合わせによる再帰ループのリスクが常に存在します。自動検出機能がそのセーフティネットとして機能します。

### Amazon EC2 R9g/R9gd インスタンス - Graviton5 世代の性能向上

AWS Graviton5プロセッサを搭載したメモリ最適化インスタンスR9gとR9gdが一般提供開始となりました。これらは前世代のGraviton4ベースのR8g/R8gdと比較して、最大25%のコンピュート性能向上を実現しています。

**パフォーマンスの詳細**

発表によると、R9g/R9gdインスタンスはGraviton4ベースのR8g/R8gd比で以下の性能向上を達成しています。

- データベースワークロード：最大30%高速化
- ウェブアプリケーション：最大35%高速化
- 機械学習ワークロード：最大35%高速化

さらにキャッシュ容量が5倍に拡大し、AWSはこれを「クラウド上のプロセッサインスタンスとして最速のメモリ」と表現しています。想定ワークロードとして挙げられているのは、データベース、インメモリキャッシュ、リアルタイムビッグデータ分析です。

**R9g と R9gd の使い分け**

R9gインスタンスは、データベース、インメモリキャッシュ、リアルタイムビッグデータ分析、そしてコンテナ化アプリケーション（Kubernetes、Docker、EKS、ECS）の実行に向いています。対応するプログラミング言語も豊富で、Python、Java、Go、Rust、Node.jsなどが動作します。

一方、R9gdインスタンスはローカルNVMe SSDストレージを搭載しており、オープンソースデータベース、分散型のリアルタイムビッグデータ分析、大規模インメモリデータベースなど、ローカルストレージを必要とするワークロードに適しています。高速なローカルストレージにより、一時データの読み書きやキャッシュ層として利用でき、EBSボリュームへのネットワークトラフィックを削減できます。

**セキュリティ強化：Nitro Isolation Engine**

R9g/R9gdは第6世代AWS Nitro Systemを搭載し、新機能のNitro Isolation Engineを導入しています。この機能は形式検証（formal verification）により、顧客のワークロードが他の顧客およびAWSのオペレーターから分離されていることを数学的に保証します。

## SRE視点での活用ポイント

### ネットワーク分離とガバナンス強化の実践

Redshift EVRとIAM Identity Center統合は、ゼロトラストアーキテクチャの実装において重要な一歩となります。Terraformでインフラを管理している環境であれば、VPCエンドポイントとセキュリティグループの設定をコード化し、すべてのデータアクセスをVPC内に閉じ込める設計を標準化できます。

特に、VPC Flow Logsと組み合わせることで、誰がいつどの経路でRedshiftにアクセスしたかを継続的に監視できます。CloudWatch Logsに集約したフローログをAthenaでクエリし、異常なアクセスパターンを検出するランブックを整備すれば、インシデント対応時の調査時間を短縮できます。

導入時の注意点として、PrivateLinkインターフェースエンドポイントの作成にはENIが必要であり、サブネットのIPアドレス枯渇に注意が必要です。また、EVR有効化により既存のデータロードパイプラインが影響を受ける可能性があるため、段階的な移行とテストが推奨されます。

### Lambda再帰ループ検出による予防的運用

Lambda再帰ループ検出は、特にイベント駆動アーキテクチャにおける防御的なプラクティスとして価値があります。CloudWatch Alarmsと組み合わせて、AWS Health Dashboard通知をSlackやPagerDutyにルーティングすれば、再帰ループ発生時の即座なアラートが可能になります。

既存のLambda関数に対しては、どの関数がS3、SQS、SNSと相互作用しているかを棚卸しし、意図しないループの可能性がないか検証することが推奨されます。特に、複数チームが独立してLambda関数を開発している場合、チーム間の依存関係が可視化されていないことが多く、潜在的なリスクとなります。

PutFunctionRecursionConfig APIを使って検出機能を無効化する場合は、その理由と承認プロセスをドキュメント化し、定期的なレビューの対象とすることが重要です。意図的な再帰処理であっても、終了条件の実装ミスやリソース制限の見落としがないか、コードレビューで確認すべきです。

### Graviton5 インスタンスへの移行計画

R9g/R9gdインスタンスは、特にコスト最適化とパフォーマンス向上の両立が求められる環境で検討価値があります。既存のx86ベースのR7iやR6iからの移行では、アプリケーションがArm64アーキテクチャに対応しているか確認が必要です。幸い、PostgreSQL、MySQL、Redis、Elasticsearchなど主要なオープンソースソフトウェアはすでにArm64対応しています。

移行時のリスクを低減するには、まず開発環境でR9gインスタンスを起動し、アプリケーションの動作とパフォーマンスベンチマークを実施します。その後、Blue/Greenデプロイメントやカナリアリリースの手法で、段階的に本番トラフィックを新インスタンスに移行するアプローチが安全です。

Reserved InstancesやSavings Plansの契約がある場合、既存のコミットメントとの兼ね合いを考慮する必要があります。コスト分析ツール（AWS Cost ExplorerやAWS Compute Optimizer）を活用し、移行によるコスト削減効果を定量的に評価した上で、経営層への提案資料を作成することが推奨されます。

> **AWS Interconnect とは？** クラウド事業者間をまたぐプライベート接続を短時間でプロビジョニングするための AWS の新サービス。AWS はネットワーク相互運用性のオープン仕様を公開しており、どの事業者でも採用できるフレームワークとして位置づけています。Microsoft Azure 向けはプレビュー、OCI と Google Cloud 向けは一般提供です。

> **AWS Agent Registry とは？** 組織内のエージェント・ツール・スキル・MCP サーバー・カスタムリソースを対象とした、プライベートで統制されたカタログ／ディスカバリ層（GA）。CloudFormation / Terraform / AWS CDK でコードとして管理でき、AWS RAM でアカウント間共有や組織全体のレジストリ作成が可能です。

> **ASR（Automated Security Response on AWS）とは？** Amazon Inspector・GuardDuty・Macie・AWS Security Hub の検出結果に対する修復を自動化する AWS ソリューション。今回追加された AI Remediation Toolkit は、セーフガードを組み込んだガイド付きプロンプトにより、カスタム修復の開発期間を数週間から数時間に短縮します。

> **Apache Iceberg v3 とは？** データレイク向けオープンテーブルフォーマットの最新バージョン。デフォルト列値、行系統（row lineage）、削除ベクトルが追加され、既存テーブルへの列追加といったスキーマ進化や、高頻度の更新・削除ワークロードの読み書きを改善します。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| Amazon Redshift | IAM Identity Center認証が強化VPCルーティング（EVR）に対応。すべてのトラフィックがVPC内に留まり、PrivateLinkインターフェースエンドポイント経由で認証を実施 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-redshift-supports-idc-evr) |
| AWS Lambda | 再帰ループ検出機能が全商用リージョンで利用可能に。デフォルトで有効化され、S3、SQS、SNSなどのイベントソースとの間の再帰呼び出しを自動検出・停止 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/lambda-recursion-regions) |
| Amazon EC2 | Graviton5プロセッサ搭載のR9g/R9gdメモリ最適化インスタンスが一般提供開始。前世代比で最大25%のコンピュート性能向上、データベースで最大30%、ウェブアプリで最大35%高速化 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-r9g-and-r9gd-memory-optimized-instances-are-now-available/) |
| Amazon Timestream for InfluxDB | 8つの新リージョン（ケープタウン、バンコク、香港、ハイデラバード、メルボルン、ソウル、チューリッヒ、テルアビブ）で利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-timestream-influxdb-regions/) |
| AWS Interconnect | クラウド事業者間のプライベート接続をプロビジョニングする新サービス。Microsoft Azure 向けがパブリックプレビュー開始（OCI・Google Cloud 向けは一般提供済み）。AWS が公開したネットワーク相互運用のオープン仕様に基づく | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-announces-AWS-interconnect-multicloud-microsoft-azure-preview/) |
| AWS Agent Registry | AIエージェント・ツール・リソースを一元管理できるレジストリが一般提供開始。CloudFormation・Terraform・CDK対応、AWS RAM組織間共有、AgentCore自動検出機能を実装 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available) |
| Automated Security Response on AWS (ASR) | AI駆動のRemediation Toolkitを追加。カスタム修復の開発期間を数週間から数時間に短縮。Amazon Inspector、GuardDuty、Macie、AWS Security Hub の検出結果に対応し、Email・Slack・Jira・ServiceNowで通知可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/automated-security-response-adds-AI-toolkit/) |
| Amazon Cognito | GetClientToken API操作を追加。ユーザープールドメイン設定なしでマシン間（M2M）認可用アクセストークンを直接取得可能に。AWS WAFとPrivateLink対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-cognito-get-client-token/) |
| Amazon Redshift | Apache Iceberg v3テーブルの読み書きに対応。デフォルト列値、行系統追跡、削除ベクトルをサポートし、スキーマ進化と高頻度更新ワークロードを改善 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-redshift-supports-apache-iceberg-v3) |
| AWS Elastic Beanstalk | Windows Server環境でActive Directoryドメイン参加を自動化。カスタムスクリプト不要で、設定オプションのみでドメイン統合を実現 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/elastic-beanstalk-active-directory-domain-join/) |
| Amazon OpenSearch Service | Cluster Insightsに17個の新インサイトを追加。Red/Yellowステータス時に根本原因を自動特定し、解決策を即座に提案 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/opensearch-cluster-status-insight/) |

## まとめ

今回のアップデート群は、セキュリティ、ガバナンス、パフォーマンス、運用効率という、エンタープライズ環境における4つの重要な柱を強化するものです。

特にネットワーク分離とアイデンティティ管理の統合（Redshift EVRとIAM Identity Center）、予防的な自動保護機能（Lambda再帰ループ検出）、そしてAIエージェントの統一管理（AWS Agent Registry）は、現代のクラウドアーキテクチャにおける重要なトレンドを反映しています。

Graviton5世代のR9g/R9gdインスタンスは、Armアーキテクチャの成熟を示すとともに、コスト効率とパフォーマンスの両立という現実的な課題への回答となっています。AWS Interconnect の Azure 接続は現時点でパブリックプレビューのため、本番採用前に SLA・料金体系を確認しておく価値があります（OCI・Google Cloud 向けはすでに一般提供）。

既存環境への影響が少なく導入しやすいのは、Redshift EVR と IAM Identity Center の統合、そして Lambda 再帰ループ検出の2点です。前者は認証経路をVPC内に閉じるだけで監査要件に応えられ、後者はデフォルト有効のため既存関数への変更が不要です。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)