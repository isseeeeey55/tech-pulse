---
title: "【AWS】2026/03/24 のアップデートまとめ"
tags: ["aws", "polly", "healthimaging", "tts", "streaming"]
date: "2026-03-24T08:00:00+09:00"
categories: ["AWS Updates"]
summary: "Amazon PollyのGenerative TTSエンジン大幅拡張（新音声10個・Bidirectional Streaming API）と、AWS HealthImagingのロンドンリージョン対応の2件。"
draft: false
---

![](/tech-pulse/images/aws-updates-20260324/header.png)

## はじめに

2026年3月24日のAWSアップデートは2件。Amazon PollyのGenerative TTSエンジンにBidirectional Streaming APIが追加され、AWS HealthImagingがロンドンリージョンで利用可能になりました。

## 注目アップデート深掘り

### Amazon Polly Generative TTS の大幅機能拡張

Amazon Pollyに10の新しい高表現力音声が追加され、2つの新リージョン（ロンドン、カナダ中部）がサポートされました。さらに、LLMの出力をリアルタイムで音声合成するBidirectional Streaming APIが導入されています。

**新音声のテスト**

新音声は7つのロケール（英語4地域、フランス語、イタリア語、ドイツ語）をカバーしています。AWS CLIで試す場合：

```bash
# Generativeエンジンで新音声をテスト
$ aws polly synthesize-speech \
    --output-format mp3 \
    --voice-id Matthew \
    --text "Hello, I'm excited to demonstrate the new expressive capabilities of Amazon Polly's generative TTS engine." \
    --engine generative \
    output.mp3
```

**Bidirectional Streaming APIの技術的革新**

従来の方式では、LLMが完全にレスポンスを生成してから音声合成を開始していました。新しいBidirectional Streaming APIでは、部分的なテキストを受け取り次第、即座に音声生成を開始できます。

以下は概念的な実装イメージです（APIの正確なインターフェースは[AWS公式ドキュメント](https://docs.aws.amazon.com/polly/)を参照してください）：

```python
import boto3

def synthesize_with_generative_engine(text: str, voice_id: str = "Matthew") -> bytes:
    """Generativeエンジンでの音声合成"""
    polly_client = boto3.client("polly")

    response = polly_client.synthesize_speech(
        Engine="generative",
        OutputFormat="mp3",
        Text=text,
        VoiceId=voice_id,
    )

    return response["AudioStream"].read()
```

Bidirectional Streaming APIを使うと、LLMが最初のトークンを生成した時点から音声合成が並行して走るため、ユーザーが音声を聞き始めるまでの待ち時間を大幅に短縮できます。

**Terraformでの権限設定例**

```hcl
resource "aws_iam_role_policy" "polly_generative_policy" {
  name = "polly-generative-policy"
  role = aws_iam_role.app_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "polly:SynthesizeSpeech",
          "polly:StartSpeechSynthesisTask",
          "polly:DescribeVoices"
        ]
        Resource = "*"
      }
    ]
  })
}
```

### AWS HealthImaging がロンドンリージョンで利用可能に

> **AWS HealthImagingとは？**
> 医療画像（DICOM形式のCTスキャン、MRIなど）をクラウド上で保存・検索・分析するためのマネージドサービスです。従来のオンプレミスPACS（医療画像管理システム）の代替として、ストレージコスト削減とAI/ML連携を実現します。

医療画像データの管理・処理サービスであるAWS HealthImagingが、ヨーロッパ（ロンドン）リージョンで利用可能になりました。これにより、欧州の医療機関がデータ主権要件を満たしつつクラウドを活用できるようになります。

**データ主権とコンプライアンス**

欧州の医療データはGDPRに加え、各国の医療データ規制の対象です。ロンドンリージョンの追加により、英国の医療機関がデータをUK域内に保持したままHealthImagingを利用できるようになりました。

**Terraformでの構成例**

```hcl
resource "aws_medical_imaging_datastore" "medical_images" {
  datastore_name = "hospital-imaging-store"

  tags = {
    Environment = "production"
    Region      = "eu-west-2"
    Compliance  = "GDPR"
  }
}
```

既存のus-east-1やap-southeast-2のデータストアとは別に、欧州向けのデータストアをロンドンリージョンに構築することで、地理的な冗長性とコンプライアンスを両立できます。

## SRE視点での活用ポイント

**Polly Bidirectional Streamingの運用考慮事項**

音声AIアプリケーションでBidirectional Streaming APIを導入する場合、従来のバッチ処理とは異なる監視が必要です。ストリーム中断時の復旧手順や、部分的な音声出力の品質検証を含めたランブックの更新を検討してください。CloudWatchメトリクスで音声合成のレイテンシを監視し、ユーザー体験の品質を定量的に管理できます。

新しいリージョン（ロンドン、カナダ中部）の追加により、地理的な冗長性を考慮した音声サービスの設計も可能になりました。Generative TTSは従来のNeural TTSよりも高品質ですが処理コストも高くなるため、ユースケースに応じたエンジン選択がコスト最適化の鍵です。

**HealthImagingのリージョン展開**

医療画像系のワークロードを運用している場合、ロンドンリージョンの追加はDR設計の選択肢を広げます。既存リージョンとの間でデータレプリケーションを構成する際は、転送コストとレイテンシのバランスを考慮してください。

## 全アップデート一覧

| サービス | アップデート内容 | 概要 |
|----------|------------------|------|
| [Amazon Polly](https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-polly-expands-tts-new-voices-and-bidirectional-streaming/) | Generative TTSエンジンの大幅機能拡張 | 10の新しい高表現力音声の追加（7ロケール対応）、2つの新リージョンサポート、LLMとリアルタイム統合可能なBidirectional Streaming API導入 |
| [AWS HealthImaging](https://aws.amazon.com/about-aws/whats-new/2026/03/aws-healthimaging-europe-london/) | ヨーロッパ（ロンドン）リージョン対応 | 医療画像データの管理・処理サービスがロンドンリージョンで利用可能になり、欧州の医療機関でのデータ主権要件に対応 |

## まとめ

PollyのBidirectional Streaming APIは、対話型AIアプリケーションの音声レイテンシ改善に直結するアップデートです。LLMと音声合成を組み合わせている環境では検討の価値があります。HealthImagingのロンドンリージョン対応は、欧州で医療画像ワークロードを扱っている場合にデータ主権とDR設計の両面でプラスになります。
