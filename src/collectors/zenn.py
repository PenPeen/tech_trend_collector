"""Zenn RSS取得モジュール"""

import socket
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any

import feedparser

from src.utils.config import RSS_TIMEOUT, ZENN_RSS_URL
from src.utils.logger import get_logger

logger = get_logger("collectors.zenn")


def fetch_trending_articles() -> list[dict[str, Any]]:
    """Zennのトレンド記事を取得する

    Returns:
        記事情報のリスト（タイトル、URL、著者、公開日時、タグ、ソース）
        取得失敗時は空リスト
    """
    logger.info("Zenn トレンド記事の取得を開始")

    try:
        # タイムアウト付きでRSSを取得
        feed = feedparser.parse(
            ZENN_RSS_URL,
            request_headers={"User-Agent": "TechTrendCollector/1.0"},
        )

        # feedparserの内部でタイムアウトを設定
        socket.setdefaulttimeout(RSS_TIMEOUT)

        # フィードのステータスチェック
        if hasattr(feed, "bozo") and feed.bozo:
            if hasattr(feed, "bozo_exception"):
                logger.warning(f"RSSパースに問題がありました: {feed.bozo_exception}")

        if not feed.entries:
            logger.warning("Zenn RSSから記事が取得できませんでした")
            return []

        articles = []

        for entry in feed.entries:
            try:
                # 公開日時のパース
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).isoformat()

                # Zennの著者情報取得
                author = ""
                if hasattr(entry, "author"):
                    author = entry.author

                article = {
                    "title": entry.title,
                    "url": entry.link,
                    "author": author,
                    "published": published,
                    "tags": [],  # ZennのRSSにはタグ情報がない
                    "source": "zenn",
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"記事のパースに失敗: {e}")
                continue

        logger.info(f"Zenn から {len(articles)} 件の記事を取得完了")
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
