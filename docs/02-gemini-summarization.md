# 実行計画書 02: Gemini Pro 要約機能追加

## 概要

| 項目 | 内容 |
|------|------|
| フェーズ | Phase 2: 要約機能追加 |
| 目的 | Gemini Pro APIを使用して記事の要約を生成し、マークダウンに含める |
| 前提条件 | Phase 1（PR #01）がマージ済みであること |

---

## スコープ

### 含まれるもの
- Gemini Pro API連携
- 記事要約生成機能
- マークダウン生成の拡張（要約セクション追加）
- GitHub Secrets設定ドキュメント

### 含まれないもの
- メール通知機能（Phase 3）
- エラーハンドリング強化（Phase 4）

---

## 実装タスク

### 1. 依存関係追加

- [ ] `requirements.txt` に追加
  - google-generativeai

### 2. 設定追加

- [ ] `src/utils/config.py` 更新
  - `GEMINI_API_KEY` 環境変数読み込み追加
- [ ] `.env.example` 更新
  - `GEMINI_API_KEY=your_api_key_here` 追加

### 3. 要約サービス実装

- [ ] `src/services/summarizer.py` 作成
  - `initialize_gemini()` 関数
    - Gemini Pro モデル初期化
  - `summarize_article(url)` 関数
    - プロンプト設計:
      ```
      以下の技術記事を要約してください。

      【記事URL】
      {url}
      ```
    - Gemini Proにリクエスト送信
    - 要約テキスト返却
  - API失敗時の例外ハンドリング（空文字列を返す）

### 4. マークダウン生成の拡張

- [ ] `src/generators/markdown.py` 更新
  - `generate_article_markdown(article, summary)` に引数追加
  - 要約セクションをマークダウンに含める
  - 要約が空の場合は「（要約の取得に失敗しました）」表示

### 5. メインスクリプト更新

- [ ] `src/main.py` 更新
  - Gemini初期化処理追加
  - 各記事に対して要約を生成
  - 要約をマークダウン生成に渡す
  - GEMINI_API_KEYが未設定の場合はスキップ（警告表示）

### 6. GitHub Actions更新

- [ ] `.github/workflows/daily-collect.yml` 更新
  - `GEMINI_API_KEY` 環境変数を追加

---

## 作成/変更ファイル一覧

| パス | 操作 | 説明 |
|------|------|------|
| `src/services/summarizer.py` | 新規 | Gemini要約サービス |
| `src/generators/markdown.py` | 更新 | 要約セクション追加 |
| `src/main.py` | 更新 | 要約処理追加 |
| `src/utils/config.py` | 更新 | GEMINI_API_KEY追加 |
| `requirements.txt` | 更新 | google-generativeai追加 |
| `.env.example` | 更新 | GEMINI_API_KEY追加 |
| `.github/workflows/daily-collect.yml` | 更新 | 環境変数追加 |

---

## GitHub Secrets設定

PRマージ前に以下のSecretを設定する必要があります。

| Secret名 | 説明 | 取得方法 |
|----------|------|----------|
| `GEMINI_API_KEY` | Gemini Pro APIキー | [Google AI Studio](https://aistudio.google.com/app/apikey) から取得 |

---

## 完了条件

1. `python src/main.py` がローカルで正常に実行できる（GEMINI_API_KEY設定時）
2. 各記事に対してGemini Proが要約を生成する
3. 生成されるマークダウンに「要約」セクションが含まれる
4. GEMINI_API_KEY未設定時でもエラーなく動作する（要約スキップ）
5. GitHub Actionsが正常に動作する

---

## PRテンプレート

```markdown
## 概要
TechTrendCollector Phase 2: Gemini Pro要約機能追加

Gemini Pro APIを使用して記事の要約を自動生成する機能を追加しました。

## 変更内容
- Gemini Pro API連携（google-generativeai）
- 記事要約生成サービス
- マークダウン生成に要約セクション追加

## 設定が必要なSecrets
- `GEMINI_API_KEY`: Gemini Pro APIキー

## テスト方法
1. `.env` に `GEMINI_API_KEY` を設定
2. `pip install -r requirements.txt`
3. `python src/main.py`
4. 生成されたマークダウンに要約が含まれることを確認

## 関連Issue
なし
```

---

## 備考

- Gemini ProはURLを渡すと記事内容をフェッチして要約可能
- API レート制限に注意（1分あたりのリクエスト数）
- 要約生成に失敗しても処理は継続（エラーハンドリング）
- 要約の品質調整はPhase 4で検討
