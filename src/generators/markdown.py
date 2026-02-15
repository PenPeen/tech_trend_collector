"""マークダウン生成モジュール"""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.config import ARTICLES_DIR

# ソース名の表示用マッピング
SOURCE_DISPLAY_NAMES = {
    "qiita": "Qiita",
    "zenn": "Zenn",
    "hackernews": "Hacker News",
    "hatena": "はてなブックマーク",
}


def _build_metric_label(article: dict[str, Any]) -> str:
    """記事のメトリクスラベルを生成する

    Args:
        article: 記事情報

    Returns:
        メトリクスラベル文字列（例: "123 users", "45 points", "67 likes"）
        メトリクスがない場合は空文字列
    """
    source = article.get("source", "")
    if source == "hatena":
        bookmarks = article.get("bookmarks", 0)
        if bookmarks:
            return f"{bookmarks} users"
    elif source == "hackernews":
        points = article.get("points", 0)
        if points:
            return f"{points} points"
    elif source in ("qiita", "zenn"):
        likes = article.get("likes", 0)
        if likes:
            return f"{likes} likes"
    return ""


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
    # 長すぎる場合は切り詰める
    # Linuxのファイル名上限は255バイト。拡張子(.md=3バイト)を考慮し、250バイトまでに制限
    max_bytes = 250
    encoded = sanitized.encode("utf-8")
    if len(encoded) > max_bytes:
        # バイト数で切り詰めた後、UTF-8として正しくデコードできるよう調整
        truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
        sanitized = truncated.rstrip()
    return sanitized


def generate_article_markdown(article: dict[str, Any]) -> str:
    """記事のマークダウンコンテンツを生成する

    Args:
        article: 記事情報

    Returns:
        マークダウン形式の文字列
    """
    source_display = SOURCE_DISPLAY_NAMES.get(
        article["source"], article["source"].capitalize()
    )

    # メトリクスラベルの生成
    metric_label = _build_metric_label(article)
    title_suffix = f" ({metric_label})" if metric_label else ""

    lines = [
        f"# {article['title']}{title_suffix}",
        "",
        "## 記事情報",
        "",
        f"- **URL**: {article['url']}",
        f"- **ソース**: {source_display}",
        f"- **著者**: {article['author'] or '不明'}",
        f"- **公開日時**: {article['published'] or '不明'}",
    ]

    if article.get("tags"):
        tags_str = ", ".join(article["tags"])
        lines.append(f"- **タグ**: {tags_str}")

    lines.append("")

    return "\n".join(lines)


def save_markdown(
    article: dict[str, Any], date: datetime | None = None
) -> Path:
    """マークダウンファイルを保存する

    Args:
        article: 記事情報
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
    content = generate_article_markdown(article)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
