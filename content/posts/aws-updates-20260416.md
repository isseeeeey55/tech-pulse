---
title: "【AWS】2026/04/16 のアップデートまとめ"
date: 2026-04-16T08:01:56+09:00
draft: true
tags: ["aws", "payment-cryptography", "transit-gateway", "cloud-wan", "quicksight", "ec2"]
categories: ["AWS Updates"]
summary: "2026/04/16 のAWSアップデートまとめ"
---

# AWS 2026/04/16 アップデート情報

## はじめに

2026年4月16日、AWSから4件のアップデートが発表されました。本日の注目ポイントは、マルチクラウド接続を実現する **AWS Interconnect - multicloud** の一般提供開始と、決済処理向けマネージドサービス **AWS Payment Cryptography** のサンパウロリージョン展開です。加えて、QuickSight の UX 改善機能と GovCloud リージョンでの P6-B300 インスタンス展開も発表されています。特に AWS Interconnect - multicloud は、複数クラウドプロバイダー間のプライベート接続を簡素化する新サービスとして、マルチクラウド戦略を採用する企業にとって重要な選択肢となるでしょう。

## 注目アップデート深掘り

### AWS Interconnect - multicloud の一般提供開始

AWS Interconnect - multicloud は、複数のクラウドプロバイダー間でシンプルかつ高速な専用プライベート接続を提供する新しいサービスです。従来、マルチクラウド環境では、各クラウドプロバイダーの Direct Connect やそれに相当するサービスを個別に設定し、さらにそれらをデータセンターやコロケーション施設を介して接続する必要がありました。このアプローチは複雑で、構築に数週間から数ヶ月を要し、運用管理も煩雑でした。

**なぜこのアップデートが重要なのか**

多くの企業がマルチクラウド戦略を採用する背景には、ベンダーロックインの回避、ワークロード最適化、災害復旧、規制対応などの理由があります。しかし、クラウド間の接続が複雑であることが、マルチクラウド導入の大きな障壁となっていました。AWS Interconnect - multicloud は、この課題を解決し、AWS と他のクラウドプロバイダー（Google Cloud、Microsoft Azure、Oracle Cloud Infrastructure）間の接続を大幅に簡素化します。

**従来の方法との比較**

| 項目 | 従来の方法 | AWS Interconnect - multicloud |
|------|-----------|-------------------------------|
| 構築期間 | 数週間〜数ヶ月 | 数日以内 |
| 接続形態 | 各クラウドの専用線を個別設定 | 単一のマネージドサービス |
| 運用管理 | 複数の契約・SLA管理が必要 | AWS 単一の管理画面 |
| 料金体系 | 複雑（各プロバイダーごと） | シンプルな単一料金 |
| レジリエンス | 自前で冗長化設計が必要 | 組み込みの高可用性 |

**実装例：AWS Transit Gateway との連携**

AWS Interconnect - multicloud は AWS Transit Gateway や AWS Cloud WAN と組み合わせることで、複数の VPC やリージョンへのスケーリングが容易になります。以下は、AWS CLI を使用して Transit Gateway Attachment を作成する例です。

```bash
$ aws ec2 create-transit-gateway-attachment \
    --transit-gateway-id tgw-1234567890abcdef0 \
    --vpn-connection-id vpn-multicloud-1234567890 \
    --tag-specifications 'ResourceType=transit-gateway-attachment,Tags=[{Key=Name,Value=multicloud-google-connection}]'
```

Terraform を使用した場合の構成例は以下の通りです。

```hcl
resource "aws_ec2_transit_gateway" "main" {
  description = "Transit Gateway for multicloud connectivity"
  
  tags = {
    Name = "multicloud-tgw"
  }
}

resource "aws_ec2_transit_gateway_vpc_attachment" "vpc_attachment" {
  subnet_ids         = var.subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.main.id
  vpc_id            = var.vpc_id

  tags = {
    Name = "multicloud-vpc-attachment"
  }
}

# AWS Interconnect - multicloud 接続の設定
# (実際のリソースタイプは GA 時のドキュメントを参照)
```

**料金の最適化**

2026年5月から、リージョンあたり 500Mbps のローカル接続が無料で提供されます。これにより、小〜中規模のデータ同期や管理トラフィックを無料枠内で処理できます。帯域幅が必要な場合は、1Gbps、10Gbps、100Gbps などのオプションが用意されており、利用料金は選択した帯域幅と地理的スコープに応じて決まります。

> **Note:** Google Cloud が最初のパートナーとして利用可能で、Microsoft Azure と Oracle Cloud Infrastructure は 2026年後半に対応予定です。

### Amazon QuickSight のシートツールチップ機能

Amazon QuickSight に追加されたシートツールチップ機能は、ダッシュボードの UX を大幅に向上させる新機能です。従来のツールチップは基本的なテキスト情報の表示に限定されていましたが、シートツールチップでは、専用のシートを作成し、そこに複数のビジュアライゼーション、テキストボックス、画像を配置できます。

**なぜこの機能が重要なのか**

BI ツールにおける情報探索（Data Exploration）では、サマリービューから詳細データへのドリルダウンが頻繁に発生します。従来は別のダッシュボードやシートに遷移する必要があり、文脈（フィルター状態など）が失われたり、操作が煩雑になったりする課題がありました。シートツールチップは、ホバーアクションだけで詳細情報を表示し、元のビジュアルのフィルターを自動継承するため、分析フローが中断されません。

**従来のツールチップとの比較**

| 機能 | 基本ツールチップ | 詳細ツールチップ | シートツールチップ |
|------|-----------------|-----------------|-------------------|
| カスタムレイアウト | ❌ | ❌ | ✅ |
| 複数ビジュアル | ❌ | ❌ | ✅ |
| 画像・テキスト | ❌ | ❌ | ✅ |
| フィルター継承 | 部分的 | 部分的 | 完全自動 |
| データポイント固有フィルター | ❌ | ❌ | ✅ |

**実装手順**

以下は、QuickSight コンソールでシートツールチップを作成する手順です。

1. **ツールチップシートの作成**
   - ダッシュボード編集モードで「新しいシートを追加」を選択
   - シート名を「Tooltip_SalesDetail」のように命名（識別しやすい名前を推奨）
   - シートタイプとして「Tooltip Sheet」を選択

2. **コンテンツの配置**
   - ツールチップシートに表示したいビジュアルを追加（例：折れ線グラフ、KPI カード、テーブル）
   - テキストボックスで説明文や補足情報を追加
   - 必要に応じて画像（ロゴ、アイコンなど）を配置

3. **ツールチップの関連付け**
   - 元のダッシュボードに戻り、ツールチップを適用したいビジュアルを選択
   - ビジュアルの設定メニューから「Tooltip」セクションを開く
   - 「Tooltip type」で「Sheet tooltip」を選択
   - 作成したツールチップシートを選択

**Python SDK を使用した自動化例**

QuickSight API を使用すると、ツールチップの設定をプログラムで管理できます。

```python
import boto3

quicksight = boto3.client('quicksight', region_name='us-east-1')

# ダッシュボードの更新（ツールチップの設定を含む）
response = quicksight.update_dashboard(
    AwsAccountId='123456789012',
    DashboardId='sales-dashboard',
    Name='Sales Dashboard',
    SourceEntity={
        'SourceTemplate': {
            'DataSetReferences': [...],
            'Arn': 'arn:aws:quicksight:...'
        }
    },
    # ツールチップシートの設定
    Definition={
        'Sheets': [
            {
                'SheetId': 'main-sheet',
                'Visuals': [
                    {
                        'VisualId': 'sales-bar-chart',
                        'ChartConfiguration': {
                            'Tooltip': {
                                'TooltipVisibility': 'VISIBLE',
                                'SelectedTooltipType': 'DETAILED',
                                'FieldBasedTooltip': {
                                    'TooltipTitleType': 'PRIMARY_VALUE',
                                    'TooltipFields': [
                                        {
                                            'FieldId': 'sales-amount',
                                            'Label': 'Sales',
                                            'Visibility': 'VISIBLE'
                                        }
                                    ]
                                }
                            }
                        }
                    }
                ]
            },
            {
                'SheetId': 'tooltip-sheet-sales-detail',
                'Name': 'Sales Detail Tooltip',
                'SheetType': 'TOOLTIP',
                'Visuals': [...]
            }
        ]
    }
)

print(f"Dashboard updated: {response['DashboardId']}")
```

**ユースケース例：営業ダッシュボード**

営業マネージャーが地域別の売上を示す棒グラフを見ているとき、特定の地域（例：「関東」）にホバーすると、以下の情報を含むツールチップシートが表示されます。

- 月次売上トレンドの折れ線グラフ（過去12ヶ月）
- 前年度比成長率の KPI カード（+15.3% など）
- トップ3商品カテゴリーの内訳テーブル
- 地域名と担当者名のテキスト情報

このとき、元のダッシュボードに設定されている期間フィルター（例：2026年1-3月）が自動的に継承され、さらに「関東」という地域フィルターが追加適用されます。

> **Note:** シートツールチップはインタラクティブシートでのみ利用可能で、テーブルとピボットテーブルもサポートされています。

## SRE視点での活用ポイント

### AWS Interconnect - multicloud の運用活用

マルチクラウド環境を運用する SRE チームにとって、AWS Interconnect - multicloud は可観測性とインシデント対応の改善に貢献します。例えば、AWS で CloudWatch を使用し、Google Cloud で Cloud Monitoring を使用している場合、これまではメトリクスやログをパブリックインターネット経由で集約する必要がありました。専用接続を使うことで、メトリクスの転送遅延が削減され、リアルタイムに近い監視が可能になります。

Terraform でマルチクラウドインフラを管理している場合、AWS Interconnect - multicloud のリソース定義を Terraform コードに組み込むことで、接続設定も Infrastructure as Code として管理できます。これにより、災害復旧時のフェイルオーバー手順や、新リージョン展開時のネットワーク構築が自動化され、運用負荷が軽減されます。

導入時の判断基準としては、クラウド間のデータ転送量が月間 100GB を超える場合、またはレイテンシが 50ms 以下であることが要求される場合に検討価値があります。ただし、500Mbps の無料枠があるため、まずはスモールスタートで試験運用し、トラフィック増加に応じて帯域幅を拡張するアプローチが現実的です。

### QuickSight シートツールチップの監視ダッシュボード活用

SRE が運用する監視ダッシュボードでは、アラート数や応答時間などのメトリクスを一目で把握できることが重要です。シートツールチップを活用すると、例えば CPU 使用率のグラフにホバーしたときに、対象インスタンスのメモリ使用率、ネットワークトラフィック、ディスク I/O などの関連メトリクスを一度に表示できます。これにより、障害発生時のトリアージが迅速化され、根本原因の特定までの時間が短縮されます。

また、オンコール担当者がモバイルデバイスでダッシュボードを確認する際にも、シートツールチップは有効です。画面サイズが限られる環境でも、必要な情報をホバー（モバイルではタップ）で即座に確認できるため、深夜のインシデント対応時のストレスが軽減されます。

導入時の注意点として、ツールチップシートに過剰な情報を詰め込むと、かえって認知負荷が高まります。表示する情報は「次のアクションを決定するために必要な最小限の情報」に絞り、詳細はドリルダウンリンクで別ダッシュボードに誘導する設計が推奨されます。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [AWS Payment Cryptography now available in South America (São Paulo)](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-payment-cryptography-south/) | 決済専用の暗号化とキー管理を行う完全マネージドサービスがサンパウロリージョンで利用可能に。PCI PIN および PCI P2PE 準拠で、専用 HSM 不要。 |
| 2 | [AWS announces general availability of AWS Interconnect - multicloud](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-announces-ga-AWS-interconnect-multicloud/) | 複数クラウドプロバイダー間のプライベート接続を提供する新サービス。Google Cloud が対応済み、Azure と OCI は2026年後半対応予定。 |
| 3 | [Amazon QuickSight Introduces Sheet Tooltips for Rich, Contextual Data Exploration](https://aws.amazon.com/about-aws/whats-new/2026/04/quick-sheet-tooltips/) | ダッシュボードのデータポイントにホバー時、リッチなビジュアライゼーションを含む詳細情報を表示する新機能。フィルター自動継承でシームレスな分析体験を実現。 |
| 4 | [Amazon EC2 P6-B300 instances are now available in the AWS GovCloud (US-East) Region](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-p6-b300-govcloud-us-east/) | NVIDIA Blackwell GPU を搭載した P6-B300 インスタンスが GovCloud (US-East) リージョンで利用可能に。大規模 LLM トレーニングや政府機関向け AI 研究に対応。 |

## まとめ

本日のアップデートは、マルチクラウド戦略の実現性向上（AWS Interconnect - multicloud）、決済処理の地理的拡張（AWS Payment Cryptography）、BI ツールの UX 改善（QuickSight シートツールチップ）、そして GovCloud での AI ワークロード強化（P6-B300 インスタンス）と、多様な領域にわたっています。

特に AWS Interconnect - multicloud は、これまで「複雑すぎる」という理由でマルチクラウドを諦めていた企業にとって、新たな選択肢を提供します。Google Cloud との接続が即座に可能であり、Azure や OCI との接続も今後数ヶ月以内に実現する見込みです。マルチクラウド環境の運用が標準化されることで、クラウドアーキテクチャの選択肢がさらに広がるでしょう。

QuickSight のシートツールチップは小さな機能改善に見えますが、ダッシュボードの使い勝手を大きく向上させます。特に SRE や DevOps チームが日常的に使う監視ダッシュボードにおいて、情報探索の効率化は生産性向上に直結します。今後の QuickSight の進化にも期待が高まります。