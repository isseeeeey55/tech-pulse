---
title: "【AWS】2026/04/14 のアップデートまとめ"
date: 2026-04-14T08:01:39+09:00
draft: false
tags: ["aws", "opensearch", "fsx", "aurora-dsql", "ec2", "govcloud", "elastic-disaster-recovery", "iot", "ipv6"]
categories: ["AWS Updates"]
summary: "OpenSearch Serverless の Derived Source、EC2 R8i/M8i の GovCloud (US-West) 展開、Aurora DSQL PHP コネクタ、Elastic Disaster Recovery の IPv6 対応など 7 件のアップデートを紹介します。"
---

![](/images/aws-updates-20260414/header.png)

## はじめに

2026年4月14日のAWSアップデートは6件（EC2 R8i と M8i の GovCloud 展開はペアでカウント）です。目玉は OpenSearch Serverless に追加された Derived Source、EC2 R8i/M8i の GovCloud (US-West) 展開、Aurora DSQL の PHP コネクタの3つ。残りは FSx バックアップの Opt-in リージョン間コピー、Elastic Disaster Recovery の IPv6 対応、AWS IoT のリージョン拡張です。

## 注目アップデート深掘り

### Amazon OpenSearch Serverless — Derived Source でインデックスストレージを削減

![OpenSearch Serverless Derived Source の仕組み](/images/aws-updates-20260414/derived-source-compare.png)

OpenSearch Serverless に **Derived Source** が追加されました。従来、OpenSearch は各ドキュメントを検索インデックスとは別に `_source` フィールドとして丸ごと保存しており、長期のログ保持や高カーディナリティのイベントデータではここがストレージ使用量のかなりの部分を占めていました。

> **Derived Source とは？**
> ドキュメントの別コピーを保持する代わりに、**インデックスに既に格納されている値から `_source` を動的に再構築する**方式です。公式は「ストレージ消費を大幅に削減」と表現していますが、削減率は格納するフィールド構成に依存するため具体数値は示されていません。

有効化はインデックスマッピングの作成・更新時にインデックス単位で行います。AWS CLI でコレクションを作るところまでは従来通りです。

```bash
$ aws opensearchserverless create-collection \
    --name "logs-derived" \
    --type TIMESERIES \
    --description "Time-series logs with derived source"
```

インデックステンプレート側で Derived Source を有効化します（設定例、実際のキー名は最新の公式ドキュメントを確認してください）。

```json
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "index": {
        "derived_source": {
          "enabled": true
        }
      }
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "message":    { "type": "text" },
        "level":      { "type": "keyword" }
      }
    }
  }
}
```

注意点は「`_source` 全体を返すクエリ」のレスポンスに若干のオーバーヘッドが乗ることです。集計クエリや特定フィールドだけ返す検索が主であればほぼ影響しません。一方で、取得したドキュメント本体を再インジェストしたりリプレイしたりする用途が多い場合は、導入前に実環境で読み取りレイテンシを測定しておくのが無難です。

提供リージョン: OpenSearch Serverless がサポートされている全リージョン。

### EC2 R8i / R8i-flex / M8i / M8i-flex — GovCloud (US-West) に展開

![R8i/M8i の性能プロファイル](/images/aws-updates-20260414/r8i-m8i-perf.png)

AWS GovCloud (US-West) リージョンで R8i / R8i-flex / M8i / M8i-flex インスタンスが利用できるようになりました。R8i はメモリ最適化、M8i は汎用用途で、両方とも AWS 向けにカスタマイズされた Intel Xeon 6 プロセッサを搭載しています。

公式が示す主な数値は次の通りです。

| 指標 | 向上率 | 基準 |
|---|---|---|
| 総合性能（R8i） | **20% higher** | R7i 比 |
| 価格性能 | **up to 15% better** | 前世代比 |
| メモリ帯域 | **2.5x** | 前世代比 |
| PostgreSQL | up to 30% faster | 前世代比 |
| NGINX | up to 60% faster | 前世代比 |
| 深層学習推奨モデル | up to 40% faster | 前世代比 |

R8i は SAP 認証を取得しており、**142,100 aSAPS** を達成しています。SAP HANA やその他の SAP ワークロードを GovCloud 上で運用しているチームには直接効いてきます。

R8i-flex は「Flex 系列としては初のメモリ最適化版」で、CPU を常時フル利用しないタイプのメモリ集約ワークロード向けです。ラージから 16xlarge までのサイズがあり、M6i/R7i-flex と同じく CPU クレジットでバースト可能です。コンスタントに CPU を回すワークロードなら無印の R8i、CPU 使用率が平均的に低めならまず R8i-flex を試す、という切り分けになります。

既存の R7i / M7i で動いているワークロードを乗せ替える際は、CloudWatch の既存メトリクス・アラーム閾値を R8i の性能プロファイルに合わせて見直してください。たとえば「CPU 80% で警告」を流用すると、処理性能が上がった分、同じ負荷では CPU 使用率が下がって鳴らなくなる、といったズレが起きます。

### Aurora DSQL — PHP コネクタの提供開始

Aurora DSQL に PHP 向けのコネクタが追加されました。PDO_PGSQL 互換で、`awslabs/aurora-dsql-connectors` リポジトリで提供されています。

> **Aurora DSQL とは？**
> AWS が提供するサーバーレスの分散 SQL データベースで、PostgreSQL 互換のプロトコルで接続できます。マルチリージョン active-active とリージョン内のスケールアウトを組み合わせた設計で、Aurora と DynamoDB の中間的なポジションに位置します。

このコネクタのポイントは **IAM トークンを接続ごとに自動生成する**点です。Aurora DSQL はパスワード認証ではなく IAM ベースの短期トークンで接続する設計で、従来の PHP アプリから使うには自前でトークン発行と更新ロジックを書く必要がありました。このコネクタは次のような処理を自動で肩代わりしてくれます。

- 接続ごとの IAM 認証トークン自動生成
- SSL 設定
- 接続プーリング
- Aurora DSQL 特有の OCC（Optimistic Concurrency Control）リトライ — exponential backoff 付き
- カスタム IAM 認証プロバイダや AWS プロファイルの指定

既存の PDO ベースの PHP アプリケーションは接続設定部分だけ差し替えれば Aurora DSQL に乗せられます。DSQL 自体のリージョン展開状況と合わせて、マルチリージョン DR 構成の選択肢が広がります。

## SRE視点での活用ポイント

**OpenSearch Serverless の Derived Source** は、長期保持ログや高カーディナリティなイベントデータで効きます。まずステージング環境で、同じデータセットを通常インデックスと Derived Source インデックスに並行でインデックスして、ストレージ使用量と `_source` 取得クエリのレイテンシを実測するのがおすすめです。集計や特定フィールドの検索が主であれば、そのまま本番に適用できるはずです。

**R8i / M8i の GovCloud 展開**は、規制業界で前世代インスタンスのままだった SAP / PostgreSQL / 推論ワークロードの乗せ替え候補になります。性能が上がった分、同じ台数で捌ける量が増えるので、Auto Scaling のスケールアウト頻度やピーク時台数の見直しもセットで行うとコスト面でも得が出ます。モニタリング側は、既存のアラーム閾値（特に CPU ベース）を機械的に流用しないこと。

**Aurora DSQL PHP コネクタ**は、いまから PHP で DSQL を触るチームにはほぼ必須です。IAM トークンを自前で扱う面倒が消えるので、接続エラーや認証エラーのトラブルシュートが楽になります。既存の Aurora PostgreSQL から DSQL への検証移行を検討しているなら、このタイミングで PoC を組むのが良いでしょう。

**Elastic Disaster Recovery の IPv6 対応**は、IPv6 専用 VPC やデュアルスタック構成で運用している環境で、DR レプリケーション経路を IPv4 に落とさずに組めるようになった、という話です。社内セキュリティポリシーで IPv4 Egress を絞っている環境では素直に効きます。

## 全アップデート一覧

> **AWS Elastic Disaster Recovery とは？**
> 略称 DRS。オンプレや別クラウドのサーバを、対象インフラ上で継続的にブロックレベルで AWS にレプリケートしておき、障害発生時に EC2 インスタンスとして数分で起動する災害復旧サービスです。

| サービス | タイトル | 概要 |
|---------|---------|------|
| [Amazon OpenSearch Serverless](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-opensearch-serverless-supports-derived-source/) | Derived Source 対応 | `_source` をインデックス値から動的再構築し、ストレージ消費を削減 |
| [Amazon FSx](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-fsx-copying-backups-opt-in-regions/) | Opt-in リージョン間バックアップコピー | ファイルシステムバックアップを Opt-in リージョンとの間でコピー可能に |
| [Aurora DSQL](https://aws.amazon.com/about-aws/whats-new/2026/04/aurora-dsql-connector-for-php/) | PHP 用コネクタ提供開始 | PDO_PGSQL 互換、IAM トークン自動生成 + OCC リトライ対応 |
| Amazon EC2 | [R8i/R8i-flex](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-r8i-instances-govcloud-us-west/) / [M8i/M8i-flex](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-m8i-flex-govcloud-us-west/) が GovCloud (US-West) 対応 | カスタム Intel Xeon 6、R7i 比 20% 性能向上、up to 15% 価格性能向上、2.5x メモリ帯域 |
| [AWS Elastic Disaster Recovery](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-elastic-disaster-recovery-ipv6/) | IPv6 サポート追加 | DRS のレプリケーション経路に IPv6 を選択可能に |
| [AWS IoT](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-iot-israel-tel-aviv-europe-milan/) | Israel (Tel Aviv) / Europe (Milan) 展開 | IoT Core の対象リージョンが追加 |

## まとめ

目新しい機能は OpenSearch Serverless の Derived Source と Aurora DSQL の PHP コネクタです。前者はストレージ最適化で既存クラスタにそのまま効く話、後者は DSQL を実運用に近づけるための地味だが必要な整備です。EC2 R8i/M8i の GovCloud 展開は規制業界の乗せ替え案件で効いてきます。IPv6 対応とリージョン拡張は、該当する環境で使っている場合にだけ効く「あれば助かる」系の更新です。
