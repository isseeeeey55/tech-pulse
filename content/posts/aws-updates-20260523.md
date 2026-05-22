---
title: "【AWS】2026/05/23 のアップデートまとめ"
date: 2026-05-23T08:02:36+09:00
draft: true
tags: ["aws", "cloudwatch", "security", "sagemaker", "clean-rooms", "workspaces", "keyspaces", "glue", "transform", "lake-formation"]
categories: ["AWS Updates"]
summary: "2026/05/23 のAWSアップデートまとめ"
---

# 2026年5月23日 AWS アップデート情報

## はじめに

2026年5月23日、AWSは9件のアップデートを発表しました。本日は、マイグレーション評価の高度化、SageMakerのドメイン管理・ガバナンス強化、セキュリティ運用の自動化、そしてログ分析機能の大幅拡張など、エンタープライズ運用の効率化に直結するアップデートが多数含まれています。

特に注目すべきは、**Amazon CloudWatch Logs Insights に追加された13個の新しいコマンドと関数**です。これにより、ログ分析の表現力が大きく向上し、従来は前処理が必要だった複雑な解析がクエリ内で完結できるようになります。また、**AWS Security Agent がペネトレーションテストの検証スクリプトを自動生成**する機能も追加され、セキュリティチームの負荷軽減と対応スピード向上が期待できます。

本記事では、これらの中から特に実務インパクトの大きいアップデートを深掘りし、SRE視点での活用ポイントを解説します。

---

## 注目アップデート深掘り

### Amazon CloudWatch Logs Insights の新クエリコマンド・関数

Amazon CloudWatch Logs Insights のクエリ言語に、**13個の新しいコマンドと関数**が追加されました。これにより、ログ分析の柔軟性と表現力が大幅に向上します。

#### なぜこのアップデートが重要なのか

従来、CloudWatch Logs Insights では基本的な文字列操作や数値演算は可能でしたが、Base64エンコードされたペイロードの解析や、logfmt形式のログパース、ネストされたJSON配列の展開などは、事前にLambdaやログ送信側での変換処理が必要でした。今回の機能追加により、**クエリ実行時にその場で高度な変換・解析が可能**となり、ログ基盤の設計がシンプルになります。

#### 追加された機能カテゴリ

新機能は以下の3つのカテゴリに分類されます。

**1. 文字列・数値関数**

- `startswith` / `endswith`：文字列の接頭辞・接尾辞チェック
- `case`：条件分岐による値の変換
- `regex_replace`：正規表現による文字列置換
- `round`：数値の四捨五入
- `haversine`：GPS座標から距離計算

**2. エンコード/デコード関数**

- `base64encode` / `base64decode`：Base64エンコード/デコード
- `urlencode` / `urldecode`：URLエンコード/デコード

**3. 解析・分析コマンド**

- `parse logfmt`：logfmt形式のログを自動パース
- `expand`：JSON配列を個別レコードに展開
- `relevantfields`：高カーディナリティログから重要フィールドを自動抽出

#### 実践例：Base64デコードとlogfmt解析

API Gatewayのアクセスログで、リクエストボディがBase64エンコードされている場合の解析例です。

```
fields @timestamp, requestId, base64decode(requestBody) as decodedBody
| filter statusCode >= 500
| parse decodedBody "user_id=* action=* result=*" as userId, action, result
| stats count() by userId, action
```

従来は別途Lambda関数でデコード処理を挟む必要がありましたが、クエリ内で直接デコードできるようになりました。

logfmt形式（`key1=value1 key2=value2`形式）のログを解析する例：

```
fields @timestamp, @message
| parse logfmt @message
| filter status="error"
| stats count() by service, error_code
```

`parse logfmt`コマンドが自動的にキー・バリューペアをフィールドとして展開するため、スキーマ定義なしで構造化ログとして扱えます。

#### 地理的距離計算の活用

`haversine`関数を使えば、GPS座標からの距離計算がクエリ内で可能です。配送業務やIoTデバイスの移動分析に有用です。

```
fields @timestamp, deviceId, latitude, longitude
| sort @timestamp asc
| fields deviceId, 
         haversine(latitude, longitude, 
                   lag(latitude, 1), lag(lag(longitude, 1), 1)) as distance_km
| stats sum(distance_km) as total_distance by deviceId
```

このクエリは、各デバイスの連続した位置情報から移動距離を計算し、デバイスごとの総移動距離を算出します。

#### 配列展開による詳細分析

ネストされたJSON配列を個別レコードに展開することで、配列内の各要素を個別に分析できます。

```
fields @timestamp, requestId, items
| expand items as item
| fields @timestamp, requestId, item.productId, item.quantity, item.price
| stats sum(item.quantity) as total_quantity, 
        sum(item.price * item.quantity) as total_amount 
  by item.productId
```

従来はアプリケーション側で配列を展開してログ出力する必要がありましたが、元のログ構造を保ったまま柔軟に分析できるようになりました。

---

### AWS Security Agent の検証スクリプト自動生成

AWS Security Agent が**ペネトレーションテストの検出結果に対する検証スクリプトを自動生成**する機能を追加しました。

#### 背景：セキュリティ検証の課題

セキュリティチームがペネトレーションテストを実施した際、検出された脆弱性が実際に悪用可能かを検証するには、レポートに記載された再現手順を手動で実行する必要がありました。この作業は以下の課題を抱えていました。

- 手順書の解釈ミスによる検証失敗
- 環境固有のパラメータ設定の煩雑さ
- 機密情報（トークン、パスワード等）の取り扱いリスク
- 複数の検出結果を検証する際の時間コスト

#### 新機能の仕組み

AWS Security Agent は、各検出結果に対して**実行可能なスクリプトを自動生成**します。生成されたスクリプトには以下が含まれます。

- **セットアップ手順**：必要なツールや依存関係のインストール方法
- **ドキュメント化された環境変数**：対象システムのエンドポイント、認証情報などをパラメータ化
- **機密値のマスキング処理**：パスワードやAPIキーが平文で保存されない仕組み

#### 利用フロー

```bash
# 1. AWS Security Agent コンソールから検証スクリプトをダウンロード
$ aws security-agent download-verification-script \
    --finding-id finding-12345 \
    --output-file verify-finding-12345.sh

# 2. 環境変数を設定
$ export TARGET_ENDPOINT="https://api.example.com"
$ export API_KEY="your-api-key-here"

# 3. スクリプト実行
$ bash verify-finding-12345.sh
```

スクリプトは検証結果を標準出力に返し、終了コードで成功・失敗を判定できるため、CI/CDパイプラインへの組み込みも容易です。

#### 従来手法との比較

| 項目 | 従来（手動実行） | 新機能（自動生成スクリプト） |
|------|----------------|---------------------------|
| 検証準備時間 | 検出結果ごとに15〜30分 | 環境変数設定のみ（5分以内） |
| 再現性 | チームメンバー間でばらつき | スクリプト化により一貫性を保証 |
| 機密情報管理 | 手順書に平文記載のリスク | 環境変数経由で安全に管理 |
| 自動化 | 困難 | CI/CDパイプライン統合可能 |

#### CI/CDパイプラインへの統合例

GitLab CI/CD での統合例を示します。

```yaml
verify-security-findings:
  stage: security-verification
  script:
    - aws security-agent download-verification-script --finding-id $FINDING_ID --output-file verify.sh
    - export TARGET_ENDPOINT=$STAGING_ENDPOINT
    - export API_KEY=$STAGING_API_KEY
    - bash verify.sh
  only:
    - schedules
  artifacts:
    reports:
      junit: verification-report.xml
```

定期的なスケジュール実行により、修復後の再検証を自動化できます。

---

### AWS Clean Rooms の変更可能な支払い設定

AWS Clean Rooms が、コラボレーション内の**支払い設定を後から変更可能**にする機能をサポートしました。

#### 従来の課題

AWS Clean Rooms では、複数の組織が互いにデータを共有せずに共同分析を行う「コラボレーション」を作成できますが、従来は**コラボレーション作成時に誰が費用を負担するかを固定**する必要がありました。これにより、以下の問題が発生していました。

- プロジェクト進行中にビジネス関係が変化しても、費用分担を調整できない
- 高コストな分析（ML推論、PySpark処理）と低コストな分析（簡易SQL）で負担者を分けられない
- 初期の試験段階と本格運用で負担者を変更したい場合、コラボレーションを再作成する必要

#### 新機能：柔軟な費用分担

新機能では、**コスト種別ごとに異なる支払者**を指定でき、さらに**コラボレーション作成後も変更可能**です。

対応するコスト種別：

- SQL クエリ実行コスト
- PySpark ジョブ実行コスト
- ML モデルの学習コスト
- ML モデルの推論コスト
- 合成データ生成コスト

#### チェンジリクエストによるガバナンス

支払い設定の変更は**チェンジリクエスト**方式で行われ、すべてのコラボレーションメンバーの承認が必要です。これにより、透明性と合意形成プロセスが担保されます。

変更フロー：

1. いずれかのメンバーがチェンジリクエストを作成
2. 他のすべてのメンバーに通知が送信
3. 全員が承認すると変更が適用
4. 1人でも拒否すると変更は却下

#### 活用シナリオ例

**シナリオ1：段階的なコスト負担の移行**

製薬企業Aと医療機関Bが臨床試験データの共同分析を行う場合：

- **初期段階**：製薬企業Aがすべてのコストを負担（実証実験フェーズ）
- **本格運用段階**：簡易な統計分析（SQL）は医療機関Bが負担、高度なML推論は製薬企業Aが負担

この切り替えを、コラボレーションを再作成せずに実施できます。

**シナリオ2：複数支払者による柔軟な運用**

同じコスト種別に対して複数の支払者を事前に登録しておき、分析実行時に選択することも可能です。例えば、小売企業3社が共同でマーケット分析を行う場合：

- SQL クエリの支払者候補：企業A、企業B、企業C
- 実行時に各企業の予算状況に応じて支払者を選択

---

## SRE視点での活用ポイント

### CloudWatch Logs Insights の新機能

ログ分析は SRE の日常業務の中核であり、今回の機能追加は以下のシーンで特に効果を発揮します。

**インシデント対応の高速化**

障害発生時、複数のサービスにまたがるトレースログから根本原因を特定する際、Base64デコードやJSON配列の展開をクエリ内で完結できるため、調査時間を大幅に短縮できます。特に、`relevantfields`コマンドによる自動フィールド検出は、未知のログ構造を持つサードパーティサービスのログ調査で威力を発揮するでしょう。

**既存ログ基盤の簡素化検討**

現在、ログを構造化するためにLambda関数やFluentdでの前処理を行っている場合、新機能により**ログ収集はシンプルに保ち、解析時にクエリで柔軟に処理**するアーキテクチャへの移行を検討できます。これにより、ログパイプラインの複雑さとコストを削減しつつ、分析の自由度を高められます。

**地理的分散システムの監視**

グローバルにデプロイされたIoTデバイスやエッジコンピューティング環境では、`haversine`関数を活用して、デバイスの移動距離や配置状況をリアルタイムに監視できます。これをCloudWatch アラームと組み合わせれば、異常な移動パターンの検知や、サービスエリア外への逸脱検知が可能になります。

**注意点とリスク**

新しいクエリ関数は強力ですが、複雑なクエリはスキャンするデータ量が増加し、**コストとクエリ実行時間が増大する可能性**があります。本番環境で導入前に、過去のログを使用してクエリパフォーマンスを検証し、コスト影響を見積もることを推奨します。また、`expand`コマンドによる配列展開は、大量の配列要素を持つログで実行すると、結果セットが爆発的に増加するため、適切なフィルタ条件との併用が必須です。

### AWS Security Agent の検証スクリプト自動生成

セキュリティ脆弱性の検証プロセスは、SREがセキュリティチームと連携する場面で頻繁に発生します。

**ランブックへの組み込み**

障害対応ランブックや緊急対応手順書に、生成された検証スクリプトを組み込むことで、**誰でも一貫した手順で脆弱性を確認**できるようになります。これにより、担当者による対応品質のばらつきを削減し、オンコール対応の負担を軽減できます。

**DevSecOpsパイプラインの強化**

Terraform や CloudFormation でインフラ変更を適用した後、自動的に検証スクリプトを実行してセキュリティリグレッションがないかを確認するステップを追加できます。これにより、**インフラ変更が既知の脆弱性を再導入していないことを継続的に保証**できます。

**トリアージの優先順位付け**

検証スクリプトを実行することで、検出結果が実際に悪用可能な脆弱性かを迅速に判断できます。これにより、**誤検知を早期に排除し、真に修復が必要な項目にリソースを集中**できます。

**導入時の考慮事項**

検証スクリプトの実行には、本番環境またはそれに近い環境へのアクセスが必要です。そのため、**検証専用の隔離された環境を用意**することが推奨されます。また、スクリプトが生成する通信トラフィックが、既存のセキュリティ監視（WAF、IDS/IPS）で誤検知されないよう、事前にホワイトリスト設定を調整する必要があります。

### AWS Clean Rooms の支払い設定変更

データコラボレーション環境での費用管理は、複数ステークホルダーが関与するプロジェクトで重要な課題です。

**コスト配分の透明性確保**

SREがマルチテナント環境やパートナー連携システムを運用する場合、誰がどのリソースを使用し、どれだけのコストが発生しているかを可視化することが求められます。Clean Roomsの新機能により、**分析種別ごとのコスト分担を柔軟に設計**でき、各パートナーへの適切なチャージバックが可能になります。

**プロジェクトフェーズごとの費用戦略**

プロジェクト初期段階では、一方の組織がコストを全額負担し、成果が確認できた後に段階的に他の組織も負担するといった戦略を、**コラボレーション環境を再構築せずに実現**できます。これにより、初期導入のハードルを下げつつ、長期的な費用分担への移行をスムーズに行えます。

**リスクと注意点**

チェンジリクエストには全メンバーの承認が必要なため、意思決定プロセスが遅延するリスクがあります。事前に**支払い設定変更のガバナンスルール**（誰が提案できるか、承認期限はどう設定するか）をステークホルダー間で合意しておくことが重要です。また、変更履歴が適切に記録されるため、監査対応やコンプライアンス報告にも活用できます。

---

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [New agentic migration assessment capabilities now available with AWS Transform](https://aws.amazon.com/about-aws/whats-new/2026/05/assessment-capabilities-transform>) | エージェント型マイグレーション評価機能を追加。What-Ifシナリオ作成、カスタマイズ可能な仮定条件、複数のTCO評価オプションで最適なAWSマイグレーションパスを決定 |
| 2 | [Amazon SageMaker expands domain management across domain types](https://aws.amazon.com/about-aws/whats-new/2026/05/domain-management-iam-idc/) | SageMaker Unified StudioがIdentity Centerベースドメインのドメイン管理に対応。プロジェクト、ユーザー権限、ネットワーク設定を一元管理 |
| 3 | [Amazon SageMaker adds business metadata and governance in IAM-based domains](https://aws.amazon.com/about-aws/whats-new/2026/05/sagemaker-catalog-iam-domains/) | IAMベースドメインでビジネスメタデータとガバナンス機能をサポート。AI生成メタデータ、用語集、メタデータフォームテンプレートでデータカタログを強化 |
| 4 | [Amazon Keyspaces (for Apache Cassandra) expands to Asia Pacific (Malaysia) and Asia Pacific (Thailand) Regions](https://aws.amazon.com/about-aws/whats-new/2026/05/amazon-keyspaces-malaysia-thailand/) | Amazon Keyspacesがマレーシアとタイリージョンで利用可能に。低レイテンシーでデータレジデンシー要件を満たすCassandra互換アプリケーションを構築可能 |
| 5 | [AWS Security Agent adds verification scripts for pentest findings](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-security-agent/) | ペネトレーションテストの検出結果に対する検証スクリプトを自動生成。トリアージと修復対応を加速 |
| 6 | [AWS Clean Rooms now supports mutable payment configurations for collaborations](https://aws.amazon.com/about-aws/whats-new/2026/05/aws-clean-rooms-mutable-payments) | コラボレーション作成後も支払い設定を変更可能に。コスト種別ごとに異なる支払者を指定でき、柔軟な費用分担を実現 |
| 7 | [Amazon WorkSpaces Personal now supports WorkSpace Migration for Linux WorkSpaces](https://aws.amazon.com/about-aws/whats-new/2026/05/workspaces-linux-migration) | Linux WorkSpace間でのシームレスな移行をサポート。ホームディレクトリのユーザーデータが自動移行され、手動コピー不要 |
| 8 | [Amazon CloudWatch Logs Insights adds new query commands and functions](https://aws.amazon.com/about-aws/whats-new/2026/06/amazon-cloudwatch-logs-insights/) | 13個の新しいコマンドと関数を追加。文字列操作、エンコード/デコード、logfmt解析、JSON配列展開、地理的距離計算などが可能に |
| 9 | [SageMaker Unified Studio automates Glue connector provisioning for cross-subnet job retries](https://aws.amazon.com/about-aws/whats-new/2026/05/sagemaker-unified-studio-glue/) | 複数サブネット間でのGlueジョブ自動リトライに対応。IPアドレス枯渇やAZ障害時に自動フェイルオーバーし、手動バックアップコネクタ設定が不要に |

---

## まとめ

本日のアップデートは、**運用効率化**と**ガバナンス強化**が主要テーマとなっています。特に、CloudWatch Logs Insights の機能拡張は、長年ユーザーから要望されていた高度なログ解析機能を提供し、ログ基盤のアーキテクチャ設計に新たな選択肢をもたらしました。

また、AWS Security Agent の検証スクリプト自動生成や、SageMaker Unified Studio の自動プロビジョニング機能は、**手動作業の自動化によるヒューマンエラー削減**という共通のメリットを提供します。これらは、DevOps・SREチームが「Toil（面倒な手作業）」を削減し、より戦略的な業務に集中するための重要なステップです。

一方、AWS Clean Rooms や SageMaker の新機能は、**マルチアカウント・マルチテナント環境でのガバナンス**を強化し、エンタープライズ規模でのデータ利活用を支援します。これらの機能は、単なる技術的な拡張ではなく、ビジネスプロセスと密接に連携した設計がなされている点が特徴です。

今後も、これらの新機能を活用した具体的なユースケースや、既存システムへの統合方法について、継続的にキャッチアップしていくことが重要です。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)