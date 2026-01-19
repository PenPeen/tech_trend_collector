"""マークダウン生成モジュール"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.config import ARTICLES_DIR


def sanitize_filename(title: str) -> str:
    """ファイル名に使用不可な文字を除去する

    Args:
        title: 元のタイトル

    Returns:
        サニタイズされたファイル名
    """
    # ファイル名に使用不可な文字を除去
    sanitized = re.sub(r'[<>:"/\\|?*]', "", title)
    # 前後の空白を除去
    sanitized = sanitized.strip()
    # 連続する空白を単一の空白に置換
    sanitized = re.sub(r"\s+", " ", sanitized)
    # 長すぎる場合は切り詰める（拡張子を考慮して200文字まで）
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized


def generate_article_markdown(article: dict[str, Any], summary: str = "") -> str:
    """記事のマークダウンコンテンツを生成する

    Args:
        article: 記事情報
        summary: 要約テキスト（空の場合はエラーメッセージ表示）

    Returns:
        マークダウン形式の文字列
    """
    lines = [
        f"# {article['title']}",
        "",
        "## 記事情報",
        "",
        f"- **URL**: {article['url']}",
        f"- **ソース**: {article['source'].capitalize()}",
        f"- **著者**: {article['author'] or '不明'}",
        f"- **公開日時**: {article['published'] or '不明'}",
    ]

    if article.get("tags"):
        tags_str = ", ".join(article["tags"])
        lines.append(f"- **タグ**: {tags_str}")

    # 要約セクション
    summary_text = summary if summary else "（要約の取得に失敗しました）"
    lines.extend(
        [
            "",
            "## 要約",
            "",
            summary_text,
            "",
        ]
    )

    return "\n".join(lines)


def save_markdown(
    article: dict[str, Any], summary: str = "", date: datetime | None = None
) -> Path:
    """マークダウンファイルを保存する

    Args:
        article: 記事情報
        summary: 要約テキスト
        date: 保存日付（指定がなければ今日）

    Returns:
        保存したファイルのパス
    """
    if date is None:
        date = datetime.now()

    # ディレクトリ作成
    date_str = date.strftime("%Y-%m-%d")
    output_dir = ARTICLES_DIR / date_str
    output_dir.mkdir(parents=True, exist_ok=True)

    # ファイル名生成
    filename = sanitize_filename(article["title"]) + ".md"
    filepath = output_dir / filename

    # マークダウン生成・保存
    content = generate_article_markdown(article, summary)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
