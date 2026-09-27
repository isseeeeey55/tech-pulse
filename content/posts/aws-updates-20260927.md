---
title: "【AWS】2026/09/27 のアップデートまとめ"
date: 2026-09-27T08:02:12+09:00
draft: false
tags: ["aws", "ec2", "ses", "end-user-messaging", "mcp"]
categories: ["AWS Updates"]
summary: "2026/09/27 のAWSアップデートまとめ"
---

# 直近の AWS アップデート 4 件を紹介：MCP Server 対応 AI スキルと新世代インスタンスの拡大

![](/images/aws-updates-20260927/header.png)

## はじめに

今回は、直近で発表された 4 件の AWS アップデートを紹介します。内容は 2 つのトピックに分かれます。1 つ目は、AWS End User Messaging と Amazon SES が AWS MCP Server 向けに公開した AI エージェントスキルで、AI コーディングエージェントに自然言語で依頼してメッセージの構築・送信を進められるようになりました。2 つ目は、AWS 専用のカスタム Intel Xeon 6 プロセッサを搭載した EC2 インスタンス（C8i/C8i-flex、R8i/R8i-flex、M8i/M8i-flex）が AWS European Sovereign Cloud（ドイツ）リージョンで利用可能になったというものです。前世代の Intel ベースインスタンスと比べて最大 15% の価格性能比向上と 2.5 倍のメモリ帯域幅をうたっています。

本記事では「MCP Server 向け AI エージェントスキル」と「Intel Xeon 6 搭載 EC2 インスタンス」を中心に、SRE の視点での活用ポイントを整理します。

---

## 注目アップデート深掘り

### AWS MCP Server 向け AI エージェントスキルの登場

#### 自然言語でメッセージング設定を進める背景

告知によると、これまでメッセージング関連のタスクを完了するには、複数のドキュメントページと管理コンソールの画面を行き来する必要がありました。今回のスキルは、送信元 ID の検証、ブランド化された RCS（Rich Communication Services）エージェントの構築、本番メールの送信といったタスクについて、ステップバイステップの検証済みガイダンスをエージェントに提供します。

対応する AI コーディングエージェントとして、Claude Code、Codex、Cursor、Kiro が挙げられています。

#### Model Context Protocol（MCP）とは

MCP（Model Context Protocol）は、AI エージェントが外部のツールやサービスと連携するための標準化されたプロトコルです。AWS MCP Server はこの仕組みで AI エージェントから AWS を扱うためのサーバーで、今回のスキルはその上にメッセージング領域のガイダンスを追加するものです。

#### セットアップ方法

まず AWS MCP Server をエージェントに接続します。導入方法はエージェントによって異なります。

- **Claude Code / Codex / Cursor**：**aws-core プラグイン**が、サーバーと厳選されたスキル群をまとめて 1 回でインストールします
- **Kiro やその他のエージェント**：MCP 設定ファイルにサーバーを追加します

そのうえで、使いたいチャネル（SES、SMS/RCS、WhatsApp）のスキルを追加すると、エージェントがガイドできる状態になります。各スキルの内容とインストール方法は、チャネルごとのエージェントセットアップガイド（End User Messaging SMS/RCS、End User Messaging WhatsApp、Amazon SES）にまとめられています。

#### 告知で示されている利用例

- **Amazon SES**：送信元 ID を検証し、最初の本番メールを送信する
- **AWS End User Messaging（RCS）**：ブランド化された RCS エージェントを構築し、カードやボタン付きのリッチメッセージを自分宛てに送信する

告知は、これによりドキュメントを手作業で探したりコンソール画面を切り替えたりする必要がなくなり、自然言語のコマンドでメッセージングのワークフローを完了できるとしています。WhatsApp については専用のセットアップガイドが用意されていますが、告知本文に具体的なタスク例は挙げられていません。

---

### Intel Xeon 6 搭載の EC2 インスタンス群

#### 性能の数値（各告知の記載）

C8i/C8i-flex、R8i/R8i-flex、M8i/M8i-flex は、AWS 専用のカスタム Intel Xeon 6 プロセッサを搭載しています。告知では、クラウド上の同等の Intel プロセッサの中で最高の性能と最速のメモリ帯域幅を提供するとしています。3 ファミリー共通で、**前世代の Intel ベースインスタンス比**で最大 15% の価格性能比向上と 2.5 倍のメモリ帯域幅がうたわれています。

7 世代との比較とワークロード別の数値は、ファミリーごとに告知の記載が異なります。

| ファミリー | 7 世代比の性能 | ワークロード別（7 世代比） |
|-----------|---------------|---------------------------|
| C8i/C8i-flex | C7i/C7i-flex 比で最大 20% 向上 | NGINX 最大 60%、AI 深層学習レコメンデーションモデル 最大 40%、Memcached 35% 高速 |
| R8i/R8i-flex | R7i 比で 20% 向上 | PostgreSQL 最大 30%、NGINX 最大 60%、AI 深層学習レコメンデーションモデル 最大 40% 高速 |
| M8i/M8i-flex | M7i/M7i-flex 比で最大 20% 向上 | PostgreSQL 最大 30%、NGINX 最大 60%、AI 深層学習レコメンデーションモデル 最大 40% 高速 |

#### 各インスタンスタイプの特徴と使い分け

**C8i/C8i-flex（コンピューティング最適化）**

C8i-flex は large から 16xlarge までの一般的なサイズで提供され、ウェブ/アプリケーションサーバ、データベース、キャッシュ、Apache Kafka、Elasticsearch、エンタープライズアプリケーションなど、コンピューティング集約型ワークロードの大半で価格性能を得る最も簡単な方法と位置づけられています。コンピューティングリソースをフルに使い切らないアプリケーションの第一候補です。C8i は、最大級のインスタンスサイズや継続的な高 CPU 使用率を必要とするワークロード向けで、2 つのベアメタルサイズと新しい 96xlarge を含む 13 サイズが用意されています。

**R8i/R8i-flex（メモリ最適化）**

R8i-flex は AWS 初のメモリ最適化 Flex インスタンスで、large から 16xlarge までのサイズでメモリ集約型ワークロードの大半を対象とします。R8i は最大級のサイズや継続的な高 CPU 使用率を必要とするメモリ集約型ワークロード向けで、2 つのベアメタルサイズと 96xlarge を含む 13 サイズです。R8i は SAP 認定を取得しており、142,100 aSAPS を達成しています。告知によると、これはオンプレミスとクラウドの同等マシンの中で最高の値です。

**M8i/M8i-flex（汎用）**

M8i-flex は large から 16xlarge までのサイズで、ウェブ/アプリケーションサーバ、マイクロサービス、小〜中規模のデータストア、仮想デスクトップ、エンタープライズアプリケーションなどの汎用ワークロードを対象とします。M8i は最大級のサイズや継続的な高 CPU 使用率を必要とする汎用ワークロード向けで、SAP 認定を取得しており、2 つのベアメタルサイズと 96xlarge を含む 13 サイズで提供されます。

#### 購入オプション

C8i/C8i-flex と R8i/R8i-flex の告知では、Savings Plans、オンデマンド、スポットの各購入方法が挙げられています（M8i/M8i-flex の告知には購入方法の記載はありません）。

---

## SRE 視点での活用ポイント

### MCP Server AI スキルの運用活用

新しい通知チャネルを追加する場面では、送信元 ID の検証や RCS エージェントの構築といった初期設定の手順をエージェントが案内してくれるため、手動でドキュメントを参照する工程を減らせます。設定手順をエージェントとの対話で確認しながら進めれば、その過程をランブック作成の下書きとして残すこともできます。

一方で、本番アカウントでの利用には慎重さが必要です。エージェントが提案する操作内容を必ず確認し、エージェントに渡す IAM 権限は必要最小限に絞ってください。まずは開発環境や検証用アカウントで挙動を確認し、段階的に取り入れるのが安全です。

### 新世代インスタンスの移行判断

告知でワークロード別の数値が示されているのは NGINX、PostgreSQL（R8i/M8i）、Memcached（C8i）、AI 深層学習レコメンデーションモデルです。これらを運用している場合でも、数値は「最大」値なので、パイロット環境で自分のワークロードの性能とコストを測定してから判断するのが現実的です。

flex バリアントは、コンピューティングリソースをフルに使い切らないアプリケーション向けと位置づけられています。継続的に高い CPU 使用率が続くワークロードや、16xlarge を超えるサイズが必要なワークロードでは、通常の C8i/R8i/M8i が候補になります。

移行時には、既存の CloudWatch アラームの閾値や Auto Scaling ポリシーが新しいインスタンスタイプの性能特性に合っているかを見直してください。Terraform や CloudFormation でインフラを管理している場合は、インスタンスタイプの変更をコードレビューを通して反映し、ロールバック手順も用意しておくと安心です。

なお、今回の提供開始は AWS European Sovereign Cloud（ドイツ）リージョンが対象です。同リージョンを利用している、または利用を検討している組織にとって、選べるインスタンスの世代が増えたことになります。

---

## 全アップデート一覧

| タイトル | 概要 | リンク |
|---------|------|--------|
| AWS End User Messaging and Amazon SES now offer AI agent skills for the AWS MCP Server | AWS End User Messaging と Amazon SES が MCP Server 向けの AI エージェントスキルを提供開始。Claude Code、Codex、Cursor、Kiro などの AI コーディングエージェントと連携し、自然言語でメッセージングタスクを実行可能に。送信元 ID の検証、ブランド化された RCS エージェントの構築、本番メールの送信などをステップバイステップでガイド。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/aws-messaging-ses-ai-skills-mcp-server/) |
| Amazon EC2 C8i and C8i-flex instances are now available in additional regions | C8i/C8i-flex インスタンスが AWS European Sovereign Cloud（ドイツ）で利用可能に。カスタム Intel Xeon 6 プロセッサ搭載で、前世代 Intel ベース比で最大 15% の価格性能比向上、2.5 倍のメモリ帯域幅。C7i/C7i-flex 比で NGINX 最大 60%、AI 深層学習レコメンデーションモデル最大 40%、Memcached 35% 高速。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/c8i-c8i-flex-thf-september-2026/) |
| Amazon EC2 R8i and R8i-flex instances are now available in additional regions | R8i/R8i-flex インスタンスが AWS European Sovereign Cloud（ドイツ）で利用可能に。メモリ最適化インスタンスとして前世代 Intel ベース比で最大 15% の価格性能比向上、2.5 倍のメモリ帯域幅。R7i 比で PostgreSQL 最大 30%、NGINX 最大 60%、AI 深層学習レコメンデーションモデル最大 40% 高速。R8i は SAP 認定で 142,100 aSAPS を達成。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/ec2-r8i-r8i-flex-thf/) |
| Amazon EC2 M8i and M8i-flex instances are now available in additional regions | M8i/M8i-flex インスタンスが AWS European Sovereign Cloud（ドイツ）で利用可能に。汎用インスタンスとして前世代 Intel ベース比で最大 15% の価格性能比向上、2.5 倍のメモリ帯域幅。M7i/M7i-flex 比で PostgreSQL 最大 30%、NGINX 最大 60%、AI 深層学習レコメンデーションモデル最大 40% 高速。M8i は SAP 認定取得。 | [詳細](https://aws.amazon.com/about-aws/whats-new/2026/09/amazon-ec2-m8i-m8i-flex-thf/) |

---

## まとめ

今回紹介した 4 件のアップデートは、メッセージング領域での AI エージェント連携と、Intel Xeon 6 搭載 EC2 インスタンスの提供リージョン拡大の 2 つです。

MCP Server 向けの AI エージェントスキルは、SES と End User Messaging の初期設定や送信手順を、Claude Code・Codex・Cursor・Kiro などから自然言語で進められるようにするものです。

C8i/R8i/M8i（および各 flex）の AWS European Sovereign Cloud（ドイツ）での提供開始により、同リージョンでも前世代 Intel ベース比で最大 15% の価格性能比向上と 2.5 倍のメモリ帯域幅を持つインスタンスが選べるようになりました。

SRE の視点では、AI エージェントスキルは開発環境での検証から始め、新世代インスタンスはパイロット環境での性能測定を経て本番適用を判断する、という段階的な進め方をおすすめします。

---

## 📚 AWSをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17586246%2F%3Fscid%3Daf_pc_etc%26sc2id%3Daf_103_0_10000645%26rafcid%3Dwsc_i_is_6d64a945-e1c8-4754-a103-b4ec90d7cfa6" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">AWS認定ソリューションアーキテクト - アソシエイト 完全攻略（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [AWS公式ドキュメント](https://docs.aws.amazon.com/)