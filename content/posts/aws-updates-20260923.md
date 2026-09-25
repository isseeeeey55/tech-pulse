---
title: "【AWS】2026/09/23 のアップデートまとめ"
date: 2026-09-23T08:02:15+09:00
draft: false
tags: ["aws", "rds", "route53", "glue", "billing", "securityhub", "bedrock", "evs", "ecs", "outposts", "vmware", "cloudtrail", "inspector"]
categories: ["AWS Updates"]
summary: "2026/09/23 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260923/header.png)

# 今回は、直近で発表された10件のAWSアップデートを紹介します

## はじめに

今回の10件では、生成AIモデルの提供拡大と運用機能の強化が目立ちます。Amazon Bedrock では OpenAI の GPT-6 Sol と GPT-6 Luna が一般提供となり、Claude Opus 5.5 も AWS（GovCloud (US) を含む）で利用可能になりました。運用面では、AWS Glue Data Quality のルール推奨に生成AIを使う Advanced mode、Amazon ECS コンソールでのデプロイのリアルタイム可観測性、Security Hub AI Inventory の Azure 対応が追加されています。

本記事では Glue Data Quality と ECS の2件を深掘りし、SRE 視点での活用ポイントを解説します。

## 注目アップデート深掘り

### AWS Glue Data Quality：Advanced mode でルールを数秒で生成

AWS Glue Data Quality が、AWS Glue Data Catalog のテーブルに対するデータ品質ルールを数秒で生成できるようになりました。ルール推奨の新しい **Advanced mode** では、生成AIがデータの意図を検出し、データの使われ方を反映したビジネス上意味のあるルールを提案します。手作業の設定なしで、すべてのカラムをカバーするルールセットが得られます。

告知が挙げる使い方は次の2つです。

- 新しくオンボードしたデータセットのルールを一から用意する
- 大規模なデータレイク全体に、ルールを1つずつ手書きせずにベースラインのチェックを設ける

推奨ルールは確認して必要に応じて調整し、ルールセットとして保存すると、すぐに監視が始まります。

対応リージョンは、アジアパシフィック（メルボルン、大阪、シドニー、東京）、カナダ（中部）、欧州（フランクフルト、アイルランド、ロンドン、ミラノ、パリ、スペイン、ストックホルム、チューリッヒ）、米国東部（バージニア北部、オハイオ）、米国西部（北カリフォルニア、オレゴン）です。

### Amazon ECS：コンソールでデプロイをリアルタイムに可観測化

Amazon ECS コンソールで、ネイティブの Linear / Canary / Blue/Green デプロイ戦略について、サービスのデプロイをリアルタイムに追跡できるようになりました。デプロイの追跡とトラブルシューティングを1か所で行え、複数のツールを行き来する必要がなくなります。

告知に記載された主な表示内容は次の通りです。

- **ライブのデプロイタイムライン**: デプロイの各フェーズ、サービスイベント、タスクの起動・終了の進捗を、デプロイの進行に合わせて表示
- **タイムラインと並ぶ状態表示**: サーキットブレーカーの状態とタスク失敗のライブ監視、デプロイアラームの状態、コンテナとロードバランサーのヘルスチェック、ライフサイクルフックの状態
- **失敗時の診断**: 失敗したタスクが診断コンテキストとともにタイムラインに表示され、AWS CloudTrail などへのディープリンクから根本原因を特定できる

追加料金なしで、すべての AWS 商用リージョンと AWS GovCloud (US) リージョンの、ネイティブ Linear / Canary / Blue/Green デプロイを使う ECS サービスで利用できます。

## SRE視点での活用ポイント

### Glue Data Quality の Advanced mode

- データ品質チェックが未整備のテーブルに、まず Advanced mode でベースラインのルールを作り、レビューしてから保存する進め方が取れます
- 推奨ルールはそのまま採用せず、組織固有のビジネスルールや許容範囲を踏まえて調整します。厳しすぎるルールは誤検知につながるため、運用開始直後は検知結果を見ながら見直します

### ECS デプロイの可観測性

- オンコール時に「障害がデプロイに起因するか」を確認する際、デプロイタイムライン上でタスク失敗やアラーム状態を追えます
- 失敗タスクから CloudTrail などへのディープリンクをたどれるため、原因調査の起点として使えます
- 対象はネイティブの Linear / Canary / Blue/Green デプロイを使うサービスなので、自サービスのデプロイ方式が該当するかを確認します

### Security Hub AI Inventory の Azure 対応

Security Hub AI Inventory が、Microsoft Azure 上のセルフホストインスタンスで動く AI アセットの検出とカタログ化に対応しました。Amazon Inspector の SBOM 分析が拡張され、Azure の仮想マシンにインストールされた推論エンドポイント、モデル、AI エージェント（Ollama、vLLM、Hugging Face TGI などのフレームワークを含む）を識別します。検出した AI アセットは基盤のインフラに対応付けられ、セキュリティ検出結果と関連付けられます。AWS と Azure をまたいで AI インベントリを絞り込み・グループ化・クエリでき、Security Hub Essentials に追加料金なしで含まれます。

## まとめ

Bedrock での GPT-6 Sol / Luna の一般提供と Claude Opus 5.5 の提供開始により、利用できる生成AIモデルが増えました。運用面では、Glue Data Quality の Advanced mode によるルールの自動生成、ECS コンソールでのデプロイのリアルタイム可観測性、Security Hub AI Inventory の Azure 対応が加わっています。このほか、RDS Custom for SQL Server の最新 CU 対応、第2世代 Outposts ラックでの Route 53 Resolver の一般提供、Billing Transfer の請求グループ自動作成、Amazon EVS の FedRAMP Class C 対象範囲入りがありました。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| Amazon RDS Custom | SQL Server 2022 CU26（KB5093420、RDS バージョン 16.00.4265.3.v1）に対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-rds-custom-supports-latest-cu-gdr-microsoft-sql-server/) |
| Route 53 Resolver | 第2世代 AWS Outposts で一般提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/route-53-resolver-gen2-outposts/) |
| AWS Glue Data Quality | ルール推奨の Advanced mode を追加。生成AIでデータの意図を検出し、全カラムのルールを数秒で生成 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/glue-data-quality-rule-recommendations/) |
| AWS Billing | Billing Transfer の自動請求グループ作成機能追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-billing-transfer-supports-automatic-billing-group-creation/) |
| Security Hub | AI Inventory が Azure セルフホストインスタンス対応 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/security-hub-ai-inventory-azure-support/) |
| Amazon Bedrock | OpenAI GPT-6 Sol & Luna モデル一般提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/openai-gpt-6-sol-luna-on-amazon-bedrock/) |
| Amazon Bedrock | Claude Opus 5.5 利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/claude-opus-5-5-aws/) |
| Amazon Bedrock (GovCloud) | Claude Opus 5.5 が GovCloud (US) で利用可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/claude-opus-5-5-aws-govcloud/) |
| Amazon EVS | 米国の全リージョンで FedRAMP Class C（旧 Moderate ベースライン）の対象範囲に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-evs-fedramp-class-c/) |
| Amazon ECS | Linear / Canary / Blue/Green デプロイのリアルタイム可観測性をコンソールに追加（追加料金なし） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ecs-console-deployment-observability/) |

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)