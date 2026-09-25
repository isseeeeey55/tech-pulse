---
title: "【New Relic】2026/09/25 のアップデートまとめ"
date: 2026-09-25T08:00:55+09:00
draft: false
tags: ["newrelic", "infrastructure-agent", "security"]
categories: ["New Relic Updates"]
summary: "2026/09/25 のNew Relicアップデートまとめ"
---

![](/images/newrelic-updates-20260925/header.png)

# New Relic Infrastructure Agent 1.80.5 リリースノートまとめ

## はじめに

New Relic Infrastructure Agent 1.80.5 が 2026年9月24日（GitHub リリース日、UTC）に公開されました。本リリースには5件の変更が含まれ、そのうち1件は **権限昇格（privilege escalation）バグの修正** です。`integration_user` で実行ユーザーを制限した（サンドボックス化した）インテグレーションが、root 権限の子プロセスを起動できてしまう問題が修正されました。インテグレーションの実行ユーザーを制限している環境では、優先して確認すべきリリースです。

---

## 注目アップデート深掘り

### Infrastructure Agent 1.80.5: サンドボックス化したインテグレーションの権限昇格バグを修正

GitHub リリースの記載は次の通りです。

> fix: privilege escalation bug that allowed sandboxed integrations to spawn root children

**何が問題だったのか**

Infrastructure Agent の v4 インテグレーション設定では、`integration_user` でインテグレーションを実行する OS ユーザーを指定できます。一方、インテグレーションは実行中に「コマンドリクエスト」や「設定リクエスト」を出力し、エージェントに別のコマンド（子インテグレーション）を起動させることができます。

修正前は、こうして起動される子プロセスに親インテグレーションの `integration_user` が引き継がれていませんでした。そのため、実行ユーザーを制限したインテグレーションでも、リクエスト経由で制限のない（root の）子プロセスを起動できる状態でした。

**どう修正されたのか**

修正 PR（[#2338](https://github.com/newrelic/infrastructure-agent/pull/2338)）では次の2点が変更されています。

- コマンドリクエストから生成される子インテグレーションは、常に親インテグレーションのユーザーを引き継ぐ
- 設定リクエストで出力された子の設定が別のユーザーを指定していても、親に `integration_user` が設定されていれば親のユーザーが優先される

これにより、実行ユーザーを制限したインテグレーションが、自分の子プロセスの権限を引き上げることはできなくなりました。

**影響を受ける構成**

`integration_user` でインテグレーションの実行ユーザーを制限し、かつそのインテグレーションがコマンドリクエストや設定リクエストを使う構成が該当します。実行ユーザーを制限している環境では、1.80.5 以降へのアップグレードを検討してください。

**アップグレード手順の例**

パッケージマネージャーで `newrelic-infra` パッケージを更新します。RHEL 系（Amazon Linux を含む）の場合：

```bash
$ sudo yum update newrelic-infra -y
```

Ubuntu / Debian 系の場合：

```bash
$ sudo apt-get update
$ sudo apt-get install --only-upgrade newrelic-infra -y
```

更新後、バージョンを確認します：

```bash
$ newrelic-infra -version
```

### その他の変更

1.80.5 には上記の修正のほかに、次の定例的な更新が含まれます。いずれも GitHub リリース上は `chore` 扱いで、セキュリティ修正としての記載はありません。

- Agent Control の型定義を v1.0.0 に更新
- 依存関係の `newrelic/nrjmx` を v2.15.0 に更新
- 依存関係の crypto を v0.57.0 に更新
- 同梱の OHI（On-Host Integration）のバージョンを更新

---

## SRE視点での活用ポイント

- **自環境が該当するか確認する**: インテグレーション設定ファイルで `integration_user` を使っているかを確認します。使っていれば今回の修正の対象です
- **子プロセスの実行ユーザーが変わる点に注意する**: 修正後は、制限したインテグレーションから起動される子プロセスも親と同じユーザーで動きます。これまで子プロセスが root で動くことを前提に動作していたインテグレーションは、アップグレード後に権限不足で失敗する可能性があるため、ステージング環境で動作を確認してから展開します
- **段階的に展開する**: 一部のホストから先にアップグレードし、インテグレーションのデータが New Relic 上で途切れていないことを確認してから全体に広げます

---

## 全アップデート一覧

| カテゴリ | 対象 | 概要 | リンク |
|---------|------|------|--------|
| Security Fix | Infrastructure Agent 1.80.5 | サンドボックス化（`integration_user` で実行ユーザーを制限）したインテグレーションが root の子プロセスを起動できた権限昇格バグを修正 | [詳細](https://github.com/newrelic/infrastructure-agent/releases/tag/1.80.5) |
| Chore | Infrastructure Agent 1.80.5 | Agent Control 型定義 v1.0.0、nrjmx v2.15.0、crypto v0.57.0、同梱 OHI の更新 | [詳細](https://github.com/newrelic/infrastructure-agent/releases/tag/1.80.5) |

---

## まとめ

Infrastructure Agent 1.80.5 の主な変更は、`integration_user` で実行ユーザーを制限したインテグレーションが root の子プロセスを起動できた権限昇格バグの修正です。修正後は子プロセスが親のユーザーを引き継ぐため、制限したユーザーでインテグレーションを動かしている環境では、アップグレード後にインテグレーションが期待通り動作するかを確認してください。

---

## 📚 New Relicをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17631627%2F%3Fl-id%3Dsearch-c-item-text-01" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">New Relic実践入門 第2版 オブザーバビリティの基礎と実現（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [New Relic 公式ドキュメント](https://docs.newrelic.com/)