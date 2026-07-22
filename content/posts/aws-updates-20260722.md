---
title: "【AWS】2026/07/22 のアップデートまとめ"
date: 2026-07-22T08:02:09+09:00
draft: false
tags: ["aws", "ec2", "ses", "rds", "sql-server", "prometheus", "ecs", "cloudwatch", "s3", "kinesis-data-firehose", "bedrock", "sagemaker", "lambda"]
categories: ["AWS Updates"]
summary: "2026/07/22 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260722/header.png)

# 直近の AWS アップデート情報まとめ（2026年7月）

## はじめに

今回は、直近で発表された 7 件の AWS アップデートを紹介します。Amazon EC2 の新世代ネットワーク最適化インスタンスの地域拡大、Amazon SES の新価格プラン導入、RDS for SQL Server の AI 統合機能を備えた 2025 バージョン対応、Amazon Managed Service for Prometheus の大規模スケール対応、そして Amazon ECS の新しい可観測性機能など、運用効率とパフォーマンスの向上に直結するアップデートが揃っています。特に ECS の Action Logs と RDS for SQL Server 2025 の AI 統合機能は、SRE の観点からも注目すべき内容です。

## 注目アップデート深掘り

### Amazon ECS Action Logs によるデプロイメント可視化の革新

Amazon ECS に新たに導入された **Action Logs** は、コンテナオーケストレーションの運用における長年の課題を解決する重要な機能です。これまで ECS のデプロイメントやタスクの起動・停止において、AWS 側で何が起きているのかを把握するには、複数のログソース（CloudTrail、タスクイベント、コンテナログなど）を手動で突き合わせる必要がありました。特に深夜の障害対応時や、複雑なローリングデプロイメント中のトラブルシューティングでは、この可視性の欠如が平均復旧時間（MTTR）の増大につながっていました。

Action Logs は、サービスデプロイメントと ECS Managed Daemon の更新時に、**ECS が実行するすべてのアクションを時系列で記録**します。各ログエントリには、タイムスタンプ、イベント名、ログレベル（INFO、WARN、ERROR）、関連リソースの ARN、そしてステータス理由が含まれます。告知はこれらを「これまで見えなかったサービス側の操作」と表現しており、サービスデプロイと Managed Daemon 更新における主要なデプロイ状態遷移が記録対象です。

この機能はクラスタレベルでオプトインする形式で、Amazon ECS コンソールまたは Amazon CloudWatch の vended logs API から有効化できます。ログの配信先は **CloudWatch Logs、Amazon S3、Amazon Kinesis Data Firehose** の 3 つから選択可能です。CloudWatch Logs に配信すれば Logs Insights でクエリ分析ができますし、S3 への長期保存はコンプライアンス要件に対応できます。Kinesis Data Firehose 経由であれば、リアルタイムのストリーミング処理や外部 SIEM への連携も実現できます。

さらに注目すべきは、**Amazon Q との統合**です。ECS コンソール内の Amazon Q が Action Logs を解析し、サーキットブレーカーによるロールバックや不安定なサービスリビジョンなどのデプロイメント問題を自動検出します。根本原因の分析とリメディエーション方法まで提示されるため、経験の浅いエンジニアでも迅速に対応できるようになります。

なお料金については、告知は「ログの取り込みと保存には CloudWatch Logs、Amazon S3、Amazon Data Firehose の標準料金が適用される」と述べています。Action Logs 自体の追加料金ではなく、配信先サービスの標準課金が発生する点を前提に配信先を選ぶ必要があります。

### RDS for SQL Server 2025 の AI 統合による新しいデータベースアーキテクチャ

Amazon RDS for SQL Server が Microsoft SQL Server 2025 に対応したことで、データベース層から直接 AI サービスを呼び出す新しいアーキテクチャパターンが実現可能になりました。SQL Server 2025 の最大の特徴は、**T-SQL から REST エンドポイントを直接呼び出せる**機能です。これにより、Amazon Bedrock、Amazon SageMaker、AWS Lambda などの AWS サービスと、既存のデータベースワークロードをシームレスに統合できます。

従来、データベース内のデータを AI モデルで処理する場合、アプリケーション層で一度データを取得し、別途 API コールを行い、結果をデータベースに戻すという多段階のプロセスが必要でした。SQL Server 2025 では、ストアドプロシージャ内から直接 Bedrock の基盤モデルを呼び出して、クエリ最適化の提案を受けたり、自然言語でのデータ分析を実行したりできます。これは単なる利便性の向上ではなく、データの往復回数削減によるレイテンシ改善と、ビジネスロジックの一元管理というアーキテクチャ上の利点をもたらします。

もう一つの重要な機能強化が、**ネイティブベクトルデータ型のサポート**です。これまでベクトル埋め込みを SQL Server に保存する場合、NVARCHAR(max) や VARBINARY(max) を使い、アプリケーション側でシリアライズ・デシリアライズを行う必要がありました。告知は「ベクトル埋め込みをデータベース内で直接保存・クエリできる」ネイティブ型の追加としており、性能の改善幅は示していません。RAG（Retrieval-Augmented Generation）パターンを実装する際に、ベクトルの保存先として既存の SQL Server 環境を選択肢に入れられる点が変化になります。

開発・テスト環境向けには、新たに **Standard Developer Edition（Dev-SE）** が追加されました。告知はこれを「ライセンスコストなしで開発・テストに利用できる新しい無料エディション」と説明しており、本番移行前の検証環境をライセンス費用なしで用意できます。Standard Edition も機能強化されており、コア数上限が 32 コアに、バッファプール上限が 256 GB に拡大され、Resource Governor によるリソース制御も利用可能になっています。これまで Enterprise Edition でしか実現できなかったワークロードの一部が、Standard Edition でも対応可能になるため、コスト最適化の余地が広がります。

なお告知が挙げている呼び出し先は Amazon Bedrock、Amazon SageMaker、Amazon S3、AWS Lambda の 4 つで、「追加のミドルウェアなしに」外部 REST エンドポイントを呼べる点が要点です。具体的な構文や DDL の書き方は告知には含まれないため、実装にあたっては RDS および SQL Server 2025 の公式ドキュメントを確認してください。

## SRE 視点での活用ポイント

### ECS Action Logs の運用統合

SRE チームにとって、ECS Action Logs は MTTR 短縮の強力な武器になります。特に価値が高いのは、**デプロイメントパイプラインとの統合**です。CI/CD パイプライン（GitHub Actions、GitLab CI、Jenkins など）から ECS デプロイを実行する際、CloudWatch Logs Insights を使って Action Logs をリアルタイムで監視し、WARN や ERROR レベルのイベントが発生したらパイプラインを自動停止する仕組みを構築できます。

また、**ランブックの自動化**にも活用できます。サーキットブレーカーが作動したケースでは、Action Logs から直前のタスク定義変更を特定し、自動的に前回の安定版にロールバックするスクリプトを組み込めます。Amazon Q の根本原因分析結果を Slack や PagerDuty に通知する連携を追加すれば、オンコール対応の初動がさらに迅速化します。

長期的な運用改善の観点では、Action Logs を S3 に蓄積し、Amazon Athena でクエリして「どの時間帯にデプロイ失敗が多いか」「特定のサービスで繰り返される問題は何か」といった傾向分析を行うことで、予防保全的なアプローチが可能になります。

### RDS for SQL Server 2025 の段階的導入戦略

AI 統合機能は魅力的ですが、本番環境への導入には慎重な検証が必要です。まずは Dev-SE を使って開発環境で十分にテストし、特に REST エンドポイント呼び出し時のタイムアウト設定やエラーハンドリングを確認します。Bedrock や SageMaker のエンドポイントが一時的に利用できない場合のフォールバック処理を T-SQL 内に組み込んでおくことが重要です。

既存の SQL Server ワークロードを 2025 にアップグレードする際は、RDS の Blue/Green デプロイメント機能を使えば、新バージョンの環境を並行稼働させながら切り替えを検証できます。メジャーバージョンアップグレードにあたるため、既存のアプリケーションクエリやストアドプロシージャの互換性は、切り替え前に Blue 環境で実地に確認しておくのが確実です。

ベクトル検索を導入する場合、告知は性能値を示していないため、従来の NVARCHAR(max) 実装とネイティブベクトル型の両方で自環境のデータ量・次元数に基づくベンチマークを行い、改善幅を実測してから移行を判断するのが安全です。

### Amazon Managed Service for Prometheus の大規模監視基盤

15 億アクティブメトリクス時系列と 20 万ルール（記録・アラート合計）という新しい上限は、マルチテナント SaaS や大規模マイクロサービス環境を運用する SRE にとって大きな変化です。1アカウントで多数のワークスペースを作成できるため、**テナント分離**や**部門別の監視独立性**を確保しながら、組織全体で数十億規模のメトリクスを扱えます。

ただし、この規模になるとコストとクエリパフォーマンスのバランスが課題になります。高カーディナリティメトリクス（Kubernetes の Pod ラベルなど）を無制限に取り込むのではなく、**メトリクスリレーベリング**による不要ラベルの削除、**記録ルール**による事前集計、**サンプリング戦略**の導入などで、コストとクエリ速度を最適化します。

セルフホスト Prometheus からの移行を検討する場合、まず HA 構成の運用コスト（EC2 インスタンス、EBS、データ冗長化、バックアップ管理）と AMP の従量課金を比較します。メトリクス取り込み数とクエリ頻度に基づいた試算を行い、規模が大きいほど AMP の運用負荷削減効果が大きくなることを確認してから移行判断を下すのが賢明です。

## 全アップデート一覧

| タイトル | 概要 | リンク |
|---------|------|--------|
| Amazon EC2 C6in instances are now available in Asia Pacific (Taipei) Region | ネットワーク最適化インスタンス C6in が台北リージョンで利用可能に。最大 200Gbps のネットワーク帯域幅、100Gbps の EBS 帯域幅を提供。ネットワーク仮想アプライアンス、5G UPF、HPC、AI/ML ワークロードに最適 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-c6in/) |
| Amazon EC2 R6in and R6idn instances are now available in additional regions | メモリ最適化インスタンス R6in/R6idn がパリ・カナダ中部リージョンで利用可能に。最大 200Gbps ネットワーク帯域幅で、SQL/NoSQL データベース、分散キャッシュ、インメモリデータベース、ビッグデータ分析に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-r6in-r6idn/) |
| Amazon SES introduces pricing plans | SES に Essentials / Pro / Enterprise の3つの価格プランを導入。Essentials は配信可能性インサイト、Pro はマネージド専用 IP・メール検証・グローバル受信ボックス配置可視化、Enterprise はマルチリージョン耐性・ワークロード単位のレピュテーション分離・年次配信可能性評価を提供。上位プランほど個別課金より割引 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ses-pricing-plans/) |
| Amazon RDS for SQL Server now supports Microsoft SQL Server 2025 | RDS for SQL Server が SQL Server 2025 に対応。T-SQL から REST エンドポイント（Bedrock、SageMaker、Lambda など）を直接呼び出し可能に。ネイティブベクトルデータ型のサポート、Dev-SE の追加、Standard Edition の機能拡張を実現 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/rds-sqlserver-supports-sqlserver-2025) |
| Amazon RDS now supports the latest CU and GDR updates for Microsoft SQL Server | RDS for SQL Server が最新の累積更新（CU）および一般配布リリース（GDR）に対応。SQL Server 2016 SP3+GDR（KB5089271）、2017 CU31+GDR（KB5090354）、2019 CU32+GDR（KB5090407）、2022 CU25（KB5081477）をサポート。GDR 更新は CVE-2026-40370 に記載された脆弱性に対応（※AWS 告知ページの URL がリンク切れのため公式ドキュメントを掲載） | [詳細](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_SQLServer.html) |
| Amazon Managed Service for Prometheus supports 1.5B active metrics and 200K rules per workspace | AMP がワークスペースあたり最大 15 億アクティブメトリクス時系列と、記録・アラートルール合計 20 万をサポート。1アカウントで多数のワークスペースを作成でき、組織全体で数十億規模の Prometheus メトリクスを保存・分析可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-managed-service-prometheus-1500m-metrics-workspace/) |
| Amazon ECS now provides Action Logs for deployment and orchestration visibility | ECS に Action Logs 機能を追加。サービスデプロイと Managed Daemon 更新時の ECS 側アクションを時系列で記録し、CloudWatch Logs、S3、Kinesis Firehose に配信可能。Amazon Q 統合により自動問題検出と根本原因分析を提供 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ecs-action-logs/) |

## まとめ

今回のアップデートは、**可観測性の強化**と**新しいアーキテクチャパターンの実現**という 2 つの軸で整理できます。ECS Action Logs と AMP の大規模スケール対応は、複雑化するクラウドネイティブ環境での運用負荷削減に直結します。一方、RDS for SQL Server 2025 の AI 統合機能は、データベースを中心とした新しいアプリケーションアーキテクチャの可能性を示しています。

EC2 インスタンスの地域拡大や SES の価格プラン導入は、既存サービスの継続的な改善を示すもので、グローバル展開やコスト最適化を進める上で有用です。RDS のセキュリティパッチ対応は地味ながら重要で、コンプライアンス要件を満たすための迅速な対応を可能にします。

SRE の観点では、これらのアップデートを単独で見るのではなく、**既存の運用フローにどう組み込むか**という視点が重要です。ECS Action Logs はデプロイパイプラインと統合してこそ真価を発揮しますし、RDS 2025 の AI 機能も段階的な検証と導入計画があってこそ安全に活用できます。それぞれのアップデートについて、自組織の運用課題と照らし合わせながら、優先順位をつけて検証・導入を進めることをおすすめします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)