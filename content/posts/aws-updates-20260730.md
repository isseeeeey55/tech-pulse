---
title: "【AWS】2026/07/30 のアップデートまとめ"
date: 2026-07-30T08:02:08+09:00
draft: false
tags: ["aws", "waf", "ec2", "redshift", "iam", "efs", "cloudformation", "auto-scaling", "govcloud"]
categories: ["AWS Updates"]
summary: "2026/07/30 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260730/header.png)

# 直近の AWS アップデート情報 (2026年7月) — マルチクラウド・高可用性・セキュリティ強化に注目

## はじめに

今回は、直近で発表された6件のAWSアップデートを紹介します。内容はセキュリティ強化（AWS WAF の新テキスト変換機能）、高可用性とディザスタリカバリー（EFS クロスアカウントレプリケーション、IAM Identity Center マルチリージョン対応）、デプロイ自動化（EC2 Auto Scaling の CloudFormation 統合）、データ処理効率化（Redshift Data API の改善）、そしてマルチクラウド接続（AWS Interconnect - multicloud の GA）と多岐にわたります。特に注目したいのは、**AWS WAF のプリパーステキスト変換**と**EC2 Auto Scaling の Instance Refresh が CloudFormation で統合された点**です。前者はアプリケーションセキュリティの盲点を塞ぎ、後者は IaC による安全なデプロイメントを大きく前進させるものです。

---

## 注目アップデート深掘り

### 1. AWS WAF にプリパーステキスト変換と10種類の新テキスト変換が追加

#### なぜこのアップデートが重要なのか

クエリ文字列の解析方法がアプリケーションと WAF で異なる場合、攻撃者はその差異を悪用してルールをすり抜けられる可能性があります。AWS はこの種のギャップを **HTTP パラメータ汚染（HTTP parameter pollution）** および **パーサ微分回避（parser differential evasion）のギャップ** と表現しています。

今回の **プリパーステキスト変換** は、AWS WAF がクエリ文字列をキーバリューペアに解析する **前** に、生のクエリ文字列を正規化します。告知はこの機能が上記のギャップに対処するものと位置づけています。

#### 機能の詳細

プリパーステキスト変換では、以下のような正規化処理をクエリ文字列解析の前段階で実行できます。

- **URL デコード**: パーセントエンコードされた文字を元に戻す
- **重複クエリ引数の結合**: 同じキーが複数回現れる場合、それらの値をコンマで結合
- **セミコロンをアンパサンドに置換**: 一部のアプリケーションがセミコロンをパラメータ区切り文字として扱うケースに対応

最大 **10 個の変換** をチェーン接続でき、単一のルールステートメント内でさらに標準のポストパース変換（解析後の変換）を重ねることも可能です。

また、任意のルールステートメントで使用可能な **10 種類の新しいテキスト変換** も追加されました。大文字化、トリミング、空白削除、SHA256 ハッシュ化などの業界標準オプションに加え、Amazon Threat Research Team が開発した **OS 対応コマンドラインデコード機能** と **JavaScript デコード機能** が含まれます。これにより、JavaScript インジェクションや OS コマンドインジェクションの難読化されたペイロードを可視化して検査できます。

#### コストとリソース消費

各テキスト変換は **10 WCU（Web ACL Capacity Units）** を消費します。AWS WAF の標準料金以外に追加費用は発生しません。すべての AWS リージョンで利用可能です。

#### 検証のポイント

AWS WAF コンソールで実際に新しいテキスト変換を設定し、以下のような攻撃シナリオを試してみることをおすすめします。

- クエリ文字列に `%3Cscript%3E` のような URL エンコードを含めたリクエストを送信し、プリパース変換でデコードされることを確認
- 同じキーが複数回現れるクエリ文字列（`?id=1&id=2`）を送信し、重複クエリ引数がコンマで結合されることを確認
- JavaScript や OS コマンドの難読化されたペイロードを送信し、新しいデコード機能で正規化・検出されることを確認

HTTP パラメータ汚染やパーサ微分回避攻撃の具体例を調査し、従来の WAF ルールでは検出できなかったケースが、新しい変換により検出可能になることを実証すると、アップデートの価値がより明確になります。複数の変換をチェーンした場合の WCU 消費量を計測し、パフォーマンスへの影響を把握しておくことも重要です。

---

### 2. Amazon EC2 Auto Scaling が CloudFormation で Instance Refresh をサポート

#### なぜこのアップデートが重要なのか

CloudFormation に新しいアップデートポリシー **`AutoScalingInstanceRefresh`** が追加され、インスタンスの置き換えが必要なプロパティ更新時に、CloudFormation が **Instance Refresh** をトリガーするようになりました。

告知は「スケーリングポリシーやヘルスチェックといった Auto Scaling の機能は更新中も引き続き有効であり、デプロイ中にサービスの健全性が損なわれることはない」と述べています。つまり、IaC 側からインスタンス置き換えを伴う更新を仕掛けても、Auto Scaling 本来の制御が効いたまま入れ替えが進みます。

#### Instance Refresh の高度な機能が CloudFormation で利用可能に

告知が挙げている Instance Refresh の機能は以下の4点です。

- **ルートボリュームの置き換えによるインプレース更新**（replace root volume for in-place updates）
- **launch-before-terminate**: 新しいインスタンスを起動してから、古いインスタンスを終了する
- **アラームベースの監視**（alarm-based monitoring）
- **チェックポイントとベイクタイム**: 制御されたロールアウトのため、更新を段階的に区切って待機時間を挟む

本機能はすべての AWS リージョンで、追加コストなしに利用できます。

#### 検証のポイント

以下のような検証を行うことで、この機能の効果を実感できます。

1. **サンプル CloudFormation テンプレートを作成**: `AutoScalingInstanceRefresh` ポリシーを設定し、AMI を更新して動作確認
2. **ローリング更新中のスケーリング動作を確認**: 負荷をかけながら更新を実行し、スケールアップ/ダウンが正常に機能することを検証
3. **アラームベースの監視を設定**: CloudWatch アラームと連携させ、更新中にエラー率が上昇したらロールバックするシナリオをテスト
4. **ロールバックシナリオをテスト**: CloudFormation スタックのロールバック時に、Instance Refresh がどのように動作するかを確認

既存システムで導入する場合、段階的なマイグレーション（まず開発環境で試し、次にステージング、最後に本番環境へ展開）を推奨します。

---

## SRE視点での活用ポイント

### AWS WAF のプリパーステキスト変換

WAF ルールを定期的に見直す運用を持っている環境では、今回のプリパーステキスト変換を既存ルールの補強材料として検討できます。告知が対象として挙げているのは、パーサ微分回避と HTTP パラメータ汚染のギャップです。

Terraform で WAF ルールを管理している環境では、新しいテキスト変換を `aws_wafv2_web_acl` リソースの `rule` ブロック内で定義し、段階的にロールアウトすることが可能です。まずは検出モードでログを収集し、誤検知がないことを確認してから、ブロックモードへ切り替えるアプローチが安全です。

導入時の注意点として、新しい変換は1つあたり 10 WCU を消費するため、変換をチェーンするほど消費量が積み上がります。Web ACL の WCU 上限（アカウントの Service Quotas で確認できる）に余裕があるかを事前に確認しておく必要があります。また、アプリケーションと WAF の解析方法の差異を把握するには、アプリケーション開発チームとの連携が欠かせません。

### EC2 Auto Scaling の Instance Refresh と CloudFormation 統合

IaC を使ったインフラ管理では、デプロイの自動化と安全性のトレードオフが課題になりがちです。`AutoScalingInstanceRefresh` ポリシーは、更新中もスケーリングポリシーとヘルスチェックが有効なまま入れ替えが進むため、CloudFormation からのインスタンス置き換えを扱いやすくします。

CloudWatch アラームと組み合わせれば、デプロイ中にエラー率や応答時間が閾値を超えた場合に自動的にロールバックする仕組みを構築できます。たとえば、ALB のターゲットヘルスチェック失敗率やアプリケーションメトリクスをアラームとして設定し、Instance Refresh に紐付けることで、人手を介さない自動復旧が可能になります。

Terraform ユーザーにとっては、Terraform の `aws_autoscaling_group` リソースで `instance_refresh` ブロックを定義することで、同様の機能を実現できます。CloudFormation と Terraform のどちらを使用するかは、既存のツールチェーンや組織のポリシーに依存しますが、いずれにせよ「安全なローリング更新」が標準化されたことは大きな前進です。

導入時の判断基準としては、以下が検討ポイントになります。

- **トラフィックパターン**: ピーク時間帯を避けてデプロイするか、段階的ロールアウトで影響を最小化
- **ヘルスチェックの信頼性**: ヘルスチェックが正しく機能しているか事前に確認
- **ロールバック戦略**: 自動ロールバックの閾値設定と、手動介入の判断基準

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [AWS WAF adds pre-parse text transformations and new text transformations](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-waf/) | プリパーステキスト変換と10種類の新テキスト変換を追加。HTTP パラメータ汚染やパーサ微分回避のギャップに対処。最大10個の変換をチェーン接続可能。各変換は10 WCUを消費し、標準料金以外の追加費用なし。すべてのリージョンで利用可能。 |
| 2 | [Amazon EC2 Auto Scaling now supports Instance Refresh in CloudFormation](https://aws.amazon.com/about-aws/whats-new/2026/07/ec2-auto-scaling-instance-refresh-cloudformation) | CloudFormationに新しいアップデートポリシー「AutoScalingInstanceRefresh」を追加。更新中もスケーリングポリシーとヘルスチェックが有効なまま。ルートボリューム置き換え、launch-before-terminate、アラームベース監視、チェックポイントとベイクタイムに対応。全リージョンで追加コストなし。 |
| 3 | [Amazon Redshift Data API announces long polling, session management, and flexible batch execution](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-redshift-data-api-longpolling-listsession-flexiblebatchexecute/) | ロングポーリングによりSQLステートメントのメタデータ/結果取得のAPI呼び出しを削減。ListSessionsでセッション管理。AUTO_COMMITモードでバッチ内の各ステートメントが独立実行され、1件の失敗でバッチ全体がロールバックされなくなる。Provisioned・Serverless両方、全コマーシャルリージョンとGovCloud (US)で利用可能。 |
| 4 | [AWS IAM Identity Center extends multi-Region support to Identity Center directory](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-iam-identity-center-extends-multi-region-support-to-identity-center-directory) | Identity Centerディレクトリでもマルチリージョンレプリケーションをサポート。プライマリリージョンで障害が発生しても、追加リージョンにプロビジョニング済みの権限でAWSアカウントへのアクセスを継続できる。デフォルトで有効な17のコマーシャルリージョンが対象。組織インスタンスにマルチリージョンのカスタマー管理KMSキー（CMK）の設定が必要。 |
| 5 | [Amazon EFS now supports cross-account Replication in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-efs-cross-account-replication-aws-gov-cloud-us) | AWS GovCloud (US)でEFSのクロスアカウントレプリケーションが利用可能に。複数アカウント間でファイルシステムを自動レプリケーション。ビジネス継続性、DR、コンプライアンス要件に対応。 |
| 6 | [AWS announces AWS Interconnect - multicloud connectivity with Oracle Cloud Infrastructure in GA](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-announces-AWS-interconnect-multicloud-OCI-GA/) | Oracle Cloud Infrastructure (OCI)とのマルチクラウド接続「AWS Interconnect - multicloud」が一般提供開始。OCIとGoogle Cloudで同じ一貫した接続体験を利用できる。Microsoft Azureは2026年後半にローンチ予定。OCI向けはus-east-1（バージニア北部）リージョンで利用可能。 |

---

## まとめ

今回紹介したアップデートは、**セキュリティ、高可用性、デプロイ自動化、マルチクラウド接続** という多様な領域にわたります。特に AWS WAF のプリパーステキスト変換は、攻撃手法の高度化に対応するセキュリティ強化の一例であり、EC2 Auto Scaling の CloudFormation 統合は IaC を使った安全なデプロイメントの実現に大きく貢献します。

また、IAM Identity Center のマルチリージョン対応や EFS のクロスアカウントレプリケーションは、高可用性やコンプライアンス要件を持つ環境の基盤となる機能です。AWS Interconnect - multicloud の GA により、OCI と Google Cloud を同じ接続体験で扱えるようになりました。

詳細は各告知および公式ドキュメントを参照し、自社の要件に合わせて段階的に導入を検討することをおすすめします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)