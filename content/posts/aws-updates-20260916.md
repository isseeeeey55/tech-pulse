---
title: "【AWS】2026/09/16 のアップデートまとめ"
date: 2026-09-16T08:02:03+09:00
draft: false
tags: ["aws", "billing-conductor", "sagemaker", "iam", "cloudtrail", "amazon-q", "connect", "glue"]
categories: ["AWS Updates"]
summary: "2026/09/16 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260916/header.png)

# 直近発表のAWSアップデート情報まとめ — Billing Conductor カスタムレート、SageMaker インスタンス優先度リストほか

## はじめに

今回は、直近で発表された7件のAWSアップデートを紹介します。AWS Billing Conductor のカスタムレート設定、Amazon SageMaker AI のインスタンス優先度リスト、ルートユーザーサインインのリージョナル回復性向上、CloudTrail と Amazon Q Console の統合による自然言語分析、Amazon Connect のシフト入札機能、SageMaker Unified Studio の ODBC 接続対応、そして AWS Glue zero-ETL のテーブル所有権管理まで、多岐にわたる領域でのアップデートが含まれています。

なかでも Billing Conductor のカスタムレートは、パーセンテージ換算を介さずに交渉済みの料金をそのまま設定できるようにするもので、リセラーやグループ内課金の請求設計に直接効きます。SageMaker のインスタンス優先度リストは、容量不足でジョブが開始待ちになりやすい環境向けの変更です。

## 注目アップデート深掘り

### AWS Billing Conductor: カスタムレートと利用段階別料金の直接指定が可能に

AWS Billing Conductor に**カスタムレート**と**利用段階別料金**の設定機能が追加されました。マルチテナント環境やリセラー、グループ企業内課金を運用する組織が対象です。

#### パーセンテージ換算の限界と、カスタムレートが解決すること

従来、AWS Billing Conductor で顧客ごとの独自料金体系を実現するには、AWS の公開オンデマンド料金に対して**パーセンテージベースのマークアップ・マークダウン**を設定する方式が前提でした。さらに利用段階は AWS があらかじめ定義した区切りに紐づいており、交渉済みの固定単価や独自の段階区切りをそのまま表現することはできませんでした。

今回のアップデートにより、**SKU スコープの料金ルール**で直接カスタム料金と利用段階の閾値を指定できるようになりました。告知の言葉では、公開オンデマンド料金に対するパーセンテージのマークアップ・マークダウンを計算する必要がなくなり、Pro Forma 請求データの設定を正確に制御できます。手動の料金換算と、それに伴う計算ミスのリスクが下がります。

#### 従来方式との比較

**従来のマークアップ方式**では、提供したい単価を公開オンデマンド料金からの相対値（何%上乗せ／値引き）に換算して設定する必要があり、AWS 側の料金改定があるたびに換算をやり直すことになります。段階別の料金も、AWS があらかじめ定義した利用段階に従う形でしか組めませんでした。

**新しいカスタムレート方式**では、SKU スコープの料金ルールに対して、提供単価そのものと、独自の段階区切り（tier break）を直接入力します。告知は具体的な料金例を示していないため、実際の値は自社の契約条件に合わせて設定することになります。

#### 移行時の確認事項

マルチテナント SaaS 環境では、顧客ごとに異なる契約条件を管理する必要があります。Billing Groups で顧客ごとに料金ルールセットを適用する構成は従来どおりで、そのルールの中身をパーセンテージからカスタムレートへ置き換えられる、というのが今回の変更点です。

移行時には、既存のマークアップルールとカスタムレートで Pro Forma 請求データの結果が一致するかを、切り替え前に突き合わせておくと安全です。

この機能は、Sinnet が運営する中国（北京）リージョンと NWCD が運営する中国（寧夏）リージョンを除く、全商用 AWS リージョンで利用可能です。詳細は [AWS Billing Conductor ユーザーガイド](https://docs.aws.amazon.com/billingconductor/latest/userguide/what-is-billingconductor.html) を参照してください。

### Amazon SageMaker AI: インスタンス優先度リストでジョブ開始を高速化

Amazon SageMaker AI のトレーニングおよび処理ジョブに**インスタンス優先度リスト**機能が追加されました。GPU インスタンスの容量待ちでジョブが止まりやすい環境で効果が出やすい変更です。

#### 従来の課題と新機能の動作

機械学習のトレーニングジョブでは、指定した GPU インスタンスの容量が確保できず、ジョブが開始待ちのままになることがあります。従来は、ジョブが通らなければ手動で別のインスタンスタイプに指定し直して再投入する、という手作業が発生していました。

**インスタンス優先度リスト**では、ワークロードが受け入れ可能なインスタンスタイプを優先順位付きのリストで指定すると、SageMaker がその中で最初に利用可能な構成を選んでジョブを実行します。告知が挙げている例は「ml.g6.48xlarge を 2 インスタンス、あるいは ml.g5.48xlarge を 4 インスタンス」という形で、台数を含めた構成単位で候補を並べられる点が特徴です。告知はこれにより、ジョブがより早く開始される可能性が高く、差別化につながらない手動リトライが減る、と説明しています。

#### 実装と活用のポイント

この機能は、SageMaker が利用可能な全 AWS リージョンで、SageMaker の CLI、API、SDK、Console UI から利用できます。具体的な API 呼び出し方法やパラメータの詳細は [Amazon SageMaker API リファレンス](https://docs.aws.amazon.com/sagemaker/latest/APIReference/) を参照してください。

また、同一のジョブ送信の中で、オンデマンドの容量と、予約済みの SageMaker Flexible Training Plans の容量のどちらから調達するかを構成できます。予約済み容量を優先し、足りない場合にオンデマンドへ回す、といった組み立てが可能です。

優先度リストを組むときは、候補に並べるインスタンスの性能差を把握しておくことが前提になります。性能が大きく異なる構成を混在させると、どの候補で実行されたかによってジョブ完了時間が変わり、下流の処理のスケジュールが読みにくくなります。

## SRE視点での活用ポイント

### Billing Conductor カスタムレート: 財務可観測性の向上

カスタムレートの利点は、請求ルールが「公開料金からの相対値」ではなく「契約書に書かれた単価そのもの」になることです。ルールの中身と契約書を直接突き合わせられるため、レビューのコストが下がります。Billing Groups と料金ルールを Infrastructure as Code で管理している場合も、レビュー対象が換算式から実値に変わります。

導入時には、既存の請求計算ロジックとの整合性を検証し、移行期間中は並行運用で Pro Forma 請求データの一致を確認しておくと安全です。

### SageMaker インスタンス優先度リスト: ML パイプラインの信頼性向上

これまでワークフロー側やランブックに書いていた「容量が取れなかったらどのインスタンスにフォールバックするか」という分岐を、ジョブ送信時の宣言としてサービス側に寄せられるのが運用上の変化です。フォールバック先の判断が実行時のオンコール作業ではなくなり、レビュー可能な設定として残ります。

一方で、どの候補で実行されたかによってジョブの所要時間は変わります。完了時刻を前提に後続処理を組んでいる場合は、許容できる性能差の範囲でリストを構成し、実行されたインスタンスタイプを記録して追えるようにしておく必要があります。

### ルートユーザーサインインの3リージョン化: CloudTrail 監視の見直し

ルートユーザーのサインインは US East（バージニア北部）、US East（オハイオ）、US West（オレゴン）の3リージョンで提供され、サインイントラフィックが3リージョンに分散されるようになりました。運用面で影響があるのは監視側です。CloudTrail の `ConsoleLogin` イベントは、実際にサインインを処理したリージョンに記録されます。ルートユーザーのサインインを検知するルールを単一リージョンで組んでいる場合、取りこぼしが起きるため、3リージョンすべてを対象にする必要があります。

### CloudTrail と Amazon Q Console の統合: インシデント対応の迅速化

CloudTrail イベントを自然言語で調査できるようになったことで、クエリを書く前の当たりをつける工程が短くなります。告知によると、Amazon Q Console はユーザーに代わって CloudTrail トレイル、関連する CloudWatch ロググループ、イベントデータストアを照会し、トレイル設定やログ取得範囲の確認、誰がリソースにアクセスしたかの調査、リソースの作成・削除やエラーの追跡といった用途を想定しています。

ただし、この機能は調査の出発点として扱い、判断の根拠にする際は元の CloudTrail イベントを確認するフローを維持すべきです。回答の網羅性は、Amazon Q が参照できるデータソースの設定範囲に依存します。この統合は、Amazon Q Console がサポートされる全 AWS 商用リージョンで利用できます。

## 全アップデート一覧

| サービス | アップデート内容 | リンク |
|---------|----------------|--------|
| AWS Billing Conductor | カスタムレートと利用段階別料金設定に対応。SKU スコープで直接料金と段階閾値を指定可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/AWS-Billing-Conductor-custom-rates-usage-tier) |
| Amazon SageMaker AI | トレーニング・処理ジョブでインスタンス優先度リストをサポート。複数インスタンスタイプを指定し、自動的に利用可能な構成を選択 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-sagemaker-training-processing-instance-pref-lists/) |
| AWS Root User | ルートユーザーサインインが US East（バージニア北部）・US East（オハイオ）・US West（オレゴン）の3リージョンで提供され、トラフィックが分散。CloudTrail の `ConsoleLogin` は処理したリージョンに記録される | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/root-user-regional-resiliency/) |
| AWS CloudTrail | Amazon Q Console と統合。自然言語で CloudTrail イベントを分析・調査可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/cloudtrail-amazon-q-console/) |
| Amazon Connect | エージェントが希望シフトに入札可能に。スケジューラが設定したエージェントランキングと予測需要をもとにシフトを提示し、各エージェントを希望順位が最も高い空きシフトへ自動割り当て（同順位はランキングでタイブレーク） | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-connect-customer-shift-bidding/) |
| Amazon SageMaker Unified Studio | ODBC 接続に対応。Amazon Athena ODBC ドライバ経由で Microsoft Power BI などの ODBC 互換ツールからプロジェクト内のガバナンス対象データへ直接接続可能に | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/sagemaker-unified-studio-odbc-power-bi/) |
| AWS Glue zero-ETL | ターゲットテーブルのプロパティを所有インテグレーションに紐付け、競合を検出。別インテグレーションが所有するテーブルを指定すると所有者を提示し、別ターゲットの選択か既存の更新を促す | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/glue-zero-etl-ownership-conflicts/) |

## まとめ

今回のラインナップは請求・ML・認証・データ基盤と領域が散らばっていますが、共通しているのは、これまで人手やスクリプトで埋めていた部分をサービス側の設定として宣言できるようにする方向性です。Billing Conductor では料金の換算式が実値の入力に、SageMaker では容量不足時のリトライがジョブ送信時の優先度リストに、Glue zero-ETL ではテーブル衝突の事前調査が所有権チェックに置き換わります。

運用への影響という点で見落としやすいのは、ルートユーザーサインインの3リージョン化です。`ConsoleLogin` イベントが処理したリージョンに記録されるため、単一リージョンで監視ルールを組んでいる場合は対象の見直しが必要になります。

Billing Conductor のカスタムレートと SageMaker の優先度リストは、該当する運用があればすぐに試せる変更です。各機能の詳細は公式ドキュメントを参照し、自組織の要件に合わせて検証してください。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)