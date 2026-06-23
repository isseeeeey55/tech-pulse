---
title: "【AWS】2026/06/24 のアップデートまとめ"
date: 2026-06-24T08:02:02+09:00
draft: true
tags: ["aws", "cognito", "kms", "cloudwatch", "opensearch", "sagemaker", "ec2", "healthomics", "bedrock", "lambda", "nextflow"]
categories: ["AWS Updates"]
summary: "2026/06/24 のAWSアップデートまとめ"
---

# 直近の AWS アップデート — SRE が押さえておきたい 10 の新機能

## はじめに

今回は、直近で発表された 10 件の AWS アップデートを紹介します。Amazon Cognito のカスタマー管理キー対応、CloudWatch Logs のマネージド syslog インジェション、Lambda MicroVMs の登場など、セキュリティ強化と運用効率化を両立させる機能が目立ちます。特に注目したいのは、エージェントレスでネットワークデバイスのログを集約できる CloudWatch Logs の新機能と、VM レベルの分離を実現する Lambda MicroVMs です。これらは既存のログ収集基盤やサーバーレスアーキテクチャを大きく刷新する可能性を秘めています。以下、主要なアップデートを深掘りしながら、SRE 視点での活用ポイントを整理していきます。

## 注目アップデート深掘り

### CloudWatch Logs のマネージド syslog インジェション — エージェントレスで実現するログ統合基盤

Amazon CloudWatch Logs が **マネージド syslog インジェション** 機能をリリースしました。これにより、ファイアウォール、ルーター、スイッチ、Linux サーバーなどのネットワークデバイスから syslog メッセージを直接 CloudWatch Logs に送信できるようになります。

#### なぜ重要なのか

従来、ネットワークデバイスのログを CloudWatch Logs に集約するには、Logstash や Fluentd などの log shipper を別途構築・運用する必要がありました。これらの中継基盤は、高可用性を確保するためのクラスタ構成、障害監視、バージョン管理など、運用コストが無視できないレベルで発生します。今回の機能により、デバイス側の設定だけで VPC エンドポイント経由に syslog を送信可能になり、エージェント管理の負担が大幅に削減されます。

#### 対応プロトコルとフォーマット

通信プロトコルとして **TCP、TCP+TLS、UDP** に対応しており、セキュリティ要件に応じて暗号化通信を選択できます。また、RFC 5424（Syslog Protocol）、RFC 3164（旧 BSD Syslog）、Cisco FTD/ASA 形式など、幅広い syslog フォーマットをサポートしているため、既存デバイスの設定をほぼそのまま流用可能です。

#### 自動パース機能による検索性の向上

CloudWatch Logs が syslog メッセージを受信すると、**facility、severity、hostname、application name** などの構造化フィールドを自動抽出します。これにより、カスタムパース処理を書くことなく、Logs Analytics で「severity = ERROR」「hostname = firewall-01」といった条件で直接検索できるようになります。セキュリティイベント調査や接続問題のトラブルシューティングが大幅に効率化されるでしょう。

#### 検証ステップ例

実際の動作確認には、以下のようなステップが考えられます。

1. **VPC エンドポイントの作成**：CloudWatch Logs 用の VPC エンドポイントをプライベートサブネットに配置
2. **デバイス設定**：ルーターやファイアウォールの syslog 送信先をエンドポイント IP に変更
3. **ログ確認**：CloudWatch Logs コンソールまたは CLI でログストリームを確認し、構造化フィールドが正しく抽出されているかを検証
4. **パフォーマンス測定**：高頻度でログを送信し、取り込み遅延やスロットリング発生の有無を観測

従来の log shipper 経由と比較して、インフラ構成がシンプルになり、メンテナンスウィンドウも削減できるはずです。

---

### Lambda MicroVMs — VM レベル分離でユーザーコードを安全に実行

AWS Lambda MicroVMs は、ユーザーや AI が生成したコードを **VM レベルのセキュリティ分離** で実行する新しいサーバーレスコンピューティング基盤です。Firecracker 仮想化技術を採用し、ほぼ瞬時の起動・再開速度と最大 8 時間の状態保持を実現します。

#### なぜこのアップデートが重要なのか

従来の Lambda 関数は、同一ホスト上の複数実行環境が論理的に分離されているものの、マルチテナント SaaS やコーディングプラットフォームでユーザー提供コードを実行する際には、さらに強固な分離が求められるケースがあります。Lambda MicroVMs は、毎月 15 兆以上の Lambda 実行を支える Firecracker を活用し、各ユーザーやジョブごとに独立した仮想マシンを提供します。これにより、仮想化インフラの管理を AWS に委譲しながら、VM レベルの分離を享受できます。

#### 状態保持と長時間実行

Lambda MicroVMs は最大 8 時間の状態保持が可能で、インタラクティブな開発環境や長時間のバッチジョブに適しています。状態を中断・再開できるため、処理の途中でリソースを解放し、必要に応じて再開することでコスト最適化も図れます。

#### 接続性とプロトコル対応

HTTP/2、gRPC、WebSocket に対応しており、リアルタイム通信やストリーミング処理を必要とするアプリケーションにも統合しやすい設計です。

#### 実装の流れ

公式ドキュメントに記載されている手順に沿って、以下のステップで MicroVM を構築できます。

1. **コンテナイメージの準備**：Dockerfile からアプリケーションイメージをビルド
2. **MicroVM の起動**：AWS マネジメントコンソールまたは CloudFormation でリソース定義
3. **動作検証**：起動速度、レイテンシ、状態保持時間を実測
4. **セキュリティ確認**：VM 分離レベルと Firecracker の仕組みを深掘り

従来の Lambda 関数や EC2 インスタンスと比較して、起動速度とセキュリティ分離のバランスが優れている点が魅力です。

---

### Amazon Cognito のカスタマー管理キー対応 — データガバナンスの強化

Amazon Cognito が、ユーザープールのデータ暗号化に **AWS KMS のカスタマー管理キー** をサポートしました。従来の AWS 所有キーに加えて、組織が独自の暗号化キーを管理できるようになり、データガバナンスと監査要件をより厳密に満たせます。

#### カスタマー管理キーの利点

カスタマー管理キーを使用することで、以下のメリットが得られます。

- **キーの無効化・削除によるアクセス即座取り消し**：離職者や不正アクセス発生時に、キーを無効化することで暗号化データへのアクセスを瞬時に遮断
- **AWS CloudTrail による完全な監査**：ID データへのアクセス状況を詳細にトレース可能
- **コンプライアンス要件への対応**：金融・医療などの規制産業で求められるキー管理ポリシーに準拠

Essentials と Plus ティアのユーザープールで追加費用なく利用でき、標準的な KMS 料金のみが発生します。

#### 検証手順

実際の設定では、以下の流れで検証できます。

1. **KMS キーの作成**：AWS KMS コンソールでカスタマー管理キーを作成し、キーポリシーを設定
2. **Cognito ユーザープールの作成**：新規ユーザープール作成時に、カスタマー管理キーを指定
3. **CloudTrail ログの確認**：キー使用イベントを取得し、監査ログの内容を確認
4. **キー無効化テスト**：キーを無効化し、Cognito ユーザープールへのアクセスが遮断されることを検証

既存ユーザープールからの移行については、公式ドキュメントに記載された手順と注意点を事前に確認しておく必要があります。

## SRE 視点での活用ポイント

### ログ統合基盤の簡素化とコスト削減

CloudWatch Logs のマネージド syslog インジェション機能は、既存の log shipper（Logstash、Fluentd など）を廃止する絶好の機会です。Terraform でネットワークデバイスの syslog 設定と VPC エンドポイントを管理している環境であれば、デバイス設定モジュールに syslog 送信先を追加するだけで統合が完了します。CloudWatch Alarms と連携して、特定の severity レベル（CRITICAL、ERROR）のイベント発生時に自動通知を設定すれば、障害対応のランブックに組み込むことも容易です。

導入時の判断基準としては、送信ログ量と KMS 暗号化の要否を事前に見積もり、従来の log shipper 運用コストと比較することが重要です。また、UDP は信頼性が低いため、重要なセキュリティログには TCP+TLS を選択するなど、通信プロトコルの選定にも注意が必要です。

### マルチテナント SaaS のセキュリティ分離

Lambda MicroVMs は、マルチテナント SaaS でユーザー提供コードを実行する際の新しい選択肢となります。従来はコンテナベースの分離やサーバーレス関数の論理分離に頼っていましたが、VM レベルの分離により、セキュリティ要件の高いユースケース（AI コーディングアシスタント、データ分析プラットフォームなど）でも安心して採用できます。

状態保持機能を活用すれば、Jupyter ノートブックのようなインタラクティブ環境を構築し、ユーザーごとに独立したコンピューティング環境を提供できます。導入時のリスクとしては、起動時間やコストモデルが従来の Lambda 関数と異なるため、ベンチマークテストでレイテンシとコストを事前に測定しておくことが推奨されます。

### 暗号化キー管理の一元化とコンプライアンス対応

Cognito のカスタマー管理キー対応は、既存の KMS キー管理体制に Cognito を統合し、組織全体の暗号化ポリシーを統一する好機です。複数ユーザープールを運用している場合、キーローテーションポリシーやアクセス制御を一元管理できるようになります。

注意点としては、キーを誤って削除するとユーザープールへのアクセスが完全に失われるため、キーポリシーと削除保護の設定を慎重に行う必要があります。また、CloudTrail ログの保存期間と監査要件を事前に確認し、ログ分析基盤（Amazon Athena や CloudWatch Logs Insights など）と連携することで、監査対応の自動化を図ることができます。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [Amazon Cognito now supports customer managed key for encryption at rest](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cognito-customer-managed-key) | ユーザープールのデータ暗号化に AWS KMS のカスタマー管理キーをサポート。データガバナンスと監査要件を厳密に満たせるようになった。 |
| [Amazon CloudWatch Logs supports managed syslog ingestion](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cloudwatch-syslog-ingestion/) | ネットワークデバイスから syslog を直接 CloudWatch Logs に送信可能に。エージェントレスで RFC 5424/3164、Cisco 形式に対応。 |
| [Amazon OpenSearch Service now offers AI-assisted migrations](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-opensearch-service-ai-migrations) | Migration Assistant に AI 支援機能を追加。Solr、Elasticsearch、OpenSearch からの移行を AI ツールで加速。 |
| [SageMaker Notebook Instances now support G6e instance types](https://aws.amazon.com/about-aws/whats-new/2026/03/g6e-new-launch-sagemaker-notebook-instances/) | G6e インスタンスタイプ（NVIDIA L40s GPU 搭載）を SageMaker Notebook で利用可能に。G5 比で最大 2.5 倍のパフォーマンス向上。 |
| [AWS HealthOmics now supports ephemeral storage for private workflows](https://aws.amazon.com/about-aws/whats-new/2026/06/healthomics-scratch-storage/) | プライベートワークフローに一時ストレージ機能を追加。デフォルト 16 GiB、最大 3,072 GiB のスクラッチスペースを提供。 |
| [Amazon Bedrock AgentCore Memory now supports cross-account access](https://aws.amazon.com/about-aws/whats-new/2026/06/agentcore-memory-cross-account-access) | AgentCore Memory がクロスアカウントアクセスに対応。マルチアカウントアーキテクチャでメモリリソースを共有可能に。 |
| [Automated Reasoning checks in Amazon Bedrock Guardrails add new policy refinement workflows](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-guardrails/) | Guardrails の Automated Reasoning checks に自動ポリシー改善ワークフローを追加。反復的改善と曖昧性削減を提供。 |
| [AWS Transform for migrations now supports all AWS commercial regions as migration targets](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-transform-migrations-region-expansion/) | 全商用リージョンへの移行をサポート。データレジデンシー要件への対応が柔軟に。 |
| [AWS introduces Lambda MicroVMs for isolated execution of user and AI-generated code](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-lambda-microvms/) | VM レベルのセキュリティ分離を実現する Lambda MicroVMs を発表。最大 8 時間の状態保持と Firecracker 仮想化技術を採用。 |
| [AWS HealthOmics now supports Nextflow profiles](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-healthomics-nextflow-profiles/) | Nextflow profiles に対応。ワークフロー実行時に事前定義された設定をアクティベート可能に。 |

## まとめ

今回紹介したアップデートは、セキュリティ強化と運用効率化の両面で大きな前進を示しています。特に、CloudWatch Logs のマネージド syslog インジェション、Lambda MicroVMs、Cognito のカスタマー管理キー対応は、既存の運用体制を見直す契機となるでしょう。

SageMaker での G6e インスタンス対応や OpenSearch の AI 支援移行機能は、生成 AI ワークロードと大規模データ基盤の運用を加速させます。また、Bedrock Guardrails の自動ポリシー改善ワークフローや HealthOmics の Nextflow profiles 対応は、開発と本番環境の橋渡しを簡素化し、DevOps サイクルの高速化に貢献します。

全体的に、マネージドサービスの範囲が拡大し、インフラ管理の負担が軽減される方向性が見て取れます。今後も、各アップデートの詳細を公式ドキュメントで確認しながら、自社環境への適用可能性を検討していくことが重要です。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)