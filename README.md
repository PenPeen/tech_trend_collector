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
pip install -r requirements.txt

cp .env.example .env
```

## 使い方

本ツールは GitHub Actions 上で動作することを想定しています。

1. GitHub リポジトリの **Actions** タブを開きます。
2. 左サイドバーから **Daily Article Collection** を選択します。
3. **Run workflow** ボタンをクリックして手動実行します。

※ 毎日 JST 17:00 にも自動実行されます。

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

毎日 JST 17:00 に自動実行されます。

## ライセンス

MIT
