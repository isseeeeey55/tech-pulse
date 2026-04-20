---
title: "【AWS】2026/04/21 のアップデートまとめ"
date: 2026-04-21T08:02:44+09:00
draft: false
tags: ["aws", "iot-greengrass", "eks", "documentdb", "s3", "amazon-connect"]
categories: ["AWS Updates"]
summary: "IoT Greengrass v2.17 の非root実行と lite コンポーネント、EKS の IAM condition keys による事前ガバナンス強制、DocumentDB 5.0 → 8.0 インプレースアップグレードほか 8 件を解説"
---

# 2026年4月21日 AWS アップデート情報

![AWS アップデートまとめ 2026/04/21](/images/aws-updates-20260421/header.png)

## はじめに

2026年4月21日は 8件のAWSアップデートが発表されました。エッジコンピューティングのセキュリティ、マネージドサービスの運用性、ストレージの運用ワークフローと、カバー範囲は広めです。

この記事では、AWS IoT Greengrass v2.17 の非rootユーザー実行対応と軽量コンポーネント、Amazon EKS の新しい IAM condition keys によるガバナンス事前強制を掘り下げます。いずれも「既存機能の積み増し」ではなく、導入や運用の障壁そのものを下げるタイプの変更です。

そのほか、Amazon DocumentDB 5.0 → 8.0 のインプレースアップグレード、Amazon Connect のフローモジュール全タイプ対応、S3 Express One Zone の Inventory 対応なども含まれています。

## 注目アップデート深掘り

### AWS IoT Greengrass v2.17 - 非rootユーザー実行とコンポーネント軽量化

> **AWS IoT Greengrass とは？**
> エッジデバイス側で AWS Lambda や機械学習推論、MQTT ブローカーなどを動かすためのランタイムです。クラウドとのオフライン同期やデバイス間通信をマネージドで提供します。工場やゲートウェイ機器上で常駐させるため、root 権限で動く点がこれまで導入時の論点になりがちでした。

![AWS IoT Greengrass v2.17: 非root実行と lite コンポーネントによる変化](/images/aws-updates-20260421/greengrass-v217.png)

#### 非root実行が解消する導入の壁

従来の Greengrass は root 権限での実行が前提でした。セキュリティポリシーが厳格な業界（金融、医療、政府機関）では常駐プロセスの root 実行が禁止されていることが多く、例外申請や回避策が必要でした。

v2.17 では非rootユーザーでのインストール・実行に対応しました。標準的なセキュリティポリシーの範囲内で導入できます。あわせて nucleus lite によるコンポーネント軽量化が入り、メモリ制約が厳しいエッジデバイスでも現実的に載せられるようになりました。

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

実測結果では 36MB → 4MB の削減（約 1/9）を確認できます。メモリが 512MB 以下の組み込み Linux や IoT ゲートウェイでは、この差がコンポーネント同居可否を分けます。

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

この設定により、秘密鍵は HSM 内に保存され、AWS IoT Core への認証時にも HSM 内で署名処理が実行されます。秘密鍵がメモリやディスクに露出しないため、デバイス盗難時の鍵流出リスクを抑えられます。

> **Note:** PKCS#11対応には、デバイス側にPKCS#11対応のHSMまたはソフトウェアライブラリが必要です。本番環境ではSoftHSMではなく、ハードウェアHSMまたはTPM 2.0の使用を推奨します。

### Amazon EKS - 新しいIAM condition keysによるガバナンス強化

#### 事後検証から事前強制へ

マルチアカウント・マルチテナントで EKS クラスタを運用するとき、組織全体で一貫したセキュリティポリシーを適用するのが悩みどころでした。これまではクラスタ作成後にスクリプトや AWS Config で設定を検証する形が一般的で、事後検証であるぶんポリシー違反のクラスタが一時的に走ってしまう余地がありました。

今回追加された 7 つの IAM condition keys を使うと、CreateCluster / UpdateClusterConfig 実行前に要件をチェックできます。SCP で一度書いておけば、組織内のどのアカウントからも違反クラスタは作れなくなります。

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

エッジデバイスの大規模運用では、セキュリティとリソース効率のトレードオフがつきまといます。v2.17 の非rootユーザー実行対応はそのバランスを少しずつ変えていきます。

セキュリティ監査対応の場面では、ISO 27001 や SOC 2 の取得を目指す組織でシステムアカウントの最小権限原則が問われます。Greengrass を非rootで動かせることで、「なぜこの常駐プロセスに root が必要なのか」への例外申請や補足説明が不要になります。監査応対の作業量がそのぶん減ります。

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

段階的な導入としては、まず AWS CloudTrail で EKS API コールを記録し、既存クラスタの設定パターンを把握することをおすすめします。そのうえで、最も譲れない要件（例: プライベートエンドポイント）から順に SCP に組み込み、影響範囲を確認しながら拡大していく進め方が安全です。

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

> **Amazon EVS とは？**
> VMware Cloud Foundation のスタックを AWS 上にマネージドで載せるサービスです。vSphere / vSAN / NSX をそのまま使いつつ、EC2 上のベアメタルで動かせるため、オンプレの VMware 資産を最小限の書き換えで AWS に持ち込めます。

> **S3 Express One Zone とは？**
> S3 の低遅延（ミリ秒〜サブミリ秒）ストレージクラスで、単一 AZ に集約することで標準 S3 より高速にアクセスできます。高頻度アクセスのキャッシュ的な用途向けで、通常の S3 と API 互換です。

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

今日のアップデートは、セキュリティ、運用、性能それぞれの側面で「既存の運用フローをそのままにしておける」方向の変更が多めです。

セキュリティ面では、Greengrass v2.17 の非root実行、EKS の IAM condition keys、Managed Microsoft AD の LAPS がそれぞれ「セキュリティチームに説明するコスト」を減らします。例外申請や事後監査に頼っていた部分を、常時の設定で担保できるようになります。

運用面では、DocumentDB 5.0 → 8.0 のインプレースアップグレードがわかりやすい改善です。これまでは blue/green で切り替える手順が必要でしたが、エンドポイント据え置きで進められます。EBS の 4 回/日の修正対応、Connect のフローモジュール全タイプ対応も日常作業の摩擦を減らす類です。

性能では、Greengrass nucleus lite の 36MB → 4MB、DocumentDB 8.0 の「クエリレイテンシ最大 7 倍」が目立ちます。前者はデバイス側で他のプロセスと同居できる余地が生まれる話で、後者は読み負荷の高いワークロードでインスタンスサイズを一段階落とせるかどうかに関わります。

総じて、規制対応やコンプライアンス要件の厳しいワークロードで、追加のカスタム対策なしに設定できる選択肢が増えた、と捉えるのが実用的です。