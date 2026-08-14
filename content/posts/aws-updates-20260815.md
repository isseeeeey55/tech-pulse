---
title: "【AWS】2026/08/15 のアップデートまとめ"
date: 2026-08-15T08:01:45+09:00
draft: true
tags: ["aws", "rds", "oracle", "ses", "redshift", "billing", "cost-management"]
categories: ["AWS Updates"]
summary: "2026/08/15 のAWSアップデートまとめ"
---

# 今回は、直近で発表された4件のAWSアップデートを紹介します

今回取り上げるアップデートは、Amazon RDSのOracle APEX対応、Amazon SESのモバイルディープリンキング強化、Amazon RedshiftのGovCloudでの新インスタンスサイズ提供、そしてAWS Billing and Cost ManagementのManaged Dashboards導入の4件です。中でも、Amazon SESのクリック追跡機能強化は、モバイルアプリ開発者にとってエンゲージメント測定とユーザー体験の両立という長年の課題を解決する重要な機能です。また、AWS Billing and Cost ManagementのManaged Dashboardsは、FinOps実践において即座にコスト可視化を実現できる、セットアップ不要の強力なツールとして注目されます。

## 注目アップデート深掘り

### Amazon SES クリック追跡がモバイルアプリディープリンキングに対応

Amazon SESのクリック追跡機能に、モバイルアプリのディープリンキングを両立させる新機能が追加されました。従来、SESのクリック追跡を有効にすると、メール内のリンクURLがSESの追跡用ドメインに書き換えられてしまい、iOSのUniversal LinksやAndroidのApp Linksが機能しなくなるというトレードオフがありました。エンゲージメント測定を優先するとアプリへのシームレスな遷移を犠牲にし、逆にディープリンキングを優先するとクリック数の計測ができなくなるという、モバイルマーケティング担当者にとって悩ましい選択を迫られていたのです。

今回の機能強化により、新しい `ses:custom-path` HTML属性を `<a>` タグに追加することで、この課題が解決されます。具体的には、以下のような形で実装できます：

```html
<a href="https://your-tracking-domain.com/products/12345" 
   ses:custom-path="/products/12345">
   商品を見る
</a>
```

この属性を指定すると、SESはクリック追跡用のリダイレクトURLを生成する際に、パスセグメント（`/products/12345`）を保持します。これにより、iOSやAndroidのOSは、リダイレクト先URLのドメインとパスを認識し、適切なアプリに遷移させることができます。

この機能を利用するには、カスタムリダイレクトドメインに以下のいずれかを配置する必要があります：

- **iOS向け**: Apple App Site Association (AASA) ファイルを `https://your-tracking-domain.com/.well-known/apple-app-site-association` に配置
- **Android向け**: Digital Asset Links JSONファイルを `https://your-tracking-domain.com/.well-known/assetlinks.json` に配置

これらのファイルは、特定のドメインとアプリの関連性をOSに証明するための検証ファイルです。カスタムリダイレクトドメインにこれらを配置することで、SESの追跡用URLからでもアプリへの直接遷移が可能になります。

従来の方法では、ディープリンクを実現するためにはクリック追跡を無効にする必要がありました。これにより、どのリンクがクリックされたか、どのキャンペーンが効果的だったかというデータが取得できず、マーケティング施策の改善サイクルが回せませんでした。新機能により、Eコマースアプリであれば「メールから商品ページへの直接遷移」と「どの商品へのリンクがクリックされたか」の両方を同時に把握できるようになります。ニュースアプリやSNSアプリでも、記事やチャネルへの直接遷移とエンゲージメント分析を両立できるため、ユーザー体験を損なわずにデータドリブンなマーケティングが実現できます。

> **Note:** カスタムパスにはURLエンコーディングが必要な文字が含まれる場合があります。また、パスの長さにも実用上の制限があるため、過度に長いパスは避けることが推奨されます。

### AWS Billing and Cost Management Managed Dashboards で即座にコスト可視化

AWS Billing and Cost Management（BCM）に追加されたManaged Dashboardsは、FinOps実践におけるコスト可視化の初期ハードルを大きく下げる機能です。従来、AWSのコストを体系的に分析するには、Cost Explorer APIやCURデータを使ってカスタムダッシュボードを構築するか、QuickSightなどのBIツールで可視化環境を整える必要がありました。これらは柔軟性が高い反面、初期構築に時間とコストがかかり、「とりあえずコスト状況を把握したい」というニーズに対しては過剰でした。

Managed Dashboardsは、AWSが事前に設計した5つのダッシュボードを提供します。これらはセットアップ不要で、アカウントデータが自動的に入力されるため、BCMコンソールにアクセスした瞬間から利用できます。提供されるダッシュボードには以下が含まれます：

- **コスト概要・トレンド**: 12ヶ月間のコスト推移、月別・サービス別の内訳、予測
- **Compute・Database**: EC2、RDS、Lambdaなどのコンピューティングリソースの詳細コスト分析
- **Reservations**: Reserved Instancesの利用状況、カバレッジ、未活用状況
- **Savings Plans**: Savings Plansのコミットメント消化率、コスト削減効果

これらのダッシュボードは読み取り専用ですが、複製してカスタマイズすることができます。例えば、特定のタグでフィルタリングしたり、独自のウィジェットを追加したり、レイアウトを変更したりすることが可能です。また、PDFやCSV形式でエクスポートできるため、定期的な経営報告や部門別コストレビューにそのまま活用できます。

FinOps導入の初期段階では、「現状のコストがどうなっているか」を迅速に把握することが最優先です。Managed Dashboardsを使えば、構築期間ゼロでコスト分析を開始でき、Reserved InstancesやSavings Plansの購入効果測定、未利用リソースの検出といった実務的な分析がすぐに行えます。複数アカウント・複数リージョンで運用している組織では、一元的なコスト監視基盤として標準化することで、全社的なコスト最適化文化の醸成にも寄与します。

すべてのダッシュボードはAWSによって管理・更新されるため、新しいAWSサービスや料金体系の変更にも自動的に対応します。これにより、ダッシュボードのメンテナンスコストが削減され、運用チームは分析とアクションに集中できます。

> **Note:** Managed Dashboardsは読み取り専用ですが、複製することで自由にカスタマイズできます。組織の分析ニーズに応じて、ベースラインとして活用しながら独自の分析軸を追加していくことが推奨されます。

## SRE視点での活用ポイント

Amazon SESの新しいディープリンキング機能は、モバイルアプリを運用するSREチームにとって、ユーザー体験の向上とエンゲージメントデータの取得という二つの目標を同時に達成できる手段となります。例えば、障害復旧の通知やメンテナンス案内をメールで送信する際、アプリのステータスページに直接遷移させながら、どれだけのユーザーが通知を確認したかを追跡できます。CloudWatch アラームと連携して、障害検知時に自動的に通知メールを送信し、そのエンゲージメント率をメトリクスとして収集することで、通知の到達性や有効性を継続的に改善できます。導入時には、カスタムリダイレクトドメインのDNS設定とSSL証明書の管理、AASAファイルやDigital Asset Linksファイルの配置とバージョン管理を、Infrastructure as Code（Terraform等）で管理することが望ましいでしょう。また、リダイレクトドメインの可用性監視も忘れずに実施する必要があります。

AWS Billing and Cost Management Managed Dashboardsは、SREが担うコスト最適化の責任を果たすための即効性のあるツールです。Terraformで管理しているインフラがあれば、定期的にManaged Dashboardsでコストトレンドを確認し、予期しないコスト増加を早期に検出できます。例えば、Compute・DatabaseダッシュボードでEC2やRDSのコストが急増していることを検知したら、CloudWatch Logsやメトリクスと突き合わせて原因を特定し、オートスケーリング設定の見直しやインスタンスサイズの最適化を検討するというフローが構築できます。Reserved Instancesダッシュボードでカバレッジが低い場合は、長期的なキャパシティプランニングを見直し、Savings Plansの購入を検討する判断材料になります。導入リスクは非常に低く、既存のコスト管理プロセスに追加するだけで済みます。ただし、ダッシュボードはあくまで可視化ツールであり、コスト削減施策の実行は別途必要です。定期的なレビュー会議でダッシュボードを共有し、アクションアイテムを明確化するプロセスを整備することが重要です。

## 全アップデート一覧

| タイトル | 概要 |
|---------|------|
| [Amazon RDS for Oracle が Oracle APEX 26.1 に対応](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-rds-oracle-apex-26-1/) | RDS for Oracle で低コード開発プラットフォーム APEX 26.1 が利用可能に。モダンUIを備えたエンタープライズアプリケーションを迅速に構築できます。全リージョンで提供開始。 |
| [Amazon SES クリック追跡がカスタムURLパスに対応](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-ses-supports-customurl-deeplinking/) | `ses:custom-path` 属性により、モバイルアプリのディープリンキングとクリック追跡を両立。iOS Universal Links と Android App Links に対応しながらエンゲージメント測定が可能に。 |
| [Amazon Redshift が GovCloud リージョンで rg.large/rg.12xlarge を提供開始](https://aws.amazon.com/about-aws/whats-new/2026/08/amazon-redshift-adds-rg-large-12xlarge-aws-govcloud-regions/) | AWS GovCloud (US) で RG インスタンスの新サイズを提供。RA3 比で最大2.4倍高速、vCPUあたりコスト30%削減。ベクトル化クエリエンジンで Iceberg/Parquet を直接処理。 |
| [AWS Billing and Cost Management に Managed Dashboards 追加](https://aws.amazon.com/about-aws/whats-new/2026/08/aws-billing-and-cost-management-managed-dashboards/) | セットアップ不要の読み取り専用ダッシュボードを5種類提供。コスト概要、Compute・Database、Reservations、Savings Plans などを12ヶ月分自動可視化。複製してカスタマイズ可能。 |

## まとめ

今回取り上げたアップデートは、開発生産性の向上（Oracle APEX 26.1）、モバイルマーケティングの効率化（SES ディープリンキング）、政府機関向けデータ分析基盤の強化（Redshift RG インスタンス）、そしてFinOpsの初動加速（Managed Dashboards）と、多様な領域をカバーしています。特にManaged Dashboardsは、コスト最適化という全ての組織に共通する課題に対して、即効性のある解決策を提供しています。SESのディープリンキング対応は、モバイルファーストの時代において、ユーザー体験とデータ分析の両立を可能にする重要な進化です。いずれのアップデートも、運用負荷の軽減やコスト効率の改善といったSRE視点で見ても有用な機能であり、既存システムへの導入を積極的に検討する価値があります。各機能の詳細は公式ドキュメントで確認し、自組織の要件に合わせた活用方法を検討してみてください。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)