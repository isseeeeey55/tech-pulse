---
title: "【New Relic】2026/05/06 のアップデートまとめ"
date: 2026-05-06T08:00:59+09:00
draft: false
tags: ["newrelic", "infrastructure-agent", "windows", "monitoring", "sre"]
categories: ["New Relic Updates"]
summary: "2026/05/06 のNew Relicアップデートまとめ"
---

![](/images/newrelic-updates-20260506/header.png)

## はじめに

New Relic から **Infrastructure Agent 1.74.3** がリリースされました（公開: 2026-05-05 12:28 UTC）。本バージョンは単一のバグ修正のみで、内容は **Infrastructure Agent 自身を Windows サービスとして登録する際の `BinaryPathName` にクォートを付与する** 修正です（PR #2230）。

参考: [infrastructure-agent v1.74.3 リリース](https://github.com/newrelic/infrastructure-agent/releases/tag/1.74.3) / [PR #2230](https://github.com/newrelic/infrastructure-agent/pull/2230)

---

## 注目アップデート深掘り

### Infrastructure Agent 1.74.3: 自身の Windows サービス登録 `BinaryPathName` 修正

#### 修正内容（リリースノート原文）

> fix: Add quotes to service BinaryPathName for paths with spaces (PR #2230)

これは Infrastructure Agent **自身**が Windows サービスとしてインストールされるときの、レジストリ上の `BinaryPathName`（実行可能ファイルへのパス）にダブルクォートを付ける修正です。**監視対象サービス側の問題ではありません**。

#### なぜクォートが必要なのか（Windows サービスの古典的な落とし穴）

Windows のサービスマネージャは `BinaryPathName` の文字列を空白区切りで解釈し、先頭部分を実行可能ファイル、後続をその引数として扱います。インストールパスにスペースが含まれている場合、たとえば次のような登録は曖昧になります:

```
C:\Program Files\New Relic\newrelic-infra\newrelic-infra.exe
```

サービスマネージャはこれを以下の順で実行ファイル候補として試します:

1. `C:\Program.exe` を `Files\New Relic\newrelic-infra\newrelic-infra.exe` という引数で起動
2. `C:\Program Files\New.exe` を後続を引数として起動
3. `C:\Program Files\New Relic\newrelic-infra\newrelic-infra.exe` を引数なしで起動

最終的に正しいパスへフォールバックして起動できることが多いものの、**同名の実行ファイルが上位に存在する場合（`C:\Program.exe` を作る既知の権限昇格テクニック含む）に意図しない実行ファイルへ解決されるリスク**があり、また一部の Windows 構成で起動失敗の原因になります。

正しい登録は次のように **実行ファイル部分をダブルクォートで囲む** ことです:

```
"C:\Program Files\New Relic\newrelic-infra\newrelic-infra.exe"
```

1.74.3 はこの登録をクォート付きに修正します。

#### 影響範囲

- 影響を受けるのは **Infrastructure Agent 自身** の Windows サービス登録です。エージェントが収集する `SystemSample` / `ProcessSample` / 他サービスの監視データには直接影響しません。
- 既に正常起動して稼働しているエージェントは、再インストール（または `BinaryPathName` を上書きするアップグレード）で修正値が書き込まれます。
- スペースを**含まない**パス（`C:\nr\` などカスタムインストール）に入れている環境は、もともと挙動的な差は生じません。レジストリ上の表現が「整合した形（クォート付き）」になる、という性格の修正です。

#### アップグレード手順

MSI による上書きインストールで完結します。`newrelic-infra.yml` は引き継がれるため設定変更は不要です。フリート全体に展開する場合は Ansible / Chef / Puppet / Intune / GPO のいずれかで通常のロールアウトを行ってください。再起動時はメトリクス収集が短時間途切れるため、ホスト単位のローリング適用を推奨します。

---

## SRE視点での活用ポイント

### 既存環境のクォート状態を確認する

該当ホストで PowerShell から以下を実行すると、現在の `BinaryPathName` が確認できます:

```powershell
Get-WmiObject -Query "SELECT Name, PathName FROM Win32_Service WHERE Name='newrelic-infra'" | Select Name, PathName
# または
sc.exe qc newrelic-infra
```

`BINARY_PATH_NAME` の実行ファイル部分が `"…"` で括られていれば修正後の状態、括られていなければ 1.74.2 以前の状態です。スペースを含むパス（`Program Files` 配下など）にエージェントを置いているフリートで、未クォートの登録が残っている場合に 1.74.3 を当てる優先度が高くなります。

### 優先度判断

- **高**: スペースを含むパスにインストール、かつ `C:\Program.exe` のような早期解決される名前のバイナリを許容してしまう環境（共有開発機など）。クォート不在は権限昇格関連のハードニング指針上もマイナス。
- **中**: スペースを含むパスにインストールしているが、ホスト管理ポリシー上 `C:\Program*` 直下に書き込み権限を持つ攻撃面が存在しない通常の本番ホスト。
- **低**: スペースを含まない独自パスにインストールしているフリート。実害は出ていない。

### ロールアウト

マイナーアップデートのため通常のローリング適用で問題ありません。MSI 上書きで `BinaryPathName` のみが整い、設定ファイルやエージェント ID は維持されます。再起動の数十秒だけメトリクスが欠ける程度なので、メンテナンスウィンドウは不要なケースが多いはずです。

### 関連設定（再点検しても損はない項目）

- エージェントがアクセスする他の Windows サービスマネージャ系の設定（`processes_enabled` など）
- Windows のサービス回復オプション（`sc.exe failure newrelic-infra ...`）の有無

---

## 全アップデート一覧

| カテゴリ | バージョン | 概要 |
|---------|-----------|------|
| Infrastructure Agent | 1.74.3 | Windows サービス登録の `BinaryPathName` にクォートを付与。スペースを含むパスでの曖昧解釈・潜在的な実行ファイル誤解決を解消（PR #2230） |

---

## まとめ

1.74.3 は単発の Windows 用バグ修正で、影響範囲は **Infrastructure Agent 自身** の Windows サービス登録だけです。スペースを含むパスにインストールしているフリートでは、`sc.exe qc newrelic-infra` の `BINARY_PATH_NAME` がクォート付きになっているかを確認した上で、通常のローリング適用で当てておくのが無難です。スペースを含まないパス運用の環境では、急いで適用する理由はありません。

---

## 📚 New Relicをもっと深く学ぶなら

<a href="//af.moshimo.com/af/c/click?a_id=5509186&p_id=54&pc_id=54&pl_id=616&url=https%3A%2F%2Fbooks.rakuten.co.jp%2Frb%2F17631627%2F%3Fl-id%3Dsearch-c-item-text-01" rel="nofollow" referrerpolicy="no-referrer-when-downgrade">New Relic実践入門 第2版 オブザーバビリティの基礎と実現（楽天ブックス）</a><img src="//i.moshimo.com/af/i/impression?a_id=5509186&p_id=54&pc_id=54&pl_id=616" width="1" height="1" style="border:none;" alt="" loading="lazy">

- [New Relic 公式ドキュメント](https://docs.newrelic.com/)