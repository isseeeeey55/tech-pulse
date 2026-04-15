---
title: "【AWS】2026/04/16 のアップデートまとめ"
date: 2026-04-16T08:01:56+09:00
draft: false
tags: ["aws", "interconnect", "multicloud", "payment-cryptography", "quick", "quicksight", "ec2", "blackwell", "govcloud"]
categories: ["AWS Updates"]
summary: "AWS Interconnect - multicloud の GA、AWS Payment Cryptography の São Paulo 展開、Amazon Quick (QuickSight) の Sheet Tooltips、EC2 P6-B300 の GovCloud (US-East) 展開の 4 件を紹介します。"
---

![](/images/aws-updates-20260416/header.png)

## はじめに

2026年4月16日のAWSアップデートは4件です。目玉は **AWS Interconnect - multicloud の GA**。他クラウドプロバイダとの専用プライベート接続を AWS 側のマネージドサービスとして組める新しい選択肢です。加えて、AWS Payment Cryptography の São Paulo 展開、Amazon Quick (QuickSight) の Sheet Tooltips、EC2 P6-B300 の GovCloud (US-East) 展開の 3 件を取り上げます。

## 注目アップデート深掘り

### AWS Interconnect - multicloud — 他クラウドとのプライベート接続が GA

![AWS Interconnect - multicloud の位置づけ](/images/aws-updates-20260416/interconnect-multicloud.png)

**AWS Interconnect - multicloud** は、他のパブリッククラウドとの間にプライベートかつ高帯域の専用接続を、AWS 側からマネージドサービスとして張れるようにする新サービスで、今回 GA しました。

公式が発表している主要ポイントは次の通りです（公式の記述を超えた解釈は避けています）。

| 項目 | 内容 |
|---|---|
| 対応クラウド（ローンチ時） | **Google Cloud** のみ |
| 対応予定 | Microsoft Azure / Oracle Cloud Infrastructure — **2026 年後半** |
| 利用可能リージョン | **5 AWS Region**（具体的なリージョン名は未公開） |
| 無料枠 | **1 リージョンあたり 500 Mbps のローカル接続 1 本** — 2026 年 5 月から提供 |
| 連携サービス | AWS Transit Gateway / AWS Cloud WAN |

### アーキテクチャ上の位置づけ

従来、AWS から Google Cloud への専用プライベート接続を張るには、Direct Connect + コロケーション + 相手クラウド側の Interconnect / Partner Interconnect を個別に契約する構成が一般的でした。Interconnect - multicloud は、このコロケーション区間を AWS マネージドに寄せて、エッジロケーション間の物理接続をユーザーが直接扱わないで済むように設計された、というのが技術的な要点です。

接続は Transit Gateway や Cloud WAN と同じ VPC Attachment 系のリソースとして接続でき、既存のマルチ VPC / マルチリージョンのネットワーク設計にそのまま統合できます。

### 料金

リージョンあたり 500 Mbps の無料ローカル接続が 1 本（2026 年 5 月開始）。それを超える帯域は、帯域幅と地理的スコープに応じた単一料金体系が適用されます（GA 時点の詳細な料金表は公式ページを参照）。小規模なメタデータ同期や監視トラフィックは無料枠に収まるため、まず無料枠で試してから本番帯域を決める運用がしやすい設計です。

### EC2 P6-B300 — NVIDIA Blackwell Ultra 搭載、GovCloud (US-East) に展開

![P6-B300 スペック概要](/images/aws-updates-20260416/p6-b300-spec.png)

EC2 **P6-B300** が AWS GovCloud (US-East) で利用できるようになりました。搭載される GPU は **8× NVIDIA Blackwell Ultra** で、1 インスタンスあたりのリソースは次の通りです。

- **GPU 数**: 8× NVIDIA Blackwell Ultra
- **GPU メモリ**: 2.1 TB（高帯域幅）
- **EFA ネットワーク**: 6.4 Tbps
- **ENA スループット（専用）**: 300 Gbps
- **システムメモリ**: 4 TB

前世代比で **ネットワーク帯域幅 2 倍、GPU メモリ 1.5 倍、GPU TFLOPS 1.5 倍** という数字で、兆パラメータ級のモデル学習・推論を想定した構成です。

> **EFA（Elastic Fabric Adapter）とは？**
> EC2 で低レイテンシ・高帯域の分散学習ノード間通信を実現するためのネットワークインターフェースです。通常の ENA（Elastic Network Adapter）とは別系統で、MPI や NCCL などの集合通信ライブラリから直接呼べる OS-bypass 通信パスを提供します。LLM 学習時のノード間 AllReduce 性能を出すために必須の部品です。

現時点で P6-B300 が利用できるのは **US West (Oregon)** と **AWS GovCloud (US-East)** の 2 リージョン。GovCloud 側は政府機関や規制業界の LLM トレーニングワークロードの主要な選択肢になります。

### Amazon Quick (QuickSight) — Sheet Tooltips で詳細ビューをホバー表示

Amazon Quick 配下の QuickSight（AWS の BI プロダクト）に、**Sheet Tooltips** が追加されました。従来のテキスト中心のツールチップと異なり、**専用のツールチップシートを作成して、そこにビジュアル・テキスト・画像を自由レイアウトで配置**できる仕組みです。

> **Amazon Quick とは？**
> AWS の新しいデータ + 生成 AI プロダクトの名前で、従来の QuickSight を含む BI/分析・AI 機能を統合したブランドです。この記事の Sheet Tooltips は Amazon Quick 配下の QuickSight コンポーネントで提供される機能です。

動作のポイント:

- ビューアがビジュアル上のデータポイントにホバーすると、ツールチップシートが表示される
- ツールチップシートは**ソースビジュアルのフィルタをすべて継承**、さらにホバーしたデータポイント固有のフィルタが自動で追加適用される
- **テーブル / ピボットテーブル** もサポート対象
- **インタラクティブシート専用**（埋め込みダッシュボードでも利用可）

使いどころは、運用メトリクスの詳細ドリルダウンで「別画面に遷移せずその場で詳細を見せたい」ケース。たとえばサービスごとのエラー率を示す棒グラフで、特定サービスにホバーすると直近 1 時間の時系列グラフ・関連 CloudWatch アラームの一覧・担当チームの連絡先を 1 画面でまとめて見せる、といった設計が組めます。

## SRE視点での活用ポイント

**AWS Interconnect - multicloud** は、マルチクラウド監視基盤の観点で効く変更です。AWS で CloudWatch、Google Cloud で Cloud Monitoring を使っていて、両方のメトリクスを 1 か所に集約している環境では、現状パブリックインターネット経由でログやメトリクスを送っているケースが多いです。Interconnect - multicloud を通すと経路が AWS のプライベート側に寄るので、転送レイテンシとデータ漏洩リスクの両方が下がります。無料 500 Mbps 枠で PoC を組んでから判断できるので、検証コストは低めです。Azure / OCI 側は 2026 年後半なので、現時点で即効性があるのは Google Cloud 連携のみです。

**P6-B300 の GovCloud 展開**は、規制業界（政府機関・医療・金融など）で LLM 学習を GovCloud の中で完結させたいチームに直接効きます。EFA 6.4 Tbps + GPU メモリ 2.1 TB のスペックは、従来 US 商用リージョンでしか選べなかったサイズの選択肢を GovCloud に広げるもので、コンプライアンス要件を満たしながらフロンティアモデル級の訓練を回せるようになります。

**QuickSight Sheet Tooltips** は、運用ダッシュボードの「クリックで別画面に飛ばずに詳細を見せる」設計の選択肢を増やす変更です。オンコール担当者が夜間の初動トリアージで別シートを開かずにホバーだけで関連情報を取れるのが利点。ただしツールチップシートに情報を詰め込みすぎると認知負荷が上がるので、「次のアクション判断に必要な最小限」に絞る設計が無難です。

**Payment Cryptography São Paulo** は、南米（ブラジル）でカード決済系のワークロードを扱うチーム向けの純粋なリージョン追加です。PCI PIN / PCI P2PE 準拠は従来と同じで、専用 HSM を自前で持たずにクラウド上で鍵管理・暗号化操作ができる点もそのまま。該当地域にユーザーを持つ決済事業者には有用です。

## 全アップデート一覧

| # | タイトル | 概要 |
|---|---------|------|
| 1 | [AWS Interconnect - multicloud GA](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-announces-ga-AWS-interconnect-multicloud/) | 他クラウドとのプライベート接続を AWS マネージドで提供。Google Cloud 先行、Azure/OCI は 2026 後半。5 リージョン、500 Mbps 無料枠 |
| 2 | [Amazon EC2 P6-B300 が GovCloud (US-East) 対応](https://aws.amazon.com/about-aws/whats-new/2026/04/ec2-p6-b300-govcloud-us-east/) | 8× NVIDIA Blackwell Ultra / GPU メモリ 2.1 TB / EFA 6.4 Tbps / ENA 300 Gbps / システムメモリ 4 TB |
| 3 | [Amazon Quick — QuickSight Sheet Tooltips](https://aws.amazon.com/about-aws/whats-new/2026/04/quick-sheet-tooltips/) | ツールチップシートに自由配置でビジュアル/テキスト/画像を表示、フィルタ自動継承。テーブル・ピボットテーブル対応 |
| 4 | [AWS Payment Cryptography が São Paulo 対応](https://aws.amazon.com/about-aws/whats-new/2026/04/aws-payment-cryptography-south/) | 決済向けマネージド暗号化/鍵管理サービスの南米展開。PCI PIN / PCI P2PE 準拠 |

## まとめ

目玉は AWS Interconnect - multicloud の GA で、これまで「複雑すぎて諦めた」マルチクラウド専用接続の選択肢が素直に取れるようになりました。ただし現時点で即効性があるのは Google Cloud 側のみで、Azure / OCI は 2026 年後半待ちです。P6-B300 の GovCloud 展開は規制業界の LLM 学習チームに直接効く拡張、QuickSight Sheet Tooltips は運用ダッシュボード設計の幅を広げる地味に使える機能追加、Payment Cryptography São Paulo は該当地域にユーザーを持つ決済チーム向けのリージョン追加、という位置付けです。
