"""TechTrendCollector メインスクリプト"""

from src.collectors import qiita, zenn
from src.generators.markdown import save_markdown
from src.services.deduplicator import Deduplicator
from src.services.notifier import (
    is_notifier_enabled,
    send_failure_notification,
    send_success_notification,
)
from src.services.summarizer import initialize_gemini, summarize_article


def main() -> None:
    """メイン処理"""
    print("=" * 50)
    print("TechTrendCollector - 記事収集開始")
    print("=" * 50)

    # Gemini初期化
    gemini_enabled = initialize_gemini()
    if gemini_enabled:
        print("[Gemini] 要約機能が有効です")
    else:
        print("[Gemini] GEMINI_API_KEYが未設定のため要約をスキップします")

    # 通知機能確認
    notifier_enabled = is_notifier_enabled()
    if notifier_enabled:
        print("[Resend] 通知機能が有効です")
    else:
        print("[Resend] RESEND_API_KEY/NOTIFICATION_EMAILが未設定のため通知をスキップします")

    # 重複チェッカー初期化
    deduplicator = Deduplicator()
    deduplicator.load_history()

    # 統計情報
    stats = {
        "qiita_fetched": 0,
        "zenn_fetched": 0,
        "new_articles": 0,
        "duplicates": 0,
        "summaries_generated": 0,
    }

    # Qiita記事取得
    print("\n[Qiita] トレンド記事を取得中...")
    qiita_articles = qiita.fetch_trending_articles()
    stats["qiita_fetched"] = len(qiita_articles)
    print(f"[Qiita] {len(qiita_articles)}件の記事を取得")

    # Zenn記事取得
    print("\n[Zenn] トレンド記事を取得中...")
    zenn_articles = zenn.fetch_trending_articles()
    stats["zenn_fetched"] = len(zenn_articles)
    print(f"[Zenn] {len(zenn_articles)}件の記事を取得")

    # 全記事をマージ
    all_articles = qiita_articles + zenn_articles

    # 全ソース失敗チェック
    if stats["qiita_fetched"] == 0 and stats["zenn_fetched"] == 0:
        error_message = "全てのソース（Qiita, Zenn）からの記事取得に失敗しました"
        print(f"\n[エラー] {error_message}")
        if notifier_enabled:
            if send_failure_notification(error_message):
                print("[通知] エラー通知を送信しました")
        return

    # 新規保存された記事を追跡
    saved_articles: list[dict] = []

    # 重複チェック・保存
    print("\n[処理] 記事を処理中...")
    for article in all_articles:
        if deduplicator.is_duplicate(article["url"]):
            stats["duplicates"] += 1
            print(f"  [スキップ] {article['title'][:40]}...")
            continue

        # 要約生成
        summary = ""
        if gemini_enabled:
            print(f"  [要約生成中] {article['title'][:40]}...")
            summary = summarize_article(article["url"])
            if summary:
                stats["summaries_generated"] += 1

        # マークダウン保存
        filepath = save_markdown(article, summary)
        print(f"  [保存] {filepath.name}")

        # 履歴に追加
        deduplicator.add_to_history(article)
        saved_articles.append(article)
        stats["new_articles"] += 1

    # 履歴保存
    deduplicator.save_history()

    # サマリー出力
    print("\n" + "=" * 50)
    print("実行結果サマリー")
    print("=" * 50)
    print(f"  Qiita取得: {stats['qiita_fetched']}件")
    print(f"  Zenn取得:  {stats['zenn_fetched']}件")
    print(f"  新規保存:  {stats['new_articles']}件")
    print(f"  要約生成:  {stats['summaries_generated']}件")
    print(f"  重複スキップ: {stats['duplicates']}件")
    print("=" * 50)

    # 成功通知送信
    if notifier_enabled:
        print("\n[通知] メール通知を送信中...")
        if send_success_notification(saved_articles, stats):
            print("[通知] 成功通知を送信しました")
        else:
            print("[通知] 通知送信に失敗しました")


if __name__ == "__main__":
    main()
