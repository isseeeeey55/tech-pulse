---
title: "【AWS】2026/08/01 のアップデートまとめ"
date: 2026-08-01T08:02:23+09:00
draft: true
tags: ["aws", "lambda", "rds", "aurora", "cloudwatch", "ec2", "codedeploy", "sagemaker", "eks", "ecs", "msk", "opensearch"]
categories: ["AWS Updates"]
summary: "2026/08/01 のAWSアップデートまとめ"
---

# 直近の AWS アップデート情報まとめ（2026年8月版）

## はじめに

今回は、直近で発表された8件のAWSアップデートを紹介します。Lambda の実行環境刷新、RDS for Oracle の最新インスタンスタイプへの Reserved Instances 対応、Aurora DSQL のマルチリージョン拡大、CloudWatch のマネージド Prometheus コレクター登場など、コンピュート・データベース・監視基盤の各分野で重要なアップデートが含まれています。特に注目したいのは、CloudWatch のマネージド Prometheus コレクターと Aurora DSQL のマルチリージョン対応です。前者は従来自前で構築・運用していた OpenTelemetry Collector の管理負担を完全に排除し、後者はグローバル展開企業のデータベース基盤に強い一貫性とアクティブ-アクティブ構成を提供します。以下、これらのアップデートを技術的に深掘りしていきます。

## 注目アップデート深掘り

### CloudWatch マネージド Prometheus コレクター：運用負担ゼロの統一監視基盤

Amazon CloudWatch が **マネージド Prometheus コレクター** のサポートを開始しました。これは、EKS・EC2・ECS・MSK・OpenSearch Service といった複数のワークロードから Prometheus メトリクスを収集する際に、エージェントのデプロイや管理を一切不要にする仕組みです。

#### なぜこのアップデートが重要なのか

従来、Prometheus メトリクスを収集するには OpenTelemetry Collector を自分で構築し、スケーリング・保守・トラブルシューティングを行う必要がありました。大規模な Kubernetes クラスタや複数の AWS サービスを監視する環境では、コレクターのキャパシティ管理やバージョンアップ、障害対応が運用チームの大きな負担となっていました。マネージド Prometheus コレクターはこの運用負担を完全に排除し、スクレイプ設定とリソース接続を指定するだけで、CloudWatch が自動的にプロビジョニング・スケーリング・収集を実行します。

#### 収集対象とサービスディスカバリー

マネージド Prometheus コレクターは以下のサービスディスカバリー方式に対応しています：

- **Kubernetes サービスディスカバリー（EKS）**：Pod や Node のメトリクスを自動的に検出・収集
- **DNS ベースのサービスディスカバリー（ECS via AWS Cloud Map）**：コンテナベースのマイクロサービス環境に対応
- **直接インスタンススクレイピング（EC2）**：従来のインスタンスベース監視をそのまま移行可能
- **オープン監視エンドポイント（MSK、OpenSearch）**：マネージドサービスの組み込みメトリクスエンドポイントを活用

#### 統一ダッシュボードと PromQL クエリ

収集されたメトリクスは OpenTelemetry 形式で提供され、PromQL を使用して AWS の標準メトリクスと一緒にクエリ可能です。EKS・MSK・OpenSearch のメトリクスについては、自動ダッシュボードが用意されており、PromQL クエリや CloudWatch アラームもすぐに利用できます。これにより、従来は分散していた監視データを統一ダッシュボード上で相関分析し、サービス間の関連付けも容易に行えるようになります。

#### 具体的な検証ポイント

公式ドキュメントを参照しながら、以下のステップで検証を進めることをお勧めします：

1. **EKS 環境での動作確認**：Kubernetes サービスディスカバリーで Pod・Node メトリクスが自動収集される様子を確認
2. **エージェントレス運用の実感**：従来の OpenTelemetry Collector デプロイと比較し、セットアップ時間や運用工数を測定
3. **PromQL クエリの動作検証**：自動ダッシュボードから PromQL を使った複雑なクエリを実行し、AWS 標準メトリクスとの統合を確認
4. **スケーラビリティテスト**：大規模 Kubernetes クラスタでメトリクス収集がどのように自動スケールするかを観察

エージェント管理の運用負担が完全になくなることで、SRE チームは監視基盤の保守から解放され、より本質的なシステム改善に集中できるようになります。

---

### Aurora DSQL マルチリージョン対応の拡大：グローバル展開の新選択肢

Amazon Aurora DSQL が **4つの追加リージョン** でマルチリージョンクラスタに対応しました。新たに対応したのは、ヨーロッパ（ストックホルム）、ヨーロッパ（スペイン）、アジアパシフィック（ムンバイ）、アジアパシフィック（シンガポール）です。これにより、マルチリージョンクラスタは合計16リージョンで利用可能となりました。

#### Aurora DSQL マルチリージョンクラスタの特徴

Aurora DSQL はサーバーレスで分散SQLデータベースであり、**アクティブ-アクティブな高可用性** と **マルチリージョン強い一貫性** を提供します。各マルチリージョンクラスタはピアリングされた両リージョンに書き込みエンドポイントを持ち、一つのリージョンが利用不可になっても可用性を維持する単一の論理データベースとして機能します。

従来の RDS クロスリージョンレプリケーションや DynamoDB グローバルテーブルと比較して、Aurora DSQL は **両リージョンで同時に書き込み可能** かつ **強い一貫性を保証** する点が大きな特徴です。これは、金融・決済システムのようにトランザクションの一貫性が厳格に求められるシステムにとって重要な要件を満たします。

#### ヨーロッパ+アジアの多拠点運用シナリオ

今回対応したリージョンは、GDPR 対応が必要なヨーロッパ（ストックホルム、スペイン）とアジア太平洋地域（ムンバイ、シンガポール）であり、グローバル展開企業がヨーロッパとアジアをまたいだシステムで両リージョンに同期されたデータを保持する構成が容易になります。例えば、スペインとシンガポールをペアにしたマルチリージョンクラスタを構築すれば、両地域のユーザーが最寄りリージョンの書き込みエンドポイントでローカルアクセスでき、レイテンシを最小化しながら強い一貫性を維持できます。

#### 具体的な検証ステップ

公式ドキュメントを参照しながら、以下の検証を推奨します：

1. **新対応リージョンでのセットアップ確認**：ストックホルム+ムンバイ、スペイン+シンガポールなど異なるリージョン組み合わせでマルチリージョンクラスタを構築し、セットアップ手順をドキュメント化
2. **データ同期タイムの実測**：マルチリージョン間でのトランザクション同期にかかる時間を測定し、他のDBサービス（RDS クロスリージョンレプリケーション、DynamoDB グローバルテーブル）と比較
3. **フェイルオーバー検証**：一つのリージョンを意図的にシャットダウンし、フェイルオーバー動作と RPO/RTO を測定
4. **レイテンシ特性の測定**：異なるリージョン組み合わせ（例：スペイン+ムンバイ）での書き込みレイテンシとクロスリージョン読み取りレイテンシを計測
5. **コスト比較**：シングルリージョンクラスタとマルチリージョンクラスタのコスト試算シートを作成

AWS Free Tier でも利用開始できるため、まずは無料枠内で動作を確認してから本番適用を検討するとよいでしょう。

---

### RDS for Oracle R8i/M8i Reserved Instances：最大53%のコスト削減

Amazon RDS for Oracle において、最新の **R8i および M8i インスタンスタイプ** に対する Reserved Instances（予約インスタンス）が利用可能になりました。1年および3年の契約期間で、On-Demand 価格比で **最大 53% のコスト削減** が実現できます。

#### R8i / M8i インスタンスの性能特性

R8i と M8i インスタンスは AWS 独自のカスタム Intel Xeon 6 プロセッサを搭載しており、前世代の Intel ベースインスタンスと比べて **最大 15% 優れた価格性能比** と **2.5 倍のメモリバンド幅** を実現しています。特にメモリ多用型ワークロード（データウェアハウス、OLAP 処理）では、メモリバンド幅の向上が顕著なパフォーマンス改善につながります。

#### Reserved Instances の柔軟性

予約インスタンスの割引は Multi-AZ と Single-AZ の両構成に適用でき、同じインスタンスクラス内での構成変更が柔軟に可能です。さらに BYOL（ライセンス持ち込み）モデルでは、同一インスタンスファミリー内のあらゆるサイズに自動的に割引が適用される **サイズフレキシビリティ** が提供されます。これにより、ワークロード変動に応じてインスタンスサイズを変更しても、予約割引を無駄にすることなく継続利用できます。

#### コスト最適化の検証手順

AWS 公式ドキュメントで R8i / M8i インスタンスの仕様詳細（CPU コア数、メモリ容量、ネットワーク性能）を確認し、前世代との具体的な比較表を作成することをお勧めします。また、AWS Pricing Calculator を使用し、実際のワークロード想定下で On-Demand と Reserved Instances（1年・3年両方）のコスト比較シミュレーションを実施することで、投資回収期間や総所有コストを明確にできます。

## SRE視点での活用ポイント

今回のアップデートは、SRE の日常業務に直結する改善が多く含まれています。

**CloudWatch マネージド Prometheus コレクター** は、Terraform で管理している EKS クラスタや EC2 フリートがあれば、既存の監視スタックを大幅に簡素化できます。従来は OpenTelemetry Collector のデプロイ・スケーリング・バージョン管理を Helm チャートや Terraform モジュールで管理していたケースが多いでしょう。マネージド化により、これらのインフラコードを削除し、スクレイプ設定だけを管理すればよくなります。CloudWatch アラームと組み合わせれば、Prometheus メトリクスに基づいた統一アラート体系を構築でき、PagerDuty や Slack への通知フローも既存の CloudWatch Logs Insights クエリと統合できます。

導入時の判断基準としては、現在 Prometheus + Grafana を自前運用している環境で、運用工数の削減が優先課題であれば積極的に移行を検討すべきです。一方、PromQL の高度な機能や Grafana の豊富なプラグインに依存している場合は、マネージド版の機能セットと照らし合わせて移行範囲を慎重に判断する必要があります。

**Aurora DSQL のマルチリージョン対応** は、ディザスタリカバリ戦略を見直す好機です。現在 RDS のクロスリージョンリードレプリカで DR 構成を組んでいる場合、Aurora DSQL に移行することで両リージョンでアクティブに書き込みが可能になり、フェイルオーバー時の手動切り替えや読み取り専用期間を排除できます。障害対応のランブックに組み込む際は、フェイルオーバーの自動化と RPO/RTO の実測値を事前に検証し、SLO に反映させることが重要です。リスクとしては、強い一貫性を保証するためのレイテンシ増加が考えられるため、本番適用前に負荷テストで実測することを推奨します。

**RDS for Oracle の Reserved Instances** は、長期稼働が確定している本番データベースで即座にコスト削減効果が得られます。Terraform で RDS インスタンスを管理している場合、既存の `aws_db_instance` リソースに Reserved Instances を適用するための追加設定は不要で、AWS コンソールまたは CLI から予約を購入するだけです。既存のコスト管理プロセスに組み込む際は、AWS Cost Explorer でタグベースのコスト配分を活用し、チームごとの Reserved Instances 利用率を可視化すると効果測定がしやすくなります。

**EC2 C7i / C7i-flex インスタンス** のリージョン拡大は、ヨーロッパ（ミラノ）やカナダ西部（カルガリー）でコンピュート最適化が必要な場合に選択肢が増えます。既存の C6i インスタンスから移行する場合、Auto Scaling グループの起動テンプレートを更新し、段階的にインスタンスタイプを切り替えることで、リスクを抑えながら価格性能比の向上を実現できます。バッチ処理やビデオエンコーディングのような CPU バウンドなワークロードでは、ベンチマークを取得して実際のコスト削減効果を定量化することが重要です。

**CodeDeploy のリージョン拡大** は、アジア太平洋地域やメキシコに展開する CI/CD パイプラインで、ローカルリージョンからの低レイテンシーデプロイを実現します。CodePipeline と組み合わせて、GitHub や GitLab からのコミットトリガーで自動デプロイする構成を構築すれば、グローバル展開でも統一的な DevOps プロセスを維持できます。データレジデンシー要件がある国では、コードやアーティファクトをローカルリージョン内で完結させることでコンプライアンス対応が容易になります。

**SageMaker Unified Studio の Git バージョン管理** は、機械学習チームでの共同開発を改善します。Notebooks に対する Git サポートが初めて実装されたことで、Jupyter Notebook の変更履歴を追跡し、ブランチ戦略を適用できるようになります。CI/CD パイプラインに組み込む際は、GitHub Actions や GitLab CI でノートブックの自動テストやモデルのデプロイを実行する構成を検討するとよいでしょう。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [AWS Lambda now supports Java 8, 11, and 17 on Amazon Linux 2023](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-lambda-java-amazon-linux/) | Lambda の Java ランタイムが Amazon Linux 2023 ベースに刷新され、Java 8、11、17 をサポート |
| [Amazon RDS for Oracle now offers Reserved Instances for R8i and M8i instances](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-rds-oracle-r8i-m8i/) | RDS for Oracle で R8i / M8i インスタンスの Reserved Instances が提供開始。最大53%のコスト削減、前世代比15%優れた価格性能比、メモリバンド幅2.5倍 |
| [Amazon Aurora DSQL adds multi-Region cluster support in four more Regions](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-aurora-dsql-adds-multi-region-clusters-four-more-regions/) | Aurora DSQL がストックホルム、スペイン、ムンバイ、シンガポールでマルチリージョンクラスタに対応。アクティブ-アクティブ構成と強い一貫性を提供 |
| [Amazon CloudWatch announces managed Prometheus collectors](https://aws.amazon.com/about-aws/whats-new/2026/07/cloudwatch-managed-collectors/) | CloudWatch がマネージド Prometheus コレクターをサポート。EKS、EC2、ECS、MSK、OpenSearch から自動収集し、エージェント管理が不要に |
| [Amazon EC2 C7i instances now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-c7i-instances-mxp-yyc-region/) | C7i インスタンス（コンピュート最適化、Intel Xeon 第4世代搭載）がミラノとカルガリーで利用可能に。前世代比15%優れた価格性能比 |
| [Amazon EC2 C7i-flex instances now available in Europe (Milan) region](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-ec2-c7i-flex-instances-MXP-region/) | C7i-flex インスタンス（コンピュート最適化、柔軟サイズ）がミラノで利用可能に。C6i比19%の価格性能改善 |
| [AWS CodeDeploy now available in five additional AWS regions](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-codedeploy-five-additional-regions) | CodeDeploy がニュージーランド、タイ、台北、マレーシア、メキシコ中部で利用開始。34商用リージョンに拡大 |
| [Amazon SageMaker Unified Studio brings richer Git version control to all project tools](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-sagemaker-unified-studio-git/) | SageMaker Unified Studio で Notebooks を含む全ツールに Git バージョン管理を統合。ファイル単位での柔軟な管理とブランチ操作が可能に |

## まとめ

今回のアップデート群は、運用効率の向上とコスト最適化、グローバル展開の容易化という3つのテーマが際立っています。CloudWatch のマネージド Prometheus コレクターは、監視基盤の運用負担を大幅に削減し、SRE チームがインフラ保守からシステム改善にシフトする後押しとなるでしょう。Aurora DSQL のマルチリージョン対応拡大は、ヨーロッパとアジアをまたぐグローバルアプリケーションに強い一貫性とアクティブ-アクティブ構成を提供し、ディザスタリカバリ戦略の選択肢を広げます。RDS for Oracle の Reserved Instances は、長期稼働が見込まれる本番データベースで即座にコスト削減効果を発揮します。

EC2 インスタンスタイプの拡充や CodeDeploy のリージョン拡大は、地理的な展開とコンプライアンス要件に柔軟に対応するための基盤を整えます。SageMaker Unified Studio の Git 統合は、機械学習プロジェクトにおけるバージョン管理とチーム開発を改善し、MLOps の成熟度を高める一歩となるでしょう。

これらのアップデートを活用する際は、公式ドキュメントで詳細仕様を確認し、実環境での検証を通じて具体的な効果を測定することが重要です。特にコスト削減やパフォーマンス改善を謳うアップデートについては、実測値を取得してから本番適用を判断することをお勧めします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)