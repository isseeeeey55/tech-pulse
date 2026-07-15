---
title: "【AWS】2026/07/15 のアップデートまとめ"
date: 2026-07-15T08:02:02+09:00
draft: false
tags: ["aws", "flink", "drs", "ec2", "ebs", "iam-identity-center", "aurora", "guardduty", "bedrock", "sagemaker", "security-hub", "workspaces", "storage-gateway", "cloudfront", "documentdb", "managed-service-for-prometheus", "s3", "cloudtrail", "organizations"]
categories: ["AWS Updates"]
summary: "2026/07/15 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260715/header.png)

# 直近の AWS アップデート情報まとめ（2026年7月）

## はじめに

今回は、直近で発表された **13件** の AWS アップデートを紹介します。特に注目すべきは、AI/ML ワークロード向けのセキュリティ強化、ディザスタリカバリーの高速化、そして OpenAI の最新モデル GPT-5.6 ファミリーの Bedrock 対応です。AWS が AI セキュリティとオブザーバビリティに力を入れている動向が顕著に表れており、Amazon GuardDuty と Security Hub に新たに AI 特化型の機能が追加されました。また、AWS Elastic Disaster Recovery (DRS) の復旧時間短縮や、CloudFront Functions のロギング機能強化など、運用面での改善も多数含まれています。

---

## 注目アップデート深掘り

### 1. AWS Elastic Disaster Recovery による AWS-to-AWS ワークロードの復旧時間短縮

AWS Elastic Disaster Recovery (AWS DRS) に、AWS 上で既に実行されている EC2 ワークロードの復旧を高速化する新機能が追加されました。この機能により、**Windows で最大 65%、Linux で最大 40% の復旧時間短縮**が実現されています。

#### なぜこのアップデートが重要なのか

従来、AWS DRS は主にオンプレミスから AWS への DR ソリューションとして利用されてきましたが、AWS 上で既に実行されているワークロードを別リージョンやアカウントへレプリケートする "AWS-to-AWS" の DR シナリオも増加しています。しかし、既に AWS 環境で動作しているワークロードは、AWS 互換のドライバーや設定を備えているにもかかわらず、これまでは復旧時に不要な準備ステップを実行していました。

今回のアップデートでは、Amazon EC2 上で稼働するソースサーバーについて、これらのワークロードに不要となった準備ステップをスキップすることで、復旧を高速化しています。

#### 高速復旧の仕組みと設定方法

AWS DRS の高速復旧機能は、ソースサーバーが既に AWS EC2 上で動作している場合に自動的に適用可能になります。設定は **アカウント全体** または **個別サーバー単位** で有効化でき、必要に応じていつでも切り替えられる柔軟な設計になっています。

高速化のポイントは以下のとおりです：

- **不要な準備ステップのスキップ**: AWS 上で稼働するワークロードは AWS 互換のドライバーと設定を既に備えているため、より少ないステップで起動できます
- **自動適用は維持**: ネットワーク、ドライバー、ライセンスは引き続き自動的に適用されるため、復旧はシンプルかつハンズオフのままです
- **柔軟な切り替え**: 設定はアカウント全体または個別サーバー単位で有効化でき、必要に応じていつでも変更できます

この最適化により、アプリケーションをより早くオンラインに戻すことができます。

#### 従来の方法との比較

従来の AMI ベースの DR 戦略と比較すると、AWS DRS の高速復旧には以下のような利点があります：

- **継続的なレプリケーション**: AMI スナップショットは定期的な取得が必要ですが、DRS は継続的にデータをレプリケートするため RPO（目標復旧時点）が短い
- **自動化された復旧フロー**: 復旧時の手動操作が最小限で済み、オペレーションミスのリスクが低減
- **コスト効率**: 追加費用なしでこの高速化機能を利用可能

---

### 2. Amazon GuardDuty AI Protection による AI ワークロードの脅威検知

Amazon GuardDuty に **AI Protection** という新機能が追加され、Amazon Bedrock や Amazon SageMaker などの AWS AI サービスを対象とした脅威検知が可能になりました。

#### AI ワークロード特有のセキュリティ課題

組織が生成 AI や機械学習を急速に導入する中で、セキュリティチームは AI ワークロード特有の脅威に対する可視性を欠いていることが課題となっています。告知では以下の脅威が挙げられています：

- **異常なモデル呼び出し（anomalous model invocations）**: 通常の利用パターンから逸脱したモデル呼び出し
- **コスト搾取攻撃（cost harvesting attacks）**: GPU 時間やトークンを過剰に消費させる攻撃
- **プロンプトインジェクションの試行（prompt injection attempts）**

これらは従来の Web アプリケーションやデータベースに対する攻撃とは異なる特性を持ち、専用の検知ロジックが必要です。

#### GuardDuty AI Protection の動作原理

GuardDuty AI Protection は **CloudTrail の管理イベントとデータイベントを分析** し、疑わしい活動を自動検知します。手動設定やカスタムツールは不要で、Amazon Bedrock と Amazon SageMaker を対象に、前述の異常なモデル呼び出し・コスト搾取攻撃・プロンプトインジェクションの試行を検知します。

検出された脅威は **AWS Security Hub に直接連携**され、他のセキュリティイベントと一元的に管理・対応できます。

#### セットアップと運用

GuardDuty AI Protection の有効化は、GuardDuty または Security Hub のコンソール内で数ステップで完了します。AWS Organizations を利用している場合、組織全体の複数アカウントで一括有効化することも可能です。

GuardDuty 利用者向けに **30 日間の無料トライアル**が提供されているため、まずは検証環境で実際の検知動作を確認することをおすすめします。トライアル期間中に、以下のような検証シナリオを試すと効果的です：

- Bedrock または SageMaker への API 呼び出しパターンの記録
- 意図的に異常なアクセスパターンを発生させ、検知精度を確認
- Security Hub でのアラート表示内容とトリアージフローの確認

---

## SRE 視点での活用ポイント

### ディザスタリカバリー戦略の見直し

AWS DRS の高速復旧機能は、**AWS 内でのマルチリージョン DR 戦略**を採用している環境で特に有効です。SRE チームは以下のような観点で活用を検討できます：

- **定期的な DR ドリル**: 復旧時間が短縮されることで、より頻繁に DR 訓練を実施しやすくなり、復旧手順の確実性が向上します
- **RTO の再定義**: 従来の RTO 目標が達成困難だった場合、この機能により目標値を短縮できる可能性があります
- **コスト最適化**: 追加費用なしで復旧時間が短縮されるため、費用対効果が高い改善施策として位置づけられます

ただし、高速復旧を有効化する際は、**サーバーごとの復旧要件を精査**することが重要です。例えば、ステートレスな Web サーバーと、ステートフルなデータベースサーバーでは復旧手順が異なる場合があるため、個別サーバー単位での設定変更も検討する価値があります。

### AI ワークロードのセキュリティ監視

GuardDuty AI Protection は、**AI/ML パイプラインを本番環境で運用している SRE チーム**にとって重要な監視ツールになります。特に以下のようなシナリオで活用できます：

- **コスト異常の早期発見**: AI サービスは従量課金モデルのため、攻撃による過剰利用を早期に検知することで予期しないコスト増加を防げます
- **CloudWatch アラームとの統合**: Security Hub との連携により、既存のアラート基盤（Amazon EventBridge、SNS、PagerDuty など）に GuardDuty の検知イベントを組み込むことが可能です
- **インシデント対応ランブックの整備**: AI 特有の脅威に対する対応手順を事前に準備し、検知時の初動を迅速化できます

導入時の注意点として、**誤検知（false positive）の可能性**を考慮する必要があります。例えば、バッチ処理による大量の推論リクエストが正当なものであっても、異常として検知される場合があります。トライアル期間中に正常な利用パターンを記録し、必要に応じて検知ルールの調整を行うことが推奨されます。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [Amazon Managed Service for Apache Flink now offers AI Agent Skills](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-managed-service-flink-agent-skills/) | Apache Flink アプリケーションの構築・運用を簡素化する AI Agent Skills を提供開始 |
| 2 | [AWS Elastic Disaster Recovery reduces recovery time for AWS-to-AWS workloads](https://docs.aws.amazon.com/drs/) | AWS EC2 ベースのワークロード復旧を高速化。Windows で最大 65%、Linux で最大 40% の復旧時間短縮（告知ページが未公開のため公式ドキュメントへリンク） |
| 3 | [AWS Elastic Disaster Recovery now supports Amazon EBS volume initialization rate](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-drs-fast-hydration/) | EBS ボリューム初期化レート機能をサポート。スナップショット復旧後のフルパフォーマンス到達時間を短縮 |
| 4 | [AWS IAM Identity Center achieves FedRAMP Class C Certification](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-identity-center-fedramp/) | IAM Identity Center が FedRAMP Class C 認証を取得。米国政府機関向けアクセス管理が可能に |
| 5 | [Amazon Aurora DSQL is now available in Europe (Spain)](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-aurora-dsql-available-in-spain/) | Aurora DSQL がスペインリージョンで利用可能に。スペインを含む計 20 リージョンで展開 |
| 6 | [Introducing Amazon GuardDuty AI Protection for AWS AI workloads](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-guardduty-ai-protection-aws/) | Bedrock・SageMaker などの AI サービスを対象とした脅威検知機能を追加 |
| 7 | [AWS Security Hub now provides AI inventory for organization-wide visibility of AI assets](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-security-hub-ai/) | 組織全体の AI アセット（Bedrock、SageMaker、自己ホスト型 LLM など）を一元管理する AI インベントリ機能を追加 |
| 8 | [Amazon WorkSpaces Personal simplifies bulk PCoIP to DCV protocol migration](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-workspaces-personal-pcoip/) | WorkSpaces の PCoIP から DCV への大規模マイグレーション機能を強化。自動ロールバック機能と停止状態対応を追加 |
| 9 | [AWS Storage Gateway adds console support for copying file shares across gateways](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-storage-gateway-console-copy-file-shares/) | ファイル共有を異なるゲートウェイ間でコンソールからコピー可能に。AL2023 アップグレード時の設定移行が簡素化 |
| 10 | [Amazon CloudFront Functions now supports logging to CloudFront access logs](https://aws.amazon.com/about-aws/whats-new/2026/07/cloudfront-functions-access-logs/) | CloudFront Functions からカスタムデータを CloudFront アクセスログに直接書き込める `cf.logCustomData()` メソッドを追加 |
| 11 | [Amazon DocumentDB (with MongoDB compatibility) adds support for 46 new MongoDB operators in version 8.0.1](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-documentdb-mongodb-8-0-1-mongo-api) | DocumentDB 8.0.1 で 46 個の新しい MongoDB オペレーターとカーソルメソッドをサポート |
| 12 | [Amazon Managed Service for Prometheus is now available in Asia Pacific (New Zealand) Region](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-managed-service-prometheus-new-zealand/) | Managed Service for Prometheus がニュージーランドリージョンで利用可能に |
| 13 | [OpenAI GPT-5.6 Sol, Terra, and Luna now generally available on Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/07/openai-gpt-sol-terra/) | OpenAI の最新モデル GPT-5.6 ファミリー（Sol, Terra, Luna）が Bedrock で一般提供開始 |

---

## まとめ

今回のアップデートでは、**AI/ML ワークロードのセキュリティとオブザーバビリティの強化**が際立っています。GuardDuty AI Protection と Security Hub AI Inventory の追加により、AWS は AI サービスの脅威検知とアセット管理を統合的に提供する体制を整えました。生成 AI の急速な普及に伴い、セキュリティチームが直面する新たな課題に対応する姿勢が明確に示されています。

また、AWS DRS や CloudFront Functions のような運用効率化機能の改善も注目すべき点です。特に DRS の復旧時間短縮は、AWS 内でのマルチリージョン DR 戦略を採用している企業にとって、追加費用なしで RTO を改善できる重要なアップデートです。

リージョン拡大の動きも活発で、Aurora DSQL のスペイン対応や Managed Service for Prometheus のニュージーランド対応など、グローバル展開が進んでいます。これらのアップデートは、地理的に近いリージョンを選択することでレイテンシーを削減し、データレジデンシー要件に対応できる選択肢を広げています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)