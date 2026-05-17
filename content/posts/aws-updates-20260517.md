---
title: "【AWS】2026/05/17 のアップデートまとめ"
date: 2026-05-17T08:01:25+09:00
draft: false
tags: ["aws", "cloudwatch", "partner-central", "bedrock-agentcore"]
categories: ["AWS Updates"]
summary: "2026/05/17 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260517/header.png)

# 2026年5月17日 AWS アップデート情報

## はじめに

本日まとめる AWS アップデートは2件です。注目は、**Amazon CloudWatch Logs のクエリ結果上限が10倍に拡大**したことです（公式アナウンスは2026年5月15日付）。これまで10,000件だった上限が100,000件に引き上げられ、大規模ログ分析の効率が劇的に向上します。あわせて、Amazon Bedrock AgentCore をベースにした **AWS Partner Central agents**（2026年3月にGA）も取り上げ、パートナー企業の営業オペレーションがどう変わるかを整理します。特に CloudWatch Logs のアップデートは、ログ分析や障害調査を日常的に行うエンジニアにとって待望の改善といえるでしょう。

## 注目アップデート深掘り

### Amazon CloudWatch Logs のクエリ結果上限拡大

#### なぜこのアップデートが重要なのか

従来、CloudWatch Logs Insights でクエリを実行した際、取得可能な結果は最大10,000件に制限されていました。大規模システムでは1時間分のログが数万件に達することも珍しくなく、全体像を把握するために時間範囲を細かく分割してクエリを複数回実行する必要がありました。この作業は手間がかかるだけでなく、API 呼び出しコストの増加や、分析の一貫性を損なうリスクもありました。

今回のアップデートにより、**1回のクエリで最大100,000件まで取得可能**になり、時間範囲分割の手間が大幅に削減されます。さらに GetQueryResults API がページネーション対応となり、1呼び出しで最大10,000件を返しながらトークンを提供するため、プログラマティックな大量データ取得も効率化されます。

#### LIMIT コマンドの使い方

CloudWatch Logs Insights では、クエリ内に `LIMIT` コマンドを記述することで取得件数を指定できます。以下は基本的な使用例です。

```
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100000
```

この例では、ERROR を含むログを最新の順に並べ、最大100,000件を取得します。従来は `limit 10000` までしか指定できませんでしたが、今回の改善により100,000件まで拡張されました。

#### GetQueryResults API のページネーション実装

AWS CLI を使った実装例を示します。まず、クエリを開始して queryId を取得します。

```bash
$ aws logs start-query \
  --log-group-name /aws/lambda/my-function \
  --start-time 1747468800 \
  --end-time 1747472400 \
  --query-string 'fields @timestamp, @message | sort @timestamp desc | limit 100000'
```

次に、GetQueryResults API を使って結果を取得します。結果が10,000件を超える場合、nextToken が返されます。

```bash
$ aws logs get-query-results --query-id <queryId>
```

Python boto3 を使ったページネーション実装例は以下のとおりです。

```python
import boto3

client = boto3.client('logs')

query_id = '<your-query-id>'
all_results = []
next_token = None

while True:
    if next_token:
        response = client.get_query_results(
            queryId=query_id,
            nextToken=next_token
        )
    else:
        response = client.get_query_results(queryId=query_id)
    
    all_results.extend(response['results'])
    
    if 'nextToken' in response:
        next_token = response['nextToken']
    else:
        break

print(f"Total results: {len(all_results)}")
```

このコードは、nextToken が存在する限りループし、最大100,000件のすべての結果を取得します。1回の API 呼び出しで最大10,000件ずつ取得されるため、100,000件の場合は最大10回の呼び出しが発生します。

#### 従来方式との比較

**従来のアプローチ（時間範囲分割）:**

```bash
# 1時間を6分割して10分ごとにクエリ実行
$ aws logs start-query --start-time 1747468800 --end-time 1747469400 ...
$ aws logs start-query --start-time 1747469400 --end-time 1747470000 ...
# ... 以下同様に繰り返し
```

このアプローチでは、時間範囲の計算、複数クエリの並列実行、結果の結合処理が必要でした。API 呼び出し回数も増加し、コスト面でも不利です。

**新しいアプローチ:**

```bash
# 1回のクエリで1時間分すべてを取得
$ aws logs start-query --start-time 1747468800 --end-time 1747472400 \
  --query-string 'fields @timestamp, @message | limit 100000'
```

1回のクエリで完結するため、実装がシンプルになり、API 呼び出し数も削減されます。

#### 実践的なユースケース

大規模なマイクロサービス環境で、特定のトランザクション ID に関連するすべてのログを一度に取得する例です。

```
fields @timestamp, @message, @logStream
| filter @message like /transaction_id=ABC123/
| sort @timestamp asc
| limit 100000
```

従来は「10,000件取得→最後のタイムスタンプを確認→次の時間範囲でクエリ」という手動イテレーションが必要でしたが、今回の改善により1回で完了します。

## SRE視点での活用ポイント

CloudWatch Logs の上限拡大は、障害対応の初動調査フェーズで特に威力を発揮します。インシデント発生時には「まず全体像を把握する」ことが重要ですが、従来の10,000件制限では部分的なデータしか見られず、重要なエラーログを見落とすリスクがありました。100,000件まで一度に取得できるようになったことで、より包括的な調査が可能になります。

ランブックに組み込む際は、boto3 を使ったスクリプトで自動的にログを取得し、Slack や PagerDuty に通知する仕組みを構築すると効果的です。ページネーション処理を実装すれば、大量のログを確実に取得できます。ただし、100,000件のログをすべてダウンロードする場合は処理時間が増加するため、タイムアウト設定の見直しが必要です。

また、定期的なログ監査やコンプライアンスレポート生成では、CloudWatch Logs Insights で大量データを一括取得し、CSV エクスポートして外部ツールで加工する運用が考えられます。従来は複数回のクエリ実行と結果の手動結合が必要でしたが、この手間が削減され、自動化スクリプトの保守性も向上します。

コスト面では、API 呼び出し回数が削減されるため、頻繁にログ分析を行う環境では長期的にコスト削減が期待できます。ただし、1回のクエリで大量データをスキャンするため、クエリ実行コスト自体は変わらない点に留意が必要です。フィルタ条件を適切に設定し、スキャン対象のログ量を最小化することが、コスト最適化のポイントです。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [Announcing AWS Partner Central agents to accelerate co-sell](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-partner-central-agents-accelerate-co-sell/) | AWS Partner Central に AI エージェント機能（Amazon Bedrock AgentCore ベース）が追加され、営業案件管理が自然言語ベースに進化。会議議事録や提案資料、メールを共有すると、AI が情報を抽出してオポチュニティのフィールドを自動補完。資金プログラムの適格性確認や事前入力済みのファンドリクエスト作成も支援。Model Context Protocol (MCP) 経由で既存 CRM 等とも統合可能。全商用 AWS リージョンで提供開始（2026年3月16日アナウンス）。 |
| 2 | [Amazon CloudWatch Logs announces increased query result limits](https://aws.amazon.com/about-aws/whats-new/2026/05/cloudwatch-logs-query-results/) | CloudWatch Logs のクエリ結果上限が10,000件から100,000件に拡大。LIMIT コマンドで指定可能。GetQueryResults API がページネーション対応となり、1呼び出しで最大10,000件を返しながらトークンを提供。すべての商用 AWS リージョンで利用可能。 |

## まとめ

今日のアップデートは、AWS の運用効率を大きく向上させる改善が中心でした。特に CloudWatch Logs のクエリ結果上限拡大は、ログ分析の効率を劇的に改善する実用的なアップデートです。大規模システムの運用では、1回のクエリで包括的なデータを取得できることが、迅速な障害対応や分析の質向上に直結します。

AWS Partner Central agents（2026年3月16日にGA）は、パートナー企業の co-sell プロセスを効率化する取り組みです。Amazon Bedrock AgentCore をベースに、会議議事録や提案資料を取り込んでオポチュニティ情報を補完し、Model Context Protocol (MCP) 経由で既存 CRM とも統合できる点は、今後の AWS サービス全体における AI 活用の方向性を示唆しています。

どちらのアップデートも既存の全商用リージョンで利用可能なため、すぐに実践投入できる点が魅力です。特に CloudWatch Logs のアップデートは、既存のクエリに `limit 100000` を追加するだけで恩恵を受けられるため、今日からでも試してみる価値があります。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)