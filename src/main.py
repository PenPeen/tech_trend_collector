"""TechTrendCollector メインスクリプト"""

import sys
from datetime import datetime

from src.collectors import hackernews, hatena, qiita, zenn
from src.generators.markdown import save_markdown
from src.services.deduplicator import Deduplicator
from src.services.notifier import (
    is_notifier_enabled,
    send_failure_notification,
    send_success_notification,
)
from src.services.translator import translate_hn_titles
from src.utils.config import PRIORITY_TOPICS, validate_config
from src.utils.logger import get_logger

logger = get_logger("main")


def print_summary(stats: dict, execution_time: str, output_dir: str) -> None:
    """実行結果サマリーを出力

    Args:
        stats: 統計情報
        execution_time: 実行日時
        output_dir: 出力先ディレクトリ
    """
    qiita_new = stats["qiita_fetched"] - stats.get("qiita_duplicates", 0)
    zenn_new = stats["zenn_fetched"] - stats.get("zenn_duplicates", 0)
    hn_new = stats["hn_fetched"] - stats.get("hn_duplicates", 0)
    hatena_new = stats["hatena_fetched"] - stats.get("hatena_duplicates", 0)

    summary = f"""
========================================
TechTrendCollector 実行結果
========================================
実行日時: {execution_time}

[記事取得]
- Qiita:        {stats['qiita_fetched']}件取得 (新規: {qiita_new}件, 重複: {stats.get('qiita_duplicates', 0)}件)
- Zenn:         {stats['zenn_fetched']}件取得 (新規: {zenn_new}件, 重複: {stats.get('zenn_duplicates', 0)}件)
- Hacker News:  {stats['hn_fetched']}件取得 (新規: {hn_new}件, 重複: {stats.get('hn_duplicates', 0)}件)
- はてなブックマーク: {stats['hatena_fetched']}件取得 (新規: {hatena_new}件, 重複: {stats.get('hatena_duplicates', 0)}件)

[マークダウン生成]
- 生成ファイル数: {stats['new_articles']}件
- 出力先: {output_dir}

[優先トピック (AWS/Python)]
- 取得記事数: {stats.get('priority_fetched', 0)}件 (新規: {stats.get('priority_new', 0)}件)

[通知]
- メール送信: {stats.get('notification_status', '未送信')}
========================================
"""
    print(summary)
    logger.info("実行結果サマリーを出力しました")


def main() -> int:
    """メイン処理

    Returns:
        終了コード（0: 正常, 1: エラー）
    """
    execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_date = datetime.now().strftime("%Y-%m-%d")

    logger.info("=" * 50)
    logger.info("TechTrendCollector - 記事収集開始")
    logger.info("=" * 50)

    # 設定バリデーション
    logger.info("設定を検証中...")
    is_valid, warnings = validate_config()
    for warning in warnings:
        logger.warning(warning)

    # 通知機能確認
    notifier_enabled = is_notifier_enabled()
    if notifier_enabled:
        logger.info("Resend 通知機能が有効です")
    else:
        logger.info("Resend 通知機能は無効です")

    # 重複チェッカー初期化
    deduplicator = Deduplicator()
    if not deduplicator.load_history():
        logger.warning("履歴ファイルの読み込みに問題がありました")

    # 統計情報
    stats = {
        "qiita_fetched": 0,
        "zenn_fetched": 0,
        "hn_fetched": 0,
        "hatena_fetched": 0,
        "qiita_duplicates": 0,
        "zenn_duplicates": 0,
        "hn_duplicates": 0,
        "hatena_duplicates": 0,
        "new_articles": 0,
        "duplicates": 0,
        "priority_fetched": 0,
        "priority_new": 0,
        "notification_status": "未送信",
    }

    # Qiita記事取得
    logger.info("Qiita トレンド記事を取得中...")
    qiita_articles = qiita.fetch_trending_articles()
    stats["qiita_fetched"] = len(qiita_articles)

    # Zenn記事取得
    logger.info("Zenn トレンド記事を取得中...")
    zenn_articles = zenn.fetch_trending_articles()
    stats["zenn_fetched"] = len(zenn_articles)

    # Hacker News記事取得
    logger.info("Hacker News トップ記事を取得中...")
    hn_articles = hackernews.fetch_top_articles()
    stats["hn_fetched"] = len(hn_articles)

    # HN記事タイトルを日本語に翻訳（Gemini API 1回呼び出し）
    if hn_articles:
        logger.info("Hacker News 記事タイトルを翻訳中...")
        hn_articles = translate_hn_titles(hn_articles)

    # はてなブックマーク記事取得
    logger.info("はてなブックマーク ホットエントリを取得中...")
    hatena_articles = hatena.fetch_hotentry_articles()
    stats["hatena_fetched"] = len(hatena_articles)

    # AWS/Python 優先トピック記事の取得
    priority_articles: list[dict] = []  # {topic, source, articles} のリスト管理用
    priority_all_articles: list[dict] = []  # 全優先記事のフラットリスト

    for topic in PRIORITY_TOPICS:
        logger.info(f"優先トピック '{topic}' の記事を取得中...")

        # Qiita: タグ別API取得
        topic_qiita = qiita.fetch_articles_by_tag(topic)
        if topic_qiita:
            priority_articles.append({"topic": topic, "source": "qiita", "articles": topic_qiita})
            priority_all_articles.extend(topic_qiita)

        # Zenn: トピック別API取得
        topic_zenn = zenn.fetch_articles_by_topic(topic)
        if topic_zenn:
            priority_articles.append({"topic": topic, "source": "zenn", "articles": topic_zenn})
            priority_all_articles.extend(topic_zenn)

        # はてなブックマーク: 取得済み記事からフィルタリング
        topic_hatena = hatena.filter_articles_by_tag(hatena_articles, topic)
        if topic_hatena:
            priority_articles.append({"topic": topic, "source": "hatena", "articles": topic_hatena})
            priority_all_articles.extend(topic_hatena)

    stats["priority_fetched"] = len(priority_all_articles)

    # 全記事をマージ
    all_articles = qiita_articles + zenn_articles + hn_articles + hatena_articles

    # 全ソース失敗チェック
    if stats["qiita_fetched"] == 0 and stats["zenn_fetched"] == 0 and stats["hn_fetched"] == 0 and stats["hatena_fetched"] == 0:
        error_message = "全てのソース（Qiita, Zenn, Hacker News, はてなブックマーク）からの記事取得に失敗しました"
        logger.error(error_message)
        if notifier_enabled:
            if send_failure_notification(error_message):
                stats["notification_status"] = "エラー通知送信済み"
        print_summary(stats, execution_time, f"articles/{target_date}/")
        return 1

    # 新規保存された記事を追跡
    saved_articles: list[dict] = []

    # 重複チェック・保存
    logger.info("記事を処理中...")
    for article in all_articles:
        source = article["source"]

        if deduplicator.is_duplicate(article["url"]):
            stats["duplicates"] += 1
            if source == "qiita":
                stats["qiita_duplicates"] += 1
            elif source == "zenn":
                stats["zenn_duplicates"] += 1
            elif source == "hatena":
                stats["hatena_duplicates"] += 1
            else:
                stats["hn_duplicates"] += 1
            logger.debug(f"[スキップ] 重複: {article['title'][:40]}...")
            continue

        # マークダウン保存
        filepath = save_markdown(article)
        logger.info(f"保存完了: {filepath.name}")

        # 履歴に追加
        deduplicator.add_to_history(article)
        saved_articles.append(article)
        stats["new_articles"] += 1

    # 優先トピック記事の重複チェック・保存
    saved_priority_articles: list[dict] = []
    logger.info("優先トピック記事を処理中...")
    for article in priority_all_articles:
        if deduplicator.is_duplicate(article["url"]):
            logger.debug(f"[スキップ] 重複（優先トピック）: {article['title'][:40]}...")
            continue

        filepath = save_markdown(article)
        logger.info(f"保存完了（優先トピック）: {filepath.name}")

        deduplicator.add_to_history(article)
        saved_priority_articles.append(article)
        stats["priority_new"] += 1
        stats["new_articles"] += 1

    # 履歴保存
    if not deduplicator.save_history():
        logger.warning("履歴ファイルの保存に問題がありました")

    # 成功通知送信
    if notifier_enabled:
        logger.info("メール通知を送信中...")
        if send_success_notification(saved_articles, stats, priority_articles=priority_articles):
            stats["notification_status"] = "成功"
        else:
            stats["notification_status"] = "失敗"

    # サマリー出力
    print_summary(stats, execution_time, f"articles/{target_date}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
