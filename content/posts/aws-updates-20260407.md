---
title: "【AWS】2026/04/07 のアップデートまとめ"
date: 2026-04-07T08:01:18+09:00
draft: true
tags: ["aws", "s3", "rds", "fsx", "workspaces", "verifiedpermissions", "oracle", "openzfs"]
categories: ["AWS Updates"]
summary: "2026/04/07 のAWSアップデートまとめ"
---

# AWS が 2026年4月7日に発表した6つのアップデート：注目は S3 セキュリティ強化と Verified Permissions の進化

## はじめに

2026年4月7日、AWS から6つの重要なアップデートが発表されました。今回のアップデートで特に注目すべきは、Amazon S3 のセキュリティベストプラクティスが新規・既存バケットでデフォルト適用される変更と、Amazon Verified Permissions でポリシー管理がより直感的になるエイリアス機能の追加です。その他にも、Oracle データベース管理の強化、FSx for OpenZFS のメルボルンリージョン展開、Smithy-Java フレームワークの一般提供開始、WorkSpaces Personal の PrivateLink 機能拡張など、企業のクラウド活用を支援する機能が多数リリースされています。

## 注目アップデート深掘り

### Amazon S3 のセキュリティベストプラクティス自動適用

Amazon S3 が新規・既存バケットに対してセキュリティベストプラクティスをデフォルトで適用する重要な変更が開始されました。この変更は、S3 バケットの設定ミスによるデータ漏洩事故を防ぐための根本的な対策として注目されます。

従来、S3 バケットのセキュリティ設定は利用者が個別に構成する必要があり、設定漏れや誤設定が原因でセキュリティインシデントが発生するケースが後を絶ちませんでした。今回のアップデートにより、AWS がセキュリティのベースラインを自動的に適用することで、「セキュア・バイ・デフォルト」の原則が強化されます。

具体的な検証手順として、まず新規バケット作成時の動作を確認してみましょう：

```bash
# 新規バケット作成（リージョン指定）
$ aws s3api create-bucket --bucket test-secure-bucket-2026 --region ap-northeast-1 --create-bucket-configuration LocationConstraint=ap-northeast-1

# バケットのパブリックアクセス設定を確認
$ aws s3api get-public-access-block --bucket test-secure-bucket-2026
```

既存バケットについても、段階的にセキュリティ設定が自動適用される予定です。現在のバケット設定を確認し、変更による影響を事前に評価することが重要です：

```bash
# 既存バケット一覧とセキュリティ設定の確認
$ aws s3api list-buckets --query 'Buckets[].Name' --output table

# 特定バケットの詳細なセキュリティ設定確認
$ aws s3api get-bucket-policy-status --bucket existing-bucket-name
$ aws s3api get-bucket-encryption --bucket existing-bucket-name
```

Terraform を使用している場合は、以下のように明示的なセキュリティ設定を追加することで、AWS の自動適用と整合性を保てます：

```hcl
resource "aws_s3_bucket" "secure_bucket" {
  bucket = "my-secure-bucket-2026"
}

resource "aws_s3_bucket_public_access_block" "secure_bucket_pab" {
  bucket = aws_s3_bucket.secure_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "secure_bucket_encryption" {
  bucket = aws_s3_bucket.secure_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

この変更により、意図しないパブリックアクセスの防止、暗号化の強制適用、アクセスログの有効化など、複数のセキュリティ要素が統合的に管理されるようになります。

### Amazon Verified Permissions のポリシー管理機能拡張

Amazon Verified Permissions にポリシーストアエイリアスと名前付きポリシー機能が追加され、マルチテナント環境での権限管理が大幅に簡素化されました。従来はシステム生成の UUID でポリシーを管理していたため、可読性と運用性に課題がありました。

Cedar 言語ベースの認可サービスである Verified Permissions の新機能を実際に試してみましょう。まず、ポリシーストアにわかりやすいエイリアスを設定します：

```bash
# ポリシーストアエイリアスの作成
$ aws verifiedpermissions create-policy-store \
    --validation-settings mode=STRICT \
    --configuration '{"CedarJson":{"commonTypes":"{}"}}' \
    --description "Multi-tenant application policy store"

# エイリアスの設定（ポリシーストアID取得後）
$ aws verifiedpermissions put-policy-store-alias \
    --policy-store-id "PSEXAMPLEabcdefg012345" \
    --alias "production-tenant-policies"
```

名前付きポリシーの作成では、直感的な名前でポリシーを参照できるようになります：

```python
import boto3

client = boto3.client('verifiedpermissions')

# 名前付きポリシーの作成例
policy_definition = {
    'static': {
        'statement': 'permit(principal == User::"alice", action == Action::"read", resource == Document::"doc1");'
    }
}

response = client.create_policy(
    policyStoreId='production-tenant-policies',  # エイリアス使用
    policyId='alice-document-read-policy',       # 意味のあるポリシー名
    definition=policy_definition
)
```

ポリシーテンプレートを活用することで、テナント固有のパラメータを動的に適用できます：

```python
# ポリシーテンプレートの作成
template_definition = {
    'static': {
        'statement': '''
        permit(
            principal == ?principal,
            action in [Action::"read", Action::"write"],
            resource in Folder::"?tenant"
        );
        '''
    }
}

template_response = client.create_policy_template(
    policyStoreId='production-tenant-policies',
    templateId='tenant-folder-access-template',
    definition=template_definition
)
```

Cedar 言語の特徴として、型安全な条件式と豊富な演算子をサポートしており、複雑な業務ルールを簡潔に表現できます。従来の JSON ベース IAM ポリシーと比較して、可読性と保守性が大幅に向上します。

## SRE視点での活用ポイント

今回のアップデートは、SRE の日常業務において運用負荷の軽減とセキュリティ向上の両面でメリットをもたらします。

S3 のセキュリティ強化については、インフラストラクチャコードでバケット作成を自動化している環境では、CI/CD パイプラインでのセキュリティチェックプロセスを簡素化できます。Terraform や CloudFormation のテンプレートから明示的なセキュリティ設定を段階的に削除し、AWS のデフォルト設定に委譲することで、コードの複雑性を減らしながらセキュリティレベルを維持できます。ただし、既存のパブリック公開が必要なバケットについては、事前に影響範囲を調査し、明示的な設定で公開を維持する必要があります。

Verified Permissions の機能拡張は、マイクロサービスアーキテクチャでの認可機能実装において、運用チームとビジネスチームの協働を促進します。従来の UUID ベースのポリシー管理では、障害発生時のトラブルシューティングで「どのポリシーが何を制御しているか」の把握に時間を要していましたが、名前付きポリシーにより迅速な問題特定が可能になります。

CloudWatch アラームと組み合わせた監視設定では、ポリシー評価のメトリクスをエイリアス名でグループ化することで、テナント別の認可パフォーマンス分析が容易になります。特に、認可の失敗率やレスポンス時間をテナント単位で監視し、リソース使用量の最適化に活用できます。

導入時の注意点として、Verified Permissions は Cedar 言語の学習コストが発生するため、チーム内での知識共有体制の整備が重要です。また、既存の認可システムからの移行では、段階的な導入計画を立て、影響範囲を最小限に抑える戦略が必要になります。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|-----------------|--------|
| Amazon S3 | 新規・既存バケットでセキュリティベストプラクティスをデフォルト適用開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/s3-default-bucket-security-setting/) |
| Amazon RDS for Oracle | Oracle Management Agent version 24.1.0.0.v1 サポート（Oracle Enterprise Manager Cloud Control 24aiR1 対応） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-rds-oracle-supports-oracle-management-agent-version-for-oracle-enterprise-manager=cloud-control/) |
| Amazon FSx for OpenZFS | AWS Asia Pacific (Melbourne) リージョンでサービス提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-fsx-openzfs-melbourne-region/) |
| Smithy-Java | Java 21仮想スレッドを活用したクライアントフレームワークが一般提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/03/smithy-java-client-framework/) |
| Amazon WorkSpaces Personal | PrivateLink で独自 DNS 名をサポート開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-workspaces-personal-privatelink/) |
| Amazon Verified Permissions | ポリシーストアエイリアス、名前付きポリシー、ポリシーテンプレート機能を追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-verified-permissions-policy-store/) |

## まとめ

今回のアップデートは、AWS のセキュリティファーストアプローチと運用効率化への取り組みが色濃く反映されています。特に S3 のセキュリティ自動適用は、クラウドセキュリティの責任共有モデルにおいて AWS 側の責任範囲を拡張する重要な変更であり、多くの組織でセキュリティインシデントのリスク軽減に寄与するでしょう。

Verified Permissions の機能拡張も、エンタープライズ環境でのマイクロサービス導入を加速させる要因となりそうです。従来は自社開発していた認可機能をマネージドサービスに移行することで、開発チームはビジネスロジックにより集中できるようになります。

地理的な展開では FSx for OpenZFS のメルボルンリージョン対応、開発フレームワークでは Smithy-Java の一般提供など、AWS エコシステムの着実な拡充も見て取れます。これらのアップデートを通じて、2026年も AWS が企業のデジタルトランスフォーメーションを技術面で強力にサポートしていく姿勢が明確になっています。