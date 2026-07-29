---
title: "【AWS】2026/07/30 のアップデートまとめ"
date: 2026-07-30T08:02:08+09:00
draft: true
tags: ["aws", "waf", "ec2", "redshift", "iam", "efs", "cloudformation", "auto-scaling", "govcloud"]
categories: ["AWS Updates"]
summary: "2026/07/30 のAWSアップデートまとめ"
---

# 直近の AWS アップデート情報 (2026年7月) — マルチクラウド・高可用性・セキュリティ強化に注目

## はじめに

今回は、直近で発表された7件のAWSアップデートを紹介します。内容はセキュリティ強化（AWS WAF の新テキスト変換機能）、高可用性とディザスタリカバリー（EFS クロスアカウントレプリケーション、IAM Identity Center マルチリージョン対応）、デプロイ自動化（EC2 Auto Scaling の CloudFormation 統合）、データ処理効率化（Redshift Data API の改善）、そしてマルチクラウド接続（AWS Interconnect - multicloud の GA）と多岐にわたります。特に注目したいのは、**AWS WAF のプリパーステキスト変換**と**EC2 Auto Scaling の Instance Refresh が CloudFormation で統合された点**です。前者はアプリケーションセキュリティの盲点を塞ぎ、後者は IaC による安全なデプロイメントを大きく前進させるものです。

---

## 注目アップデート深掘り

### 1. AWS WAF にプリパーステキスト変換と10種類の新テキスト変換が追加

#### なぜこのアップデートが重要なのか

従来の WAF ルールでは、攻撃者が複数のエンコード手法や HTTP パラメータ汚染を組み合わせることで、ルールをバイパスできるケースがありました。たとえば、クエリ文字列の解析方法がアプリケーションと WAF で微妙に異なる場合、攻撃者はその差異を悪用して WAF を素通りし、アプリケーション側で悪意のあるペイロードを実行できてしまいます。これを **パーサ微分回避攻撃** と呼びます。

今回の **プリパーステキスト変換** は、クエリ文字列がキーバリューペアに解析される **前** に生のクエリ文字列を正規化します。これにより、WAF とアプリケーションの解析方法の差異を埋め、HTTP パラメータ汚染やパーサ微分回避のギャップを塞ぐことができます。

#### 機能の詳細

プリパーステキスト変換では、以下のような正規化処理をクエリ文字列解析の前段階で実行できます。

- **URL デコード**: パーセントエンコードされた文字を元に戻す
- **重複クエリ引数の結合**: 同じキーが複数回現れる場合、それらの値をコンマで結合
- **セミコロンをアンパサンドに置換**: 一部のアプリケーションがセミコロンをパラメータ区切り文字として扱うケースに対応

最大 **10 個の変換** をチェーン接続でき、さらに従来のポストパース変換（解析後の変換）を重ねることも可能です。これにより、多段階でエンコードされた攻撃ペイロードも正規化して検査できるようになります。

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

従来、CloudFormation を使った Auto Scaling グループの更新では、ローリング更新中にスケーリングポリシーやヘルスチェックが一時的に機能しなくなるケースがありました。また、インスタンスの置き換えが必要なプロパティ変更（AMI の更新など）を安全にロールアウトする方法が限られていました。

今回、CloudFormation に新しいアップデートポリシー **`AutoScalingInstanceRefresh`** が追加され、インスタンスの置き換えが必要なプロパティ更新時に、CloudFormation が自動的に **Instance Refresh** をトリガーするようになりました。これにより、**ローリング更新中もスケーリングポリシーとヘルスチェックが動作し続ける** ため、デプロイ中もサービスの可用性が保たれます。

#### Instance Refresh の高度な機能が CloudFormation で利用可能に

Instance Refresh には以下のような高度な機能があり、すべて CloudFormation で制御できるようになりました。

- **ルートボリュームのインプレース更新**: インスタンスを置き換えることなく、ルートボリュームのみを更新
- **段階的なロールアウト**: 一定の割合のインスタンスを更新してから次の段階へ進む（カナリアデプロイメント的な運用が可能）
- **アラームベースの監視**: CloudWatch アラームと連携し、更新中に異常を検知したら自動的にロールバック
- **チェックポイント**: 更新を一時停止し、手動で確認してから次へ進める
- **ベイクタイム**: 新しいインスタンスが起動してから、一定時間の安定稼働を確認してから次のインスタンスを更新

#### 従来の方法との比較

従来の CloudFormation のローリング更新では、`AutoScalingRollingUpdate` ポリシーを使用していましたが、以下のような制約がありました。

- ローリング更新中にスケーリングポリシーが機能しない
- 段階的なロールアウトやチェックポイント機能が限定的
- アラームベースの自動ロールバックが未対応

新しい `AutoScalingInstanceRefresh` ポリシーでは、これらの制約が解消され、より安全で柔軟なデプロイメントが可能になります。

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

セキュリティインシデント対応のランブックに、「攻撃パターンの多様化に対応するため、WAF ルールを定期的に見直す」というタスクが含まれている組織は多いでしょう。今回のプリパーステキスト変換を活用すれば、既存のルールを補強し、パーサ微分回避や HTTP パラメータ汚染といった高度な攻撃手法に対する防御を強化できます。

Terraform で WAF ルールを管理している環境では、新しいテキスト変換を `aws_wafv2_web_acl` リソースの `rule` ブロック内で定義し、段階的にロールアウトすることが可能です。まずは検出モードでログを収集し、誤検知がないことを確認してから、ブロックモードへ切り替えるアプローチが安全です。

導入時の注意点として、変換のチェーンが深くなるほど WCU 消費量が増加するため、Web ACL 全体の WCU 上限（デフォルト 1500 WCU）に余裕があるかを事前に確認しておく必要があります。また、アプリケーションと WAF の解析方法の差異を完全に把握するには、アプリケーション開発チームとの連携が不可欠です。

### EC2 Auto Scaling の Instance Refresh と CloudFormation 統合

IaC を使ったインフラ管理を実践している組織では、デプロイの自動化と安全性のトレードオフが常に課題となります。従来、CloudFormation でのローリング更新は「動作するが、本番環境で使うには少し不安」という声も聞かれました。今回の `AutoScalingInstanceRefresh` ポリシーは、その不安を大きく軽減します。

CloudWatch アラームと組み合わせれば、デプロイ中にエラー率や応答時間が閾値を超えた場合に自動的にロールバックする仕組みを構築できます。たとえば、ALB のターゲットヘルスチェック失敗率やアプリケーションメトリクスをアラームとして設定し、Instance Refresh に紐付けることで、人手を介さない自動復旧が可能になります。

Terraform ユーザーにとっては、Terraform の `aws_autoscaling_group` リソースで `instance_refresh` ブロックを定義することで、同様の機能を実現できます。CloudFormation と Terraform のどちらを使用するかは、既存のツールチェーンや組織のポリシーに依存しますが、いずれにせよ「安全なローリング更新」が標準化されたことは大きな前進です。

導入時の判断基準として、以下を考慮すると良いでしょう。

- **トラフィックパターン**: ピーク時間帯を避けてデプロイするか、段階的ロールアウトで影響を最小化
- **ヘルスチェックの信頼性**: ヘルスチェックが正しく機能しているか事前に確認
- **ロールバック戦略**: 自動ロールバックの閾値設定と、手動介入の判断基準

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [AWS WAF adds pre-parse text transformations and new text transformations](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-waf>) | プリパーステキスト変換と10種類の新テキスト変換を追加。HTTP パラメータ汚染やパーサ微分回避攻撃のギャップを塞ぐ。最大10個の変換をチェーン接続可能。各変換は10 WCUを消費。すべてのリージョンで利用可能。 |
| 2 | [Amazon EC2 Auto Scaling now supports Instance Refresh in CloudFormation](https://aws.amazon.com/about-aws/whats-new/2026/07/ec2-auto-scaling-instance-refresh-cloudformation>) | CloudFormationに新しいアップデートポリシー「AutoScalingInstanceRefresh」を追加。ローリング更新中もスケーリングポリシーとヘルスチェックが動作し続ける。段階的ロールアウト、アラームベース監視などの高度な機能を利用可能。 |
| 3 | [Amazon Redshift Data API announces long polling, session management, and flexible batch execution](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-redshift-data-api-longpolling-listsession-flexiblebatchexecute>) | ロングポーリングによりAPI呼び出しを削減。ListSessionsでセッション管理を簡素化。AUTO_COMMITモードで各ステートメントが独立実行。Provisioned・Serverless両方に対応。 |
| 4 | [AWS IAM Identity Center extends multi-Region support to Identity Center directory](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-iam-identity-center-extends-multi-region-support-to-identity-center-directory>) | Identity Centerディレクトリでもマルチリージョンレプリケーションをサポート。プライマリリージョン障害時も他リージョンでアクセス継続可能。17のAWSコマーシャルリージョンで利用可能。カスタマー管理KMSキーが必要。 |
| 5 | [Amazon EFS now supports cross-account Replication in AWS GovCloud (US)](https://aws.amazon.com/about-aws/whats-new/2026/07/amazon-efs-cross-account-replication-aws-gov-cloud-us>) | AWS GovCloud (US)でEFSのクロスアカウントレプリケーションが利用可能に。複数アカウント間でファイルシステムを自動レプリケーション。ビジネス継続性、DR、コンプライアンス要件に対応。Console、CLI、CloudFormation、APIで設定可能。 |
| 6 | [AWS announces AWS Interconnect - multicloud connectivity with Oracle Cloud Infrastructure in GA](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-announces-AWS-interconnect-multicloud-OCI-GA>) | Oracle Cloud Infrastructure (OCI)とのマルチクラウド接続ソリューション「AWS Interconnect - multicloud」が一般提供開始。標準化された仕様で一貫性のある接続体験を提供。Google Cloudも対応、Microsoft Azureは2026年後半対応予定。us-east-1で利用可能。 |
| 7 | [Amazon EFS now supports cross-account Replication in AWS GovCloud (US)](https://aws.amazon.com/amazon-efs-cross-account-replication-aws-gov-cloud-us>) | （アップデート5と同内容）AWS GovCloud (US)でEFSのクロスアカウントレプリケーションをサポート。マルチテナント環境でのディザスタリカバリー、コンプライアンス対応に有効。 |

---

## まとめ

今回紹介したアップデートは、**セキュリティ、高可用性、デプロイ自動化、マルチクラウド接続** という多様な領域にわたります。特に AWS WAF のプリパーステキスト変換は、攻撃手法の高度化に対応するセキュリティ強化の一例であり、EC2 Auto Scaling の CloudFormation 統合は IaC を使った安全なデプロイメントの実現に大きく貢献します。

また、IAM Identity Center のマルチリージョン対応や EFS のクロスアカウントレプリケーションは、グローバル展開や高可用性要件を持つ組織にとって重要な基盤機能です。AWS Interconnect - multicloud の GA は、マルチクラウド戦略を推進する企業にとって、複雑なネットワーク構築から解放される選択肢を提供します。

これらのアップデートを組み合わせることで、より堅牢で柔軟なクラウド環境を構築できるでしょう。詳細は各リリースノートおよび公式ドキュメントを参照し、自社の要件に合わせて段階的に導入を検討することをおすすめします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)