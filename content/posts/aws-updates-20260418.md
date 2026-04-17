---
title: "【AWS】2026/04/18 のアップデートまとめ"
date: 2026-04-18T08:02:19+09:00
draft: false
tags: ["aws", "sagemaker", "jumpstart", "grafana", "cloudwatch", "ec2", "u7i", "deadline-cloud", "rum"]
categories: ["AWS Updates"]
summary: "SageMaker JumpStart の optimized deployments、Amazon Managed Grafana 12.4、EC2 High Memory U7i の Singapore 対応、AWS Deadline Cloud の AI トラブルシューティング、CloudWatch RUM の European Sovereign Cloud 対応など 6 件を紹介します。"
---

![](/images/aws-updates-20260418/header.png)

## はじめに

2026年4月18日のAWSアップデートは6件です。目玉は **SageMaker JumpStart の optimized deployments** と **Amazon Managed Grafana 12.4** の 2 つ。残りは EC2 High Memory U7i の Singapore 対応、Deadline Cloud の AI トラブルシューティング、CloudWatch RUM の European Sovereign Cloud 対応、そして [前日に詳細カバー済み](/posts/aws-updates-20260417/) の EC2 C8in/C8ib GA（Slack通知のタイミング差でドラフトに含まれていたので一覧に残しています）です。

## 注目アップデート深掘り

### SageMaker JumpStart — optimized deployments（最適化ターゲット選択）

![JumpStart 4つの最適化ターゲット](/images/aws-updates-20260418/jumpstart-optimization.png)

SageMaker JumpStart で基盤モデル（Foundation Model）をデプロイするとき、**4 つの最適化ターゲット**から 1 つを選ぶだけで、適切なインスタンスタイプ・レプリカ構成・推論パラメータが提案されるようになりました。公式に挙げられているターゲットは次の 4 つです。

| ターゲット | 何が最適化されるか |
|---|---|
| **cost-optimized** | コスト優先。PoC、低頻度バッチ処理向け |
| **throughput-optimized** | 単位時間あたりのリクエスト捌きを最大化。大量バッチ推論向け |
| **latency-optimized** | P50 / TTFT（Time To First Token）を最小化。対話型アプリ向け |
| **balanced performance** | コスト・スループット・レイテンシのバランス型。汎用 |

対応モデルは **30+ モデル** で、Meta / Microsoft / Mistral AI / Qwen / Google / TII の各組織から公開されているモデルが含まれます。JumpStart がサポートされている全 AWS リージョンで利用可能です。

公式の操作手順は **SageMaker Studio のコンソールから**:

1. SageMaker Studio の **Models** へ移動
2. **JumpStart Models** タブから対象の基盤モデルを選択
3. **Deploy** を押し、optimized deployment の最適化ターゲットを選ぶ

公式リリースでは CLI や SDK での設定方法は明記されていません。`OptimizationTarget=cost` のような CreateEndpointConfig の API パラメータは**公式アナウンスに記載がない**ので、IaC で扱う場合はまず Console でデプロイした構成を CloudFormation / Terraform でインポートするのが確実です。

> **Foundation Model（基盤モデル）とは？**
> 大規模な事前学習済み言語・画像・マルチモーダルモデルの総称です。GPT 系、Llama 系、Claude 系、Mistral 系など、下流タスクにファインチューニングして使うことを前提とした汎用モデル群を指します。JumpStart はこれらを AWS 上で数クリックでデプロイ可能にするハブです。

### Amazon Managed Grafana — 12.4 workspace 対応

![Grafana 12.4 の主要機能](/images/aws-updates-20260418/grafana-124.png)

Amazon Managed Grafana で **Grafana 12.4** のワークスペースが作成可能になりました。12.4 の主要な改善は 4 つです。

**Queryless Drilldown apps**: Prometheus metrics / Loki logs / Tempo traces / Pyroscope profiles を対象に、クエリを書かずに対話的にデータを掘り下げられるアプリが追加されました。オブザーバビリティデータを探索するときに「クエリ言語を思い出す」コストが減るのが大きい点です。

**Scenes-powered rendering engine**: ダッシュボード描画のパフォーマンスが向上。大量パネルのダッシュボードを開いたときの重さが改善されます。

**変数と transformation**: ダッシュボード変数を transformation の中でも参照可能に。複雑な加工パイプラインでの表現力が上がります。

**テーブル可視化の改善**: CSS cell styling と interactive actions が入り、セル単位のスタイル制御とクリックアクション設定が可能になりました。

さらに、**Amazon CloudWatch プラグイン**が拡張され、次の機能が追加されています。

- **PPL（Piped Processing Language）と SQL クエリ** を CloudWatch Logs で利用可能
- **Cross-account Metrics Insights**（複数 AWS アカウントのメトリクスを 1 クエリで横断）
- **Log anomaly detection**（ログ異常検知）

> **PPL（Piped Processing Language）とは？**
> OpenSearch 由来のクエリ言語で、Linux のパイプのようにフィルタ・集計・整形を `|` で繋げて書けます。CloudWatch Logs Insights の既存クエリ言語と SQL に加えて、3 つ目の選択肢として使えるようになった形です。

ワークスペース新規作成は AWS Console / SDK / CLI のいずれからも 12.4 を指定可能。既存 workspace のアップグレードパスは今回のリリースノートには明記されていないので、移行ドキュメントを別途確認してください。

## SRE視点での活用ポイント

**SageMaker JumpStart optimized deployments** は、LLM を自社サービスに組み込む初期フェーズで効きます。`cost-optimized` でまず PoC を立て、UX 要件が固まったら `latency-optimized` に切り替える、という 2 段階アプローチが素直です。現時点では Console 手動操作が主な導線なので、**本番運用に入ってからは CloudFormation / Terraform でリソース定義を管理** し、Console で初期構築 → IaC 取り込みのフローを組むのが現実的です。

**Managed Grafana 12.4** で一番使い所が多いのは **CloudWatch プラグインの拡張** です。特に **Log anomaly detection** はオンコール運用に直接効きます。Queryless Drilldown は、新メンバーの監視ダッシュボード操作の学習コストを下げるのに使えます。既存 workspace を持っているチームは、12.4 ベースで新 workspace を立てて段階的にダッシュボードを移行する形になります。

**EC2 High Memory U7i の Singapore 対応** は、ASEAN 圏で SAP HANA / Oracle / SQL Server などの in-memory DB を運用しているチーム向け。8 TiB / 12 TiB の DDR5 メモリは、リージョン内で完結できる DR / スケールアップの選択肢を提供します。

**AWS Deadline Cloud の AI troubleshooting** は、3DCG / レンダリング制作パイプラインを AWS 上で回しているスタジオ向けの運用改善。render job 失敗時のログ解析を Bedrock ベースで自動化します。一般的な SRE 業務というよりは、クリエイティブ業界の運用担当者に直接効く機能です。

**CloudWatch RUM の European Sovereign Cloud 対応** は、EU データ主権要件のある環境で Web アプリ RUM を導入する選択肢が増えた、という話。該当組織にピンポイントで効きます。

## 全アップデート一覧

| # | サービス | タイトル | 概要 |
|---|---|---|---|
| 1 | [Amazon SageMaker JumpStart](https://aws.amazon.com/about-aws/whats-new/2026/04/sagemaker-jumpstart-optimized-deployments/) | optimized deployments | 30+ モデルに対し cost / throughput / latency / balanced の 4 ターゲットから選択してデプロイ |
| 2 | [Amazon Managed Grafana](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-managed-grafana-v12-create/) | Grafana 12.4 workspace 対応 | Queryless Drilldown、Scenes 描画、CloudWatch プラグインで PPL/SQL・log anomaly detection・cross-account Metrics Insights |
| 3 | [Amazon EC2](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-high-memory-u7i-asia-pacific/) | High Memory U7i が Asia Pacific (Singapore) 対応 | U7i-8tb / U7i-12tb、8/12 TiB DDR5、custom 4th gen Intel Xeon (Sapphire Rapids)、SAP HANA / Oracle / SQL Server 向け |
| 4 | [AWS Deadline Cloud](https://aws.amazon.com/about-aws/whats-new/2026/04/deadline-cloud-ai-troubleshooting/) | AI-powered troubleshooting assistant for render jobs | Bedrock 活用の AI アシスタントが render job 失敗の原因分析を自動化 |
| 5 | [Amazon CloudWatch RUM](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-cloudwatch-rum-european-sovereign-cloud/) | European Sovereign Cloud 対応 | EU データレジデンシー要件下でリアルユーザーモニタリング利用可能に |
| 6 | [Amazon EC2](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ec2-c8in-c8ib-instances-ga/) | C8in / C8ib GA（再掲） | 04/17 の[詳細記事](/posts/aws-updates-20260417/) 参照。600 Gbps ネットワーク / 300 Gbps EBS、Tokyo 対応 |

## まとめ

目玉は SageMaker JumpStart の optimized deployments と Managed Grafana 12.4 の 2 つです。前者は LLM デプロイの初期負荷を下げる機能で、`latency-optimized` / `throughput-optimized` などユースケースに合う形でクリック選択できるようになりました。後者は CloudWatch プラグイン側に log anomaly detection や PPL / SQL などが入り、Grafana 側の CloudWatch 対応が実用の一段上のレイヤに引き上がっています。残り 4 件は、該当する運用チームにピンポイントで効く地域拡張・機能追加です。
