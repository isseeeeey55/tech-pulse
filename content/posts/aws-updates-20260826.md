---
title: "【AWS】2026/08/26 のアップデートまとめ"
date: 2026-08-26T08:01:55+09:00
draft: true
tags: ["aws", "iot-core", "lambda", "iam", "batch", "secrets-manager", "rds", "connect", "ecs"]
categories: ["AWS Updates"]
summary: "2026/08/26 のAWSアップデートまとめ"
---

# 直近の AWS アップデート解説：Lambda IAM ポリシー強化と IoT Core InfluxDB 統合ほか

## はじめに

今回は、直近で発表された10件のAWSアップデートを紹介します。中でも注目すべきは、AWS Lambda のフル IAM リソースベースポリシー対応と、AWS IoT Core の InfluxDB 直接ルーティング機能です。Lambda のアクセス制御が大幅に簡素化され、マルチアカウント環境での権限管理が効率化されます。一方、IoT Core の新機能により、時系列データのパイプライン構築が劇的にシンプルになります。その他にも、ECS のエージェント接続自動修復、RDS の最新セキュリティパッチ対応、IAM Roles Anywhere の Java プラグインなど、運用効率とセキュリティを向上させるアップデートが揃いました。

## 注目アップデート深掘り

### AWS Lambda のフル IAM リソースベースポリシー対応

Lambda 関数のアクセス制御が大きく進化しました。これまで Lambda 関数に対する権限付与は、プリンシパル（IAM ユーザー、IAM ロール、AWS サービス）ごとに `AddPermission` API を呼び出して個別に設定する必要がありました。複数のアカウントや複数のサービスから Lambda を呼び出す構成では、プリンシパルの数だけ権限エントリが増えていき、管理が煩雑になっていました。

今回のアップデートにより、Lambda 関数に対してフル IAM リソースベースポリシーを設定できるようになりました。これにより、複数のプリンシパルと複数のアクションを単一の JSON ポリシードキュメントで定義できるようになります。さらに、IAM の全条件キーが利用可能になるため、ソース IP アドレス制限（`aws:SourceIp`）、プリンシパルタグによる制御（`aws:PrincipalTag`）、VPC エンドポイント制限（`aws:SourceVpce`）など、きめ細かなアクセス制御を実装できます。

**従来の方式との比較**

従来は、組織内の複数アカウントから Lambda 関数を呼び出す場合、アカウントごとに以下のような権限追加が必要でした：

- アカウント A に `lambda:InvokeFunction` を許可
- アカウント B に `lambda:InvokeFunction` を許可
- アカウント C に `lambda:InvokeFunction` を許可

これが、今回のアップデートでは単一のポリシードキュメントで以下のように表現できます：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::111111111111:root",
          "arn:aws:iam::222222222222:root",
          "arn:aws:iam::333333333333:root"
        ]
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:MyFunction",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

このポリシーは、AWS Lambda コンソール、CLI、SDK、CloudFormation などから一度に適用でき、変更も一箇所で管理できます。特にマルチアカウント環境や、組織タグに基づいた動的なアクセス制御が必要な場合に、権限管理の複雑性を大幅に削減できます。

**活用シーン**

プラットフォームチームが複数の開発チームの Lambda 関数を一元管理する場合、タグベースのアクセス制御と組み合わせることで、「`Team=DataScience` タグを持つロールのみが特定の Lambda 関数を実行できる」といったポリシーを簡潔に定義できます。また、セキュリティ要件として特定の IP レンジからのみ関数実行を許可する場合も、条件キーを活用して実装できます。

> **Note:** 本機能は全 AWS 商用リージョンで追加料金なしで利用可能です。

### AWS IoT Core の InfluxDB 直接ルーティング機能

AWS IoT Core に InfluxDB への直接ルーティング機能が追加されました。これまで IoT デバイスから送信される時系列データを InfluxDB に格納する場合、Lambda 関数でデータ変換を行うか、Kinesis Data Streams や Kinesis Data Firehose を経由してカスタムコードで処理する必要がありました。

今回の新機能により、IoT Core のルールエンジンから InfluxDB データベース（Amazon Timestream for InfluxDB または自社ホスト型 InfluxDB）へ、カスタムコードやクラウド中間サービスを使わずに直接データを送信できるようになりました。データは自動的に InfluxDB のラインプロトコル形式に変換されるため、デバイス側やサーバー側での変換処理が不要です。

**アーキテクチャの変化**

従来のアーキテクチャでは以下のような構成が一般的でした：

```
IoT デバイス → AWS IoT Core → Lambda（データ変換） → InfluxDB
```

または

```
IoT デバイス → AWS IoT Core → Kinesis → Lambda/Firehose → InfluxDB
```

新機能では以下のようにシンプルになります：

```
IoT デバイス → AWS IoT Core（ルールエンジン） → InfluxDB
```

この変化により、データパイプラインのレイテンシーが削減され、運用コンポーネントが減ることで障害ポイントも減少します。

**バッチング機能によるコスト最適化**

本機能にはデバイス側とサーバー側の 2 つのバッチングオプションが用意されています。デバイス側バッチングでは、IoT デバイスが複数のメトリクスをまとめて送信することで、IoT Core へのメッセージ数を削減できます。サーバー側バッチングでは、IoT Core が複数のメッセージを集約してから InfluxDB に書き込むため、データベースへの書き込み回数を最適化できます。これらの機能を組み合わせることで、大量のセンサーデータを扱う環境でのコストとスループットを最適化できます。

**ユースケース**

医療機器や科学機器からのテレメトリーデータをリアルタイムモニタリングする場合、ミリ秒単位のグラニュラリティで大規模データを低レイテンシーで処理できます。工場のセンサーデータを時系列で集計し、異常検知やメンテナンス予測に活用する場合も、直接ルーティングにより即座にデータが可視化され、アラートシステムと連携できます。

> **Note:** Amazon Timestream for InfluxDB と自社ホスト型 InfluxDB のどちらを選択するかは、管理の自動化レベル、コスト、既存システムとの統合要件によって判断します。

## SRE視点での活用ポイント

**Lambda のフル IAM ポリシー対応**は、マルチアカウント環境での権限管理を大幅に効率化します。Terraform や CloudFormation でインフラを管理している環境では、これまで複数の `aws_lambda_permission` リソースや個別の `AddPermission` 呼び出しが必要だったものが、単一のポリシードキュメントで管理できるようになります。特に組織の成長に伴ってアカウント数が増加する場合、新しいアカウントを追加する際のポリシー更新が一箇所で完結するため、変更の追跡と監査が容易になります。

ただし、導入時には既存の権限設定との互換性を確認する必要があります。従来の `AddPermission` 方式で設定された権限と、新しいリソースベースポリシーは並行して動作するため、意図しない権限の重複や矛盾が発生しないよう、移行計画を慎重に設計することが重要です。IAM Policy Simulator を活用して、ポリシー変更前後のアクセス可否を検証することを推奨します。

**IoT Core の InfluxDB 統合**は、大量のセンサーデータを扱う環境で運用負荷を削減できます。Lambda や Kinesis を経由するパイプラインでは、それぞれのサービスの監視、ログ管理、エラーハンドリングが必要でしたが、直接ルーティングによりこれらの中間層が不要になります。CloudWatch メトリクスで IoT Core のルール実行成功率とエラー率を監視し、InfluxDB 側のメトリクスと相関させることで、エンドツーエンドの可視性を確保できます。

障害対応のランブックに組み込む際は、InfluxDB への認証エラーやネットワーク到達性の問題を想定したトラブルシューティング手順を事前に整備しておくと、インシデント発生時の MTTR（平均修復時間）を短縮できます。また、バッチング設定はコストとレイテンシーのトレードオフとなるため、本番投入前に負荷テストを実施し、要件に合った設定値を見極めることが重要です。

## 全アップデート一覧

| サービス | タイトル | 概要 |
|---------|---------|------|
| AWS IoT Core | [InfluxDB への直接ルーティングをサポート](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-iot-core-influxdb/) | 時系列データをカスタムコードなしで InfluxDB に直接送信可能。デバイス側・サーバー側バッチング機能でコスト最適化 |
| AWS Lambda | [Node.js 26 と Python 3.15 のパブリックプレビュー](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-lambda-node-js-python-public-preview/) | 新ランタイムを本番投入前にテスト可能。フィードバックにより GA 前に改善 |
| IAM Roles Anywhere | [Java SDK v2 プラグインを提供](https://aws.amazon.com/about-aws/whats-new/2026/08/iam-roles-anywhere-java/) | AWS 外のワークロードから Java アプリ内で直接一時認証情報を取得。別プロセスや credential_process 設定が不要 |
| AWS Batch | [ECS Managed Instances をサポート](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-batch-on-ecs-managed-instances/) | GPU 加速化ワークロードを AWS 管理インフラで実行。AMI 更新やセキュリティパッチを自動管理 |
| AWS Secrets Manager | [Cisco と Netskope の管理型外部シークレットに対応](https://aws.amazon.com/about-aws/whats-new/2026/08/secrets-manager-cisco-netskope/) | カスタムコードなしで第三者サービスの認証情報を自動ローテーション |
| Amazon RDS for Oracle | [2026年7月リリースアップデートに対応](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-rds-oracle-july-2026-release-update) | 19c、21c、26ai をサポート。セキュリティ修正を含むため推奨。19c で新命名形式を導入 |
| Amazon RDS for PostgreSQL | [複数マイナーバージョンをサポート](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-rds-postgresql-18-6-17-11-16-15-15-19-14-24/) | 18.6、17.11、16.15、15.19、14.24 に対応。セキュリティ脆弱性を解決 |
| Amazon Connect Cases | [ケース作成後の顧客プロフィール更新が可能に](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-connect-cases-flexible-profiles/) | ケースをオープンした後にプロフィール変更・追加可能。誤認識や後から特定する場合に対応 |
| AWS Lambda | [フル IAM リソースベースポリシーをサポート](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-lambda-full-iam-resource-based-policies/) | 複数プリンシパル・複数アクションを 1 つのポリシーで管理。IAM 全条件キーに対応 |
| Amazon ECS | [エージェント接続の自動検出と修復](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ecs-agent-connectivity-health) | コンテナインスタンスの接続問題を自動検出し、Fargate/マネージドインスタンスで自動修復 |

## まとめ

今回紹介したアップデートは、運用の自動化とセキュリティ強化という 2 つの軸で整理できます。Lambda のフル IAM ポリシー対応や ECS のエージェント自動修復は運用負荷を削減し、RDS の最新セキュリティパッチや Secrets Manager の外部シークレット管理はセキュリティ体制を強化します。IoT Core の InfluxDB 統合は、時系列データパイプラインのアーキテクチャをシンプル化し、運用とパフォーマンスの両面でメリットをもたらします。

また、Lambda の新ランタイムプレビューや AWS Batch の ECS MI 対応は、ユーザーが本番投入前に新機能を検証できる仕組みを提供し、AWS とユーザーの双方向フィードバックループを強化する取り組みとして注目されます。IAM Roles Anywhere の Java プラグインは、オンプレミスやマルチクラウド環境での AWS 認証を簡素化し、ハイブリッドクラウド戦略を推進する組織にとって有用な選択肢となるでしょう。

これらのアップデートを活用することで、より安全で効率的な AWS 環境を構築できます。特に Lambda のポリシー管理と IoT Core のデータパイプライン簡素化は、多くの環境で即座に効果を発揮する可能性が高いため、優先的に検証することをお勧めします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)