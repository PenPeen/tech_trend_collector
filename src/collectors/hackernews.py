"""Hacker News RSS取得モジュール"""

import socket
import urllib.error
from datetime import datetime
from typing import Any

import feedparser

from src.utils.config import HN_RSS_URL, RSS_TIMEOUT
from src.utils.logger import get_logger

logger = get_logger("collectors.hackernews")


def fetch_top_articles() -> list[dict[str, Any]]:
    """Hacker Newsのフロントページ記事を取得する

    Returns:
        記事情報のリスト（タイトル、URL、著者、公開日時、タグ、ソース）
        取得失敗時は空リスト
    """
    logger.info("Hacker News フロントページ記事の取得を開始")

    try:
        # タイムアウト付きでRSSを取得
        feed = feedparser.parse(
            HN_RSS_URL,
            request_headers={"User-Agent": "TechTrendCollector/1.0"},
        )

        # feedparserの内部でタイムアウトを設定
        socket.setdefaulttimeout(RSS_TIMEOUT)

        # フィードのステータスチェック
        if hasattr(feed, "bozo") and feed.bozo:
            if hasattr(feed, "bozo_exception"):
                logger.warning(f"RSSパースに問題がありました: {feed.bozo_exception}")

        if not feed.entries:
            logger.warning("Hacker News RSSから記事が取得できませんでした")
            return []

        articles = []

        for entry in feed.entries:
            try:
                # 公開日時のパース
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).isoformat()

                # hnrss.orgはオリジナル記事のリンクをentry.linkとして提供
                url = entry.link if hasattr(entry, "link") else ""

                # 著者情報
                author = ""
                if hasattr(entry, "author"):
                    author = entry.author

                article = {
                    "title": entry.title,
                    "url": url,
                    "author": author,
                    "published": published,
                    "tags": [],
                    "source": "hackernews",
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"記事のパースに失敗: {e}")
                continue

        logger.info(f"Hacker News から {len(articles)} 件の記事を取得完了")
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
