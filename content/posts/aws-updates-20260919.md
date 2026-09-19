---
title: "【AWS】2026/09/19 のアップデートまとめ"
date: 2026-09-19T08:02:12+09:00
draft: false
tags: ["aws", "privatelink", "sns", "sqs", "lambda", "firehose", "resilience-hub", "eks", "organizations", "continuum", "bedrock", "ecs", "graviton", "rtb-fabric", "ses", "s3", "quick"]
categories: ["AWS Updates"]
summary: "2026/09/19 のAWSアップデートまとめ"
---

# 直近の AWS アップデート情報 — 2026年9月版

![](/images/aws-updates-20260919/header.png)

## はじめに

今回は、直近で発表された11件のAWSアップデートを紹介します。注目のアップデートとしては、AWS PrivateLinkの新機能「Tunnel Endpoints」によるネットワークセグメント単位のプライベート接続、Amazon SNSのメッセージペイロード上限が1 MiBに拡大された点、そしてAmazon S3 Express One Zoneの提供リージョン拡大などが挙げられます。本記事では、特に運用インパクトの大きいアップデートを深掘りし、SRE視点での活用ポイントを整理します。

---

## 注目アップデート深掘り

### AWS PrivateLink Tunnel Endpoints — ネットワークセグメント単位のプライベート接続

AWS PrivateLinkに新たに追加された「Tunnel Endpoints」は、VPCエンドポイントを介して別のVPCやアカウント内のネットワークセグメント全体にプライベートかつセキュアにアクセスできる機能です。従来のPrivateLinkでは、外部ベンダーやパートナーに個別リソースを共有する際、リソースごとにResource Configurationを作成する必要がありました。今回のアップデートでは、CIDRレンジを表す単一のResource Configurationを作成し、AWS Resource Access Manager（RAM）経由で共有するだけで、ベンダーはTunnel Endpointを作成し、GENEVEカプセル化を使用してトンネル経由で顧客VPC内のリソースにアクセスできるようになります。

**従来との違い**

これまでは、外部ベンダーなどにリソースを共有する場合、リソースごとに Resource Configuration を作成して1つずつ共有する必要がありました。Tunnel Endpoints では、CIDR レンジを表す Resource Configuration を1つ作成して RAM で共有すれば、ベンダー側はその CIDR レンジ内のリソースにトンネル経由でアクセスできます。

**料金と提供リージョン**

Tunnel Endpoint には時間単位の料金と、処理したデータ量に応じた GB 単位の料金がかかります（詳細は AWS PrivateLink の料金ページ）。提供リージョンは告知に列挙されており、アジアパシフィック（東京）・（大阪）も含まれます。

**運用上の考慮事項**

共有の単位がリソースから CIDR レンジに変わるため、どの範囲を共有するかがそのまま相手に開放される範囲になります。共有する CIDR レンジの粒度は、アクセスを許可したいリソースの範囲に合わせて設計する必要があります。

> **Note:** 詳細な設定手順や制限事項については、[AWS PrivateLink公式ドキュメント](https://docs.aws.amazon.com/vpc/latest/privatelink/)を参照してください。

---

### Amazon SNS メッセージペイロード上限が1 MiBに拡大

Amazon SNSのメッセージペイロード上限が、従来の256 KiBから1 MiB（4倍）に拡大されました。この変更により、IoT、アプリケーション統合、生成AIなど、単一メッセージで大量データを扱うワークロードにおいて、従来必要だったペイロード分割やS3オフロードのロジックを削減できます。新しい `MaximumMessageSize` トピック属性を設定することで、SNS StandardとSNS FIFOの両方で1 MiBまでのメッセージをサポートします。

**従来の実装パターンとの比較**

従来、256 KiBを超えるデータをSNS経由で送信する場合、以下のような実装が一般的でした：

- **ペイロード分割方式**: メッセージを複数の256 KiB以下のチャンクに分割し、受信側で再構成
- **S3オフロード方式**: 大容量データをS3にアップロードし、SNSメッセージにはS3オブジェクトのキーのみを含める

告知では、従来の 256 KiB 制限により publish 前にペイロードをオフロードまたは分割する必要があったことが挙げられています。1 MiB 以下のペイロードであれば、こうした処理なしで直接 publish できます。

**新機能の設定方法**

SNS Standard / SNS FIFO いずれのトピックでも、新しい `MaximumMessageSize` トピック属性を設定することで最大 1 MiB のメッセージを publish できます。`MaximumMessageSize` を 256 KiB より大きく設定したトピックでサポートされるサブスクリプションは Amazon SQS、Amazon Data Firehose、AWS Lambda で、トピックあたりのサブスクリプション数は合計最大100個です。SNS が利用可能な全リージョンで提供されています。

**運用上の注意点**

`MaximumMessageSize` を 256 KiB より大きく設定したトピックでは、サブスクリプションの種類が SQS / Data Firehose / Lambda に限られ、数も合計最大100個です。それ以外のプロトコルのサブスクリプションを持つトピックや、100を超えるサブスクリプションを持つトピックでは、既存トピックの設定を変更する前にサブスクリプション構成を確認してください。また、受信側（Lambda 関数や SQS コンシューマー）が扱うメッセージサイズも大きくなるため、処理側の設定も合わせて見直す必要があります。

---

### Amazon S3 Express One Zone の7リージョン拡大

Amazon S3 Express One Zoneが、シンガポール、サンパウロ、北カリフォルニア、カナダ（中部）、パリ、シドニー、ソウルの7リージョンで新たに提供開始されました。これにより、S3 Express One Zoneは全15リージョンで利用可能になります。

**S3 Express One Zoneとは**

S3 Express One Zone は、単一のアベイラビリティゾーンに特化した高性能ストレージクラスで、最も頻繁にアクセスされるデータやレイテンシに敏感なアプリケーション向けに、一貫した一桁ミリ秒のデータアクセスを提供します。S3 Standard と比べて、データアクセス速度は最大10倍、リクエストコストは最大80%低くなります。

**適用シーン**

告知では、機械学習のトレーニング、インタラクティブ分析、AI 検索エンジンのキーバリューキャッシュといったワークロードが例として挙げられています。

**トレードオフの考慮**

S3 Express One Zone は単一 AZ のストレージクラスのため、データは1つの AZ に配置されます。複数 AZ への冗長化が必要なデータには S3 Standard など他のストレージクラスを併用する設計になります。

---

## SRE視点での活用ポイント

**AWS PrivateLink Tunnel Endpoints** は、外部ベンダーに自社 VPC 内の複数リソースへのアクセスを提供している場合に、リソースごとの Resource Configuration 作成・共有の手間を減らせます。一方で、共有範囲が CIDR レンジ単位になるため、共有前にそのレンジに含まれるリソースを棚卸ししておくことが重要です。

**Amazon SNS の 1 MiB 対応** は、ペイロードを S3 にオフロードしたり分割したりしていたパイプラインを見直すきっかけになります。ただし 256 KiB を超える設定にしたトピックはサブスクリプションの種類と数に制約があるため、既存トピックを変更するか、大容量用の新しいトピックを用意するかを判断する必要があります。

**S3 Express One Zone のリージョン拡大** により、シンガポール、シドニー、ソウルなどでも同ストレージクラスを選べるようになりました。単一 AZ である点を踏まえ、どのデータを配置するかはアクセス頻度・レイテンシ要件・冗長化要件から判断してください。

**Amazon Bedrock AgentCore の新 Runtime** は、ランタイムの作成・更新時に `platformVersion` を `V2` に設定して利用します。告知ではテスト結果として、200 MB〜2 GB のコンテナイメージで P75 コールドスタートが 1.9〜2.0 秒（V1 は 5.4〜30 秒）と示されています。us-east-1、us-east-2、us-west-2、eu-west-1、ap-northeast-1 で利用可能です。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|----------|------|
| 1 | [AWS PrivateLink announces Tunnel Endpoints](https://aws.amazon.com/about-aws/whats-new/2026/9/privatelink-tunnel-endpoint/) | VPCエンドポイント経由でネットワークセグメント全体にプライベートアクセス可能に。CIDRレンジ単位の共有でベンダー統合を簡素化 |
| 2 | [Amazon SNS now supports message payloads up to 1 MiB](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-sns-1mib-support/) | メッセージペイロード上限が256 KiBから1 MiB（4倍）に拡大。`MaximumMessageSize` 属性で設定可能 |
| 3 | [AWS Resilience Hub adds three new capabilities](https://aws.amazon.com/about-aws/whats-new/2026/09/resilience-hub-eks-dependency-policy/) | EKSラベルサポート、AI活用の依存関係インサイト、AWS Organizations経由のポリシー共有機能を追加 |
| 4 | [AWS Continuum now supports credential testing and accessible domain suggestions](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-security-agent/) | ペネトレーションテスト実行前に認証情報をテストし、アクセス可能なドメインを自動提案 |
| 5 | [Kimi K3 by Moonshot AI is now generally available on Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2026/09/moonshot-ai-kimi-k3-on-amazon-bedrock/) | 2.8兆パラメータのオープンウェイトモデル。100万トークンコンテキスト、プロンプトキャッシング対応 |
| 6 | [Amazon ECS Express Mode now supports AWS Graviton (ARM64) workloads](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ecs-express-mode-arm-architecture/) | ARM64 を指定して Graviton 上で実行可能に。x86 ベースのインスタンスと比べ最大40%優れた価格性能 |
| 7 | [AWS RTB Fabric now supports configurable Availability Zone affinity](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-rtb-fabric-configurable-availability-zone-affinity/) | 応答ゲートウェイのAZアフィニティ設定が可能に。AdTech企業のインフラ効率化を支援 |
| 8 | [Amazon SES now supports tenant-level deliverability insights](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ses-vdm-tenants/) | VDMにテナント単位の配信可能性インサイト機能を追加。`BatchGetMetricData` APIで `TENANT_NAME` ディメンション対応 |
| 9 | [The new AgentCore Runtime is now available in Amazon Bedrock AgentCore](https://aws.amazon.com/about-aws/whats-new/2026/09/new-agentcore-runtime-generally-available/) | エラスティックメモリ管理と一貫したコールドスタート時間（P75: 1.9〜2.0秒）を実現したV2ランタイム |
| 10 | [Amazon S3 Express One Zone is now available in 7 additional AWS Regions](https://aws.amazon.com/about-aws/whats-new/2026/09/s3-express-one-zone-7-regions/) | シンガポール、サンパウロ、北カリフォルニア、カナダ中部、パリ、シドニー、ソウルで提供開始。全15リージョンに拡大 |
| 11 | [Amazon Quick now generates individual sheets and builds analyses from an image](https://aws.amazon.com/about-aws/whats-new/2026/09/generate-sheet-and-generate-analysis-from-an-image/) | 自然言語でシート生成、ダッシュボード画像から編集可能な分析を再作成する機能を追加 |

---

## まとめ

今回の11件のうち、深掘りした3件は PrivateLink Tunnel Endpoints（CIDR レンジ単位でのプライベートアクセス共有）、SNS のメッセージペイロード上限 1 MiB 化、S3 Express One Zone の7リージョン追加（計15リージョン）です。

このほか、Amazon Bedrock での Kimi K3 の一般提供、ECS Express Mode の Graviton（ARM64）対応、Amazon Bedrock AgentCore の新 Runtime（`platformVersion: V2`）、SES VDM のテナント単位インサイト、Amazon Quick の Generate Sheet／画像からの分析生成なども含まれています。

Tunnel Endpoints は共有範囲の設計、SNS 1 MiB 対応はサブスクリプション構成の確認が、導入前の確認ポイントです。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)