# TechTrendCollector

Qiita/Zennの技術トレンド記事を自動収集し、マークダウン形式で保存するツール。

## 機能

- Qiita トレンド記事の自動取得（RSS経由）
- Zenn トレンド記事の自動取得（RSS経由）
- 重複記事の自動スキップ
- マークダウン形式での記事保存
- GitHub Actionsによる定期実行

## セットアップ

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定（現在は不要）
cp .env.example .env
```

## 使い方

```bash
# 手動実行
python src/main.py
```

## ディレクトリ構成

```
tech_trend_collector/
├── src/
│   ├── __init__.py
│   ├── main.py              # エントリーポイント
│   ├── collectors/          # RSS取得モジュール
│   │   ├── __init__.py
│   │   ├── qiita.py
│   │   └── zenn.py
│   ├── services/            # ビジネスロジック
│   │   ├── __init__.py
│   │   └── deduplicator.py
│   ├── generators/          # 出力生成
│   │   ├── __init__.py
│   │   └── markdown.py
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       └── config.py
├── data/
│   └── history.json         # 取得履歴
├── articles/                # 生成された記事
│   └── YYYY-MM-DD/
│       └── タイトル.md
├── .github/
│   └── workflows/
│       └── daily-collect.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## GitHub Actions

毎日 JST 17:00 に自動実行されます。手動実行も可能です。

## フェーズ

- **Phase 1 (MVP)**: RSS記事取得・重複チェック・MD生成 ← 現在
- **Phase 2**: Gemini Pro要約機能
- **Phase 3**: メール通知機能

## ライセンス

MIT
