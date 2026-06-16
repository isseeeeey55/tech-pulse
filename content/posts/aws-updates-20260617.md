---
title: "【AWS】2026/06/17 のアップデートまとめ"
date: 2026-06-17T08:02:38+09:00
draft: false
tags: ["aws", "cloudwatch", "bedrock", "redshift", "fsx", "marketplace", "partner-central", "management-console", "rds", "lambda", "ec2", "privatelink", "vpc"]
categories: ["AWS Updates"]
summary: "2026/06/17 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260617/header.png)

# 直近の AWS アップデート情報まとめ — 2026年6月版

## はじめに

今回は、直近で発表された14件のAWSアップデートを紹介します。注目すべきは、開発者エクスペリエンス向上に向けた大型フレームワーク（AWS Blocks）のプレビュー公開、観測性領域でのOpenTelemetry対応強化、そしてパートナーエコシステムの拡充に向けた複数の改善です。特に、Amazon CloudWatchのOpenTelemetryメトリクスネイティブサポート、AWS Blocksによるインフラ学習不要のバックエンド開発環境、そしてAWS Management Console Private Accessのインターネット非接続対応は、運用効率とセキュリティを大幅に改善する重要な機能強化です。

また、パートナー向けにはAI支援型の商品リスティング機能やコセル自動化エージェント、大幅な手数料引き下げなど、AWSエコシステム全体の成長を加速させる施策が揃っています。ストレージ、推論AI、認証制御の各分野でも実用的な機能追加が行われており、エンタープライズ利用の幅が広がっています。

## 注目アップデート深掘り

### Amazon CloudWatch が OpenTelemetry メトリクスをネイティブサポート、PromQL で統一的なクエリが可能に

Amazon CloudWatchがOpenTelemetry Protocol（OTLP）経由でメトリクスを直接受信し、Prometheus Query Language（PromQL）でクエリできるようになりました。このアップデートは、観測性ツールチェーンの統一と運用コスト削減において非常に重要な意味を持ちます。

#### なぜこのアップデートが重要なのか

従来、カスタムアプリケーションメトリクスとAWSサービスメトリクスを統合管理するには、複数のツールを組み合わせる必要がありました。Prometheusサーバーを自前で運用し、CloudWatch Exporterで既存のAWSメトリクスを取り込み、Grafanaで可視化するといった構成が一般的でした。この方式では、Prometheusサーバーの運用負荷、ストレージ管理、スケーリング対応、高可用性確保といった課題が常につきまとっていました。

今回のアップデートにより、OpenTelemetry SDKで計装されたアプリケーションメトリクスと、EC2、Lambda、RDSなど70以上のAWSサービスのネイティブメトリクスを、CloudWatch上で統一的に管理・クエリできるようになります。これは、既存のPrometheusベースの運用資産（PromQLクエリ、アラートルール、ダッシュボード定義）をそのまま活かしながら、管理対象のインフラストラクチャを大幅に削減できることを意味します。

#### 具体的な活用シナリオ

OpenTelemetry SDK で計装したアプリケーションから、OTLP 形式で CloudWatch にメトリクスを送信します。OTLP は SDK から直接送信できるほか、OpenTelemetry Collector を経由する構成も選択できます。送信されたメトリクスは CloudWatch 側で自動的にメトリクスストアに格納されます。

従来のPrometheus Query APIと互換性のあるAPIエンドポイントが提供されるため、既存のGrafanaダッシュボードやアラート設定は最小限の変更で移行可能です。PromQLで記述されたクエリは、そのままCloudWatchのメトリクスストアに対して実行できます。これにより、アプリケーションレイヤーのカスタムメトリクス（例：HTTPリクエストレイテンシー、エラー率）とAWSインフラレイヤーのメトリクス（例：EC2 CPU使用率、RDS接続数）を1つのPromQLクエリで結合して分析できます。

#### 課金モデルと運用メリット

課金はGB単位のインジェストベースとなり、15ヶ月のストレージが含まれます。従来のPrometheusサーバーを自己運用する場合、インスタンス費用、EBSストレージ費用、スナップショット費用、運用工数などが発生していましたが、新しいモデルでは実際に送信したメトリクスデータ量に応じた従量課金となり、運用工数はほぼゼロになります。

また、既存のCloudWatch Logsやトレース機能との統合も容易になります。メトリクス、ログ、トレースを同一のCloudWatch環境内で相関分析できるため、障害発生時のトラブルシューティングが大幅に効率化します。

#### 移行時の検証ポイント

既存のPrometheus環境からの移行を検討する際は、まずPromQLクエリの互換性確認が重要です。特に、Prometheusの拡張関数や特定のメトリクス命名規則に依存している場合、CloudWatchのPromQL実装での動作を事前検証する必要があります。また、Collectorの設定においてバッチサイズやエクスポート間隔を調整することで、コストとレイテンシーのバランスを最適化できます。

### AWS Blocks — インフラ知識不要で AWS にデプロイできる TypeScript フレームワーク

AWS Blocksは、インフラストラクチャツールの学習なしにAWS上でバックエンド機能を構築できるオープンソースのTypeScriptフレームワークとして、プレビュー公開されました。このフレームワークは、ローカル開発環境と本番AWS環境の間のギャップを埋める画期的なアプローチを採用しています。

#### なぜこのアップデートが重要なのか

従来のクラウドネイティブアプリケーション開発では、アプリケーションロジックの実装に加えて、Terraform、CloudFormation、AWS CDKといったインフラストラクチャツールの習得が必須でした。特にスタートアップやフルスタック開発者にとって、この学習コストは大きな参入障壁となっていました。また、ローカル環境での開発とAWS環境へのデプロイの間に設定の差異が生じやすく、「ローカルでは動くのに本番で動かない」という問題が頻繁に発生していました。

AWS Blocksは、この問題を「ローカルで完全に機能するアプリケーションを、コード変更なしでそのままAWSにデプロイできる」というコンセプトで解決します。開発者はAWSアカウントすら持たずに、PostgreSQL、認証機能、リアルタイムメッセージングを含む完全なバックエンドをローカル環境で構築・テストできます。

#### 開発から本番への一貫したワークフロー

ローカル環境では、Blocksが提供するビルトインのPostgreSQL、認証サービス、リアルタイムメッセージングエンジンが自動的に起動します。開発者はこれらのサービスをTypeScriptのAPIとして利用でき、データベーステーブルの定義、ユーザー認証フローの実装、WebSocketベースのリアルタイム通信の実装などを、すべて同一言語内で完結できます。

本番環境へのデプロイ時には、ローカルで動作していたアプリケーションコードを変更せずに、そのまま本番の AWS マネージドサービス上で実行できます。各コンポーネントが具体的にどの AWS サービスにマッピングされるかは、プレビュー段階の公式発表では詳細が明示されていません。いずれにせよ、この変換プロセスは自動化されており、開発者がインフラ定義を記述する必要はありません。

#### エンドツーエンドの型安全性

AWS Blocksの大きな特徴の一つが、データベーススキーマからフロントエンドまで一貫した型安全性を実現している点です。データベーステーブルをTypeScriptで定義すると、その型情報が自動的にAPIレイヤー、ビジネスロジック層、さらにはフロントエンドのReactコンポーネントまで伝播します。これにより、型の不整合によるランタイムエラーを大幅に削減でき、リファクタリング時の安全性も向上します。

コード生成ステップを介さずに型情報を伝播させる仕組みのため、開発サイクルが高速化され、型定義ファイルのメンテナンス負荷もありません。

#### フロントエンドフレームワークとの統合

React（Vite）、Next.js、Nuxt、Astroといった主要なフロントエンドフレームワークに対応しており、既存のフロントエンドプロジェクトへのバックエンド追加も容易です。フロントエンド側からは、自動生成されるTypeScript型定義を使ってバックエンドAPIを型安全に呼び出せます。

#### コストとカスタマイズ性

AWS Blocks自体に追加料金はかかりません。アプリケーションが使用したAWSサービスの標準料金のみが課金対象となります。また、高度なカスタマイズが必要な場合は、AWS CDKへ直接アクセスして細かいインフラ設定を調整することも可能です。この段階的な学習曲線により、初心者は簡易な構文から始め、経験を積むにつれてより詳細な制御が可能になります。

## SRE視点での活用ポイント

### 統合観測基盤の構築シナリオ

CloudWatchのOpenTelemetryサポートは、マイクロサービスアーキテクチャにおける観測性戦略を大きく変える可能性があります。Terraformで管理しているインフラであれば、既存のCloudWatchメトリクスとカスタムメトリクスを統合したダッシュボード・アラート定義をコード化し、バージョン管理できます。Prometheusベースのアラートルールを保持している組織であれば、それらをそのまま移植し、CloudWatch Alarmsとして運用することで、オンコール体制やインシデント対応フローを変更せずに移行を進められます。

特に注目すべきは、既存のGrafanaダッシュボードをそのまま活用できる点です。Grafanaのデータソース設定でPrometheus互換のCloudWatch APIエンドポイントを指定するだけで、既存のダッシュボードが機能し続けます。これにより、移行期間中のダッシュボード二重管理やチーム内での学習コストを最小化できます。

導入時の判断基準としては、現在のPrometheusサーバーの運用負荷（アップグレード、容量計画、バックアップ）と、CloudWatchへの移行によるコスト変動を比較検証することが重要です。特に、メトリクス保持期間が長い場合や、高頻度のクエリが実行される環境では、コスト試算を慎重に行う必要があります。

### 迅速な開発・検証環境の構築

AWS Blocksは、SREチームが新しいサービスのプロトタイプや検証環境を迅速に立ち上げる際に有効です。例えば、障害対応の自動化ツールや内製の運用ダッシュボードを構築する場合、従来はインフラ定義の作成、CIパイプラインの整備、環境変数管理などに多くの時間を費やしていました。AWS Blocksを使えば、ローカル環境で完全にテストしたツールをそのまま本番にデプロイでき、開発サイクルが大幅に短縮されます。

CloudWatchアラームと組み合わせる場合、Blocksで構築したバックエンドAPIにアラート通知を送信し、自動的に復旧スクリプトを実行したり、関連メトリクスを収集してSlackに通知したりするワークフローを簡単に実装できます。障害対応のランブックをコード化する際にも、TypeScriptの型安全性により、誤った操作を事前に防げます。

注意点としては、プレビュー段階のため、本番環境での利用には慎重な評価が必要です。特に、生成されるAWSリソースの構成や、スケーリング特性、障害時の挙動については、公式ドキュメントを参照しながら詳細な検証を行うべきです。

### セキュリティとコンプライアンスの強化

AWS Management Console Private Accessのインターネット非接続対応は、金融・医療・政府機関など、厳格なネットワーク分離要件がある環境で大きな意味を持ちます。VPCエンドポイント経由でのアクセスにより、すべてのコンソール操作がAWSネットワーク内に閉じるため、インターネットへの露出リスクを完全に排除できます。

Terraformでインフラを管理している環境であれば、VPCエンドポイントの構成と、エンドポイントポリシーによるアクセス制御をコード化し、監査可能な形で管理できます。特定のAWSアカウントへのアクセスのみを許可するポリシーを設定することで、マルチアカウント環境におけるアクセス境界を明確に定義できます。

導入時のリスクとしては、既存の運用ワークフロー（特に緊急時の対応手順）への影響を事前に評価する必要があります。インターネット経由でのアクセスが完全に遮断されるため、リモートワーク環境や外部パートナーとの協業シナリオでは、VPN接続やDirect Connectといった代替経路の整備が必須となります。

## 全アップデート一覧

| カテゴリ | アップデート | 概要 |
|---------|------------|------|
| **開発フレームワーク** | [AWS Blocks（Preview）](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-blocks-preview) | インフラ知識不要でAWSバックエンドを構築できるオープンソースTypeScriptフレームワーク。ローカル開発環境と本番AWSを統一。 |
| **観測性** | [CloudWatch OpenTelemetryサポート](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cloudwatch-otel-metrics/) | OTLP経由のメトリクス送信とPromQLクエリをネイティブサポート。カスタムメトリクスとAWSメトリクスを統合管理。 |
| **AI/機械学習** | [Grok 4.3 on Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/06/grok-amazon-bedrock/) | xAIの推論優先（reasoning-first）モデルをBedrockで提供。推論努力レベルを none/low/medium/high で設定可能で、信頼性の高いエージェント構築に対応。 |
| **データベース** | [Redshift RG instances拡大](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-redshift-rg-instances-3-additional-regions/) | Graviton搭載RGインスタンスがアフリカ・バンコク・メキシコリージョンで利用可能に。最大2.4倍高速化。 |
| **ストレージ** | [FSx for OpenZFS オプトインRegionsレプリケーション](https://aws.amazon.com/about-aws/whats-new/2026/06/on-demand-cross-region-replication/) | オプトインRegions間でのオンデマンドデータレプリケーションをサポート。ディザスターリカバリ構築が容易に。 |
| **移行** | [AWS Transform FSx for ONTAP対応（Preview）](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-transform-vmware-fsx-for-ontap-preview) | ブロックストレージのFSx for ONTAPへの直接移行をサポート。VMware環境からの移行を統合ワークフローで実現。 |
| **移行** | [AWS Transform メインフレーム統合ワークフロー](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-transform-mainframe-traceable-reimagine-workflow/) | z/OS COBOL/PL/Iアプリの最新化を単一ワークフローで実現。ポートフォリオ評価からコード生成まで追跡可能。 |
| **セキュリティ** | [AWS Sign-in RCP対応](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-sign-in/) | リソースベースポリシーとRCPによるコンソールサインインのネットワーク制限が可能に。 |
| **セキュリティ** | [Console Private Access インターネット非接続対応](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-management-console-private/) | VPCエンドポイント経由でのコンソールアクセスが可能に。インターネット接続を完全排除。 |
| **パートナー** | [Partner Central FTR検証](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-partner-central-foundational-technical-review/) | SOC 2 Type II または WAFR レポートで Foundational Technical Review を数分で完了。承認または改善フィードバックを数分以内に取得。 |
| **パートナー** | [Marketplace プロフェッショナルサービス手数料引き下げ](https://aws.amazon.com/about-aws/whats-new/2026/06/reduce-listing-fee-professional-services-aws-marketplace) | リスティング手数料を2.5%から0.5%に削減。コンサルティングパートナーの収益性向上。 |
| **パートナー** | [Marketplace AI支援型リスティング](https://aws.amazon.com/about-aws/whats-new/2026/06/ai-assisted-product-listing/) | AIが既存資産から高品質な商品リストを自動生成。SEO最適化と検索発見性を向上。 |
| **パートナー** | [Partner Central コセルAIエージェント](https://aws.amazon.com/about-aws/whats-new/2026/06/accelerate-co-selling-with-agents/) | AIがコセル機会をリアルタイム判定・推奨。Opportunity Quality Scoreで案件品質を可視化。 |
| **パートナー** | [Partner Central BVRファンディング](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-partner-business-value-realization/) | Business Value Realizationプログラム開始。段階的な価値実現に応じてファンディングを自動配分。 |

## まとめ

今回紹介したアップデート群は、AWS全体の戦略的な方向性を明確に示しています。開発者体験の向上（AWS Blocks）、オープンスタンダード対応の強化（OpenTelemetry）、パートナーエコシステムの拡充（手数料削減・AI支援）、そしてエンタープライズセキュリティの強化（Private Access、RCP）という4つの軸が顕著です。

特に、CloudWatchのOpenTelemetryサポートとAWS Blocksは、AWSがベンダーロックインを懸念する開発者・組織に対して、オープンな技術スタックとポータブルなコードを重視する姿勢を明確に示しています。一方で、これらの機能がAWS環境内で最適化されているため、実質的にはAWSエコシステム内での開発・運用効率が大幅に向上する結果となっています。

SREの観点では、観測性の統合、迅速な開発サイクル、セキュリティ境界の明確化という3つの側面で大きなメリットがあります。特に、既存のPrometheusベースの運用資産を活かしながらマネージドサービスへ移行できる道筋が示されたことは、多くの組織にとって現実的な選択肢となるでしょう。

パートナー向けの一連のアップデートは、AWSがエコシステム全体の成長を重視していることを示しています。AIによる自動化支援、手数料削減、資金援助プログラムの拡充により、特に中小規模のパートナー企業がAWSエコシステムに参入しやすくなる環境が整いつつあります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)