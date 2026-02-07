"""はてなブックマーク RSS取得モジュール"""

import socket
import urllib.error
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import feedparser

from src.utils.config import HATENA_RSS_URL, RSS_TIMEOUT
from src.utils.logger import get_logger

logger = get_logger("collectors.hatena")

# Qiita/Zennと重複するドメインを除外
EXCLUDED_DOMAINS = {"qiita.com", "zenn.dev"}


def _is_excluded_domain(url: str) -> bool:
    """URLが除外対象ドメインかどうかを判定する"""
    try:
        hostname = urlparse(url).hostname or ""
        return any(hostname == domain or hostname.endswith(f".{domain}") for domain in EXCLUDED_DOMAINS)
    except Exception:
        return False


def fetch_hotentry_articles() -> list[dict[str, Any]]:
    """はてなブックマークのテクノロジーカテゴリのホットエントリを取得する

    Returns:
        記事情報のリスト（タイトル、URL、著者、公開日時、タグ、ソース、ブックマーク数）
        取得失敗時は空リスト
    """
    logger.info("はてなブックマーク ホットエントリの取得を開始")

    try:
        socket.setdefaulttimeout(RSS_TIMEOUT)

        feed = feedparser.parse(
            HATENA_RSS_URL,
            request_headers={"User-Agent": "TechTrendCollector/1.0"},
        )

        if hasattr(feed, "bozo") and feed.bozo:
            if hasattr(feed, "bozo_exception"):
                logger.warning(f"RSSパースに問題がありました: {feed.bozo_exception}")

        if not feed.entries:
            logger.warning("はてなブックマーク RSSから記事が取得できませんでした")
            return []

        articles = []

        for entry in feed.entries:
            try:
                url = entry.link if hasattr(entry, "link") else ""

                # Qiita/Zenn URLを除外
                if _is_excluded_domain(url):
                    logger.debug(f"[スキップ] 除外ドメイン: {url}")
                    continue

                # 公開日時のパース
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).isoformat()

                # 著者情報
                author = ""
                if hasattr(entry, "author"):
                    author = entry.author

                # タグ（dc:subject）
                tags = []
                if hasattr(entry, "tags"):
                    tags = [tag.term for tag in entry.tags if hasattr(tag, "term")]

                # ブックマーク数
                bookmarks = 0
                if hasattr(entry, "hatena_bookmarkcount"):
                    try:
                        bookmarks = int(entry.hatena_bookmarkcount)
                    except (ValueError, TypeError):
                        pass

                article = {
                    "title": entry.title,
                    "url": url,
                    "author": author,
                    "published": published,
                    "tags": tags,
                    "source": "hatena",
                    "bookmarks": bookmarks,
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"記事のパースに失敗: {e}")
                continue

        # ブックマーク数で降順ソート
        articles.sort(key=lambda a: a["bookmarks"], reverse=True)

        logger.info(f"はてなブックマーク から {len(articles)} 件の記事を取得完了")
        return articles

    except urllib.error.URLError as e:
        logger.error(f"ネットワークエラー: {e}")
        return []
    except socket.timeout:
        logger.error(f"タイムアウト ({RSS_TIMEOUT}秒)")
        return []
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        return []
