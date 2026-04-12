---
title: "【AWS】2026/04/07 のアップデートまとめ"
date: 2026-04-07T08:01:18+09:00
draft: false
tags: ["aws", "s3", "rds", "fsx", "workspaces", "verifiedpermissions", "oracle", "openzfs", "smithy"]
categories: ["AWS Updates"]
summary: "2026/04/07 のAWSアップデートまとめ。S3でSSE-Cがデフォルト無効化開始、Verified Permissionsにポリシーストアエイリアスと名前付きポリシーが追加など6件"
---

![](/images/aws-updates-20260407/header.png)

## はじめに

2026年4月7日のAWSアップデートは6件です。S3でSSE-C（顧客提供キーによるサーバーサイド暗号化）がデフォルト無効になる変更のロールアウトが始まりました。Verified Permissionsにはポリシーストアエイリアスと名前付きポリシーが追加されています。

## 注目アップデート深掘り

### Amazon S3 — SSE-C デフォルト無効化のロールアウト開始

![S3 SSE-C デフォルト無効化：影響範囲マップ](/images/aws-updates-20260407/s3-sse-c-impact.png)

S3が新規・既存バケットでSSE-C（Server-Side Encryption with Customer-provided keys）をデフォルト無効にする変更を展開し始めました。2025年11月に予告されていたもので、4月6日から数週間かけて37リージョン（中国・GovCloud含む）に順次適用されます。

SSE-Cは、暗号化キーをリクエストごとにユーザーが提供する方式です。AWSがキーを保持しないため鍵管理の負担が大きく、誤ったキー運用によるデータ復旧不能のリスクもありました。今回の変更で、意図せずSSE-Cを使ってしまうケースを防ぎます。

**影響範囲の整理:**

| 対象 | 動作 |
|------|------|
| 新規バケット | SSE-Cは自動的に無効 |
| 既存バケット（SSE-Cオブジェクトなし） | 新規書き込みでSSE-Cが無効化 |
| 既存バケット（SSE-C使用実績あり） | 変更なし |

SSE-Cを意図的に使っている場合は影響を受けません。現在の暗号化設定を確認するには以下のコマンドが使えます：

```bash
# バケットの暗号化設定を確認
$ aws s3api get-bucket-encryption --bucket my-bucket
```

多くの環境ではSSE-S3やSSE-KMSを使っているため、実質的な影響は限定的です。ただし、IaCで明示的にSSE-C設定を管理しているなら、デフォルト値との整合性を `terraform plan` 等で確認しておくと安心です。

### Amazon Verified Permissions — ポリシーストアエイリアスと名前付きポリシー

> **Amazon Verified Permissionsとは？**
> Cedar言語ベースのマネージド認可サービスです。アプリケーションの権限管理をコードから切り離し、ポリシーとして宣言的に記述できます。IAMがAWSリソースへのアクセス制御を担うのに対し、Verified Permissionsはアプリケーション内のユーザー操作の認可を担います。

ポリシーストアに人間が読めるエイリアスを付けられるようになりました。加えて、ポリシーやテンプレートにも意味のある名前を付けられます。

マルチテナント環境では、テナントごとにポリシーストアを分けるのが一般的です。これまではシステム生成のUUID（`ps-aBcDeFgHiJkLmNoP` のような文字列）でしか参照できず、テナントIDとポリシーストアIDの対応表を自前で管理する必要がありました。エイリアスを使えば `tenant-acme-prod` のような名前で直接API呼び出しができます。

ポリシー自体も同様です。`policy-abc123` ではなく `admin-read-all-documents` のように命名できるようになったことで、監査やデバッグ時の視認性が上がります。

対応リージョンはVerified Permissionsが利用可能な全リージョンです。

## 実用的な活用ポイント

**S3 SSE-Cデフォルト無効化**は、ほとんどの環境で対応不要です。SSE-S3やSSE-KMSを使っていれば影響なし。ただし、`aws s3api put-object --sse-c-algorithm` を使っているスクリプトやアプリケーションがある場合は事前検証をおすすめします。

**Verified Permissionsのエイリアス・名前付きポリシー**は、地味ですが運用改善効果が大きい変更です。ポリシー管理のIaC化やCI/CDパイプラインでの参照がUUIDから名前ベースになるため、コードレビューやトラブルシュート時の認知負荷が下がります。

**FSx for OpenZFSのメルボルンリージョン対応**は、オーストラリアにインフラを持つ組織向け。メルボルンリージョンは2022年開設と比較的新しいため、ストレージ系サービスの対応が追いついてきた形です。

## 全アップデート一覧

> **Smithy-Javaとは？**
> AWSが開発したオープンソースのJavaクライアント生成フレームワークです。Smithyモデル（AWSのAPI定義言語）から型安全なクライアントコードを自動生成します。Java 21の仮想スレッドを活用し、非同期パターンなしでシンプルなブロッキングAPIを記述できるのが特徴です。

| サービス | アップデート内容 | リンク |
|---------|-----------------|--------|
| Amazon S3 | SSE-C（顧客提供キー暗号化）を新規・既存バケットでデフォルト無効化開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/s3-default-bucket-security-setting/) |
| Amazon RDS for Oracle | Oracle Management Agent version 24.1.0.0.v1 サポート（Oracle Enterprise Manager Cloud Control 24aiR1 対応） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-rds-oracle-supports-oracle-management-agent-version-for-oracle-enterprise-manager=cloud-control/) |
| Amazon FSx for OpenZFS | AWS Asia Pacific (Melbourne) リージョンで提供開始 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-fsx-openzfs-melbourne-region/) |
| Smithy-Java | Java 21仮想スレッド対応のクライアント生成フレームワークがGA | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/03/smithy-java-client-framework/) |
| Amazon WorkSpaces Personal | PrivateLink VPCエンドポイントに一意のDNS名をサポート | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-workspaces-personal-privatelink/) |
| Amazon Verified Permissions | ポリシーストアエイリアスと名前付きポリシー・テンプレートを追加 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-verified-permissions-policy-store/) |

## まとめ

S3のSSE-Cデフォルト無効化は、昨年11月の予告どおり粛々と進んでいます。影響範囲は限定的ですが、SSE-Cを使っている環境では設定確認を。Verified Permissionsのエイリアス・命名機能は、マルチテナント環境でのポリシー管理が楽になる実用的な改善です。

残りはリージョン展開、バージョン更新、フレームワークGA、PrivateLink機能追加と、手堅いアップデートが並んだ日でした。
