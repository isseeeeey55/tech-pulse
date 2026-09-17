---
title: "【AWS】2026/09/17 のアップデートまとめ"
date: 2026-09-17T08:02:35+09:00
draft: false
tags: ["aws", "amazon-connect", "workspaces", "client-vpn", "ecs", "s3", "efs", "sts", "cloudtrail", "cloudwatch", "step-functions", "lambda", "glue", "salesforce", "direct-connect", "billing-and-cost-management", "mediatailor", "pcs"]
categories: ["AWS Updates"]
summary: "2026/09/17 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260917/header.png)

# 直近の AWS アップデート情報まとめ — 2026年9月版

## はじめに

今回は、直近で発表された 14 件の AWS アップデートを紹介します。今回のアップデートは、**コスト管理の透明性向上**、**AI による業務効率化**、**セキュリティとガバナンスの強化**、そして**開発者体験の改善**という 4 つの大きなテーマで構成されています。

特に注目したいのが、AWS Direct Connect のフラットレート料金体系の導入と、AWS Billing and Cost Management ダッシュボードへの異常検知ウィジェット追加です。これらは FinOps の観点から予算の予測性を高める重要なアップデートです。また、Amazon Connect への AI を活用した評価フォームインポート機能や、AWS Step Functions の自動サービス統合など、運用効率を高める機能も多数リリースされています。

SRE やクラウドエンジニアにとって、日々の運用を改善するヒントが詰まった今回のアップデート群を、詳しく見ていきましょう。

---

## 注目アップデート深掘り

### AWS Direct Connect のフラットレート料金体系導入 — 予測可能なネットワークコスト管理へ

AWS Direct Connect の 10Gbps および 100Gbps 専有接続に、フラットレート料金体系が導入されました。これは、ハイブリッドクラウド環境や大規模データ転送を行う組織にとって、非常に重要な変更です。

#### DTO の変動リスクが消える — フラットレートのメリットと限界

従来の AWS Direct Connect は、ペイアズユーゴー方式でデータ転送量（DTO）に応じて課金されていました。そのため、月によってデータ転送量が大きく変動する場合、ネットワークコストの予測が困難でした。特に、オンプレミスから AWS へのバックアップやレプリケーション、大規模なデータ分析パイプラインでは、月額費用が数十万円単位で変動することもあり、財務チームにとって予算管理の難しさが課題となっていました。

新しいフラットレート料金体系では、接続帯域幅と地理的スコープに基づいた固定の月額料金となります。地理的スコープは、同一メトロからグローバルまでの 5 つのティアが用意されており（告知では個々のティア名は示されていません）、自社のトラフィックパターンに合ったスコープを選択します。これにより、データ転送量に関わらず月額費用が一定となり、年間予算の策定や FinOps チームによるコスト最適化の計画が立てやすくなります。

#### ポートペア — 冗長性を追加料金なしで実現

新たに導入された**ポートペア**という概念も見逃せません。これは、異なるデバイスまたは場所にある 2 つの専有接続を同じ帯域幅でシェアする仕組みです。1 つ目の接続を通常トラフィック用、2 つ目を冗長性用として構成でき、第 2 の接続は追加料金なしで利用可能です。

ミッションクリティカルなアプリケーションでは、ネットワークの冗長性確保が必須です。従来は 2 つの接続にそれぞれ課金されていましたが、ポートペア構成により、冗長接続のコストを実質半減できる可能性があります。

#### 従来方式との比較

例えば、月間のデータ転送量が 50TB から 200TB の間で変動する企業を考えてみましょう。従来のペイアズユーゴー方式では、転送量が多い月には請求額が急増し、予算超過のリスクがありました。フラットレート方式では、最大転送量を想定した帯域幅を選択することで、月額費用を固定化できます。

もちろん、データ転送量が少ない場合には従来方式の方がコスト効率が良い可能性もあります。導入前には、過去 6〜12 ヶ月のデータ転送パターンを分析し、どちらの料金体系が自社に適しているかをシミュレーションすることが重要です。

---

### AWS Billing and Cost Management ダッシュボードに異常検知ウィジェット追加

AWS Billing and Cost Management（BCM）ダッシュボードに、**Detected Anomalies ウィジェット**が追加されました。これにより、コスト異常をダッシュボード上で直接監視できるようになり、コスト管理の効率が上がります。

#### コスト異常を他の指標と並べて評価できる

AWS Cost Anomaly Detection は、機械学習を活用して予期しないコスト増加を自動検知する強力な機能です。しかし、従来は異常検知の結果をメール通知で受け取るか、Cost Anomaly Detection コンソールに直接アクセスする必要がありました。日々のコスト管理では、予算、Savings Plans のカバレッジ、使用量トレンドなど、複数の指標を横断的に確認する必要があるため、異常検知だけを別画面で確認するのは効率的ではありませんでした。

新しい Detected Anomalies ウィジェットは、コスト・使用量、予算、コスト効率、Savings Plans・Reserved Instance のカバレッジなどと同じダッシュボード上に配置できます。これにより、**支出全体の文脈の中で異常を評価**できるようになり、優先度判断が容易になります。

#### ウィジェットの機能

ウィジェットは以下の情報を表示します：

- 検知された異常の数
- 月初からの支出に対する総コスト影響
- 各異常のコスト影響、根本原因、期間

さらに、30・60・90 日のルックバック期間を選択でき、重大度・サービス・アカウント・リージョンでフィルタリングすることで、最も関連性の高い異常のみを表示できます。ウィジェットから Cost Anomaly Detection コンソールに直接リンクしており、詳細な調査と評価記録が容易です。

#### 運用への組み込み方

このウィジェットは、ダッシュボードのエクスポート、スケジュール配信メール、CSV・PDF ダウンロード、クロスアカウントダッシュボード共有にも対応しています。これにより、以下のような運用フローが実現できます：

1. **週次レビューミーティング**：ダッシュボードを PDF エクスポートして経営層に共有し、異常の傾向を報告
2. **アラートベースの調査**：重大度が高い異常が検知された場合、ダッシュボードから直接詳細を確認し、迅速に対応
3. **複数アカウント管理**：組織全体のダッシュボードを作成し、異常を一元監視。特定のアカウントで異常が頻発している場合は、リソース管理の見直しを実施

従来は異常検知メールを個別に確認し、手動でスプレッドシートにまとめる必要がありましたが、ダッシュボード統合により、この手作業がなくなります。

---

### AWS STS のセッショントークンサイズ制限の簡素化とモニタリング機能追加

AWS Security Token Service (STS) が、セッショントークンのサイズ制限を簡素化しました。従来は複数の個別制限が存在していましたが、これが **4,096 バイトの単一制限**に統一されました。さらに、トークンサイズと使用率が CloudTrail と CloudWatch で監視可能になりました。

#### 複数の個別制限が 4,096 バイトの単一制限に統一された意味

複雑なアクセス制御を実装する大規模エンタープライズ環境では、セッショントークンに複数のマネージドポリシー、インラインポリシー、セッションタグを組み合わせる必要があります。従来は、トークンサイズとパラメータに対して個別の制限が存在し、どの制限に抵触しているのか判断が難しいケースがありました。

新しい単一制限により、トークンサイズの管理が明確になり、セッションポリシーとセッションタグのより大きな組み合わせに対応できるようになりました。これは、機械学習やデータ分析のワークロードで、詳細なタグベースのアクセス制御を実装する場合に特に有用です。

#### モニタリング機能の追加

STS はセッショントークンサイズと制限に対する使用率（パーセンテージ）をレスポンス要素として返すようになりました。これらの値は AWS CloudTrail に記録され、Amazon CloudWatch で対応するメトリクスとして公開されます。

これにより、以下のような運用が可能になります：

- **CloudWatch アラームの設定**：トークンサイズが制限の 80% に達した場合にアラートを送信し、事前に対処
- **トレンド分析**：時系列でトークンサイズの変化を追跡し、ポリシーの肥大化を検知
- **監査証跡**：CloudTrail ログから、どのアカウント・ロールが大きなトークンを生成しているかを特定

#### テスト用の新しいオプション API パラメータ

新しいオプション API パラメータを使用することで、より大きなセッショントークン（4,096 バイトの制限まで）を生成でき、アプリケーションとインフラストラクチャがそれに対応できるかをテストできます。これにより、本番環境にデプロイする前に、トークンサイズの影響を検証できます。

---

### Amazon ECS が EC2 launch type で Amazon S3 Files をサポート

Amazon ECS が Amazon EC2 launch type で Amazon S3 Files をサポート開始しました。これにより、EC2 インスタンス上で実行される ECS タスクから、Amazon S3 内のデータに対して標準的なファイルシステムセマンティクスを使ってアクセスできるようになります。

#### ファイルベースのアプリをコード変更なしで EC2 + S3 に載せる

S3 Files は Amazon EFS をベースに構築されており、S3 内のデータに低遅延でアクセス可能な共有ファイルシステムを提供します。これまで Fargate と ECS Managed Instances でのみ利用可能でしたが、今回 EC2 launch type にも拡張され、全ての ECS launch type で一貫した S3 Files へのアクセスが実現します。

従来、S3 からデータを読み込むアプリケーションでは、以下のいずれかの方法を取る必要がありました：

1. **アプリケーションコードで S3 API を実装**：アプリケーションを S3 専用に改修する必要がある
2. **データをステージング領域にコピー**：EBS ボリュームや EFS にデータをコピーし、ストレージコストと転送時間が増加
3. **サードパーティのファイルシステムツールを使用**：導入・運用の手間が増える

S3 Files を使用することで、**アプリケーションコードの変更不要**で、既存のファイルベースのアプリケーションをそのまま実行できます。データの複製やステージングも不要で、コスト効率が向上します。

#### ユースケース例

- **機械学習パイプライン**：大規模なデータセットを S3 から直接読み取り、前処理・トレーニング・推論を実行
- **ETL ワークロード**：ステージング領域を経由せず S3 からデータを読み込み・加工・書き込み
- **レガシーアプリケーションのコンテナ化**：ファイルシステムを前提とした既存アプリケーションを、S3 をバックエンドストレージとして ECS/EC2 でコンテナ化

全 AWS 商用リージョンと AWS GovCloud で利用可能であり、Fargate、Managed Instances、EC2 全ての launch type で一貫した機能が提供されます。

---

## SRE 視点での活用ポイント

### コスト管理の自動化と透明性向上

今回のアップデートで特に注目すべきは、コスト管理の透明性と予測可能性が向上した点です。AWS Direct Connect のフラットレート料金体系は、Terraform で管理しているネットワークインフラがある場合、料金体系の変更を IaC に反映させることで、コスト見積もりの自動化が可能になります。

Detected Anomalies ウィジェットは、CloudWatch アラームと組み合わせることで、異常検知時に自動的に Slack や PagerDuty に通知するフローを構築できます。例えば、重大度が「高」の異常が 2 件以上検知された場合に、オンコール担当者にアラートを送信し、障害対応のランブックに組み込むことで、迅速な対応が可能になります。

### セキュリティとガバナンスの強化

AWS STS のトークンサイズ監視機能は、セキュリティポリシーの肥大化を早期に検知する仕組みとして活用できます。CloudWatch Logs Insights を使用して、トークンサイズが急増したアカウントやロールを特定し、ポリシーの見直しを行うことで、セキュリティリスクを低減できます。

Amazon Connect のカスタムメトリクスに対するタグベースのアクセス制御は、複数チームが共有ライブラリを編集する際に、誤編集や意図しない変更を防ぐ仕組みとして有効です。IAM ポリシーでタグベースの条件を設定することで、チームごとに独立したメトリクス管理が実現し、運用の民主化と統制のバランスを取ることができます。

### 開発体験の改善とリードタイム短縮

AWS Step Functions の自動サービス統合は、新しい AWS サービスがリリースされてから数週間以内に Step Functions から直接オーケストレーションできるようになります。これにより、新機能を迅速に既存ワークフローに組み込むことができ、開発リードタイムを短縮できます。

Amazon ECS の S3 Files サポート拡張は、既存のファイルベースのアプリケーションをコンテナ化する際の障壁を下げます。レガシーアプリケーションのクラウド移行プロジェクトでは、アプリケーションコードの改修なしに S3 をストレージバックエンドとして使用でき、移行コストとリスクを低減できます。

### 導入時の判断基準とリスク

これらの新機能を導入する際には、以下の点に注意が必要です：

- **コスト最適化**：Direct Connect のフラットレート料金は、データ転送量が少ない場合には従来方式よりコスト高になる可能性があります。過去のデータ転送パターンを分析し、ROI を計算してから導入判断を行うべきです。
- **互換性確認**：S3 Files は Amazon EFS ベースですが、すべてのファイルシステム操作が S3 で完全にサポートされているわけではありません。特に、アプリケーションが高度なファイルシステム機能（POSIX ACL、ファイルロックなど）に依存している場合は、事前に互換性を検証する必要があります。
- **監視とアラート設計**：新しいモニタリング機能を導入する際は、アラート疲れを避けるため、閾値とアラート条件を慎重に設計する必要があります。特に、異常検知ウィジェットでは、重大度フィルタを適切に設定し、ノイズを減らすことが重要です。

---

## 全アップデート一覧

> **AWS PCS（Parallel Computing Service）とは？** AWS が提供する HPC クラスター管理サービスです。Slurm ベースのジョブスケジューラをマネージドで利用でき、EC2 インスタンスのプロビジョニングやオートスケーリングを自動化します。
>
> **Lambda MicroVMs とは？** AWS Lambda の実行環境を、隔離されたマイクロ VM として提供する仕組みです。今回の Step Functions の自動サービス統合では、この Lambda MicroVMs が最初の対応対象となりました。

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [Amazon Connect Customer can now import evaluation form PDFs using AI](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-connect-customer-import-evaluation-form-PDF/) | PDF の評価フォームを AI を使って自動インポート。手動再構築の手間を削減し、移行時間を短縮 |
| 2 | [Amazon Connect Customer now lets you create, manage, and search custom metrics through APIs](https://aws.amazon.com/about-aws/whats-new/2026/09/connect-customer-custom-metrics-apis/) | 7 つの新しい API オペレーションでカスタムメトリクスをプログラマティックに管理。定義ドリフトを防止 |
| 3 | [Amazon Connect Customer custom metrics now supports tag-based access control](https://aws.amazon.com/about-aws/whats-new/2026/09/connect-customer-custom-metrics-tag/) | カスタムメトリクスにタグベースのアクセス制御を追加。複数チームでの独立運用を実現 |
| 4 | [Amazon WorkSpaces adds support for NVIDIA Blackwell GPU instances](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-workspaces-nvidia-blackwell-gpu-instances/) | NVIDIA Blackwell GPU 搭載の Graphics G7 バンドル提供開始。前世代比最大 2.1 倍のグラフィックス性能 |
| 5 | [New AWS experience helps builders get started and ship faster](https://aws.amazon.com/about-aws/whats-new/2026/09/New-AWS-Builder-Experience) | 新しいビルダー向け体験でセットアップを簡素化。サインアップから即座にコーディング開始可能 |
| 6 | [AWS Client VPN is now supporting MacOS 27 Golden Gate](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-client-vpn-macos-golden-gate/) | AWS Client VPN が MacOS 27 Golden Gate に対応。バージョン 6.0 以上で利用可能 |
| 7 | [Amazon ECS extends Amazon S3 Files support to the Amazon EC2 compute type](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ecs-s3-files-ec2/) | ECS の EC2 launch type で S3 Files をサポート。全 launch type で一貫した S3 アクセスを実現 |
| 8 | [AWS STS simplifies session token size limits and adds session token size monitoring](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-sts/) | セッショントークンサイズ制限を 4,096 バイトに統一。CloudTrail と CloudWatch でモニタリング可能に |
| 9 | [AWS Elemental MediaTailor Monetization Functions adds ad response hooks](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-elemental-mediatailor-functions-ad-response-hooks) | MediaTailor に 2 つの新しいライフサイクルフック追加。広告配信の柔軟性が向上 |
| 10 | [AWS PCS now supports custom GRES, hardware topology, and MIG](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-pcs-gres-hardware-topology-mig/) | AWS PCS が Slurm 26.05、カスタム GRES 設定、NVIDIA MIG に対応。HPC・ML ワークロードの最適化が可能に |
| 11 | [AWS Step Functions adds new AWS service integrations automatically, starting with AWS Lambda MicroVMs](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-step-functions-integrations/) | Step Functions が新 AWS サービスの SDK インテグレーションを自動追加。Lambda MicroVMs から対応開始 |
| 12 | [AWS Glue zero-ETL now captures archived Salesforce records](https://aws.amazon.com/about-aws/whats-new/2026/09/glue-zero-etl-archived-salesforce/) | AWS Glue zero-ETL が Salesforce のアーカイブレコードをキャプチャ。完全なデータ同期を実現 |
| 13 | [AWS Direct Connect announces flat-rate pricing for dedicated connections](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-direct-connect-announces-flat-rate-pricing/) | Direct Connect の 10Gbps・100Gbps 専有接続にフラットレート料金体系を導入。予算予測が容易に |
| 14 | [Monitor cost anomalies directly in Billing and Cost Management Dashboards with the new Detected Anomalies widget](https://aws.amazon.com/about-aws/whats-new/2026/09/monitor-detected-anomalies-using-dashboards) | BCM ダッシュボードに Detected Anomalies ウィジェット追加。コスト異常を一元監視可能に |

---

## まとめ

今回の 14 件は、コスト可視化・セキュリティ制御・開発効率という 3 軸に散らばっていますが、共通するのは**既存の運用を大きく変えずに導入できる**変更が多い点です。とりわけ**コスト管理の透明性向上**と**AI/自動化による運用効率化**が目立ちます。

Direct Connect のフラットレート料金や、BCM ダッシュボードの異常検知ウィジェットは、FinOps の観点から予算予測と異常対応を効率化します。Amazon Connect への AI を活用した評価フォームインポートや、AWS Glue の Salesforce アーカイブレコード対応は、手動作業を削減し、データの完全性を向上させます。

また、AWS STS のトークンサイズ管理の簡素化や、Amazon Connect のタグベースアクセス制御など、セキュリティとガバナンスの強化も継続的に行われています。これらは、大規模組織が AWS を安全かつ効率的に運用するために不可欠な機能です。

まず手を付けるなら、STS のトークンサイズメトリクスに CloudWatch アラームを1本仕込むこと、そして Direct Connect については過去 6〜12 ヶ月の DTO 実績からフラットレート移行の損益分岐を計算することの 2 つです。どちらも既存構成を変えずに着手でき、効果を数字で確認できます。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)