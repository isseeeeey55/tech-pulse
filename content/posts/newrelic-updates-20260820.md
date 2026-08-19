---
title: "【New Relic】2026/08/20 のアップデートまとめ"
date: 2026-08-20T08:01:11+09:00
draft: true
tags: ["newrelic", "infrastructure-agent", "security", "azure", "secrets-management", "cve"]
categories: ["New Relic Updates"]
summary: "2026/08/20 のNew Relicアップデートまとめ"
---

# New Relic Infrastructure Agent 1.80.0 — セキュリティ強化とマルチクラウド対応の重要アップデート

## はじめに

2026年8月20日、New Relic Infrastructure Agentのバージョン1.80.0がリリースされました。今回のアップデートは1件ですが、**セキュリティ脆弱性の修正とマルチクラウド環境でのシークレット管理機能の強化**という、SREにとって見逃せない重要な内容を含んでいます。

特に注目すべきは、特権昇格に関わる脆弱性の修正（#2306）と、Azure Key Vaultへの新規対応です。本番環境でInfrastructure Agentを運用しているチームにとって、早期のアップグレード計画が推奨される内容となっています。また、埋め込みOn-Host Integration（OHI）の依存関係に含まれるCVEの修正により、DockerコンテナやPrometheusメトリクスの監視におけるセキュリティリスクも低減されています。

## 注目アップデート深掘り

### セキュリティ脆弱性修正と本番環境への影響

今回のリリースで最も優先度が高いのは、特権昇格（Privilege Escalation）に関連する脆弱性の修正です。リリースノートには`#2306`として記載されており、Infrastructure Agentが動作するホスト上でのセキュリティリスクを低減する重要なパッチが含まれています。

**なぜこのアップデートが重要なのか：**  
Infrastructure Agentは通常、ホストのシステムメトリクスやプロセス情報を収集するために、ある程度の権限で動作します。特権昇格の脆弱性が存在すると、悪意ある攻撃者やマルウェアがこの脆弱性を悪用し、Agent実行権限から更に高い権限（rootなど）を取得するリスクがあります。本番環境では、監視エージェントが全ホストに展開されているため、一つの脆弱性が広範囲に影響を及ぼす可能性があります。

**SREの日常業務への影響：**  
セキュリティ監査や脆弱性スキャンの結果に基づき、早期のアップグレードが求められます。特にコンプライアンス要件の厳しい環境（金融、医療、PCI-DSS対象システムなど）では、CVE修正を含むアップデートは優先的に適用する必要があります。また、埋め込みOHI（DockerやPrometheusなど）のCVE修正も含まれているため、コンテナ監視やカスタムメトリクス取得を行っている環境では、これらの統合機能におけるリスクも同時に低減されます。

アップグレードは、パッケージマネージャーを通じて実施するのが一般的です。例えばAWS EC2のAmazon Linux環境では以下のように実施します：

```bash
$ sudo yum update newrelic-infra -y
```

Ubuntu/Debian環境の場合：

```bash
$ sudo apt-get update
$ sudo apt-get install --only-upgrade newrelic-infra -y
```

アップグレード後は、エージェントが正常に再起動し、メトリクスの送信が継続されているかを確認します：

```bash
$ sudo systemctl status newrelic-infra
$ sudo journalctl -u newrelic-infra -n 50
```

New Relic UIのInfrastructure > Hosts画面で、該当ホストのAgent Versionが`1.80.0`に更新されていることを確認することも重要です。

### Azure Key Vault対応によるマルチクラウド環境のシークレット管理強化

もう一つの重要な機能追加は、Azure Key Vaultへの対応です。これまでInfrastructure Agentは、AWS Secrets Managerを利用した認証情報の動的取得に対応していましたが、今回のアップデートでAzure環境でも同様の仕組みが利用可能になりました。

**なぜこのアップデートが重要なのか：**  
エンタープライズ環境では、AWSとAzureを併用するマルチクラウド構成が一般的です。Infrastructure Agentの設定ファイル内に平文で認証情報を記載することは、セキュリティ上のリスクとなります。シークレット管理サービスとの統合により、認証情報のローテーションや中央管理が可能になり、監査ログの一元化やアクセス制御の強化が実現されます。

**SREの日常業務への影響：**  
これまでAzure環境では、環境変数やファイルベースでの認証情報管理が必要でしたが、Azure Key Vaultとの統合により、AWS環境と同様の運用フローを適用できるようになります。例えば、New RelicのLicense KeyやカスタムIntegrationで利用するAPIキーをKey Vaultに格納し、Infrastructure Agentがそれを動的に取得する構成が可能になります。これにより、Terraform/Ansible等のIaCツールでエージェント設定を管理する際に、シークレットを分離して管理できるため、GitOpsのベストプラクティスに沿った運用が実現します。

具体的な設定方法の詳細はリリースノートに記載されていませんが、既存のAWS Secrets Manager連携と同様の構成が期待されます。シークレット参照形式でKey Vault URIを指定する形式が想定され、Agentが起動時またはリロード時にAzure認証を通じてシークレットを取得する仕組みになっているものと考えられます。

## SRE視点での活用ポイント

今回のアップデートは、監視機能そのものの拡張よりも、**運用基盤のセキュリティと信頼性を高める**内容が中心です。SREとして押さえておくべきポイントは以下の通りです。

**セキュリティ対応の優先順位付け：**  
特権昇格の脆弱性修正は、本番環境で稼働する全ホストに影響します。まずはステージング環境で動作確認を行い、既存のカスタムIntegrationやflex設定に問題がないことを確認した上で、段階的に本番環境へ展開することを推奨します。CanaryデプロイやBlue-Greenデプロイの手法を用いることで、リスクを最小化できます。

**マルチクラウド環境でのシークレット管理標準化：**  
Azure Key Vault対応により、AWSとAzureで統一されたシークレット管理のポリシーとワークフローを策定できるようになります。これは、複数クラウドを跨ぐ監視設定の標準化や、DevOpsチーム間での運用手順の統一に寄与します。Key VaultやSecrets Managerへのアクセスログを監査ログとして活用することで、コンプライアンス要件への対応も強化されます。

**依存関係の脆弱性管理：**  
埋め込みOHI（DockerやPrometheusなど）の依存関係に含まれるCVEが修正されているため、コンテナ監視や外部メトリクス連携を利用している環境では、この機会に合わせて関連する設定やダッシュボードの見直しも検討すべきです。脆弱性スキャンツール（Trivy、Grypeなど）でAgentのバイナリやパッケージを定期的にスキャンし、既知の脆弱性が残っていないことを確認する運用も有効です。

**アップグレード時の注意点：**  
Infrastructure Agentのアップグレードは通常、ダウンタイムなしで実施できますが、エージェントの再起動が伴うため、数秒〜数十秒の監視データ欠損が発生する可能性があります。クリティカルなアラート条件が設定されている場合、アップグレードタイミングをメンテナンスウィンドウやトラフィックの少ない時間帯に調整することを推奨します。また、Auto Scaling Groupやコンテナオーケストレーション環境では、AMIやコンテナイメージに最新バージョンのAgentを組み込み、新規起動インスタンスが自動的に最新版を利用するようにしておくことも重要です。

> **Note:** Infrastructure Agentは、New RelicのホストベースおよびOn-Host Integrationの監視機能を提供するエージェントソフトウェアです。Linux、Windows、各種クラウド環境で動作し、システムメトリクスやプロセス情報を収集してNew Relicプラットフォームに送信します。

## 全アップデート一覧

| カテゴリ | 対象 | 概要 | リンク |
|---------|------|------|--------|
| Infrastructure | Infrastructure Agent 1.80.0 | 特権昇格脆弱性の修正（#2306）、Azure Key Vault対応による認証情報管理の強化、埋め込みOHIの依存関係CVE修正（Docker、Prometheus等） | [詳細](https://github.com/newrelic/infrastructure-agent/releases/tag/1.80.0) |

## まとめ

今回のInfrastructure Agent 1.80.0は、新機能の追加よりも**セキュリティとマルチクラウド対応の強化**に重点を置いたリリースとなっています。特権昇格脆弱性の修正は、本番環境での早期適用が強く推奨される内容であり、SREチームとしては計画的なアップグレード作業を優先すべきです。

また、Azure Key Vaultへの対応により、AWS環境と同様のシークレット管理フローをAzure環境でも適用できるようになったことは、マルチクラウド戦略を推進する組織にとって大きなメリットです。セキュリティ、コンプライアンス、運用効率の観点から、今回のアップデートは積極的に取り入れていくべき内容と言えるでしょう。

埋め込みOHIの脆弱性修正も含め、インフラ監視基盤全体のリスク低減に貢献する内容となっているため、ステージング環境での検証を経て、速やかに本番環境へ展開することを推奨します。

---

## 📚 New Relicをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17631627%2F%3Fl-id%3Dsearch-c-item-text-01" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">New Relic実践入門 第2版 オブザーバビリティの基礎と実現（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [New Relic 公式ドキュメント](https://docs.newrelic.com/)