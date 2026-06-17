---
title: "【AWS】2026/06/18 のアップデートまとめ"
date: 2026-06-18T08:02:50+09:00
draft: true
tags: ["aws", "rds", "postgresql", "mysql", "mariadb", "aurora", "glue", "spark", "sagemaker", "healthomics", "cloudwatch", "bedrock", "s3", "outposts", "continuum", "guardduty", "security hub", "devops", "iam", "vpc", "eventbridge", "sns"]
categories: ["AWS Updates"]
summary: "2026/06/18 のAWSアップデートまとめ"
---

# 直近のAWSアップデート - 2026年6月版

## はじめに

今回は、直近で発表された14件のAWSアップデートを紹介します。注目すべきは、Graviton5プロセッサを搭載したM9g RDSインスタンスの登場、Amazon Bedrock周りの大幅な機能拡充、そしてセキュリティを「機械速度」で実現するAWS Continuumの発表です。特にBedrockエコシステムについては、AgentCoreの最適化機能・マネージドハーネス・Guardrails統合など、本番環境でのAIエージェント運用を強化する複数のアップデートが同時にリリースされました。データベース・AI/ML・セキュリティ・DevOpsと幅広い領域をカバーしており、エンタープライズのクラウド活用がさらに加速する内容となっています。

## 注目アップデート深掘り

### Amazon RDS for PostgreSQL/MySQL/MariaDB - Graviton5ベースM9gインスタンスの登場

AWS Graviton5プロセッサを搭載したM9gデータベースインスタンスが、Amazon RDS for PostgreSQL、MySQL、MariaDBで一般利用可能になりました。同等サイズのGraviton4ベースインスタンスと比較して、最大30%のパフォーマンス向上と最大23%の価格/パフォーマンス改善を実現します（データベースエンジン・バージョン・ワークロードにより異なります）。

**なぜこのアップデートが重要なのか**

データベースはアプリケーション全体のボトルネックになりやすく、特に大規模トラフィック環境や複雑な分析クエリを実行するワークロードでは、わずかなパフォーマンス向上が運用コスト削減やユーザー体験の改善に直結します。M9gインスタンスには新たに24xlargeと48xlargeのサイズが追加されており、最大192 vCPU、最大100Gbpsの高速ネットワーク帯域幅、Amazon EBSへ最大72Gbpsの帯域幅をサポートします。これにより、従来はスケールアップが困難だった大規模データベースワークロードへの対応が可能になります。

**世代間比較とワークロード別の最適化**

Graviton4 (M7g) から Graviton5 (M9g) への移行を検討する際、まず既存のワークロード特性を把握することが重要です。読み取り重視のワークロードでは、Graviton5の改善されたキャッシュ階層とメモリ帯域幅が効果を発揮します。書き込み集約型ワークロードでは、EBSへの72Gbpsの帯域幅が特にトランザクションログの書き込み性能向上に寄与します。

PostgreSQL、MySQL、MariaDBの各エンジンで性能特性が異なるため、実際の移行前には代表的なワークロードでのベンチマークが推奨されます。リリースノートによれば、パフォーマンス向上はワークロードに依存するため、本番環境を模したテストデータとクエリパターンでの検証が不可欠です。

**ネットワークとストレージ性能の活用シーン**

100Gbpsのネットワーク帯域幅は、リージョン間レプリケーション、大規模なバックアップ転送、マルチAZ構成でのデータ同期といったシナリオで威力を発揮します。特に災害対策やグローバル展開を考慮した構成では、高速なネットワーク性能がRTO/RPO目標の達成に直結します。

現在、M9gインスタンスは米国東部（バージニア北部、オハイオ）、米国西部（オレゴン）、ヨーロッパ（フランクフルト）リージョンで利用可能です。他のリージョンへの展開は今後予定されており、グローバル展開を計画している場合はリージョン戦略の見直しが必要です。

### Amazon Bedrock AgentCore - 本番環境でのエージェント最適化機能

Amazon Bedrock AgentCoreに、本番環境で動作するエージェントを継続的に監視・改善する新しい最適化機能が追加されました。この機能が解決する最大の課題は「サイレント失敗」です。エージェントが技術的なエラーを出さずに動作しているように見えても、実際には誤った回答やタスク実行をしているケースは、ダッシュボード監視では検出できず、数週間後の顧客クレームで初めて判明することがあります。

**3段階の改善ループ**

AgentCoreの最適化機能は、理解・修正・検証の3段階で動作します。

**理解フェーズ**では、数百のセッションから「失敗パターン」「ユーザーの意図」「エージェントのタスク遂行経路」の3つの洞察を自動抽出します。サイレント失敗を含む失敗パターンを特定し、影響範囲の大きい順にランク付けすることで、優先的に修正すべき問題を明確化します。これは従来の手動トレース分析では発見困難だった、特定条件下でのみ発生する問題の検出を可能にします。

**修正フェーズ**では、本番データに基づいてシステムプロンプトやツール説明の改善案を提示します。各提案には失敗原因との関連付けが明記されており、汎用的なアドバイスではなく実装可能な具体的な改善内容が示されます。これにより、開発者は「なぜこの修正が必要なのか」を理解した上で、改善を適用できます。

**検証フェーズ**では、バッチ評価により修正案をテストデータセットで検証してから、A/Bテストで本番環境での実際の効果を確認します。この段階的アプローチにより、修正による予期しない副作用を最小限に抑えながら、継続的な品質向上が実現します。

**エージェント運用における実用性**

従来、AIエージェントの品質改善は、開発者が手動でトレースログを分析し、問題パターンを推測し、プロンプトを調整するという反復プロセスでした。この新機能により、データドリブンで根拠のある改善サイクルが実現します。特に、複数の言語や地域でエージェントを運用している場合、地域別の失敗パターンを自動検出できる点は大きな利点です。

金融取引や医療診断など高リスク領域では、エラーが出ない不正確な回答が重大な結果を招きます。AgentCoreの最適化機能は、こうした「正常に見えるが間違っている」応答を事前に発見・修正する仕組みとして、本番環境でのAIエージェント運用の信頼性を大きく向上させます。

### AWS Continuum - セキュリティを機械速度で実現

AWS Continuumは、セキュリティリスクの発見から優先順位付け、検証、修復までを「機械速度」で自動実行する新しいセキュリティプラットフォームです。従来は脆弱性発見後、どの脆弱性がビジネスに影響するか判断し、実際に悪用可能か検証し、修復するまでに複数チーム間の調整で日数を要していました。

**脆弱性管理の従来の課題**

エンタープライズ環境では、セキュリティスキャンツールが日々膨大な数の潜在的脆弱性を報告します。しかし、そのすべてが実際に悪用可能なわけではありません。セキュリティチームは手作業でトリアージを行い、どの脆弱性が本当にリスクなのか、攻撃者が実際に悪用できる経路があるのかを検証する必要がありました。この過程は時間がかかり、その間に攻撃者に悪用される可能性がありました。

**自動化された検証と修復フロー**

AWS Continuumは既存のスキャンツールと連携し、発見された脆弱性を隔離されたサンドボックス環境で実際に悪用可能か自動検証します。悪用可能と判明した脆弱性については、ガードレール内での高速な一時的修復を実施し、その後、本格的な修復を経て本番環境へデプロイします。

このプロセス全体が自動化されることで、セキュリティチームは手作業でのトリアージから戦略立案と結果承認にシフトできます。「機械速度」とは、人間が判断を下すまでの時間を除き、技術的な検証・修復プロセスを数分から数時間で完了できることを意味します。

**STRIDE形式の脅威モデリング自動生成**

Continuumは脅威モデリングも自動生成します。STRIDE（Spoofing、Tampering、Repudiation、Information Disclosure、Denial of Service、Elevation of Privilege）は、Microsoft が提唱したセキュリティ脅威の分類手法です。従来、このモデリングは経験豊富なセキュリティエンジニアの手作業で行われていましたが、Continuumは自動的にSTRIDE形式の脅威モデルを生成し、コンプライアンス要件への対応を支援します。

現在、AWS Continuumは限定プレビュー段階です。利用を希望する場合は、AWS アカウントチームを通じてアクセスを申請する必要があります。本番環境での効果測定には、既存のGuardDuty・Security Hubとの連携テストやコスト削減効果（手作業削減時間）の定量化が推奨されます。

## SRE視点での活用ポイント

**データベース性能とコスト最適化の判断軸**

M9g インスタンスへの移行を検討する際は、現在のワークロード特性を詳細に把握することが重要です。CloudWatch メトリクスで CPU 使用率、ネットワーク帯域幅、IOPS、レイテンシを定常的に監視している環境であれば、これらのメトリクスからボトルネックを特定し、M9g の高速ネットワークや EBS 帯域幅がどの程度効果を発揮するか予測できます。

Terraform で RDS インスタンスを管理している場合、インスタンスクラスのパラメータ変更だけで移行可能ですが、ダウンタイムが発生するため、メンテナンスウィンドウの設定とフェイルオーバーテストが必須です。Blue/Green デプロイメントを活用すれば、切り替え時のダウンタイムを最小化できます。

コスト面では、Graviton5 の価格/パフォーマンス改善が最大23%とされていますが、実際の削減効果はワークロードに依存します。Cost Explorer と Performance Insights を組み合わせて、現在のコストとパフォーマンスをベースライン化し、移行後の効果を測定する体制を整えておくべきです。

**AIエージェント運用の信頼性向上**

Amazon Bedrock AgentCore の最適化機能は、AIエージェントを本番環境でスケール展開する際の品質保証プロセスを大きく変える可能性があります。従来、エージェントの挙動は開発環境でのテストと限定的なカナリアデプロイで検証していましたが、本番環境での実際のユーザー行動は予測困難です。

AgentCore の継続的改善ループを活用すれば、本番データから学習してエージェントを進化させるMLOps的なアプローチが実現します。CloudWatch アラームと組み合わせて、失敗率の異常検知やパフォーマンス劣化を監視し、AgentCore の最適化機能で根本原因を特定するワークフローを構築できます。

ただし、AIエージェントの改善には慎重なガバナンスが必要です。自動的に提案された改善案を無条件に適用するのではなく、A/Bテストでの検証結果をレビューし、ビジネスロジックとの整合性を確認するプロセスを組み込むべきです。障害対応のランブックに「AgentCore で失敗パターンを確認 → 改善案の影響範囲評価 → 承認後に段階的適用」というフローを追加することで、AIエージェント運用の成熟度を高められます。

**セキュリティ自動化の導入判断**

AWS Continuum は魅力的なセキュリティ自動化ですが、導入にはリスク評価が必要です。自動修復は便利ですが、誤検知による不要な修正や、修復によるサービス影響のリスクもあります。

導入初期は、自動修復を本番環境に直接適用するのではなく、検証結果のレビューと手動承認のステップを挟むことを推奨します。セキュリティチームの承認フローを EventBridge と SNS で構築し、Continuum の検証結果を Slack や PagerDuty に通知して、人間が最終判断を下す体制が現実的です。

また、Continuum の検証環境が本番環境と完全に分離されているため、サンドボックスでの検証結果が本番環境での実際の悪用可能性と完全に一致するとは限りません。ネットワーク構成やアクセス制御の違いにより、実環境では悪用不可能なケースもあります。Continuum の結果を絶対視せず、既存の脆弱性管理プロセスと組み合わせることが重要です。

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| **データベース** | [Amazon RDS for PostgreSQL, MySQL, and MariaDB now supports M9g database instances](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-rds-postgresql-mysql-mariadb-m9g-instances/) | Graviton5 プロセッサ搭載の M9g インスタンスが利用可能に。最大 30% のパフォーマンス向上、最大 23% の価格/パフォーマンス改善。新サイズ 24xlarge・48xlarge を追加、最大 192 vCPU、100Gbps ネットワーク、72Gbps EBS 帯域幅をサポート |
| **データベース** | [Amazon Aurora and RDS for MySQL expand Extended Support for MySQL 5.7 through June 2029](https://aws.amazon.com/about-aws/whats-new/2026/06/rds-mysql-es-extension/) | MySQL 5.7 の Extended Support が 2029年6月30日 まで延長（従来は2027年2月28日）。セキュリティパッチと重大なバグ修正を継続提供、価格は Year 3 料金体系を維持 |
| **分析** | [AWS Glue Interactive Sessions now support Spark Connect for interactive workloads](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-glue-interactive-sessions-spark-connect-smus-notebooks/) | Apache Spark Connect に対応。SageMaker Unified Studio、Jupyter、VS Code から Spark アプリを開発・実行可能に。Thin client アーキテクチャで依存関係を分離、Spark UI と History Server による監視をサポート |
| **ライフサイエンス** | [AWS HealthOmics now streams workflow engine logs to Amazon CloudWatch in real time](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-healthomics-real-time-engine-log-streaming/) | HealthOmics が CloudWatch へのリアルタイムログストリーミングに対応。バイオインフォマティクスワークフローのデバッグと反復開発を加速。ワークフローイベント、タスクスケジューリング、エラーのフルスタックトレースを記録 |
| **AI/ML** | [Amazon Bedrock AgentCore introduces new optimization capabilities](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-agentcore-new-optimization-capabilities) | 本番環境でのエージェント最適化機能を追加。失敗パターン・ユーザー意図・タスク経路を分析し、サイレント失敗を検出。システムプロンプトとツール説明の改善案を提示、バッチ評価と A/B テストで検証 |
| **AI/ML** | [Amazon Bedrock Managed Knowledge Base is now generally available](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-managed-knowledge-base/) | フルマネージド RAG サービスが GA。S3、SharePoint、Confluence、Google Drive、OneDrive、Web Crawler の6つのコネクタを搭載。ハイブリッド検索、ドキュメントランキング、エージェンティック検索をサポート |
| **AI/ML** | [AgentCore harness is now generally available](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-agentcore-harness-generally-available) | 管理型エージェントハーネスが GA。YAML/JSON 設定でエージェントを定義し、数分で本番グレードのエージェントが起動。モデルとハーネスが疎結合、セッション中のモデル切り替えが可能 |
| **AI/ML** | [Amazon Bedrock AgentCore now supports Bedrock Guardrails in policy](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-agentcore-policy-guardrails-generally-available) | AgentCore ポリシーに Guardrails 統合。プロンプトインジェクション、機密データ漏洩を防御。ゲートウェイ境界で評価され、一貫した適用を保証 |
| **AI/ML** | [Amazon Bedrock Guardrails announces a new API targeting agentic AI workflows](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-guardrails-api-ai/) | InvokeGuardrailChecks API をリリース。リソースレス設計で、事前のガードレール作成が不要。検出専用モードで数値的な重大度スコアと信頼度スコアを返す。エージェントループの任意のポイントで個別セーフガードを適用可能 |
| **AI/ML** | [Amazon S3 Vectors now supports up to 10,000 similarity search results per query](https://aws.amazon.com/about-aws/whats-new/2026/06/s3-vectors-supports-10000-search-results-per-query) | S3 Vectors の類似度検索結果上限が 10,000件 に拡大（従来の100倍）。マルチステージ検索パイプライン（リランキング、集約、重複排除）に対応。QueryVectors API で topK パラメータを最大10,000に設定可能 |
| **AI/ML** | [AWS Transform now supports model-to-model migration assessment](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-transform-model-to-model-assessments) | 生成 AI ワークロードのモデル間マイグレーション評価に対応。OpenAI、Google Gemini、Anthropic から Amazon Bedrock への移行を支援。コスト比較と本番環境対応のコード変更を提供 |
| **コンピューティング** | [AWS Outposts racks now support bmn-cx3a instances](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-outposts-amd-bmn-cx3a/) | 第2世代 Outposts ラックで bmn-cx3a インスタンスを提供開始。AMD EPYC 第5世代プロセッサと NVIDIA ConnectX-7 を搭載、最大 800 Gbps のネットワーク帯域幅。L2 マルチキャストとハードウェア PTP をサポート |
| **セキュリティ** | [Introducing AWS Continuum for security at machine speed](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-continuum/) | セキュリティリスクの発見・優先順位付け・検証・修復を機械速度で自動実行。隔離サンドボックスでの悪用可能性検証、ガードレール内での高速修復、STRIDE 形式の脅威モデル自動生成 |
| **DevOps** | [AWS DevOps Agent adds release management capability (preview)](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-devops-agent-release-management/) | リリース管理機能をプレビュー追加。リリース準備状況のレビューと自動テスト実行。内部標準の乖離チェック、依存関係の影響分析、アクセス制御検証、Well-Architected ベストプラクティス遵守を検証 |

## まとめ

今回紹介したアップデート群から見える全体的な傾向として、**AIエージェントの本番環境運用の成熟化**が挙げられます。Amazon Bedrock 関連では、AgentCore の最適化機能、マネージド Knowledge Base、ハーネスの GA、Guardrails の強化など、エンタープライズが本番環境で AI エージェントを安全かつ効率的に運用するための機能が一気に揃いました。

データベース領域では、Graviton5 の登場により、価格とパフォーマンスのバランスがさらに改善され、大規模ワークロードのコスト最適化の選択肢が広がっています。MySQL 5.7 の Extended Support 延長は、レガシーシステムを運用する企業に段階的な移行計画の余裕を与えるものです。

セキュリティ面では、AWS Continuum が「機械速度」という新しい概念を提示し、従来の手作業中心の脆弱性管理からの脱却を目指しています。DevOps 領域でも、AWS DevOps Agent のリリース管理機能により、デプロイ前の自動検証が強化されています。

これらのアップデートは、いずれもエンタープライズの課題—スケール、コスト、セキュリティ、運用効率—に直接応えるものです。新機能の導入には慎重な検証が必要ですが、適切に活用すれば、システムの信頼性と開発生産性の大幅な向上が期待できます。引き続き、公式ドキュメントやベストプラクティスガイドを参照しながら、自社のワークロードに最適な活用方法を探っていくことをお勧めします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)