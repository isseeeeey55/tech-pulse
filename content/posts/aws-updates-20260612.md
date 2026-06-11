---
title: "【AWS】2026/06/12 のアップデートまとめ"
date: 2026-06-12T08:02:27+09:00
draft: false
tags: ["aws", "aurora", "postgresql", "cloudwatch", "eks", "ecs", "lambda", "ec2", "mwaa", "eventbridge", "elastic-beanstalk", "acm", "secrets-manager", "prometheus", "opensearch", "bedrock", "x-ray"]
categories: ["AWS Updates"]
summary: "2026/06/12 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260612/header.png)

## はじめに

今回は、直近で発表された10件のAWSアップデートを紹介します。Amazon Aurora の PostgreSQL 18 対応、CloudWatch Application Signals の統合トラブルシューティング機能、Amazon MWAA Serverless の EventBridge 連携、Elastic Beanstalk コンソールへの CloudWatch Logs 統合、AWS Workload Credentials Provider の新登場、Amazon Managed Service for Prometheus の順序外サンプル取り込みと Native Histograms 対応、Amazon OpenSearch Service の MCP Apps 対応、Amazon Bedrock での OpenAI GPT-5.4/5.5 提供開始、そして Amazon ECS Managed Daemons のタスク間通信サポートと、多岐にわたるアップデートが含まれています。

特に注目すべきは、オブザーバビリティとトラブルシューティングの効率化に焦点を当てたアップデートが多い点です。CloudWatch Application Signals の強化、OpenSearch Service の agentic IDE 統合、Elastic Beanstalk のログ統合など、複数ツール間の移動を減らし、単一のインターフェースで問題解決を完結させる方向性が見て取れます。また、証明書管理の自動化、メトリクス取り込みの柔軟性向上、エージェント配置の効率化など、運用負荷を軽減する実用的な改善も目立ちます。

## 注目アップデート深掘り

### CloudWatch Application Signals の統合トラブルシューティング機能

Amazon CloudWatch Application Signals に追加された新機能は、分散システムの運用における最大の課題の一つである「障害発生時のツール間切り替え」を大幅に削減します。

#### なぜこのアップデートが重要なのか

従来、マイクロサービスアーキテクチャにおける障害対応では、まずサービスマップでエラー発生箇所を特定し、次に CloudWatch Logs でログを確認、さらに X-Ray でトレースを追跡、最後に EC2 や ECS のコンソールでインフラ状態を確認する、といった複数コンソールを横断する作業が必要でした。この切り替えコストは、特に複数サービスが同時に劣化している場合や、深夜の緊急対応時に大きな負担となっていました。

今回のアップデートでは、アプリケーションマップに **ヘルスランキング表示** が追加され、unhealthy なサービスが優先順位付けされます。さらに、サービス概要ページに **インフラストラクチャ**、**ログ**、**トレース** の3つのタブが新設され、1つの画面からコンピュート環境、ログスニペット、トレース詳細まで確認できるようになりました。対応ワークロードは Amazon EKS、Amazon ECS、AWS Lambda、Amazon EC2 と幅広く、現代的なアプリケーション環境をほぼ網羅しています。

#### 検証のポイント

実際にこの機能を評価するには、以下のステップで検証することをおすすめします。

**1. デモ環境の構築と有効化**  
まず、EKS、ECS、Lambda、EC2 のいずれかで Application Signals を有効化します。CloudWatch コンソールから Application Signals の設定を行い、対象のサービスが自動検出されることを確認します。

**2. 意図的な障害注入**  
リソース枯渇（メモリ制限の引き下げ、CPU throttling）やアプリケーションエラー（エラーコードを返すエンドポイントの追加）を意図的に発生させ、ヘルスランキングに unhealthy なサービスとして表示されるまでの時間を測定します。

**3. 統合ビューの確認**  
unhealthy と判定されたサービスを選択し、インフラストラクチャタブで CPU/メモリ使用率、ログタブでエラーログのスニペット、トレースタブで該当リクエストの分散トレースが、それぞれ関連付けられて表示されることを確認します。

**4. 従来フローとの比較**  
同じ障害シナリオに対して、従来の「CloudWatch Logs → X-Ray → ECS コンソール」という手順と、新機能を使った統合ビューでの調査時間を比較します。特に、コンソール切り替え回数とタブ遷移回数、エラー原因特定までの時間を定量化すると効果が明確になります。

#### 実用化に向けた考慮事項

インフラストラクチャタブには、コンピュート環境とランタイム環境、その構成要素、およびキュレートされたデフォルトメトリクスが表示され、関連する監視ツールへのディープリンクも提供されます。表示内容は各コンピュート環境（EKS、ECS、Lambda、EC2）によって異なるため、利用環境での表示粒度は実際に確認することをおすすめします。

また、ログ・トレースタブの検索範囲と時間精度も実運用では重要です。特にトレース情報は X-Ray の既存設定に依存するため、サンプリングレートが低い場合は表示されるトレースが限定的になる点に注意が必要です。

料金面では、Application Signals 自体のメトリクス取り込み量と、関連する CloudWatch Logs、X-Ray トレースのボリュームによって変動します。既存の監視体制と重複する部分を整理し、統合によるコスト削減効果を試算することが推奨されます。

### AWS Workload Credentials Provider による証明書管理の自動化

AWS Workload Credentials Provider は、TLS 証明書とシークレット管理の運用負荷を大幅に削減する新しいクライアント側プロバイダーです。

#### 背景：短寿命証明書時代の運用課題

CA/B フォーラムの認証局マンデートにより、公開証明書の最大有効期間が段階的に短縮されています。これにより、年に数回しか発生しなかった証明書更新作業が、月次または週次の定例作業になりつつあります。

従来、ACM からエクスポートした証明書を EC2 や オンプレミスサーバーに配布するには、Amazon EventBridge で証明書更新を検知して更新済み証明書を配布するカスタム自動化を構築する必要がありました。この仕組みを数百台規模で維持することは、エラーハンドリング、リトライロジック、監視アラートの設定など、継続的な保守コストを生みます。

#### Workload Credentials Provider の仕組み

AWS Workload Credentials Provider は、証明書 ARN、配置先ファイルパス、サーバーリロード動作をシンプルな設定ファイルで指定するだけで、自動的に ACM からの証明書エクスポート、ローカルファイルシステムへの配置、ウェブサーバーのリロードまでを実行します。

対応環境は Windows と Linux で、Apache と NGINX ウェブサーバーがサポートされています。また、AWS Secrets Manager Agent との完全な後方互換性を持つため、既存のシークレットキャッシング設定を維持したまま証明書管理機能を追加できます。

#### ハイブリッド環境での活用

特にハイブリッドクラウド環境では、オンプレミスの Apache サーバーと AWS 上の ALB で同じドメインの証明書を共有するケースが多く、証明書更新の同期が課題となります。Workload Credentials Provider を使えば、オンプレミス側でも AWS と同一の証明書ライフサイクル管理が可能になり、証明書の不整合による障害リスクが低減します。

エクスポート可能な ACM 証明書と Secrets Manager に対応し、すべての AWS リージョンで利用できるため、複数リージョンにまたがる構成でも統一的な証明書配布の仕組みを組めます。

オープンソースとして GitHub で公開されているため、組織固有の要件（特定の証明書フォーマット、独自のリロードスクリプトなど）に応じたカスタマイズも可能です。

### Amazon ECS Managed Daemons のタスク間通信サポート

Amazon ECS Managed Daemons が pidMode と ipcMode の設定をサポートし、タスク間の可視性と通信が可能になりました。

#### サイドカーパターンからの脱却

これまで、トレーシングエージェント、プロファイリングツール、セキュリティエージェントなどを ECS 環境に配置する場合、各アプリケーションタスク定義にサイドカーとして組み込む方法が一般的でした。しかし、この方法では以下の課題がありました。

- 100個のタスク定義がある場合、すべてにサイドカー設定を追加・維持する必要がある
- エージェントのバージョンアップ時に全タスク定義を更新する必要がある
- 各コンテナがエージェントのコピーを実行するため、リソース効率が悪い
- アプリケーション開発者がインフラエージェントの設定を意識する必要がある

#### pidMode と ipcMode の仕組み

今回追加された **pidMode** と **ipcMode** は、デーモンタスクがインスタンス上の他のプロセスや IPC リソースにアクセスできるようにする設定です。

**pidMode: "shared"** を設定すると、デーモンタスクからインスタンス上のすべてのプロセスが見えるようになります。これにより、トレーシングエージェントがアプリケーションプロセスを検出してトレースを収集する構成が可能になります。

**ipcMode: "shared"** を設定すると、デーモンタスクが他のコンテナと IPC 名前空間を共有できます。これは、アプリケーションプロセスや共有 IPC リソースへのアクセスを必要とするプロファイリングツールやセキュリティエージェントの動作に必要です。

デフォルトは **"none"** で、デーモンはアプリケーションコンテナから分離されたまま動作します。

#### プラットフォームチームの利点

ECS Managed Daemons としてエージェントを配置することで、プラットフォームチームはアプリケーションタスク定義から独立してエージェントを管理できます。ECS は管理対象インスタンスごとにちょうど1つのデーモンタスクを配置し、アプリケーションタスクよりも先にデーモンを起動するため、アプリケーションが起動した時点でエージェントがすでに動作しています。

エージェントのバージョンアップは、デーモン定義を更新するだけで全インスタンスに展開され、各アプリケーションチームが個別に対応する必要がありません。これにより、セキュリティパッチの適用速度が向上し、組織全体で一貫性のあるオブザーバビリティ・セキュリティ体制を維持できます。

## SRE視点での活用ポイント

### 統合トラブルシューティングによるMTTRの短縮

CloudWatch Application Signals の統合機能は、特に MTTR（Mean Time To Resolution）の短縮に貢献します。分散システムでは、サービスマップでエラーを発見してから、ログでエラー内容を確認し、トレースで依存関係を追跡し、最終的にインフラの状態を確認するまでの一連の流れが、しばしば10分以上かかることがあります。

統合ビューを活用すれば、unhealthy なサービスをヘルスランキングから選択し、インフラストラクチャタブで CPU/メモリの異常を確認、ログタブで該当エラーメッセージを特定、トレースタブで上流サービスの影響を把握、という一連の調査を1つの画面で完結できます。

導入判断では、既存の統合オブザーバビリティツールとの重複を評価する必要があります。既にサードパーティの統合ツールを導入している場合は、AWS ネイティブサービスとの棲み分けを明確にすることが重要です。一方、CloudWatch と X-Ray を個別に使っている環境では、ツール間の往復が統合ビューに集約されるため導入価値が高いでしょう（コストは CloudWatch の料金体系に従うため、料金ページでの確認を推奨します）。

### 証明書ライフサイクル管理の標準化

AWS Workload Credentials Provider は、Terraform で管理しているインフラに組み込むことで、証明書管理の IaC 化が加速します。EC2 インスタンスの user data や Systems Manager の State Manager ドキュメントに組み込むことで、新規インスタンスが起動時から自動的に証明書を取得・更新する仕組みを構築できます。

短寿命証明書時代では、証明書更新の自動化は必須要件です。CA/B フォーラムのマンデートにより公開証明書の有効期間短縮が進むなか、手動更新は現実的ではありません。Workload Credentials Provider を導入することで、証明書有効期限切れによる障害リスクを大幅に削減できます。

リスクとしては、プロバイダー自体の障害や設定ミスにより、証明書が更新されない可能性があります。そのため、CloudWatch アラームで証明書の有効期限を監視し、更新失敗時に通知する仕組みを並行して構築することが推奨されます。

### デーモンベースのエージェント管理

ECS Managed Daemons の pidMode/ipcMode サポートにより、サイドカーパターンから脱却し、エージェント管理を一元化できます。特に、数百のマイクロサービスを運用している環境では、各タスク定義にサイドカーを追加・維持するオーバーヘッドが大きな負担となります。

デーモンパターンに移行することで、エージェントのバージョン管理が単一のデーモン定義に集約され、セキュリティパッチの適用速度が向上します。また、各タスクがエージェントのコピーを実行しないため、インスタンスあたりのリソース効率も改善します。

導入時には、既存のサイドカーベースのエージェントとデーモンベースのエージェントが競合しないよう、段階的に移行する計画が必要です。まず新規サービスでデーモンパターンを検証し、動作が安定してから既存サービスのサイドカーを削除する、といった慎重なアプローチが推奨されます。

## 全アップデート一覧

| アップデート | 概要 |
|------------|------|
| [Amazon Aurora now supports PostgreSQL major version 18](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-aurora-postgresql-major-version-18/) | Amazon Aurora が PostgreSQL 18 メジャーバージョンに対応しました |
| [Amazon CloudWatch Application Signals now supports infrastructure, logs, and traces context for faster troubleshooting](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Application-Monitoring-Sections.html) | CloudWatch Application Signals にヘルスランキング、インフラストラクチャ、ログ、トレースの統合ビューが追加され、複数ツール切り替えなしでトラブルシューティングが可能に（公式 What's New ページの URL が執筆時点で不達のため、リンクは Application Signals 公式ドキュメント） |
| [Amazon MWAA Serverless now supports Amazon EventBridge notifications](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-mwaa-serverless-eventbridge/) | Amazon MWAA Serverless が EventBridge 連携に対応し、ワークフローとタスクの状態変化をイベント駆動で自動化可能に |
| [AWS Elastic Beanstalk console now integrates CloudWatch Logs in the Logs tab](https://aws.amazon.com/about-aws/whats-new/2026/06/elastic-beanstalk-cloudwatch-logs/) | Elastic Beanstalk コンソールに CloudWatch Logs が統合され、環境のログを直接確認可能に |
| [AWS announces AWS Workload Credentials Provider](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-workload-credentials-provider/) | ACM からの証明書と Secrets Manager からのシークレットを自動デプロイ・ローカルキャッシュする軽量クライアント側プロバイダーが登場 |
| [Amazon Managed Service for Prometheus now supports out of order sample ingestion](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-managed-service-prometheus-outoforder-ingestion/) | Amazon Managed Service for Prometheus が順序外サンプル取り込みとルールクエリオフセットに対応し、分散環境でのデータ損失を削減 |
| [Amazon Managed Service for Prometheus now supports Native Histograms](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-managed-service-prometheus-native-histograms/) | Prometheus ネイティブヒストグラムの取り込み・保存・クエリに対応。従来 22 時系列を要したヒストグラムが 1 時系列で表現でき、事前のバケット境界定義なしに histogram_quantile() による精緻なテイルレイテンシ分析が可能。課金は実際に観測値が入ったバケットのみが対象 |
| [Amazon OpenSearch Service launches MCP Apps for agentic observability](https://aws.amazon.com/about-aws/whats-new/2026/06/opensearch-agentic-observability-mcp-app) | OpenSearch Service が MCP Apps に対応し、Claude Desktop や VS Code などの agentic IDE からログ・トレース・メトリクス・アラートを調査可能に |
| [OpenAI GPT-5.4 and GPT-5.5 models now available in US East (N. Virginia) on Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/06/openai-gpt-us-east-virginia-amazon/) | Amazon Bedrock で OpenAI の最新モデル GPT-5.4 と GPT-5.5 が米国東部（N. バージニア）リージョンで利用可能に。272K トークンのコンテキストウィンドウとマルチモーダル対応 |
| [Amazon ECS Managed Daemons now support inter-task visibility and communication](https://aws.amazon.com/about-aws/whats-new/2026/06/ecs-managed-daemons-pid-ipc-modes/) | ECS Managed Daemons が pidMode と ipcMode に対応し、トレーシング・プロファイリング・セキュリティエージェントのデーモン配置が可能に |

## まとめ

今回紹介したアップデートは、オブザーバビリティの統合、運用自動化の効率化、エージェント管理の一元化という、SRE が日常的に直面する課題に対する具体的な解決策を提供しています。

特に、CloudWatch Application Signals の統合トラブルシューティング機能と OpenSearch Service の MCP Apps 対応は、AI エージェントと従来の監視ツールの融合という新しい方向性を示しています。単一の会話スレッドやコンソール内で、ログ・トレース・メトリクス・インフラ状態を横断的に分析できる体験は、障害対応の速度と精度を大きく向上させるでしょう。

AWS Workload Credentials Provider と ECS Managed Daemons の機能強化は、証明書管理とエージェント配置という、スケールに伴って複雑化しやすい運用タスクを標準化・自動化します。これらは、組織が成長する過程で必ず直面する「運用のスケーラビリティ」問題に対する実用的な回答です。

Amazon Managed Service for Prometheus の順序外サンプル取り込み、Amazon MWAA Serverless の EventBridge 連携、Elastic Beanstalk のログ統合といった改善も、それぞれ特定のペインポイントを解消する地味ながら重要なアップデートです。日々の運用で感じていた小さなストレスが、こうした継続的な改善によって着実に解消されていくことを実感できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)