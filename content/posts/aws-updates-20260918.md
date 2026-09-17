---
title: "【AWS】2026/09/18 のアップデートまとめ"
date: 2026-09-18T08:02:31+09:00
draft: false
tags: ["aws", "ec2", "elastic-beanstalk", "eks", "transfer-family", "keyspaces", "healthomics", "batch", "connect", "ecs", "corretto", "sagemaker"]
categories: ["AWS Updates"]
summary: "2026/09/18 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260918/header.png)

# 直近のAWSアップデート11件を紹介 - EC2 T8iインスタンス、Elastic Beanstalk Cluster Mode、AWS Batch一括操作ほか

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。特に注目すべきは、コスト効率を大幅に向上させる **Amazon EC2 T8iインスタンス** の一般提供開始と、複数アプリケーションの運用効率を革新する **AWS Elastic Beanstalk Cluster Mode** の登場です。また、大規模バッチ処理の運用性を向上させる **AWS Batchの一括ジョブ操作機能**、インフラ運用の可視性を高める **Amazon ECS Managed Daemonsのデプロイメント可視化**、そしてセキュリティ強化と最新機能を盛り込んだ **Amazon Corretto 27** など、SRE視点で見逃せないアップデートが揃っています。さらに、AWS Transfer FamilyのソースIP保持機能やAmazon Keyspacesのリージョン拡大など、運用の柔軟性とコンプライアンス対応を強化するアップデートも含まれています。

## 注目アップデート深掘り

### Amazon EC2 T8iインスタンス - バースト型の新世代

AWSは低コストなバースト型の新インスタンスファミリー **T8i** の一般提供を開始しました。T8iはAWS専用のインテル Xeon 6 プロセッサ（第6世代）と最新のAWS Nitro カード（第6世代）を採用し、前世代の T3 と比較して最大30%優れた価格性能比を実現します。

**なぜT8iが重要なのか**

バースト型インスタンスは、低～中程度のCPU使用率で動作するワークロードに最適化されており、スタートアップやSMB、開発環境で広く採用されています。T8iは、T3比で最大70%の計算性能向上、1.25倍のネットワーク帯域幅、2.4倍のEBS帯域幅を提供します。T3と同じCPUクレジットシステム（Standard/Unlimitedモード）に対応しているため、クレジットの運用モデルを変えずに移行できます。

**提供サイズと適用ワークロード**

T8iは4つのサイズ（nano、micro、small、medium）で提供され、以下のようなワークロードに最適です：

- データ処理やバッチ処理
- ログインゲートウェイ
- 小規模データベース
- CI/CDパイプラインの実行環境
- マイクロサービスやイベント駆動型関数
- 低～中トラフィックのWebサイト

**移行の考慮点**

T3 と同じ Standard / Unlimited の CPU クレジットモードに対応しているため、クレジット設計を見直さずに移行できます。提供リージョンは米国・欧州・アジアパシフィック・カナダの各リージョンで、T8i.micro と T8i.small は AWS 無料利用枠の対象です。

### AWS Elastic Beanstalk Cluster Mode - 共有インフラでの効率的な複数アプリ運用

AWS Elastic Beanstalkに **Cluster Mode** という新しいデプロイメントモードが追加されました。これは、複数のアプリケーションを共有インフラ上で動作させることができる革新的な機能です。

**従来のStandard Modeとの違い**

従来のElastic Beanstalkは「1アプリケーション = 1専用環境」という構成でした。つまり、アプリケーションごとに専用のEC2インスタンスやロードバランサーがプロビジョニングされ、リソース利用効率の面で課題がありました。Cluster Modeでは、内部的にAmazon EKSを活用し、複数のアプリケーションが同じインフラリソースを共有しながら動作します。これにより、小～中規模のアプリケーションを多数運用する場合のコスト削減と管理の簡素化が実現します。

**技術的な基盤とエンタープライズ機能**

Cluster Modeは内部的にEKSを活用していますが、ユーザーはKubernetesの複雑な設定を意識する必要がありません。ソースコード、Dockerfile、またはAmazon ECRのコンテナイメージを提供するだけで、Elastic Beanstalkがコンテナ化、プロビジョニング、運用管理をすべて自動で行います。

以下のエンタープライズ機能が標準装備されています：

- **イベント駆動オートスケーリング**: トラフィックパターンに応じた自動スケール
- **OpenTelemetryベースの可観測性**: CloudWatch およびサードパーティのプロバイダーへ観測データを送信
- **AWS Secrets Manager統合**: シークレット情報の安全な管理
- **デフォルトHTTPS対応**: AWS Certificate Manager 経由で HTTPS が初期設定で有効

**CI/CD統合の簡素化**

新しい Elastic Beanstalk GitHub Action により、CI/CD パイプラインの一部としてリポジトリから直接アプリケーションをデプロイできます。

**コスト面でのメリット**

Cluster Mode 自体に追加料金はかからず、アプリケーションが消費する AWS リソースの料金が課金されます。課金対象には EKS クラスターと EKS Auto Mode の料金が含まれるため、Standard Mode との比較では共有クラスターの固定費も含めて見積もってください。

既存のStandard Modeは継続してサポートされるため、.NET、Node.js、Pythonなどの既存アプリケーションはそのまま稼働し続けることができます。Elastic Beanstalk が提供されている全ての商用 AWS リージョンで利用できます。

### AWS Batch 一括ジョブ操作 - 大規模ワークロードの運用効率化

AWS Batchに一括ジョブキャンセル・終了機能が追加されました。これにより、最大50個のジョブを1回のAPI呼び出しで一括操作できるようになり、大規模なバッチワークロード管理の複雑性が大幅に軽減されます。

**新しいAPIとその機能**

導入された新しいAPIは以下の3つです：

- **CancelJobs**: 複数のジョブを一括でキャンセル
- **TerminateJobs**: 複数のジョブを一括で終了
- **TerminateServiceJobs**: サービスジョブの一括終了

従来は、1つのジョブをキャンセル・終了するたびにAPI呼び出しが必要でしたが、新しいAPIでは最大50個のジョブを1回の呼び出しで処理し、ジョブごとの結果を1つのレスポンスで受け取れます。対象の状態は API ごとに異なり、CancelJobs は SUBMITTED / PENDING / RUNNABLE のジョブ、TerminateJobs は STARTING や RUNNING を含む任意の状態のジョブ、TerminateServiceJobs は任意の状態のサービスジョブが対象です。

**ジョブ状態追跡の改善**

`ListJobs` APIに `isCancelled` と `isTerminated` フィールドが追加され、`ListServiceJobs` には `isTerminated` が追加されることで、ジョブのライフサイクル状態をより詳細に追跡できるようになりました。これにより、ジョブがキャンセルされたのか終了されたのかを一覧から判別できます。

**運用シナリオでの活用**

この機能が特に有効なシナリオは以下の通りです：

- 機械学習のトレーニングジョブが失敗した際の関連ジョブ群の一括リソース解放
- スケジュール変更やビジネス要件の変化による複数ジョブの迅速なキャンセル
- マルチテナント環境でテナント削除時に関連するすべてのバッチジョブを一括終了
- コスト最適化のため、不要な長時間実行ジョブを一度に停止
- エラーハンドリング時に依存ジョブ群を一括キャンセルし、ワークフロー内の連鎖失敗を防止

新しい API は AWS CLI と各言語の SDK から呼び出せ、個別ジョブと配列ジョブの双方に対応します。AWS Batch が利用できる全てのリージョンで提供されています。

## SRE視点での活用ポイント

### コスト最適化とリソース効率

T8iインスタンスは、開発環境やステージング環境の段階的な刷新に最適です。Terraformで管理しているインフラがあれば、`instance_type` パラメータを `t3.micro` から `t8i.micro` に変更するだけで、計算性能とネットワーク帯域の向上と同時にコスト削減が実現できます。特に、CI/CDパイプラインの実行環境やテスト用データベースなど、24時間稼働しているが実際の負荷は低い環境での効果が大きくなります。

Elastic Beanstalk Cluster Modeは、マイクロサービスアーキテクチャを採用している場合に大きな価値を発揮します。10個の小規模マイクロサービスをそれぞれStandard Modeで運用すると、10セットのロードバランサーとEC2インスタンスが必要ですが、Cluster Modeでは共有インフラ上に集約できるため、ロードバランサーコストと最小限のEC2台数で運用可能です。ただし、リソース競合やノイジーネイバー問題のリスクもあるため、本番環境への導入前にステージング環境で負荷テストを実施し、アプリケーション間のリソース分離が適切に機能することを確認する必要があります。

### 運用自動化と可観測性

AWS Batchの一括操作機能は、障害対応のランブックに組み込むことで威力を発揮します。例えば、上流システムの障害を検知した際に、CloudWatch Alarmと連携して関連するすべての下流バッチジョブを自動的にキャンセルするLambda関数を実装することで、無駄なリソース消費を防ぎつつ、復旧後の再実行も容易になります。`isCancelled` および `isTerminated` フィールドを活用すれば、ジョブの終了理由をログに記録し、SLI/SLOのメトリクスとして集計することも可能です。

Amazon ECS Managed Daemons のデプロイメント可視化は、デーモン更新の状況をコンソールで追えるようにします。各ステップのタイムスタンプと総所要時間を示すライフサイクルタイムライン、キャパシティプロバイダーごとの進捗バー、デプロイメントサーキットブレーカー・デプロイメントアラーム・コンテナヘルスチェックの状態、そして停止理由とタスク・ログ・該当するトラブルシューティングガイドへのリンクが1つのビューにまとまります。停止したデプロイの原因調査で、参照先を探す手間が減ります。

### セキュリティとコンプライアンス

AWS Transfer FamilyのソースIP保持機能は、IP ベースのアクセス制御ポリシーを運用している環境で重要です。NLB背後にSFTPサーバーを配置する冗長構成でも、Proxy Protocol v2（PPv2）を有効化することで、クライアントの実際のIPアドレスをログ、イベント、カスタム認証プロバイダーに伝達できます。これにより、IPベースの監査とアクセス制御に必要な正確な記録を残せます。カスタム認証プロバイダー（Lambda関数など）でソースIPを活用した認証ロジックを実装する際は、VPC Flow LogsやCloudTrailと連携してログの整合性を確認し、セキュリティインシデント発生時の調査精度を高めることが推奨されます。

AWS HealthOmicsのIAMセッションポリシー対応は、マルチテナントSaaSを構築する際の権限管理を大幅に簡素化します。従来はテナントごとにIAMロールを作成する必要がありましたが、セッションポリシーを使用することで、基本的なIDベースポリシーと一時的なセッションポリシーの交集合で権限を制限できます。ただし、セッションポリシーは一時的な権限縮小のみを目的としており、基本ポリシーにない権限を付与することはできない点に注意が必要です。導入時は、最小権限の原則に基づいて基本ポリシーを設計し、セッションポリシーでテナントごとのS3バケットアクセスなど、実行単位での制限を実装する設計が推奨されます。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [AWS Builder Center now available as mobile app on iOS and Android](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-builder-center-now-available-as-mobile-app/) | AWS Builder CenterがiOSおよびAndroidのモバイルアプリとして利用可能になりました。 |
| 2 | [Introducing Amazon EC2 T8i instances](https://aws.amazon.com/about-aws/whats-new/2026/09/ec2-t8i-instances-ga/) | AWS専用のインテル Xeon 6プロセッサと最新AWS Nitroカード（第6世代）を採用した低コストバースト型インスタンス。T3比で最大30%優れた価格性能比、最大70%の計算性能向上、1.25倍のネットワーク帯域幅、2.4倍のEBS帯域幅を提供。4サイズ（nano、micro、small、medium）で提供。 |
| 3 | [AWS Elastic Beanstalk introduces Cluster Mode to run multiple applications on shared infrastructure](https://aws.amazon.com/about-aws/whats-new/2026/09/elastic-beanstalk-cluster-mode/) | 複数のアプリケーションを共有インフラ（EKS基盤）上で動作させる新モード。イベント駆動オートスケーリング、OpenTelemetry可観測性、Secrets Manager統合、デフォルトHTTPSに対応。追加料金なし。 |
| 4 | [AWS Transfer Family now supports source IP preservation for SFTP servers behind a Network Load Balancer (NLB)](https://aws.amazon.com/about-aws/whats-new/2026/09/transfer-family-sftp-source-ip-nlb/) | NLB経由のSFTPサーバーにおいて、Proxy Protocol v2を使用してクライアントのソースIPアドレスを保持。ログ、イベント、カスタム認証プロバイダーに記録・伝達され、IPベースの監査・アクセス制御に対応。 |
| 5 | [Amazon Keyspaces (for Apache Cassandra) is now generally available in 11 additional Regions](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-keyspaces/) | Amazon Keyspacesが11の新リージョンで一般提供開始。Cassandra互換アプリケーションを低レイテンシーで構築でき、データレジデンシー要件に対応。サーバーレス型で使用リソース分のみ課金。 |
| 6 | [AWS HealthOmics now supports IAM session policies](https://aws.amazon.com/about-aws/whats-new/2026/09/omics-iam-session-policy/) | IAMセッションポリシーに対応し、複数のIAMロールを作成せずに、個別の実行（run）に対して権限を動的に制限可能。マルチテナント環境や機密リソースへのアクセス制御を実行単位で実現。 |
| 7 | [AWS Batch now supports bulk job cancellation and termination](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-batch-bulk-cancellation/) | 最大50個のジョブを1回のAPI呼び出しで一括キャンセル・終了可能。新API（CancelJobs、TerminateJobs、TerminateServiceJobs）により大規模バッチワークロード管理が簡素化。ListJobsにisCancelled/isTerminatedフィールド追加。 |
| 8 | [Amazon Connect Talent is now generally available](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-connect-talent/) | Amazonの採用科学に基づくAI駆動型採用ソリューション。AIエージェントが構造化音声面接、適性検査、候補者スコアリングを自動化。24/7面接対応、数百の候補者同時評価が可能。US East (N. Virginia)およびUS West (Oregon)で提供。 |
| 9 | [Amazon ECS deployment observability for Amazon ECS Managed Daemons in AWS Management Console](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ecs-daemon-deployment-console/) | ECS Managed Daemonsのデプロイメント可視化機能を追加。ライフサイクルタイムライン、キャパシティプロバイダーごとの進捗バー、サーキットブレーカー・アラーム・ヘルスチェック状態、停止理由とトラブルシューティングガイドへのリンクを統合ビューで提供。 |
| 10 | [Amazon Corretto 27 is now generally available](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-corretto-27-generally-available/) | Amazon Corretto 27が正式版として利用可能。メモリ効率向上、量子コンピュータ対策、GC改善、セキュリティ強化、開発体験向上を含む。Linux、Windows、macOSで利用可能。2027年4月までサポート。 |
| 11 | [Amazon SageMaker AI now supports serverless model customization for NVIDIA Nemotron 3.5 Lightning](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-sagemaker-ft-nemotron-3-5-lightning/) | SageMaker AIがNVIDIA Nemotron 3.5 Lightning（3Bアクティブパラメータ、合計30BパラメータのハイブリッドMoE）のサーバーレスカスタマイズに対応。SFT、DPO、RFTの3手法で独自データによるモデルカスタマイズが可能。 |

## まとめ

今回紹介した11件のアップデートは、コスト最適化、運用効率化、セキュリティ強化という3つの軸で整理できます。EC2 T8iインスタンスやElastic Beanstalk Cluster Modeは、既存ワークロードのコスト構造を見直す良い機会を提供しています。AWS Batchの一括操作機能やECS Managed Daemonsの可視化は、大規模システムの運用性を着実に改善します。また、Transfer FamilyのソースIP保持やHealthOmicsのセッションポリシー対応は、コンプライアンスとセキュリティ要件への対応力を高めます。

特にSREの視点では、T8iへの段階的移行によるコスト削減と性能向上の両立、Cluster Modeによるマイクロサービス運用の簡素化、AWS Batchの一括操作によるランブック自動化の強化など、具体的な改善アクションに直結するアップデートが多く含まれています。Corretto 27のような基盤技術のアップデートも、長期的な運用安定性とセキュリティ対策の観点で重要です。

新しいリージョン展開（Amazon Keyspaces）やAI/ML基盤の強化（SageMaker AI、Amazon Connect Talent）も含め、AWSは幅広い領域で継続的な改善を続けています。まずは T8i への切り替え候補の洗い出しと、AWS Batch の一括キャンセルをランブックへ組み込むところから着手してください。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)