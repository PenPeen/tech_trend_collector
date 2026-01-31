"""TechTrendCollector メインスクリプト"""

import sys
from datetime import datetime

from src.collectors import hackernews, qiita, zenn
from src.generators.markdown import save_markdown
from src.services.deduplicator import Deduplicator
from src.services.notifier import (
    is_notifier_enabled,
    send_failure_notification,
    send_success_notification,
)
from src.services.translator import translate_hn_titles
from src.utils.config import validate_config
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

    summary = f"""
========================================
TechTrendCollector 実行結果
========================================
実行日時: {execution_time}

[記事取得]
- Qiita:        {stats['qiita_fetched']}件取得 (新規: {qiita_new}件, 重複: {stats.get('qiita_duplicates', 0)}件)
- Zenn:         {stats['zenn_fetched']}件取得 (新規: {zenn_new}件, 重複: {stats.get('zenn_duplicates', 0)}件)
- Hacker News:  {stats['hn_fetched']}件取得 (新規: {hn_new}件, 重複: {stats.get('hn_duplicates', 0)}件)

[マークダウン生成]
- 生成ファイル数: {stats['new_articles']}件
- 出力先: {output_dir}

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
        "qiita_duplicates": 0,
        "zenn_duplicates": 0,
        "hn_duplicates": 0,
        "new_articles": 0,
        "duplicates": 0,
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

    # 全記事をマージ
    all_articles = qiita_articles + zenn_articles + hn_articles

    # 全ソース失敗チェック
    if stats["qiita_fetched"] == 0 and stats["zenn_fetched"] == 0 and stats["hn_fetched"] == 0:
        error_message = "全てのソース（Qiita, Zenn, Hacker News）からの記事取得に失敗しました"
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

    # 履歴保存
    if not deduplicator.save_history():
        logger.warning("履歴ファイルの保存に問題がありました")

    # 成功通知送信
    if notifier_enabled:
        logger.info("メール通知を送信中...")
        if send_success_notification(saved_articles, stats):
            stats["notification_status"] = "成功"
        else:
            stats["notification_status"] = "失敗"

    # サマリー出力
    print_summary(stats, execution_time, f"articles/{target_date}/")

    return 0


if __name__ == "__main__":
    sys.exit(main())
