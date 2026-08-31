---
title: "【AWS】2026/09/01 のアップデートまとめ"
date: 2026-09-01T08:02:26+09:00
draft: true
tags: ["aws", "redshift", "lambda", "ec2", "timestream", "cognito", "beanstalk", "opensearch", "iam", "s3", "sqs", "sns", "guardduty", "inspector", "macie", "security-hub"]
categories: ["AWS Updates"]
summary: "2026/09/01 のAWSアップデートまとめ"
---

# 今回発表されたAWSアップデート11件を徹底解説

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。Amazon Redshiftの強化VPCルーティング対応IAM Identity Center認証、Lambda再帰ループ検出の全リージョン展開、Graviton5プロセッサ搭載のR9g/R9gdインスタンスといった注目機能のほか、マルチクラウド接続を実現するAWS Interconnect、AIエージェント管理のためのAWS Agent Registry、そしてセキュリティ自動修復やCognitoのマシン間認証機能など、運用効率とセキュリティを大幅に向上させるアップデートが含まれています。

特に注目したいのは、ネットワーク分離とガバナンスを重視した機能強化です。Redshift EVRとIAM Identity Centerの統合は、金融・医療など規制の厳しい業界において、データを完全にVPC内に留めたまま企業SSOを実現します。また、Lambda再帰ループ検出は、設定ミスやコードバグによる予期しないコスト急増を自動的に防止する重要な安全装置となります。

## 注目アップデート深掘り

### Amazon Redshift の IAM Identity Center 認証と強化VPCルーティング対応

Amazon Redshiftが、強化VPCルーティング（EVR）環境下でAWS IAM Identity Center認証をサポートするようになりました。これは、データの居場所や規制要件によりパブリックインターネットへのアクセスを許可できない企業にとって、極めて価値の高いアップデートです。

**なぜこのアップデートが重要なのか**

従来、Redshiftで企業のシングルサインオン（SSO）を利用する場合、認証トークンの検証と交換の過程で、パブリックインターネット経由の通信が発生する可能性がありました。金融機関、医療機関、政府機関などでは、データ主権要件やネットワーク分離ポリシーにより、すべてのトラフィックを組織の管理下に置く必要があります。

今回のアップデートでは、IAM Identity Centerのトークン検証・交換がAWS PrivateLinkインターフェースエンドポイント経由で行われるため、認証フロー全体がVPC内で完結します。これにより、すべてのRedshiftトラフィックと同じ管理されたネットワークパス上で認証が行われ、セキュリティグループ、ネットワークACL、エンドポイントポリシーによる統制、さらにVPC Flow Logsによる可視化が可能になります。

**ネットワーク分離のメカニズム**

強化VPCルーティングが有効化されたRedshiftクラスタでは、すべてのCOPYコマンド、UNLOADコマンド、その他のデータ転送がVPC経由で行われます。今回の機能追加により、IAM Identity Centerとの認証通信も同じくVPC内に閉じ込められます。具体的には以下の流れになります。

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

例えば、S3バケットへのファイルアップロードをトリガーにLambda関数が実行され、その関数内で同じバケットにファイルを書き込むと、新たなイベントが発生し、再びLambda関数がトリガーされます。このサイクルが止まらなくなると、数分で数千〜数万回の実行が発生し、予期しない高額請求につながります。

**自動検出と停止のメカニズム**

Lambda再帰ループ検出は、関数の呼び出しパターンをモニタリングし、同一のイベントソースからの繰り返し呼び出しを検知します。ループが検出されると、Lambdaサービスは自動的にイベント処理を停止し、AWS Health Dashboardに通知を送信します。通知にはトラブルシューティング手順が含まれており、開発者は迅速に問題を特定・修正できます。

この機能はサポート対象のSDKバージョンを使用している場合に自動的に動作するため、既存のLambda関数に対する変更は不要です。ただし、意図的に再帰処理を行う必要がある場合（例：再帰的なツリー構造の処理）は、PutFunctionRecursionConfig APIを使用して検出機能を無効化できます。

**運用上の安全性向上**

このアップデートにより、開発環境での検証が不十分なコードが本番環境にデプロイされた場合でも、暴走を自動的に防止できます。特に、複数のチームが並行して開発を進める大規模な環境では、意図しない設定の組み合わせによる再帰ループのリスクが常に存在します。自動検出機能がそのセーフティネットとして機能します。

### Amazon EC2 R9g/R9gd インスタンス - Graviton5 世代の性能向上

AWS Graviton5プロセッサを搭載したメモリ最適化インスタンスR9gとR9gdが一般提供開始となりました。これらは前世代のGraviton4ベースのR8g/R8gdと比較して、最大25%のコンピュート性能向上を実現しています。

**パフォーマンスの詳細**

リリースノートによると、R9g/R9gdインスタンスは以下の性能向上を達成しています。

- データベースワークロード：最大30%高速化
- ウェブアプリケーション：最大35%高速化
- 機械学習ワークロード：最大35%高速化

さらに、キャッシュ容量が5倍に増強され、「クラウド内最速のメモリ」を搭載しています。これにより、メモリアクセスが頻繁に発生するワークロード、特にインメモリデータベース（Redis、Memcached）やリアルタイムビッグデータ分析（Apache Spark、Flink）で大幅な性能向上が期待できます。

**R9g と R9gd の使い分け**

R9gインスタンスは、データベース、インメモリキャッシュ、リアルタイム分析、Kubernetesクラスタでのマイクロサービス実行など、汎用的なメモリ集約型ワークロードに最適です。対応するプログラミング言語も豊富で、Python、Java、Go、Rust、Node.jsなどが動作します。

一方、R9gdインスタンスはローカルNVMe SSDストレージを搭載しており、オープンソースデータベース（Cassandra、MongoDB、PostgreSQL）や大規模インメモリデータベースなど、ローカルストレージを必要とするワークロードに適しています。高速なローカルストレージにより、一時データの読み書きやキャッシュ層として利用でき、EBSボリュームへのネットワークトラフィックを削減できます。

**セキュリティ強化：Nitro Isolation Engine**

R9g/R9gdは第6世代AWS Nitro Systemを搭載し、新機能のNitro Isolation Engineを導入しています。この機能は数学的証明により分離保証を提供するもので、マルチテナント環境におけるセキュリティをさらに強化します。金融機関やヘルスケア分野など、高度なセキュリティ要件が求められる業界での採用が期待されます。

## SRE視点での活用ポイント

### ネットワーク分離とガバナンス強化の実践

Redshift EVRとIAM Identity Center統合は、ゼロトラストアーキテクチャの実装において重要な一歩となります。Terraformでインフラを管理している環境であれば、VPCエンドポイントとセキュリティグループの設定をコード化し、すべてのデータアクセスをVPC内に閉じ込める設計を標準化できます。

特に、VPC Flow Logsと組み合わせることで、誰がいつどの経路でRedshiftにアクセスしたかを継続的に監視できます。CloudWatch Logsに集約したフローログをAthenaでクエリし、異常なアクセスパターンを検出するランブックを整備すれば、インシデント対応時間を大幅に短縮できます。

導入時の注意点として、PrivateLinkインターフェースエンドポイントの作成にはENIが必要であり、サブネットのIPアドレス枯渇に注意が必要です。また、EVR有効化により既存のデータロードパイプラインが影響を受ける可能性があるため、段階的な移行とテストが推奨されます。

### Lambda再帰ループ検出による予防的運用

Lambda再帰ループ検出は、特にイベント駆動アーキテクチャにおける防御的なプラクティスとして価値があります。CloudWatch Alarmsと組み合わせて、AWS Health Dashboard通知をSlackやPagerDutyにルーティングすれば、再帰ループ発生時の即座なアラートが可能になります。

既存のLambda関数に対しては、どの関数がS3、SQS、SNSと相互作用しているかを棚卸しし、意図しないループの可能性がないか検証することが推奨されます。特に、複数チームが独立してLambda関数を開発している場合、チーム間の依存関係が可視化されていないことが多く、潜在的なリスクとなります。

PutFunctionRecursionConfig APIを使って検出機能を無効化する場合は、その理由と承認プロセスをドキュメント化し、定期的なレビューの対象とすることが重要です。意図的な再帰処理であっても、終了条件の実装ミスやリソース制限の見落としがないか、コードレビューで確認すべきです。

### Graviton5 インスタンスへの移行計画

R9g/R9gdインスタンスは、特にコスト最適化とパフォーマンス向上の両立が求められる環境で検討価値があります。既存のx86ベースのR7iやR6iからの移行では、アプリケーションがArm64アーキテクチャに対応しているか確認が必要です。幸い、PostgreSQL、MySQL、Redis、Elasticsearchなど主要なオープンソースソフトウェアはすでにArm64対応しています。

移行時のリスクを低減するには、まず開発環境でR9gインスタンスを起動し、アプリケーションの動作とパフォーマンスベンチマークを実施します。その後、Blue/Greenデプロイメントやカナリアリリースの手法で、段階的に本番トラフィックを新インスタンスに移行するアプローチが安全です。

Reserved InstancesやSavings Plansの契約がある場合、既存のコミットメントとの兼ね合いを考慮する必要があります。コスト分析ツール（AWS Cost ExplorerやAWS Compute Optimizer）を活用し、移行によるコスト削減効果を定量的に評価した上で、経営層への提案資料を作成することが推奨されます。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| Amazon Redshift | IAM Identity Center認証が強化VPCルーティング（EVR）に対応。すべてのトラフィックがVPC内に留まり、PrivateLinkインターフェースエンドポイント経由で認証を実施 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-redshift-supports-idc-evr>) |
| AWS Lambda | 再帰ループ検出機能が全商用リージョンで利用可能に。デフォルトで有効化され、S3、SQS、SNSなどのイベントソースとの間の再帰呼び出しを自動検出・停止 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/lambda-recursion-regions>) |
| Amazon EC2 | Graviton5プロセッサ搭載のR9g/R9gdメモリ最適化インスタンスが一般提供開始。前世代比で最大25%のコンピュート性能向上、データベースで最大30%、ウェブアプリで最大35%高速化 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ec2-r9g-and-r9gd-memory-optimized-instances-are-now-available/>) |
| Amazon Timestream for InfluxDB | 8つの新リージョン（ケープタウン、バンコク、香港、ハイデラバード、メルボルン、ソウル、チューリッヒ、テルアビブ）で利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-timestream-influxdb-regions/>) |
| AWS Interconnect | Microsoft Azureとのマルチクラウド接続を実現する新サービスのパブリックプレビュー開始。業界標準フレームワークでAzure、OCI、Google Cloudに対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-announces-AWS-interconnect-multicloud-microsoft-azure-preview/>) |
| AWS Agent Registry | AIエージェント・ツール・リソースを一元管理できるレジストリが一般提供開始。CloudFormation・Terraform・CDK対応、AWS RAM組織間共有、AgentCore自動検出機能を実装 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-agent-registry-generally-available>) |
| Automated Security Response on AWS (ASR) | AI駆動のRemediationツールキットを追加。Amazon Inspector、GuardDuty、Macieの検出結果を自動修復し、Email・Slack・Jira・ServiceNowで通知可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/automated-security-response-adds-AI-toolkit/>) |
| Amazon Cognito | GetClientToken API操作を追加。ユーザープールドメイン設定なしでマシン間（M2M）認可用アクセストークンを直接取得可能に。AWS WAFとPrivateLink対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-cognito-get-client-token/>) |
| Amazon Redshift | Apache Iceberg v3テーブルの読み書きに対応。デフォルト列値、行系統追跡、削除ベクトルをサポートし、スキーマ進化と高頻度更新ワークロードを改善 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-redshift-supports-apache-iceberg-v3>) |
| AWS Elastic Beanstalk | Windows Server環境でActive Directoryドメイン参加を自動化。カスタムスクリプト不要で、設定オプションのみでドメイン統合を実現 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/elastic-beanstalk-active-directory-domain-join/>) |
| Amazon OpenSearch Service | Cluster Insightsに17個の新インサイトを追加。Red/Yellowステータス時に根本原因を自動特定し、解決策を即座に提案 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/opensearch-cluster-status-insight/>) |

## まとめ

今回のアップデート群は、セキュリティ、ガバナンス、パフォーマンス、運用効率という、エンタープライズ環境における4つの重要な柱を強化するものです。

特にネットワーク分離とアイデンティティ管理の統合（Redshift EVRとIAM Identity Center）、予防的な自動保護機能（Lambda再帰ループ検出）、そしてAIエージェントの統一管理（AWS Agent Registry）は、現代のクラウドアーキテクチャにおける重要なトレンドを反映しています。

Graviton5世代のR9g/R9gdインスタンスは、Armアーキテクチャの成熟を示すとともに、コスト効率とパフォーマンスの両立という現実的な課題への回答となっています。また、AWS Interconnectによるマルチクラウドネイティブなアプローチは、今後のハイブリッド・マルチクラウド戦略において重要な選択肢となるでしょう。

これらのアップデートを活用することで、より安全で、効率的で、管理しやすいクラウドインフラを構築できます。特にSREやプラットフォームエンジニアリングチームにとって、これらの機能を組み合わせることで、運用の自動化と標準化を大きく前進させることができるはずです。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)