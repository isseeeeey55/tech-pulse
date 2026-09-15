---
title: "【AWS】2026/09/15 のアップデートまとめ"
date: 2026-09-15T08:02:25+09:00
draft: false
tags: ["aws", "end-user-messaging", "sagemaker", "cloudfront", "connect", "entity-resolution", "private-ca", "eks", "ebs", "quick", "marketplace", "evs", "storage-gateway", "ecs", "rds", "kms", "rekognition", "kinesis", "ram", "organizations"]
categories: ["AWS Updates"]
summary: "2026/09/15 のAWSアップデートまとめ"
---

![](/images/aws-updates-20260915/header.png)

# 直近のAWSアップデート情報（2026年9月版）

## はじめに

今回は、直近で発表された19件のAWSアップデートを紹介します。Amazon ECSのIAM条件キー拡張やEBS Volume Clonesのクロスアカウント対応といったインフラ基盤の機能強化から、Amazon QuickのデスクトップアプリGAとモバイルアプリへのアクティビティフィード追加、SageMaker JumpStartへの新しい基盤モデル追加、AWS End User MessagingのWhatsAppダイナミックフロー対応まで、幅広い領域のアップデートがありました。

---

## 注目アップデート深掘り

### Amazon ECS の RunTask / StartTask API での IAM 条件キー拡張

Amazon ECS が RunTask と StartTask API でも IAM 条件キー `ecs:task-cpu` および `ecs:task-memory` をサポートするようになりました。これまでこれらの条件キーは RegisterTaskDefinition、CreateService、UpdateService API でのみ利用可能でしたが、今回の拡張により、タスクを起動するあらゆる経路で統一的なリソース制限を IAM ポリシーレベルで適用できるようになります。

#### RunTask / StartTask でも条件キーが評価されるようになった

ECS 環境では、開発者や CI/CD パイプラインが RunTask API を使って直接タスクを起動するケースがあります。従来、`ecs:task-cpu` / `ecs:task-memory` を参照する IAM ポリシーは RegisterTaskDefinition・CreateService・UpdateService でしか評価されず、RunTask / StartTask 経由の起動は評価対象外でした。

今回の拡張で、これらの条件キーを参照する IAM ポリシーが RunTask / StartTask でも評価されるようになり、告知の表現では「ECS 環境全体でリソース割り当てを制御する単一の統一メカニズム」になります。AWS は目的として、予期しないコスト超過の防止と、ワークロードをリソースポリシーに沿わせることを挙げています。ECS が利用可能な全リージョンで、追加料金なしで利用できます。

#### 実装の詳細

IAM ポリシーに以下のような条件を追加することで、RunTask / StartTask 実行時のリソース制限を設定できます。サービス認可リファレンス上、`ecs:task-cpu` / `ecs:task-memory` はどちらも Numeric 型の条件キーなので、数値比較演算子で上限を指定できます。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:RunTask",
        "ecs:StartTask"
      ],
      "Resource": "*",
      "Condition": {
        "NumericLessThanEquals": {
          "ecs:task-cpu": "2048",
          "ecs:task-memory": "4096"
        }
      }
    }
  ]
}
```

この設定では、RunTask / StartTask で CPU `2048`・メモリ `4096` を超える値のタスクを起動しようとすると、Allow の条件を満たさないため拒否されます。値の単位はタスク定義の `cpu` / `memory` パラメータの指定と合わせて設計してください。

#### 従来との比較

従来はタスク定義の登録時（RegisterTaskDefinition）とサービスの作成・更新時にしか条件キーが評価されませんでした。今回の拡張で、タスク定義の登録時と起動時の両方に同じ条件キーでガードレールを設けられるようになります。

---

### AWS End User Messaging の WhatsApp ダイナミックフロー対応

AWS End User Messaging が WhatsApp のダイナミックフロー機能に対応しました。これにより、WhatsApp のチャット内で予約申し込み、リード獲得、ユーザー登録、アンケート、決済などのインタラクティブな体験を完結させることができるようになります。

#### フローの構成

ダイナミックフローは、Meta が提供するテンプレートまたはゼロから構築した独自フローを使用し、テキスト入力、日付ピッカー、ドロップダウン、ボタンなどの構成要素をチャット内に直接表示します。各画面はリアルタイムに独自の HTTPS エンドポイントを呼び出せるため、ライブの在庫状況や予約可能枠を表示したり、ユーザーごとにパーソナライズされた提案を行うことができます。

#### 実装の流れ

フローは JSON スキーマで定義し、メッセージテンプレート経由で配信します。フローの作成・管理は AWS End User Messaging Social 内で完結し、コンソールまたは API を使います。End User Messaging Social が利用可能な全リージョンで提供されています。

#### ユースケース

告知が挙げる用途は、予約、リード獲得、サインアップ、アンケート、決済（トランザクション）の5つです。たとえば予約フローなら、各画面から自社の HTTPS エンドポイントを呼び出して空き状況をリアルタイムに表示し、日時の選択から予約までをチャット内で完結させる構成が取れます。

---

### Amazon EBS Volume Clones のクロスアカウントコピー対応

Amazon EBS Volume Clones がアカウント間でのボリュームコピー機能に対応しました。暗号化の再設定にも対応し、ソースアカウントの EBS ボリュームをターゲットアカウントの AWS KMS キーで暗号化しながらコピーできるようになりました。

#### アカウント境界を越えてボリュームを複製できる

本番と開発のワークロードを別アカウントに分けている組織を対象にした機能です。告知では、本番データベースのボリュームを隔離された開発アカウントにクローンし、開発者に本番データの新しいコピーを安全に試してもらう用途が例示されています。暗号化されていないボリュームやカスタマーマネージドキーで暗号化されたボリュームを含め、すべてのボリュームタイプに対応しています。

また、環境ごとに異なる暗号化キーの管理が必要な場合（本番用と非本番用で異なる KMS キーを使用するなど）にも対応しており、セキュリティとコンプライアンスの要件を満たしながらデータを共有できます。

#### 実装方法

コピー方法は、まず AWS Resource Access Manager (RAM) でボリュームをターゲットアカウントと共有し、その後ターゲットアカウント側で共有ボリュームのコピーを同じアベイラビリティゾーン内に作成します。AWS Management Console、CLI、SDK で利用可能です。

提供範囲は Volume Clones をサポートする全リージョンで、商用リージョン、AWS GovCloud (US)、中国リージョン、サポート対象の Local Zones が含まれます。コピー先は共有元と同じアベイラビリティゾーンに限られる点に注意してください。

---

## SRE視点での活用ポイント

### ECS IAM 条件キー拡張の活用

Terraform で ECS タスク定義を管理している環境では、CI/CD パイプラインから RunTask を実行する際に、IAM ポリシーレベルでリソース上限を設定することで、誤った設定変更による予期しないコスト増加を防げます。特に複数のマイクロサービスを運用している場合、各サービスごとに異なるリソース上限を IAM ロールで管理することで、きめ細かいコスト管理が可能になります。

導入時の注意点として、既存の運用で意図的に大きなリソースを割り当てているタスクがある場合、IAM ポリシーを適用する前にそれらを洗い出し、ポリシーの例外を設定するか、リソース割り当てを見直す必要があります。段階的な導入として、まず CloudTrail で RunTask の実行履歴を分析し、現状のリソース使用パターンを把握してからポリシーを設計することを推奨します。

### クロスアカウント EBS コピーの活用

本番障害の再現調査で、本番ボリュームを隔離アカウントに複製してから検証する運用に使えます。本番アカウントに調査用の権限を広げずに、実データに近い状態で原因を切り分けられます。なお、コピーは同じアベイラビリティゾーン内への作成なので、リージョンをまたぐ DR 用途には別の手段を組み合わせる必要があります。

導入時は、ターゲットアカウント側で再暗号化に使う KMS キーと、RAM による共有設定をあらかじめ検証環境で確認しておくと安全です。

### WhatsApp ダイナミックフローの活用

各画面が自社の HTTPS エンドポイントをリアルタイムに呼び出す構成なので、エンドポイントはユーザー向けの本番 API として扱う必要があります。レイテンシとエラー率を SLI として監視し、在庫・予約枠などのバックエンド障害時にフローがどう振る舞うかを事前に決めておきます。

導入時の判断基準として、ユーザーベースが WhatsApp を主要なコミュニケーション手段として利用しているかどうかを確認する必要があります。また、HTTPS エンドポイントのレスポンス速度がユーザー体験に直結するため、バックエンドシステムの可用性と応答速度の監査が重要です。

---

## 全アップデート一覧

| カテゴリ | タイトル | 概要 |
|---------|---------|------|
| **メッセージング** | [AWS End User Messaging SMS の自動フェイルオーバー](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-end-user-messaging-improves-deliverability/) | SMS 配信の信頼性を強化する自動フェイルオーバー機能を追加 |
| **メッセージング** | [AWS End User Messaging WhatsApp ダイナミックフロー対応](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-end-user-messaging-whatsapp-dynamic-flows/) | WhatsApp チャット内で予約、決済、アンケートなどを完結可能に |
| **AI/ML** | [SageMaker JumpStart に Granite Speech、Kanana、OpenFold3 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/granite-speech-4.1-2b-edge-kanana-2-30b-a3b-instruct-openfold3-jumpstart/) | IBM、Kakao、OpenFold の最新基盤モデルが利用可能に |
| **AI/ML** | [SageMaker JumpStart に Gemma-4-31B 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/gemma-4-31b-it-assistant-gemma-4-31b-it-nvfp4-jumpstart/) | Google DeepMind の Gemma-4-31B フル精度版と NVIDIA 最適化版を提供 |
| **AI/ML** | [SageMaker JumpStart に Ministral-3 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/ministral-3-3b-instruct-2512-ministral-3-8B-Instruct-2512-jumpstart/) | Mistral AI のコンパクトなマルチモーダルモデルがエッジデバイスに対応 |
| **AI/ML** | [SageMaker JumpStart に Qwen3.6 と Wan2.1 追加](https://aws.amazon.com/about-aws/whats-new/2026/01/qwen3.6-35b-a3b-nvfp4-wan2.1-t2v-1.3B-diffusers-jumpstart/) | NVIDIA の量子化版エージェント型モデルとアリババのテキスト動画生成モデルを提供 |
| **CDN** | [Dynamic Image Transformation for Amazon CloudFront（AWS ソリューション）に4つの新機能](https://aws.amazon.com/about-aws/whats-new/2026/08/dynamic-image-transformation-adds-new-features/) | スマート切り抜き強化、自動最適化強化、テストプレイグラウンド、ECS/Lambda 機能パリティを実現 |
| **CRM** | [Amazon Connect Customer Profiles セグメントイベント機能](https://aws.amazon.com/about-aws/whats-new/2026/09/connect-customer-profiles-segment-events/) | 顧客がセグメントに入った/出た時にリアルタイム通知を Kinesis に送信 |
| **データ管理** | [AWS Entity Resolution レコードレベル信頼度スコア](https://aws.amazon.com/about-aws/whats-new/2026/09/entity-resolution-record-confidence/) | ML マッチングで各レコードが個別の信頼度スコアを持つように進化 |
| **セキュリティ** | [AWS Private CA EKS アドオンと AD コネクタが GovCloud 対応](https://aws.amazon.com/about-aws/whats-new/2026/09/private-ca-eks-addon-ad-govcloud/) | Kubernetes と Active Directory 向けの証明書管理を GovCloud で利用可能に |
| **ストレージ** | [EBS Volume Clones クロスアカウントコピー対応](https://aws.amazon.com/about-aws/whats-new/2026/09/ebs-volume-clones-cross-account-copy/) | アカウント間でのボリュームコピーと暗号化再設定に対応 |
| **アプリケーション** | [Amazon Quick デスクトップアプリ GA リリース](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-quick-desktop-app-generally-available-macos-windows/) | macOS・Windows でローカルファイル統合とバックグラウンドエージェントを提供 |
| **アプリケーション** | [Amazon Quick モバイルアクティビティフィード](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-quick-activity-feed-available-ios-android-mobile-devices/) | iOS・Android で企業全体のコミュニケーションツールを一元表示 |
| **アプリケーション** | [Amazon Quick 常時稼働エージェントと管理機能強化](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-quick-always-on-agents-sharper-feed-enterprise-controls/) | クラウド上で常時実行されるエージェント、改善されたフィード、エンタープライズ管理機能を追加 |
| **マーケットプレイス** | [AWS Marketplace デモ/オファー要求の自動審査](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-marketplace-demo-private-offer-requests-qualification/) | AI ワークフローで顧客要求を自動評価し、数分以内に出品者に届ける |
| **コンピューティング** | [Amazon EVS 4リージョン拡大](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-evs-available-in-additional-regions/) | VMware Cloud Foundation を大阪、台北、スペイン、テルアビブで利用可能に |
| **ストレージ** | [Storage Gateway FIPS プライベート接続対応](https://aws.amazon.com/about-aws/whats-new/2026/09/storage-gateway-fips-privatelink-s3/) | S3 File Gateway が PrivateLink 経由の FIPS 140-3 準拠接続に対応 |
| **コンテナ** | [Amazon ECS IAM 条件キー拡張](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ecs-expands-condition-key-support/) | RunTask / StartTask API で CPU・メモリの IAM 条件キーをサポート |
| **データベース** | [RDS for Oracle July 2026 SPB 対応](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-rds-oracle-supports-spatial-patch-bundle-jul-2026-ru/) | Oracle 19c・26ai で Supplemental Patch Bundle と段階的アップグレードロールアウトに対応 |

---

## まとめ

今回は、ガバナンスとマルチアカウント運用に効くアップデートが目立ちました。ECS の IAM 条件キーは RunTask / StartTask にも拡張され、EBS Volume Clones はアカウント間コピーと再暗号化に対応しています。

SageMaker JumpStart には、音声認識・音声翻訳（granite-speech）、韓国語・英語のバイリンガル指示追従（kanana）、生体分子複合体の構造予測（OpenFold3）など、用途が明確なモデルが追加されました。

AWS End User Messaging では WhatsApp ダイナミックフローと SMS の自動フェイルオーバーが、Amazon Quick ではデスクトップアプリの GA とクラウド上で動く常時稼働エージェントが提供されています。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)