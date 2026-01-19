# 実行計画書 01: MVP - RSS記事取得・重複チェック・MD生成

## 概要

| 項目 | 内容 |
|------|------|
| フェーズ | Phase 1: MVP |
| 目的 | Qiita/ZennのRSSから記事を取得し、重複チェック後にマークダウンファイルを生成する基盤を構築 |
| 前提条件 | なし（初回PR） |

---

## スコープ

### 含まれるもの
- プロジェクト基盤構築（ディレクトリ構成、依存関係）
- Qiita RSS取得機能
- Zenn RSS取得機能
- 重複チェック機能（history.json）
- マークダウン生成機能（要約なし）
- GitHub Actions定義

### 含まれないもの
- Gemini Pro要約機能（Phase 2）
- メール通知機能（Phase 3）

---

## 実装タスク

### 1. プロジェクト基盤構築

- [ ] ディレクトリ構成の作成
  ```
  src/
  ├── __init__.py
  ├── main.py
  ├── collectors/
  ├── services/
  ├── generators/
  └── utils/
  data/
  articles/
  ```
- [ ] `requirements.txt` 作成
  - feedparser
  - requests
  - python-dotenv
- [ ] `.env.example` 作成
- [ ] `.gitignore` 作成
- [ ] `README.md` 作成

### 2. 設定管理

- [ ] `src/utils/__init__.py` 作成
- [ ] `src/utils/config.py` 作成
  - 環境変数読み込み
  - パス定数定義

### 3. Qiita RSS取得

- [ ] `src/collectors/__init__.py` 作成
- [ ] `src/collectors/qiita.py` 作成
  - `fetch_trending_articles()` 関数
  - RSS URL: `https://qiita.com/popular-items/feed.atom`
  - TOP 5件取得
  - 返却データ: タイトル、URL、著者、公開日時、タグ

### 4. Zenn RSS取得

- [ ] `src/collectors/zenn.py` 作成
  - `fetch_trending_articles()` 関数
  - RSS URL: `https://zenn.dev/feed`
  - TOP 5件取得
  - 返却データ: タイトル、URL、著者、公開日時、タグ

### 5. 重複チェック機能

- [ ] `src/services/__init__.py` 作成
- [ ] `src/services/deduplicator.py` 作成
  - `load_history()` 関数
  - `is_duplicate(url)` 関数
  - `add_to_history(article)` 関数
  - `save_history()` 関数
- [ ] `data/history.json` 初期ファイル作成
  ```json
  {
    "articles": []
  }
  ```

### 6. マークダウン生成

- [ ] `src/generators/__init__.py` 作成
- [ ] `src/generators/markdown.py` 作成
  - `sanitize_filename(title)` 関数（ファイル名に使用不可文字を除去）
  - `generate_article_markdown(article)` 関数
  - `save_markdown(article, content, date)` 関数
  - 出力先: `/articles/YYYY-MM-DD/タイトル.md`

### 7. メインスクリプト

- [ ] `src/main.py` 作成
  - Qiita/Zenn両方から記事取得
  - 重複チェック
  - マークダウン生成
  - 履歴更新
  - 実行結果サマリー出力

### 8. GitHub Actions

- [ ] `.github/workflows/daily-collect.yml` 作成
  - cron: 毎日 JST 17:00 (UTC 08:00)
  - workflow_dispatch対応
  - Python 3.11セットアップ
  - 依存関係インストール
  - スクリプト実行
  - 変更のコミット・プッシュ

---

## 作成/変更ファイル一覧

| パス | 操作 | 説明 |
|------|------|------|
| `src/__init__.py` | 新規 | パッケージ初期化 |
| `src/main.py` | 新規 | エントリーポイント |
| `src/utils/__init__.py` | 新規 | utilsパッケージ |
| `src/utils/config.py` | 新規 | 設定管理 |
| `src/collectors/__init__.py` | 新規 | collectorsパッケージ |
| `src/collectors/qiita.py` | 新規 | Qiita RSS取得 |
| `src/collectors/zenn.py` | 新規 | Zenn RSS取得 |
| `src/services/__init__.py` | 新規 | servicesパッケージ |
| `src/services/deduplicator.py` | 新規 | 重複チェック |
| `src/generators/__init__.py` | 新規 | generatorsパッケージ |
| `src/generators/markdown.py` | 新規 | MD生成 |
| `data/history.json` | 新規 | 取得履歴 |
| `articles/.gitkeep` | 新規 | 空ディレクトリ維持 |
| `.github/workflows/daily-collect.yml` | 新規 | GitHub Actions |
| `requirements.txt` | 新規 | 依存関係 |
| `.env.example` | 新規 | 環境変数サンプル |
| `.gitignore` | 新規 | Git除外設定 |
| `README.md` | 新規 | プロジェクト説明 |

---

## 完了条件

1. `python src/main.py` がローカルで正常に実行できる
2. Qiita/ZennからそれぞれTOP 5件の記事が取得できる
3. 重複記事が正しくスキップされる
4. `/articles/YYYY-MM-DD/タイトル.md` 形式でファイルが生成される
5. `history.json` が正しく更新される
6. GitHub Actionsが手動トリガーで正常に動作する

---

## PRテンプレート

```markdown
## 概要
TechTrendCollector Phase 1: MVP実装

Qiita/ZennのRSSから記事を取得し、マークダウンファイルを生成する基盤を構築しました。

## 変更内容
- プロジェクト基盤構築（ディレクトリ構成、依存関係）
- Qiita RSS取得機能
- Zenn RSS取得機能
- 重複チェック機能（history.json）
- マークダウン生成機能（要約なし）
- GitHub Actions定義

## テスト方法
1. `pip install -r requirements.txt`
2. `python src/main.py`
3. `articles/` ディレクトリにマークダウンファイルが生成されることを確認

## 関連Issue
なし
```

---

## 備考

- この段階ではGemini APIキー、Resend APIキーは不要
- 要約は「（要約機能は次フェーズで実装予定）」とプレースホルダー表示
- エラーハンドリングは最小限（Phase 4で強化）
