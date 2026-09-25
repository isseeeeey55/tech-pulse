---
title: "【AWS】2026/09/10 のアップデートまとめ"
date: 2026-09-10T08:02:12+09:00
draft: false
tags: ["aws", "lambda", "connect", "systems-manager", "bedrock", "api-gateway", "sagemaker", "timestream", "ec2"]
categories: ["AWS Updates"]
summary: "2026/09/10 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260910/header.png)

# 今回は、直近で発表された11件のAWSアップデートを紹介します

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。Lambda Managed Instances での90分タイムアウトと Graviton5 対応、OpenAI GPT-6 Astra の Amazon Bedrock での一般提供など、コンピューティングとAIの領域の機能強化が並びます。また、運用効率を高める Systems Manager の診断機能拡張、SageMaker Feature Store の書き込み最適化、API Gateway のバックエンドmTLS対応など、エンタープライズ運用に直結する改善も含まれています。本記事では Lambda の90分タイムアウトと AWS Transform for .NET の CLI 対応を深掘りし、SRE視点での活用ポイントを整理します。

## 注目アップデート深掘り

### AWS Lambda 90分タイムアウト対応 - 長時間実行ワークロードのサーバーレス化

AWS Lambda が Lambda Managed Instances 上で、非同期呼び出しおよびイベントソースマッピング（ESM）呼び出しに対して、関数タイムアウトを最大90分に拡張しました。これまでの15分制限から6倍の拡張となります。

#### なぜこのアップデートが重要なのか

告知によると、メディアトランスコーディング、金融計算（モンテカルロシミュレーションなど）、AI 推論のように長い連続実行が必要なワークロードでは、15分の制限のためにアーキテクチャ上の回避策が必要でした。今回の変更で、こうしたジョブをアプリケーションを作り直さずに Lambda で実行できます。

#### Lambda Managed Instances とは

告知では Lambda Managed Instances を、インフラを管理せずに、インスタンスごとに複数の同時リクエストを処理し、特殊なコンピュート構成を使い、EC2 の価格面の利点でコスト効率を高められるものと説明しています。

#### タイムアウト拡張の適用範囲と制約

重要な点として、90分タイムアウトは**非同期呼び出しとイベントソースマッピング（ESM）呼び出しのみ**に適用されます。同期呼び出しは従来通り15分制限のままです。この違いを理解した上で、ワークロードの呼び出しパターンを設計する必要があります。

非同期呼び出しは呼び出し元がレスポンスを待たない呼び出し方（S3 イベント通知や EventBridge など）、ESM 呼び出しは SQS・Kinesis・DynamoDB Streams などのイベントソースを Lambda がポーリングして実行する呼び出し方です。

#### Durable Functions との組み合わせ

延長されたタイムアウトは、ステップのチェックポイントと再生ができる Lambda durable functions 内の呼び出しにも適用されます。非同期で呼び出した場合、複数ステップの durable execution は最長1年間実行できます。

#### 設定方法

90分までのタイムアウトは、Lambda コンソール、AWS CLI、Lambda API、IaC ツール、Agent Toolkit for AWS で設定できます。Lambda Managed Instances が提供されているすべてのリージョンで利用できます。

> **Note:** 実装時は、タイムアウト延長に伴うエラーハンドリング、リトライ戦略、コスト試算を事前に検討してください。同じワークロードを ECS や EC2 で実行する場合との価格比較も重要です。

### AWS Transform for .NET - CLI による大規模モダナイゼーション自動化

AWS Transform custom で、AWS が管理する .NET モダナイゼーション用の変換が一般提供され、1行の CLI コマンドで実行できるようになりました。対話的に実行することも、既存のパイプラインやワークフローにスクリプトとして組み込んで自律的に実行することもできます。

#### AWS Transform の機能

AWS Transform は、AWS 管理の変換とカスタム変換を組み合わせて、大規模なコード変換を実現します。対応する変換タスクは以下の通りです：

- 言語バージョンのアップグレード
- フレームワークの移行
- パフォーマンス最適化
- コードベース分析

CLI は、既存の AWS Transform for .NET の提供形態（Web アプリケーション、Visual Studio IDE、Kiro Power、MCP エージェント）を補完するものです。

#### CLI の利点：対話的実行と自動化の両立

CLI 対応により、以下の2つの運用パターンが可能になります：

**対話的実行**: 開発者が手元で変換を実行し、結果を確認しながら進められます。

**自律的な実行**: 既存のパイプラインやワークフローにスクリプトとして組み込んで実行できます。

#### コスト効率

.NET モダナイゼーションの変換には、毎月 50,000 エージェント分（agent minutes）の無料枠が含まれます。

#### 利用可能リージョン

AWS Transform custom と AWS Transform for .NET は、米国東部（バージニア北部）、アジアパシフィック（ムンバイ、東京、ソウル、シドニー）、カナダ（中部）、欧州（フランクフルト、ロンドン）の8リージョンで利用できます。

> **Note:** 具体的な CLI コマンド体系や設定ファイルフォーマットについては、AWS 公式ドキュメントを参照してください。移行対象のアプリケーションの複雑さによって、変換後の手動調整が必要になるケースもあります。

## SRE視点での活用ポイント

### Lambda 90分タイムアウトの運用シナリオ

15分に収まらないという理由で Lambda 以外を選んでいたワークロードのうち、非同期または ESM で呼び出すものは、Lambda Managed Instances 上で実行する選択肢が生まれました。

ただし、導入前には以下の点を検討すべきです：

- **コスト試算**: Lambda Managed Instances は EC2 価格ベースのため、既存の ECS や EC2 運用と比較して TCO を算出する
- **リトライ戦略**: 長時間実行の失敗時の影響範囲を考慮し、適切なエラーハンドリングとリトライポリシーを設計する
- **呼び出し方式**: 同期呼び出しは引き続き15分が上限のため、対象ワークロードが非同期または ESM で呼び出されているかを確認する

### Systems Manager の診断機能拡張による障害対応の効率化

Systems Manager の診断機能が、EC2 インスタンスやハイブリッドアクティベーションしたノードが Systems Manager の管理対象にならない原因について、新たに6つのカテゴリ（IAM 権限、SSM Agent のバージョン、インスタンスのステータスチェック、OS の設定、Default Host Management Configuration、ハイブリッドアクティベーション）を識別できるようになりました。

一部の問題は、コンソールから Systems Manager Automation のランブックを実行して解消できます。

新しくデプロイしたインスタンスが Systems Manager に管理されない場合の切り分けに使えます。

注意点として、実行したランブックには通常の Automation 使用料がかかります。

### .NET モダナイゼーションの段階的導入

AWS Transform for .NET の CLI 対応により、.NET のモダナイゼーションを既存のパイプラインに組み込めるようになりました。まず小規模なプロジェクトで変換結果を検証し、段階的に対象を広げる進め方が取れます。

パイプラインに組み込む場合は、変換後のコードのレビューとテストを必ず通す構成にします。毎月 50,000 エージェント分の無料枠の範囲で試し、変換結果と手作業での調整量を確かめてから対象を広げられます。

## 全アップデート一覧

| サービス | アップデート概要 | リンク |
|---------|----------------|--------|
| Amazon Connect | タスクとメールに対して個別の容量制限を設定可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-connect-capacity-limits/) |
| AWS Transform | .NET モダナイゼーションの AWS 管理変換が一般提供、1行の CLI コマンドで実行可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-transform-dotnet-cli) |
| AWS Lambda | Lambda Managed Instances で90分タイムアウトをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-lambda-90-minute-function/) |
| AWS Systems Manager | EC2 インスタンスが管理対象外になる原因の診断に6カテゴリを追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/systems-manager-diagnoses-ec2-unmanaged/) |
| AWS Lambda | Graviton5 搭載 EC2 インスタンスをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-lambda-graviton5-ec2/) |
| Amazon Bedrock | Confluence Data Center をネイティブデータソースコネクタとして対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-bedrock-managed-knowledge-base-confluence-data-center-native-data-source-connector/) |
| Amazon Bedrock | ドキュメントレベルアクセス制御のデバッグ用 API とコンソール機能を追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-bedrock-knowledge-base-debugging-document-access-control/) |
| Amazon API Gateway | バックエンド統合向けの相互TLS（mTLS）をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-api-gateway-mutual-tls-backend/) |
| Amazon Bedrock | OpenAI GPT-6 Astra を一般提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/openai-gpt-6-astra-on-amazon-bedrock/) |
| Amazon SageMaker | Feature Store で個別フィーチャー更新をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/08/sgm-feature-store-update-record/) |
| Amazon Timestream | InfluxDB 3 でカスタム Python プラグインをサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/timestream-influxdb-custom-plugins/) |

## まとめ

今回紹介したアップデートは、大きく3つのテーマに分類できます。

1つ目は、**コンピューティングの柔軟性向上**です。Lambda Managed Instances で、非同期・ESM 呼び出しの90分タイムアウトと Graviton5 搭載 EC2 インスタンスがサポートされました。

2つ目は、**AIと生成系サービスの強化**です。OpenAI GPT-6 Astra の Bedrock 対応、Confluence Data Center のネイティブコネクタ追加、ドキュメントレベルアクセス制御のデバッグ機能など、Bedrock まわりの機能が追加されています。

3つ目は、**運用効率と自動化の改善**です。Systems Manager の診断機能拡張、AWS Transform の CLI 対応、SageMaker Feature Store の書き込み最適化、Timestream のカスタムプラグインなど、運用まわりの改善が加わりました。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)