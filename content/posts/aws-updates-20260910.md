---
title: "【AWS】2026/09/10 のアップデートまとめ"
date: 2026-09-10T08:02:12+09:00
draft: true
tags: ["aws", "lambda", "connect", "systems-manager", "bedrock", "api-gateway", "sagemaker", "timestream", "ec2"]
categories: ["AWS Updates"]
summary: "2026/09/10 のAWSアップデートまとめ"
---

# 直近のAWSアップデート11件まとめ - Lambda 90分タイムアウト、Graviton5対応、GPT-6 Astra登場など

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。Lambda の大幅なタイムアウト拡張、最新の Graviton5 プロセッサ対応、OpenAI GPT-6 Astra の Amazon Bedrock での提供開始など、コンピューティングとAIの領域で注目すべき機能強化が揃いました。また、運用効率を高める Systems Manager の診断機能拡張、SageMaker Feature Store の書き込み最適化、API Gateway のバックエンドmTLS対応など、エンタープライズ運用に直結する改善も含まれています。本記事では、特に影響範囲が大きいと思われるアップデートを深掘りし、SRE視点での活用ポイントを整理します。

## 注目アップデート深掘り

### AWS Lambda 90分タイムアウト対応 - 長時間実行ワークロードのサーバーレス化

AWS Lambda が Lambda Managed Instances 上で、非同期呼び出しおよびイベントソースマッピング（ESM）呼び出しに対して、関数タイムアウトを最大90分に拡張しました。これまでの15分制限から6倍の拡張となります。

#### なぜこのアップデートが重要なのか

従来、Lambda の15分制限により、メディアトランスコーディング、金融計算、AI推論、バッチ処理といった長時間実行が必要なワークロードは、Step Functions で分割実行するか、ECS や EC2 などの別サービスへの移行を余儀なくされていました。今回のアップデートにより、アプリケーションの再設計なしに Lambda でこれらのワークロードを実行できるようになります。

#### Lambda Managed Instances とは

Lambda Managed Instances は、EC2 インスタンス上で Lambda 関数を実行しながら、Lambda の運用シンプルさを維持できるサービスです。インスタンスのライフサイクル管理、OS・ランタイムパッチ、ルーティング、ロードバランシング、オートスケーリングなどがすべて自動管理されるため、インフラ管理の負担なく EC2 の価格メリットを活用できます。また、インスタンスごとに複数の同時リクエストを処理でき、特殊なコンピュート構成にアクセス可能です。

#### タイムアウト拡張の適用範囲と制約

重要な点として、90分タイムアウトは**非同期呼び出しとイベントソースマッピング（ESM）呼び出しのみ**に適用されます。同期呼び出しは従来通り15分制限のままです。この違いを理解した上で、ワークロードの呼び出しパターンを設計する必要があります。

非同期呼び出しは、API Gateway、EventBridge、S3 イベント通知などから Lambda を起動する際に利用され、呼び出し元はレスポンスを待たずに処理を続行できます。ESM 呼び出しは、SQS、Kinesis、DynamoDB Streams などのイベントソースから Lambda が自動的にポーリングして実行するパターンです。

#### Durable Functions との組み合わせ

さらに、Lambda の Durable Functions（チェックポイントと再生機能を備えた長時間実行処理）と組み合わせると、非同期呼び出し時には最大1年間の実行も可能になります。これにより、極めて長時間にわたるワークフローや、中断・再開が必要な複雑なビジネスプロセスも Lambda で実装できるようになりました。

#### 設定方法

90分タイムアウトは、AWS Console、CLI、API、IaC ツール、Agent Toolkit で設定可能です。Lambda Managed Instances を利用するには、キャパシティプロバイダーの設定と、関数のタイムアウト値を90分以内で指定します。

> **Note:** 実装時は、タイムアウト延長に伴うエラーハンドリング、リトライ戦略、コスト試算を事前に検討してください。同じワークロードを ECS や EC2 で実行する場合との価格比較も重要です。

### AWS Transform for .NET - CLI による大規模モダナイゼーション自動化

AWS Transform for .NET モダナイゼーションが CLI 経由で一般利用可能になりました。この機能は、1行のコマンドを実行するだけで、.NET アプリケーションの現代化を自動的に行うことができます。

#### 背景：レガシー .NET の課題

多くの企業が .NET Framework で構築されたレガシーアプリケーションを抱えており、.NET Core や .NET 9 への移行は、互換性の問題や膨大な手作業が必要となるため、後回しにされがちです。特に大規模なコードベースでは、言語バージョンのアップグレード、フレームワークの移行、パフォーマンス最適化を手動で実施するには、数ヶ月から数年の工数がかかることも珍しくありません。

#### AWS Transform の機能

AWS Transform は、AWS 管理の変換とカスタム変換を組み合わせて、大規模なコード変換を実現します。対応する変換タスクは以下の通りです：

- 言語バージョンのアップグレード（.NET Framework → .NET Core/.NET 9）
- フレームワークの移行
- パフォーマンス最適化
- コードベース分析

これまで Web アプリケーション、Visual Studio IDE、Kiro Power、MCP エージェントの経験として提供されていましたが、CLI での操作も可能になり、より柔軟な運用が実現できます。

#### CLI の利点：対話的実行と自動化の両立

CLI 対応により、以下の2つの運用パターンが可能になります：

**対話的実行**: 開発者が手元で変換を試行し、結果を確認しながら段階的に移行を進めることができます。変換結果のレビュー、問題箇所の特定、カスタムルールの調整を繰り返しながら、安全に移行を進められます。

**自動実行**: CI/CD パイプライン（GitHub Actions、AWS CodePipeline など）に組み込んで、自動的なコード現代化を実行できます。これにより、複数のプロジェクトにおける言語バージョン統一の自動化や、社内カスタムルールをベースにした組織固有の変換ポリシーの適用が可能になります。

#### コスト効率

AWS Transform は月額50,000単位の無料枠が提供されます。この無料枠で実行可能な変換タスク量を試算し、ROI 分析を行うことで、導入判断の材料にできます。

#### 利用可能リージョン

現在、8つのリージョンでサポートされています。実装時は、対象リージョンでのサービス可用性とレイテンシーを考慮してください。

> **Note:** 具体的な CLI コマンド体系や設定ファイルフォーマットについては、AWS 公式ドキュメントを参照してください。移行対象のアプリケーションの複雑さによって、変換後の手動調整が必要になるケースもあります。

## SRE視点での活用ポイント

### Lambda 90分タイムアウトの運用シナリオ

Lambda の90分タイムアウト拡張は、バッチ処理やデータパイプラインのサーバーレス化を検討しているチームにとって大きな選択肢となります。従来は「Lambda では15分以内に収まらない」という理由で ECS や EC2 を選択していたワークロードを、インフラ管理なしで実行できるようになります。

特に、定期的なレポート生成、ログ解析、ETL パイプラインなど、スケジュール実行が中心のワークロードでは、EventBridge と Lambda の組み合わせで完結させることができます。CloudWatch アラームと組み合わせると、実行時間の監視や異常検知も容易になります。

ただし、導入前には以下の点を検討すべきです：

- **コスト試算**: Lambda Managed Instances は EC2 価格ベースのため、既存の ECS や EC2 運用と比較して TCO を算出する
- **リトライ戦略**: 長時間実行の失敗時の影響範囲を考慮し、適切なエラーハンドリングとリトライポリシーを設計する
- **監視**: 実行時間の増加に伴い、CloudWatch Logs や X-Ray による詳細なトレースが重要になる

Terraform で管理しているインフラがあれば、Lambda Managed Instances のリソース定義と、タイムアウト値の変更を IaC で管理することで、環境間の一貫性を保てます。

### Systems Manager の診断機能拡張による障害対応の効率化

Systems Manager の診断機能が6つの新しい問題カテゴリに対応したことで、EC2 インスタンスが管理対象外になる問題のトラブルシューティングが大幅に効率化されます。従来は「なぜこのインスタンスが Systems Manager に表示されないのか」を調査するために、IAM ポリシー、ネットワーク設定、SSM Agent のログなど、複数箇所を手動で確認する必要がありました。

新機能では、統一されたコンソール経験から複数インスタンスの診断を実行でき、具体的で対応可能な原因が提示されます。多くの問題は Automation ランブックで自動修復可能なため、障害対応のランブックに組み込むと、オンコール対応時の手順簡素化につながります。

特に、大規模な EC2 フリートを運用している環境では、パッチ管理や Session Manager 導入時の前提条件チェックを自動化できる点が有用です。新しい環境にデプロイしたインスタンスが Systems Manager に自動接続できない問題も、診断機能で迅速に原因を特定し、修復できます。

注意点として、診断には Standard Automation 使用料が発生するため、大量のインスタンスを頻繁に診断する場合はコストを考慮する必要があります。

### .NET モダナイゼーションの段階的導入

AWS Transform for .NET の CLI 対応により、レガシー .NET アプリケーションのモダナイゼーションを CI/CD パイプラインに組み込む選択肢が生まれました。一度に全体を移行するのではなく、まず小規模なプロジェクトで変換精度と品質を検証し、段階的に対象を広げるアプローチが現実的です。

GitHub Actions や AWS CodePipeline のワークフローに組み込む際は、変換後のコードレビューと単体テストを必須プロセスとして組み込むことで、自動変換の副作用を早期に検出できます。また、社内カスタムルールをベースにした組織固有の変換ポリシーを定義することで、コーディング規約やセキュリティ要件を自動的に適用できます。

判断基準としては、月額50,000単位の無料枠で試験的に運用し、変換品質と手動調整の工数を測定してから、本格導入を検討するのが妥当です。

## 全アップデート一覧

| サービス | アップデート概要 | リンク |
|---------|----------------|--------|
| Amazon Connect | タスクとメールに対して個別の容量制限を設定可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-connect-capacity-limits/) |
| AWS Transform | .NET モダナイゼーションが CLI で一般利用可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-transform-dotnet-cli) |
| AWS Lambda | Lambda Managed Instances で90分タイムアウトをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-lambda-90-minute-function/) |
| AWS Systems Manager | EC2 インスタンスが管理対象外になる原因の診断機能を拡張 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/systems-manager-diagnoses-ec2-unmanaged/) |
| AWS Lambda | Graviton5 搭載 EC2 インスタンスをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-lambda-graviton5-ec2/) |
| Amazon Bedrock | Confluence Data Center をネイティブデータソースコネクタとして対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-bedrock-managed-knowledge-base-confluence-data-center-native-data-source-connector/) |
| Amazon Bedrock | ドキュメントレベルアクセス制御のデバッグ用 API とコンソール機能を追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-bedrock-knowledge-base-debugging-document-access-control/) |
| Amazon API Gateway | バックエンド統合向けの相互TLS（mTLS）をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-api-gateway-mutual-tls-backend/) |
| Amazon Bedrock | OpenAI GPT-6 Astra を一般提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/openai-gpt-6-astra-on-amazon-bedrock/) |
| Amazon SageMaker | Feature Store で個別フィーチャー更新をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/sgm-feature-store-update-record/) |
| Amazon Timestream | InfluxDB 3 でカスタム Python プラグインをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/timestream-influxdb-custom-plugins/) |

## まとめ

今回紹介したアップデートは、大きく3つのテーマに分類できます。

1つ目は、**コンピューティングの柔軟性向上**です。Lambda の90分タイムアウト拡張と Graviton5 対応により、サーバーレスで実行できるワークロードの範囲が大幅に広がりました。従来は ECS や EC2 を選択せざるを得なかった長時間実行タスクも、インフラ管理なしで実行できる選択肢が増えたことは、運用効率の観点で大きな前進です。

2つ目は、**AIと生成系サービスの強化**です。OpenAI GPT-6 Astra の Bedrock 対応、Confluence Data Center のネイティブコネクタ追加、ドキュメントレベルアクセス制御のデバッグ機能など、エンタープライズ環境で生成 AI を実用化するための機能が充実してきています。特に、Knowledge Base の運用性向上は、本番環境での AI エージェント導入を検討する上で重要なマイルストーンとなります。

3つ目は、**運用効率と自動化の改善**です。Systems Manager の診断機能拡張、AWS Transform の CLI 対応、SageMaker Feature Store の書き込み最適化、Timestream のカスタムプラグインなど、日常の運用作業を効率化し、自動化の幅を広げる機能が揃いました。これらは地味に見えますが、SRE チームの日常業務の負担を軽減し、より戦略的な取り組みに時間を使えるようになる重要な改善です。

全体として、サーバーレスとAIの領域でのイノベーション、そして運用効率化のための地道な改善が並行して進んでいる状況が見て取れます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)