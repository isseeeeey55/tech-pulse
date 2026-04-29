---
title: "【AWS】2026/04/29 のアップデートまとめ"
date: 2026-04-29T08:02:33+09:00
draft: false
tags: ["aws", "bedrock", "workspaces", "ec2", "cost-optimization-hub", "glue", "kms", "redshift", "billing-conductor", "connect"]
categories: ["AWS Updates"]
summary: "2026/04/29 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260429/header.png)

# 2026年4月29日 AWS アップデート情報

## はじめに

2026年4月29日は、AWS から **15件** のアップデートがリリースされました。注目すべきは、**Amazon Bedrock への OpenAI モデル統合**と **Amazon Quick の大規模拡張**です。Bedrock では OpenAI の最新モデル、Codex、Managed Agents がリミテッドプレビューで提供開始され、エンタープライズセキュリティを保ちながら最先端の生成AI を利用できるようになりました。一方、Amazon Quick は無料プランの提供開始、Google Workspace や Zoom などの大量統合、デスクトップアプリ版リリース、ドキュメント・ビジュアル生成機能の追加など、一気に機能拡充が進みました。

また、Amazon Redshift Serverless では AI 駆動スケーリングがデフォルト化され、運用負荷の大幅な軽減が期待できます。WorkSpaces Personal の PCoIP から DCV への移行強化、AWS KMS でのキー使用状況追跡、AWS Glue 5.1 の対応リージョン拡大など、運用効率化・セキュリティ強化に関わるアップデートが目立つ一日となりました。

---

## 注目アップデート深掘り

### 1. Amazon Bedrock で OpenAI モデル、Codex、Managed Agents が利用可能に（リミテッドプレビュー）

#### なぜこのアップデートが重要なのか

AWS と OpenAI の提携拡大により、Amazon Bedrock 経由で OpenAI の最新モデルが利用可能になりました。これまで企業が OpenAI モデルを本番環境で利用する際、セキュリティ、ガバナンス、監査要件との両立が課題でした。今回のアップデートにより、Bedrock の既存エンタープライズ機能（IAM、AWS PrivateLink、ガードレール、暗号化、CloudTrail ログ）をそのまま活用しながら、OpenAI の最先端モデルを統合できるようになります。

また、**OpenAI Codex** が Bedrock 経由で利用可能になったことで、CLI、VS Code 拡張、デスクトップアプリを通じたコード生成・保守タスクの自動化が AWS 環境内で完結します。さらに、**Bedrock Managed Agents** は本番環境対応の OpenAI 駆動エージェントを高速デプロイできる仕組みで、各エージェントが独自の ID を持ち全アクションをログ記録するため、監査・コンプライアンス要件の厳しい業界でも安心して導入できます。

#### 技術的な背景と従来の課題

従来、OpenAI のモデルを直接利用する場合、AWS 外部の API エンドポイントへアクセスする必要があり、以下のような課題がありました。

- **ネットワークセキュリティ**: パブリックインターネット経由の通信が必須で、PrivateLink によるプライベート接続が不可能
- **IAM 統合の欠如**: AWS IAM ポリシーでのアクセス制御ができず、独自の認証・認可の仕組みが必要
- **監査証跡の分断**: CloudTrail でのログ記録ができず、監査対応のためのログ統合が煩雑
- **コスト管理**: AWS のクラウドコミットメントに含めることができず、別途契約・請求管理が必要

今回の Bedrock 統合により、これらの課題がすべて解決されます。

#### 具体的な利用イメージ

Bedrock 経由で OpenAI モデルを呼び出す場合、既存の Bedrock API をそのまま使用できます。以下は AWS CLI を使った呼び出し例です。

```bash
$ aws bedrock-runtime invoke-model \
  --model-id openai.gpt-4o \
  --region us-east-1 \
  --body '{"prompt": "Explain quantum computing in simple terms", "max_tokens": 100}' \
  response.json
```

IAM ポリシーで特定のユーザーやロールに対して、OpenAI モデルへのアクセスを制限することも可能です。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:us-east-1::foundation-model/openai.gpt-4o"
    }
  ]
}
```

また、AWS PrivateLink を利用することで、インターネットを経由せずにプライベートネットワーク内でモデルを呼び出すことができます。

#### Codex と Managed Agents の活用

**OpenAI Codex** は、CLI や VS Code 拡張から利用できます。開発者は IDE 内で直接コード生成・補完を受けることができ、生成されたコードはすべて AWS 環境内でログ記録されます。

**Bedrock Managed Agents** は、複雑なマルチステップのビジネスプロセスを自動実行するエージェントを高速デプロイできます。各エージェントは独立した ID を持ち、実行したすべてのアクションが CloudTrail に記録されるため、「誰が」「いつ」「何を」実行したかを追跡できます。これは金融・医療などの規制業界で特に重要な機能です。

#### コスト面でのメリット

OpenAI と Codex の利用料金は、AWS のクラウドコミットメント（Enterprise Discount Program など）に適用可能です。これにより、既存の AWS 利用額と合算してボリュームディスカウントを受けられる可能性があります。

> **Note:** リミテッドプレビューのため、利用にはプレビュー申請が必要です。詳細は AWS 公式ページを参照してください。

---

### 2. Amazon Redshift Serverless が AI 駆動スケーリングをデフォルトで有効化

#### なぜこのアップデートが重要なのか

Amazon Redshift Serverless では、これまで手動でのリソース調整やキャパシティ設定が必要でした。今回のアップデートにより、すべての新規ワークグループで **AI 駆動スケーリングがデフォルト有効** となり、機械学習を使用してコンピュートニーズを予測し、クエリがキューに溜まる前に自動的にリソースを調整します。これにより、DBA やデータエンジニアの運用負荷が大幅に削減され、手動チューニングなしに優れた価格性能が実現されます。

また、サポート対象の RPU 範囲が **32～512 RPU から 8～512 RPU に拡大** されたことで、スタートアップや小規模環境でも低コストで導入できるようになりました。

#### 従来の課題とビフォーアフター

**ビフォー（手動チューニング時代）**

- クエリのピーク時に手動でコンピュートリソースを増やす必要があった
- リソース不足によるクエリのキューイングやタイムアウトが頻発
- オフピーク時の過剰リソースでコストが無駄に発生
- パフォーマンス調整のために DBA の専門知識と定期的なモニタリングが必須

**アフター（AI 駆動スケーリング）**

- ワークロードパターンを自動学習し、クエリの複雑さ、データ量、スキャンサイズに基づいてリアルタイムでリソース調整
- クエリがキューに溜まる前にスケールアップするため、レスポンスタイムが安定
- オフピーク時は自動的にスケールダウンしてコスト削減
- 手動チューニング不要で、DBA の運用負荷が大幅に軽減

#### 価格性能スライダーの活用

AI 駆動スケーリングでは、**価格性能スライダー** を使用して運用方針を選択できます。

- **コスト優先**: 最小限のリソースで運用し、コストを最優先
- **バランス**: コストとパフォーマンスのバランスを取る（デフォルト）
- **パフォーマンス優先**: レスポンス速度を最優先し、リソースを積極的に割り当て

これにより、BI ダッシュボードのような低遅延が求められる用途では「パフォーマンス優先」、バッチ処理のようなコスト重視の用途では「コスト優先」といった使い分けが可能です。

#### 自動最適化機能の追加

AI 駆動スケーリングには、以下の自動最適化機能も含まれています。

- **自動マテリアライズドビュー**: 頻繁に実行されるクエリを自動検出し、マテリアライズドビューを作成してクエリ性能を向上
- **自動テーブル設計最適化**: テーブルのソートキーやディストリビューションスタイルを自動最適化

これらの機能により、データベース設計の知識がなくても、最適なパフォーマンスを引き出すことができます。

#### 設定方法

新規ワークグループではデフォルトで有効ですが、既存ワークグループでも AWS Management Console や API から有効化できます。

```bash
$ aws redshift-serverless update-workgroup \
  --workgroup-name my-workgroup \
  --ai-driven-scaling-enabled \
  --performance-target balanced
```

#### コスト削減のシミュレーション

8 RPU からの運用が可能になったことで、従来 32 RPU が最小だった環境と比較すると、エントリーコストが **約 75% 削減** されます。これにより、開発環境やテスト環境でも Redshift Serverless を気軽に利用できるようになります。

> **Note:** AI 駆動スケーリングは、ワークロードパターンを学習するため、導入初期は最適な調整まで数日かかる場合があります。

---

## SRE視点での活用ポイント

### Bedrock での OpenAI 統合を本番環境で安全に使う

エンタープライズ環境で生成 AI を本番投入する際、SRE が最も気にするのは「セキュリティ」「可観測性」「コスト管理」の3点です。Bedrock を経由することで、IAM によるアクセス制御、PrivateLink によるプライベート接続、CloudTrail によるすべての API コールのログ記録が可能になります。

たとえば、Terraform で Bedrock の IAM ポリシーを管理しているインフラがあれば、既存のコード資産をそのまま流用して OpenAI モデルへのアクセス制御を実装できます。また、CloudWatch メトリクスと組み合わせて、モデル呼び出しの遅延やエラー率をモニタリングし、アラートを設定することも容易です。

導入時の判断基準としては、「社内にすでに Bedrock を使った基盤があるか」「OpenAI モデルの利用頻度がどの程度か」「コンプライアンス要件としてログ記録が必須か」といった観点で検討すると良いでしょう。リスクとしては、リミテッドプレビュー段階のため、GA までに API 仕様が変更される可能性がある点に注意が必要です。

### Redshift Serverless の AI 駆動スケーリングで運用を自動化

データウェアハウスの運用では、ピーク時のパフォーマンス確保とコスト最適化の両立が常に課題です。AI 駆動スケーリングがデフォルトで有効になったことで、SRE はクエリのキューイングやタイムアウトを心配する必要がなくなります。

CloudWatch アラームと組み合わせると、「RPU が上限に達した」「スケーリングが頻繁に発生している」といったイベントを検知し、必要に応じて上限値を調整するといった運用が可能です。また、Cost Explorer で Redshift Serverless のコストをタグ別・ワークグループ別に可視化することで、チーム別のコスト配分も容易になります。

障害対応のランブックに組み込む場合、「AI 駆動スケーリングが正常に動作しているか」を確認するステップを追加し、異常があれば手動スケーリングに切り替える手順を用意しておくと安心です。ただし、AI の学習には数日かかるため、導入直後のパフォーマンスが安定するまでは注意深くモニタリングする必要があります。

### WorkSpaces の PCoIP → DCV 移行でロールバック戦略を準備

WorkSpaces Personal の PCoIP から DCV への移行では、チェックポイントスナップショットが自動作成されるため、失敗時のロールバックが可能です。大規模な WorkSpaces 環境を管理している場合、移行前にテスト環境で動作確認を行い、移行中のセッションブロックによるユーザー影響を最小化するスケジュールを組むことが重要です。

移行時のモニタリングポイントとしては、「移行にかかる時間」「スナップショット容量」「ロールバック実行時の所要時間」などを事前に計測しておくと、本番環境での移行計画が立てやすくなります。また、DCV のセキュリティ強化機能（証明書ベース認証、WebAuthN）を活用する場合、既存の認証基盤との統合も検討が必要です。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [Amazon WorkSpaces Personal enhances PCoIP to DCV protocol migration](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-workspaces-personal-pcoip/) | 管理コンソールから単一クリックでプロトコル変更可能に。チェックポイントスナップショット自動作成でロールバック対応。DCV は Windows 11 対応やセキュリティ強化を実現。 |
| 2 | [Amazon EC2 C8gn instances are now available in additional regions](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ec2-c8gn-milan-hong-kong/) | C8gn インスタンス（Graviton4 搭載、コンピューティング最適化・ネットワーク強化型）がミラノとホンコンで利用可能に。最大 600 Gbps のネットワーク帯域幅、C7gn 比で最大 30% の計算性能向上。 |
| 3 | [AWS Cost Optimization Hub now supports CSV download](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-cost-optimization-hub-csv-download/) | コンソールからワンクリックで推奨事項を CSV ダウンロード可能に。フィルタ・ソート・グループ化設定を反映。スプレッドシートでの分析やステークホルダー共有が容易に。 |
| 4 | [Build custom applications using natural language in Amazon Quick (Preview)](https://aws.amazon.com/about-aws/whats-new/2026/04/custom-applications/) | 自然言語でカスタムウェブアプリケーションを数分で作成。コーディング不要で、CRM や会計システムとの統合、AI 機能埋め込み、ワンクリック共有が可能。 |
| 5 | [AWS Glue 5.1 is now available in all AWS Commercial and AWS GovCloud (US) Regions](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-glue-5-1-all-govcloud-commercial-regions/) | Apache Spark 3.5.6、Python 3.11、Scala 2.12.18 へアップグレード。Apache Iceberg 1.10.0 対応で削除ベクトルや行系統追跡が可能に。Lake Formation の書き込み権限制御を拡張。 |
| 6 | [Amazon Quick now available as a desktop application for macOS and Windows (Preview)](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-macos-windows-preview/) | macOS/Windows 向けデスクトップアプリ提供開始。ローカルファイルへの直接アクセス、OS レベル通知、MCP 接続によるコーディングエージェント対応。 |
| 7 | [Amazon Bedrock now offers OpenAI models, Codex, and Managed Agents (Limited Preview)](https://aws.amazon.com/about-aws/whats-new/2026/04/bedrock-openai-models-codex-managed-agents/) | OpenAI 最新モデル、Codex、Managed Agents を Bedrock 経由で提供。IAM、PrivateLink、CloudTrail などのエンタープライズコントロールを継承。AWS コミットメント適用可能。 |
| 8 | [Start using Amazon Quick for free in minutes with Free and Plus pricing plans](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-free-plus/) | Amazon Quick が Free/Plus プランで利用可能に。AWS アカウント不要で個人メールでサインアップ。5 分以内でオンボーディング完了。営業、マーケ、財務など職種別ワークフロー提供。 |
| 9 | [Amazon Quick expands integrations to include Google Workspace, Zoom, Airtable, and more](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick-google-workspace-zoom/) | Google Workspace、Zoom、Airtable、Dropbox、QuickBooks など 13 個の新統合を追加。マネージド認証で数クリックで接続可能。 |
| 10 | [Amazon Quick now supports document and visual creation in chat](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-quick/) | チャット内で Word、PDF、PowerPoint、Excel 形式のドキュメントを自然言語で作成可能。チャートやインフォグラフィックスなどビジュアル生成にも対応。 |
| 11 | [AWS Announces Amazon Connect Decisions](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-connect-decisions-april/) | エージェンシック AI によるサプライチェーン計画・インテリジェンスソリューション。需要予測の統一、制約対応型供給計画の自動生成、異常検知・根本原因分析を自動化。 |
| 12 | [Amazon Connect Talent for AI-powered hiring (now available in Preview)](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-connect-talent-ai-powered/) | AI 駆動型採用ソリューション。構造化音声面接、適性評価、候補者スコアリングを自動化。24/7 対応で、数百人の応募者を同時評価可能。 |
| 13 | [AWS Billing Conductor launches Passthrough Pricing Plan for Billing Transfer users](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-billing-conductor-launches-passthrough/) | Billing Transfer ユーザー向けに Passthrough Pricing Plan を提供。AWS の割引をそのまま下位アカウントに反映。無料で利用可能。 |
| 14 | [AWS KMS now tracks last usage of all KMS keys](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-kms-tracks-last-usage-kms-keys/) | すべての KMS キーの最後の暗号化操作を自動追跡。タイムスタンプ、操作種別、CloudTrail イベント ID を確認可能。新条件キーで誤削除対策を実装可能。 |
| 15 | [Amazon Redshift Serverless AI-driven scaling is now the default for new workgroups](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-redshift-serverless-ai-driven-scaling-default/) | AI 駆動スケーリングが新規ワークグループのデフォルトに。機械学習でコンピュートニーズを予測し自動調整。RPU 範囲が 8～512 に拡大。価格性能スライダーで運用方針を選択可能。 |

---

## まとめ

2026年4月29日のアップデートは、**生成 AI の企業利用を加速する Bedrock の OpenAI 統合**と、**業務効率化を劇的に向上させる Amazon Quick の大幅機能拡張**が目玉でした。特に Bedrock では、エンタープライズセキュリティを保ちながら最先端の AI モデルを利用できる環境が整い、金融・医療などの規制業界でも安心して導入できる基盤が提供されました。

一方、運用効率化の観点では、Redshift Serverless の AI 駆動スケーリングのデフォルト化、KMS キーの使用状況自動追跡、WorkSpaces の移行強化など、SRE やインフラエンジニアの日常業務を楽にするアップデートが多数含まれています。

また、Amazon Quick の無料プラン提供開始により、AWS サービスの枠を超えた「業務全体を横断する AI アシスタント」としての利用が広がることが期待されます。今後も AWS は生成 AI と運用自動化の両面で、エンタープライズ顧客のニーズに応える形でアップデートを続けていくと予想されます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)