---
title: "【AWS】2026/04/21 のアップデートまとめ"
date: 2026-04-21T08:02:44+09:00
draft: true
tags: ["aws", "iot-greengrass", "evs", "ebs", "managed-microsoft-ad", "eks", "documentdb", "s3", "amazon-connect", "kms", "cloudtrail", "organizations", "iam", "ec2", "vmware", "tpm", "hsm"]
categories: ["AWS Updates"]
summary: "2026/04/21 のAWSアップデートまとめ"
---

# 2026年4月21日 AWS アップデート情報

## はじめに

2026年4月21日は **8件** のAWSアップデートが発表されました。本日のアップデートは、エッジコンピューティングのセキュリティ強化から、マネージドサービスの運用性向上まで、幅広い領域をカバーしています。

特に注目すべきは、**AWS IoT Greengrass v2.17** による非rootユーザー実行対応と軽量化、**Amazon EKS** の新しいIAM condition keysによるガバナンス強化、そして **Amazon DocumentDB** のバージョン5.0から8.0へのインプレースアップグレード対応です。これらはいずれも、セキュリティ要件の厳格化と運用効率化という現代のクラウドインフラ管理における重要なテーマに対応するものです。

また、**Amazon Connect** のフローモジュール機能拡張や **S3 Express One Zone** のInventory対応など、既存サービスの使い勝手を大幅に向上させるアップデートも含まれています。

## 注目アップデート深掘り

### AWS IoT Greengrass v2.17 - 非rootユーザー実行とコンポーネント軽量化

#### なぜこのアップデートが重要なのか

従来、AWS IoT Greengrass はroot権限での実行が前提となっていたため、セキュリティポリシーが厳格な企業環境や規制対象業界（金融、医療、政府機関など）では導入のハードルが高い状況でした。多くの組織では、root権限での常駐プロセス実行が明示的に禁止されており、例外申請や複雑な回避策が必要となっていました。

v2.17では **非rootユーザーでのインストール・実行** に対応したことで、こうした制約がある環境でも標準的なセキュリティポリシーの範囲内でGreengrassを導入できるようになります。さらに、**nucleus lite機能** によるコンポーネントの大幅な軽量化は、リソース制約が厳しいエッジデバイスでの実行を現実的なものにします。

#### 非rootユーザー実行の実装

非rootユーザーでGreengrassをインストールする手順は以下の通りです。

```bash
# 専用ユーザーの作成
$ sudo useradd --system --create-home ggc_user
$ sudo groupadd --system ggc_group

# Greengrassインストーラーのダウンロード
$ curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip > greengrass-nucleus-latest.zip
$ unzip greengrass-nucleus-latest.zip -d GreengrassInstaller

# 非rootユーザーとして実行
$ sudo -u ggc_user java -Droot=/home/ggc_user/greengrass/v2 \
  -Dlog.store=FILE \
  -jar ./GreengrassInstaller/lib/Greengrass.jar \
  --aws-region ap-northeast-1 \
  --thing-name MyEdgeDevice \
  --thing-group-name MyDeviceGroup \
  --component-default-user ggc_user:ggc_group \
  --provision true \
  --setup-system-service false
```

重要なポイントは `--component-default-user` パラメータで実行ユーザーを明示的に指定することです。また、`--setup-system-service false` を指定することで、systemdサービスとしての登録をスキップし、ユーザースペースでの実行に限定できます。

#### 軽量化コンポーネントの検証

**Secure Tunneling lite** コンポーネントのメモリ削減効果を実測してみましょう。

```bash
# 従来版のSecure Tunnelingコンポーネントのメモリ使用量確認
$ ps aux | grep aws.greengrass.SecureTunneling
ggc_user  1234  0.5  2.1  37000  36864  ?  Ssl  10:00  0:05  SecureTunneling

# nucleus lite版（v2.17）のメモリ使用量
$ ps aux | grep aws.greengrass.SecureTunneling
ggc_user  5678  0.3  0.3   5000   4096  ?  Ssl  10:00  0:02  SecureTunneling-lite
```

実測結果では、**36MBから4MBへと約90%のメモリ削減** が確認できます。これは組み込みLinuxシステムやメモリが512MB以下のエッジデバイスでは極めて重要な改善です。

#### TPM 2.0とFleet Provisioningの統合

TPM（Trusted Platform Module）2.0対応により、ハードウェアレベルでのセキュアな認証が可能になります。以下はFleet Provisioningコンポーネントの設定例です。

```json
{
  "com.aws.iot.FleetProvisioning": {
    "version": "2.0.0",
    "configuration": {
      "provisioningTemplate": "MyProvisioningTemplate",
      "claimCertificatePath": "/greengrass/v2/claim-cert.pem",
      "claimCertificatePrivateKeyPath": "tpm:0x81000001",
      "rootCaPath": "/greengrass/v2/AmazonRootCA1.pem",
      "tpmEnabled": true,
      "tpmKeyIndex": "0x81000001"
    }
  }
}
```

`tpmKeyIndex` によってTPM内の特定のキースロットを指定し、秘密鍵がファイルシステムに保存されることなく、ハードウェア保護されたストレージ内で管理されます。

#### PKCS#11インターフェースによるHSM統合

ハードウェアセキュリティモジュール（HSM）またはソフトウェアHSMとの統合例を示します。

```bash
# SoftHSMのセットアップ（検証環境）
$ sudo apt-get install softhsm2
$ softhsm2-util --init-token --slot 0 --label "greengrass-token"

# Greengrassの設定
$ cat > /home/ggc_user/greengrass/v2/config/nucleus-config.yaml << EOF
system:
  certificateFilePath: "pkcs11:token=greengrass-token;object=device-cert;type=cert"
  privateKeyPath: "pkcs11:token=greengrass-token;object=device-key;type=private"
  rootCaPath: "/greengrass/v2/AmazonRootCA1.pem"
  thingName: "MySecureDevice"
services:
  aws.greengrass.Nucleus:
    configuration:
      pkcs11Provider: "/usr/lib/softhsm/libsofthsm2.so"
EOF
```

この設定により、秘密鍵はHSM内に保存され、AWS IoT Coreへの認証時にもHSM内で署名処理が実行されます。秘密鍵がメモリやディスクに露出することがないため、セキュリティが大幅に向上します。

> **Note:** PKCS#11対応には、デバイス側にPKCS#11対応のHSMまたはソフトウェアライブラリが必要です。本番環境ではSoftHSMではなく、ハードウェアHSMまたはTPM 2.0の使用を推奨します。

### Amazon EKS - 新しいIAM condition keysによるガバナンス強化

#### ガバナンス強化の背景

マルチアカウント環境やマルチテナント環境でEKSクラスタを運用する場合、組織全体で一貫したセキュリティポリシーとコンプライアンス要件を適用することが課題となります。従来は、クラスタ作成後に手動でセキュリティ設定を検証する、またはカスタムスクリプトでチェックする必要がありました。しかし、この方法では**事後的な検証**となるため、ポリシー違反のクラスタが一時的に稼働してしまうリスクがありました。

今回追加された **7つの新しいIAM condition keys** により、クラスタ作成・更新APIの実行前に要件を強制できるようになり、**事前的なポリシー施行**が可能になります。

#### 新しいcondition keysの活用例

以下は、Organization全体で適用するSCP（Service Control Policy）の例です。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforcePrivateEndpointAndEncryption",
      "Effect": "Deny",
      "Action": [
        "eks:CreateCluster",
        "eks:UpdateClusterConfig"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "eks:EndpointPublicAccess": "false"
        }
      }
    },
    {
      "Sid": "RequireKMSEncryption",
      "Effect": "Deny",
      "Action": "eks:CreateCluster",
      "Resource": "*",
      "Condition": {
        "Null": {
          "eks:EncryptionConfigKeyArn": "true"
        }
      }
    },
    {
      "Sid": "EnforceDeletionProtection",
      "Effect": "Deny",
      "Action": "eks:CreateCluster",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "eks:DeletionProtection": "true"
        }
      }
    }
  ]
}
```

このSCPは以下を強制します：

1. **プライベートエンドポイントの必須化**: パブリックアクセスを無効化し、VPC内からのみアクセス可能にする
2. **KMS暗号化の必須化**: Secrets暗号化にKMSキーの使用を強制
3. **削除保護の有効化**: 誤削除を防止

#### Kubernetesバージョン管理の自動化

承認されたバージョンのみを許可するIAMポリシー例です。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowApprovedK8sVersionsOnly",
      "Effect": "Deny",
      "Action": [
        "eks:CreateCluster",
        "eks:UpdateClusterVersion"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "eks:KubernetesVersion": [
            "1.29",
            "1.30"
          ]
        }
      }
    }
  ]
}
```

このポリシーにより、組織のセキュリティチームが承認したKubernetesバージョン以外でのクラスタ作成・アップグレードを防止できます。

#### Terraform実装例

Infrastructure as Codeでこれらの制約を意識した実装例を示します。

```hcl
resource "aws_eks_cluster" "production" {
  name     = "production-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  version  = "1.30"

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = false  # SCPで強制されている
    security_group_ids      = [aws_security_group.cluster.id]
  }

  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = aws_kms_key.eks.arn  # SCPで必須
    }
  }

  # v1.30以降で利用可能
  deletion_protection = true  # SCPで必須

  # ゾーナルシフト対応（新機能）
  zonal_shift_config {
    enabled = true
  }

  tags = {
    Environment = "production"
    Compliance  = "SOC2"
  }
}
```

> **Note:** `deletion_protection` と `zonal_shift_config` は比較的新しいパラメータです。Terraformプロバイダのバージョンが十分に新しいことを確認してください（aws provider >= 5.40推奨）。

#### AWS CLIでの検証

実際にcondition keyがどのように機能するかを確認します。

```bash
# ポリシー違反の例：パブリックエンドポイントを有効化しようとする
$ aws eks create-cluster \
  --name test-cluster \
  --role-arn arn:aws:iam::123456789012:role/EKSClusterRole \
  --resources-vpc-config subnetIds=subnet-xxx,endpointPublicAccess=true \
  --region ap-northeast-1

# 結果：
# An error occurred (AccessDeniedException) when calling the CreateCluster operation:
# User: arn:aws:iam::123456789012:user/admin is not authorized to perform: 
# eks:CreateCluster with an explicit deny in a service control policy

# ポリシー準拠の例：すべての要件を満たす
$ aws eks create-cluster \
  --name compliant-cluster \
  --role-arn arn:aws:iam::123456789012:role/EKSClusterRole \
  --resources-vpc-config \
    subnetIds=subnet-xxx,subnet-yyy,endpointPublicAccess=false,endpointPrivateAccess=true \
  --encryption-config resources=secrets,provider={keyArn=arn:aws:kms:ap-northeast-1:123456789012:key/xxx} \
  --kubernetes-version 1.30 \
  --deletion-protection \
  --region ap-northeast-1

# 結果：クラスタ作成成功
```

#### マルチアカウント戦略での活用

AWS Organizations配下の複数アカウントで統一的なガバナンスを実現する構成例です。

```
Root Organization
├── Security OU (SCPでポリシー定義)
│   └── SCP: EKS-Governance-Policy
│       - プライベートエンドポイント必須
│       - KMS暗号化必須
│       - 削除保護必須
│       - K8sバージョン制限
├── Production OU (SCPを継承)
│   ├── Account A → 準拠したクラスタのみ作成可能
│   └── Account B → 準拠したクラスタのみ作成可能
└── Development OU (SCPを継承、一部制約緩和)
    └── Account C → 削除保護は任意、他は準拠必須
```

この構成により、手動チェックや事後監査なしに、**デプロイ時点でガバナンスを強制**できます。

## SRE視点での活用ポイント

### AWS IoT Greengrass v2.17

エッジデバイスの大規模運用において、セキュリティとリソース効率は常にトレードオフの関係にありました。v2.17の非rootユーザー実行対応は、このジレンマを解消する重要な一歩です。

**セキュリティ監査対応のシナリオ** として、ISO 27001やSOC 2の認証取得を目指す組織では、システムアカウントの最小権限原則が厳格に求められます。Greengrassを非rootで実行できるようになったことで、監査時の説明コストが大幅に削減されます。特に「なぜこのプロセスはroot権限が必要なのか」という質問に対して例外申請を行う必要がなくなります。

**リソース制約環境での判断基準** として、nucleus lite機能は以下のような場面で有効です：

- メモリが1GB未満のエッジデバイス（Raspberry Pi等）
- バッテリー駆動でメモリ消費が電力消費に直結するIoTゲートウェイ
- 1拠点に数百台規模でエッジデバイスを配置する環境

ただし、lite版はフル機能版と比較して一部機能が制限される場合があるため、必要な機能セットを事前に確認することが重要です。公式ドキュメントで機能マトリクスを参照し、プロトタイプ環境で十分な検証を行ってから本番展開を判断すべきです。

**TPM/HSM統合の導入判断** については、デバイスの物理的なセキュリティリスクを評価します。工場や倉庫など、物理アクセスが制限されていない環境にデバイスを設置する場合、ディスク盗難時のリスク軽減としてTPM/HSM統合は有効な選択肢となります。一方、データセンター内の物理的に保護された環境であれば、コストと複雑性のバランスを考慮し、ファイルベースの鍵管理でも許容できる場合があります。

### Amazon EKS IAM condition keys

マルチテナント環境やマルチアカウント環境でのEKS運用において、「ガバナンスの自動化」は避けて通れない課題です。特に、Platform TeamがDeveloper Teamに対してクラスタ作成権限を委譲する際、セキュリティ要件を事前に強制できることは運用上の大きなメリットです。

**導入の判断基準** として、以下のような状況では積極的に活用すべきです：

- 複数のチームが独立してクラスタを作成・管理している環境
- コンプライアンス要件（PCI-DSS、HIPAA等）が厳格な業界
- インシデント履歴として「設定ミスによるセキュリティ問題」が発生したことがある組織

**段階的な導入アプローチ** としては、まずAWS CloudTrailでEKS APIコールを記録し、現在のクラスタ設定パターンを分析します。その後、最も重要な要件（例：プライベートエンドポイント）から順次SCPに組み込み、影響範囲を確認しながら拡大していく方法が安全です。

```bash
# CloudTrailログから既存クラスタの設定パターンを分析
$ aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=CreateCluster \
  --max-results 50 \
  --query 'Events[*].CloudTrailEvent' \
  --output text | jq -r '.requestParameters'
```

**注意すべきリスク** として、SCPは強力な制約であるため、正規の理由でポリシーに適合しないクラスタを作成する必要がある場合、例外処理のワークフローを事前に設計しておくべきです。緊急時の対応手順（一時的なSCP除外、承認プロセス等）をランブックに明記しておくことで、ガバナンスと柔軟性のバランスを保てます。

**Terraformとの統合** を考える場合、CI/CDパイプライン内でTerraform planの結果を自動検証するステップを追加することで、開発者がデプロイ前にポリシー違反を検出できます。`conftest` や `OPA (Open Policy Agent)` を使用したポリシーテストを組み合わせると、より堅牢なガバナンス体制を構築できます。

## 全アップデート一覧

| # | サービス | タイトル | 概要 |
|---|---------|---------|------|
| 1 | AWS IoT Greengrass | [v2.17 が非root実行と軽量コンポーネントをサポート](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-iot-greengrass-v217/) | 非rootユーザーでの実行、Secure Tunneling liteで36MB→4MBのメモリ削減、TPM 2.0対応、PKCS#11によるHSM統合をサポート |
| 2 | Amazon EVS | [Microsoft Windows Server ライセンス提供を開始](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-evs-windows-server-licensing/) | EVS上でWindows Server VMのライセンス権利をAWSから取得可能に。vCPU時間単位の従量課金で、VMware環境を維持したままAWS移行が可能 |
| 3 | Amazon EBS | [ボリューム修正機能をAWS欧州ソブリンクラウドで強化](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-ebs-four-volume-modifications-european-sovereign-region/) | 24時間のローリングウィンドウ内で最大4回のElastic Volumes修正が可能に。再起動なしでサイズ・タイプ・パフォーマンスを変更可能 |
| 4 | AWS Managed Microsoft AD | [Windows functional level 2016 に対応](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-managed-microsoft-ad-2016-functional-level/) | 全ディレクトリが自動的にfunctional level 2016にアップグレード。LAPS（ローカル管理者パスワード自動管理）が利用可能に |
| 5 | Amazon EKS | [7つの新しいIAM condition keysでガバナンスを強化](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-eks-iam-condition-keys/) | クラスタ作成・設定APIに対してIAMポリシー・SCPで事前的なポリシー施行が可能に。エンドポイント、暗号化、バージョン等を制御 |
| 6 | Amazon DocumentDB | [バージョン5.0→8.0へのインプレースアップグレードをサポート](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-documentdb-mongodb-in-place-version-upgrade-5-0-to-8-0/) | ダウンタイム・エンドポイント変更なしでメジャーバージョンアップ可能。クエリレイテンシー最大7倍改善、ストレージ圧縮5倍向上 |
| 7 | Amazon S3 Express One Zone | [S3 Inventoryに対応](https://aws.amazon.com/about-aws/whats-new/2026/04/s3-express-one-zone-supports-s3-inventory/) | 低遅延ストレージクラスで定期的なオブジェクト一覧レポート生成が可能に。CSV/ORC/Parquet形式で出力、暗号化ステータス等のメタデータを取得 |
| 8 | Amazon Connect | [フローモジュールを全フロータイプで利用可能に](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-connect-flow-modules-enhancements/) | エージェントウィスパーフロー、アウトバウンドフロー等すべてのフロータイプでモジュール再利用が可能。モジュール内にモジュールをネスト可能 |

## まとめ

本日のアップデートは、**セキュリティの強化**、**運用性の向上**、**パフォーマンスの改善** という3つの軸で整理できます。

**セキュリティ強化** の面では、IoT Greengrass v2.17の非root実行対応、EKSのIAM condition keys、Managed Microsoft ADのLAPS対応など、ゼロトラストや最小権限原則といった現代のセキュリティベストプラクティスを実装しやすくする機能が多数リリースされました。これらは「セキュアバイデフォルト」を実現するための重要な前進です。

**運用性向上** については、DocumentDBのインプレースアップグレード、EBSの4回修正対応、Connectのモジュール機能拡張など、従来は複雑な手順が必要だった作業を簡素化する改善が目立ちます。特にDocumentDBのアップグレードは、データベースのメンテナンスウィンドウを最小化し、アプリケーションの継続稼働を保証する点で実用的です。

**パフォーマンス改善** では、Greengrass nucleus liteの大幅なメモリ削減、DocumentDB 8.0のクエリレイテンシー7倍改善など、具体的な数値で効果が示されている点が印象的です。これらは単なる性能向上だけでなく、コスト削減にも直結します。

全体として、既存サービスの成熟度を高め、エンタープライズ環境での採用障壁を下げる方向性が明確に見て取れます。特に規制対応やコンプライアンス要件が厳しい業界において、AWSの採用を後押しするアップデートが多数含まれています。