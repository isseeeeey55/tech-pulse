---
title: "【AWS】2026/06/02 のアップデートまとめ"
date: 2026-06-02T08:02:28+09:00
draft: false
tags: ["aws", "quick", "ec2", "sagemaker", "ses", "bedrock", "kms", "secrets-manager", "vpc", "cloudwatch", "fargate", "lambda", "systems-manager", "eks", "cloudtrail"]
categories: ["AWS Updates"]
summary: "2026/06/02 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260602/header.png)

# 2026年6月2日 AWS アップデート解説

## はじめに

本日は、直近で公開されたAWSのアップデート10件をまとめてお届けします。今回のアップデートは、**セキュリティとエンタープライズガバナンス機能の強化**が大きなテーマとなっています。特に注目すべきは、Amazon QuickがVPC経由でのプライベートMCPサーバー接続に対応した点、そしてAmazon BedrockのAgentCore IdentityがAWS Secrets Managerの既存シークレット参照をサポートした点です。

また、Amazon SageMaker HyperPodにAIコーディングアシスタント向けのトラブルシューティングスキルが追加され、大規模MLクラスタの運用効率が大幅に向上しています。インフラ面では、EC2の新世代インスタンス（M8azn、M8i/M8i-flex）が欧州・アジア太平洋地域で利用可能になり、グローバルなワークロード展開がさらに容易になりました。

本記事では、特にセキュリティとガバナンスに焦点を当てた2つのアップデートを深掘りし、SRE視点での活用ポイントを解説します。

## 注目アップデート深掘り

### Amazon Quick の VPC 接続対応：プライベート MCP サーバーとのセキュアな統合

Amazon Quickは、AWS が提供するAIアシスタントサービスですが、これまではインターネット上の公開MCP（Model Context Protocol）サーバーとの接続に限定されていました。今回のアップデートにより、**VPC内にホストされたプライベートMCPサーバーへの直接接続**が可能になり、機密データを扱う企業でも安全にAI機能を活用できるようになりました。

#### なぜこのアップデートが重要なのか

従来、企業が独自のビジネスロジックやレガシーシステムをAIアシスタントに統合する場合、MCPサーバーをインターネットに公開する必要がありました。これは以下のようなリスクを伴います：

- 機密データの漏洩リスク
- コンプライアンス要件（GDPR、HIPAA、PCI-DSSなど）への抵触
- 追加のセキュリティ対策（WAF、認証レイヤーなど）の必要性
- ネットワーク境界を越えることによる監査の複雑化

VPC接続対応により、これらの課題が解消され、**すべての通信がプライベートネットワーク内で完結**します。

#### セキュリティ・ネットワークモデルの比較

| 項目 | 従来（公開MCPサーバー） | VPC接続対応後 |
|------|------------------------|---------------|
| ネットワーク経路 | インターネット経由 | VPC内で完結 |
| データ露出リスク | 高（公開エンドポイント） | 低（プライベート通信） |
| 追加のセキュリティ層 | 必須（WAF、認証など） | VPCセキュリティグループで制御 |
| 監査ログ | CloudTrail + 追加ツール | VPCフローログ + CloudTrail統合 |
| コンプライアンス対応 | 追加対策が必要 | ネイティブ対応 |
| レイテンシ | 高（インターネット往復） | 低（VPC内通信） |

#### MCP コネクター作成手順

VPC接続を有効にしたMCPコネクターの作成は、以下のステップで実行できます：

1. **Amazon Quick コンソール**で「Connectors」を開き、コネクタータイプとして **Model Context Protocol (MCP)** を選択
2. 事前に用意した **VPC 接続（VPC connection）** を選択する（接続先の VPC・サブネット・セキュリティグループはこの VPC 接続にひも付く）
3. **MCP サーバーの URL**（プライベートエンドポイント、例：`http://10.0.1.50:8080/mcp`）を指定
4. 名前やアクセス権限を設定し、コネクターを作成

> ※ 上記は公式発表の「VPC 接続を選択し、MCP サーバーの URL を指定する」という流れに基づく一般的な手順です。コンソールの正確なラベルや項目は[公式の MCP 統合ドキュメント](https://docs.aws.amazon.com/quick/latest/userguide/mcp-integration.html)で確認してください。

#### トラフィックフローとVPCエンドポイントの活用

VPC接続を使用した場合のトラフィックフローは次のようになります：

```
[Amazon Quick] 
    ↓ (VPC 接続経由でプライベートに到達)
[VPC 内の ENI]
    ↓ (VPC内ルーティング)
[Security Group フィルタリング]
    ↓
[MCP Server on EC2/Fargate/Agentcore]
```

この構成により、すべての通信がAWSのバックボーンネットワーク上で処理され、インターネットを経由しません。VPCフローログを有効化することで、すべての通信パターンを記録し、異常なアクセスを検知できます。

#### 他のセキュア接続方法との比較

| 方式 | セキュリティ | 設定複雑度 | コスト | 適用場面 |
|------|------------|-----------|--------|---------|
| VPC接続（本機能） | 高 | 低 | 低 | MCPサーバーがAWS上にある場合 |
| API Gateway + VPC Link | 高 | 中 | 中 | REST APIとして公開したい場合 |
| AWS PrivateLink | 最高 | 高 | 高 | クロスアカウント・クロスVPC接続 |
| VPN/Direct Connect | 高 | 高 | 高 | オンプレミスMCPサーバーとの接続 |

Amazon QuickのVPC接続は、**AWS上にMCPサーバーが存在する場合に最もシンプルで効果的な選択肢**となります。

### Amazon Bedrock AgentCore Identity の Secrets Manager 統合

Amazon Bedrock AgentCore Identityが、AWS Secrets Managerで顧客自身が管理するシークレットを参照できるようになりました。これは一見地味なアップデートに見えますが、**エンタープライズのガバナンス要件を満たす上で極めて重要**な機能強化です。

#### 従来の課題：サービス管理型シークレットの制限

従来、AgentCore Identityはシークレット（APIキーやデータベース認証情報など）をサービス側で自動作成・管理していました。この方式には以下の制約がありました：

- **カスタマー管理キー（CMK）による暗号化ができない** - コンプライアンス要件で必須の場合がある
- **リソースタグの適用が不可** - コスト配分やアクセス制御の自動化ができない
- **シークレットのライフサイクル管理が制限される** - 自動ローテーションや承認フローを組み込めない
- **既存のセキュリティツールチェーンと統合できない** - SIEMやガバナンスツールとの連携が困難

#### Bring Your Own Secrets (BYOS) モデルのメリット

今回のアップデートにより、以下のような運用が可能になります：

```bash
# 1. まずSecrets Managerでシークレットを作成（CMKを指定）
$ aws secretsmanager create-secret \
    --name my-agentcore-credentials \
    --kms-key-id arn:aws:kms:us-east-1:123456789012:key/abcd1234-5678-90ab-cdef-EXAMPLE11111 \
    --secret-string '{"username":"agent-user","password":"SecureP@ssw0rd"}' \
    --tags Key=Environment,Value=Production Key=CostCenter,Value=AI-Team

# 2. 自動ローテーションを設定
$ aws secretsmanager rotate-secret \
    --secret-id my-agentcore-credentials \
    --rotation-lambda-arn arn:aws:lambda:us-east-1:123456789012:function:SecretsManagerRotation \
    --rotation-rules AutomaticallyAfterDays=30

```

続いて、作成済みシークレットの ARN を AgentCore Identity の認証情報プロバイダー（credential provider）から参照するよう構成します。認証情報プロバイダーは `bedrock-agentcore-control` サービス（例：`create-api-key-credential-provider` / `create-oauth2-credential-provider`）で作成・管理します。本アップデートにより、サービスが新規シークレットを自動生成する代わりに、上記で用意した既存シークレットを指定できるようになりました。正確なパラメータ仕様は[公式ドキュメント](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html)を参照してください。

この構成により、シークレットの**作成・暗号化・タグ付け・ローテーション・アクセス制御**をすべて組織のポリシーに基づいて管理できます。

#### 機能比較：サービス管理型 vs カスタマー管理型

| 機能 | サービス管理型（従来） | カスタマー管理型（新機能） |
|------|----------------------|--------------------------|
| シークレット作成主体 | AgentCore Identity | 顧客（Secrets Manager） |
| CMKによる暗号化 | ❌ 不可（AWS管理キー固定） | ✅ 可能 |
| リソースタグ | ❌ 制限あり | ✅ 完全制御 |
| 自動ローテーション | ❌ 非対応 | ✅ Lambda関数で実装可能 |
| リソースベースポリシー | ❌ 非対応 | ✅ クロスアカウントアクセス可能 |
| 監査ログの粒度 | 基本 | 詳細（CloudTrail統合） |
| 初期設定の複雑度 | 低 | 中（Secrets Manager事前作成） |
| ランタイムパフォーマンス | 同一 | 同一 |

#### 実装例：マルチアカウント環境でのシークレット管理

エンタープライズ環境では、セキュリティアカウントで一元管理されたシークレットを、複数の開発/本番アカウントから参照するケースが一般的です。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::987654321098:role/AgentCoreExecutionRole"
      },
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "secretsmanager:ResourceTag/AllowedServices": "AgentCore"
        }
      }
    }
  ]
}
```

このリソースベースポリシーをSecrets Managerのシークレットにアタッチすることで、**特定のタグを持つシークレットのみを特定のアカウントに共有**できます。

#### シークレットローテーション時の影響検証

自動ローテーションを有効化した際、AgentCore Identityの動作に影響がないことを確認することが重要です。AWS Secrets Managerのローテーションは、次の手順で実行されます：

1. **新バージョンのシークレット作成** - AWSPENDING ラベルが付与
2. **新バージョンの検証** - ターゲットサービスで接続テスト
3. **新旧バージョンの切り替え** - AWSCURRENT ラベルの移動
4. **旧バージョンの無効化** - AWSPREVIOUS ラベルに格納（ロールバック用）

AgentCore Identityは常に `AWSCURRENT` ラベルのシークレットを参照するため、ローテーションが完了して `AWSCURRENT` が新バージョンに移動すれば、アプリケーション側の設定変更なしにシークレットの切り替えが反映されます。

## SRE視点での活用ポイント

### プライベートMCPサーバー接続の運用設計

SREの観点では、Amazon QuickのVPC接続機能は**障害時の影響範囲の限定**と**セキュリティインシデント時の迅速な遮断**に大きな価値があります。

例えば、VPCフローログとCloudWatch Logs Insightsを組み合わせることで、異常なトラフィックパターンを検知できます：

```sql
fields @timestamp, srcAddr, dstAddr, bytes
| filter dstAddr like /10.0.1.50/
| stats sum(bytes) as totalBytes by srcAddr
| sort totalBytes desc
| limit 10
```

このクエリでMCPサーバーへの通信量が異常に増加したクライアントを特定し、Security Groupのルールを自動更新するLambda関数をトリガーすることで、**インシデント検知から遮断までを数分以内に完結**させられます。

また、MCP コネクターが利用する VPC・サブネット・セキュリティグループを Terraform 等でコード化しておけば、環境ごとに構成を管理できます。たとえば、コネクターからの通信を制御するセキュリティグループは次のように環境ごとに定義できます：

```hcl
resource "aws_security_group" "mcp_connector" {
  name        = "mcp-connector-${var.environment}"
  description = "Controls traffic from the Amazon Quick MCP connector"
  vpc_id      = var.vpc_id

  tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Service     = "AmazonQuick"
  }
}
```

> ※ Amazon Quick の MCP コネクター（VPC 接続）そのものを管理する専用の Terraform リソースは、本記事執筆時点では確認できていません。最新の対応状況は[公式の MCP 統合ドキュメント](https://docs.aws.amazon.com/quick/latest/userguide/mcp-integration.html)を参照してください。

本番環境では厳格なSecurity Groupルールを適用し、開発環境では柔軟なアクセスを許可するといった**環境ごとのセキュリティポリシーの差別化**が容易になります。

### Secrets Manager統合によるシークレット管理の標準化

AgentCore IdentityのSecrets Manager統合は、**組織全体でシークレット管理を統一**する絶好の機会です。SREチームが中央で管理するSecrets Managerのベストプラクティスを、AI/MLワークロードにも適用できます。

特に以下のシナリオで効果を発揮します：

**シナリオ1：コンプライアンス監査への対応**  
CloudTrailでSecrets Managerへのアクセスを記録することで、「誰が」「いつ」「どのシークレットに」アクセスしたかを完全に追跡できます。これにより、SOC2やISO27001の監査要件をクリアしやすくなります。

**シナリオ2：シークレット漏洩時のインシデント対応**  
万が一、シークレットが漏洩した疑いがある場合、Secrets Managerで該当シークレットを即座に無効化できます。AgentCore Identityは次回のアクセス時に自動的に新しいシークレットを取得するため、**アプリケーションコードの変更なしで緊急対応が完了**します。

**シナリオ3：定期的なシークレットローテーション**  
セキュリティポリシーで30日ごとのシークレットローテーションが義務付けられている場合、EventBridgeスケジュールでローテーションLambdaを起動し、Secrets Managerのローテーション機能を実行します。AgentCore Identityを含むすべてのサービスが自動的に新しいシークレットを使用するため、**運用負荷ゼロでポリシー遵守**が実現します。

ただし、導入時には以下の点に注意が必要です：

- **IAMポリシーの適切な設計** - 過剰な権限付与を避け、最小権限の原則に従う
- **KMSキーのキャパシティ管理** - CMK使用時は、暗号化オペレーションのリクエストクォータ（リージョン・キータイプにより異なる）に注意
- **リージョン間レプリケーション** - マルチリージョン構成ではSecrets Managerのレプリケーション機能を活用
- **コストの見積もり** - Secrets Manager利用料（$0.40/secret/月 + API呼び出し料金）を考慮

## 全アップデート一覧

| # | サービス | アップデート内容 | リンク |
|---|---------|----------------|--------|
| 1 | Amazon Quick | VPC経由のMCPサーバー接続をサポート。プライベートネットワーク上のMCPサーバーにセキュアに接続可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-quick-vpc-mcp/) |
| 2 | Amazon EC2 | M8aznインスタンス（AMD EPYC Turin、5GHz）がアイルランドリージョンで利用可能に。前世代比最大2倍のコンピュート性能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ec2-m8azn-europe-ireland/) |
| 3 | Amazon EC2 | M8i/M8i-flexインスタンス（Intel Xeon 6）がニュージーランドリージョンで利用可能に。PostgreSQL 30%、NGINX 60%高速化 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ec2-m8i-m8i-flex-new-zealand/) |
| 4 | Amazon SageMaker | Unified StudioがIAMパーミッションバウンダリーのカスタマイズに対応。SCP必須環境での導入が容易に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-sagemaker-scp/) |
| 5 | Amazon Quick Research | AWS KMSの顧客管理キー（CMK）による暗号化をサポート。CloudTrailでデータアクセス追跡が可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-quick-research-cm-keys/) |
| 6 | Amazon SageMaker | HyperPodにAIコーディングアシスタント向けトラブルシューティングスキルを追加。Claude Code、Cursor、Kiroと統合可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-sagemaker-hyperpod-troubleshooting-skills/) |
| 7 | Amazon SageMaker | HyperPodがEFA-onlyネットワークインターフェースをサポート。VPC内のIPアドレス枯渇を防ぎながらクラスタ拡張が可能 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-sagemaker-hyperpod-efa-only/) |
| 8 | Amazon SES | テナント単位の抑制リストをサポート。SaaSプロバイダーなどで顧客間のメール配信問題を分離可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-ses-tenant-level-suppression-lists/) |
| 9 | Amazon Bedrock | bedrock-mantleエンドポイント（OpenAI/Anthropic API互換）にCloudWatchメトリクスを追加。推論トラフィックの監視が可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-bedrock-supports-cloudwatch-metrics-bedrock-mantle-endpoint/) |
| 10 | Amazon Bedrock | AgentCore IdentityがSecrets Managerの既存シークレット参照をサポート。CMK暗号化やタグ管理が可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/06/agentcore-identity-secrets-manager/) |

## まとめ

2026年6月2日のアップデートは、**エンタープライズのセキュリティ・ガバナンス要件への対応**と**大規模MLワークロードの運用効率化**という2つの軸で整理できます。

特に注目すべきは、AWSがAI/MLサービスにおいても**従来のインフラサービスと同等のセキュリティ・ガバナンス機能を提供し始めた**点です。Amazon QuickのVPC接続対応やAgentCore IdentityのSecrets Manager統合は、「AI機能を使いたいが、セキュリティ要件が障壁になっている」という企業の課題を解決する重要な一歩と言えます。

一方、SageMaker HyperPodのトラブルシューティングスキルやEFA-only対応は、**数百〜数千ノード規模のMLクラスタ運用を現実的なものにする**インフラ改善です。AIコーディングアシスタントとの統合により、専門知識がなくても高度なクラスタ診断が可能になる点は、SREの運用負荷軽減に直結します。

また、EC2の新世代インスタンス（M8azn、M8i/M8i-flex）が欧州・アジア太平洋地域に展開されたことで、グローバルなワークロード配置の選択肢が広がりました。特にM8aznの5GHz動作は、レイテンシに敏感な金融取引システムなどで大きな価値を持ちます。

全体として、本日のアップデートは**エンタープライズのクラウド活用を次のステージに進める**基盤強化と位置付けられます。セキュリティとパフォーマンスの両立、ガバナンスと運用効率の両立が、これまで以上に現実的になってきています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)