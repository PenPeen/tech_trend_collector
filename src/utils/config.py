"""設定管理モジュール"""

import os
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# プロジェクトルートディレクトリ
ROOT_DIR = Path(__file__).parent.parent.parent

# データディレクトリ
DATA_DIR = ROOT_DIR / "data"
ARTICLES_DIR = ROOT_DIR / "articles"

# 履歴ファイルパス
HISTORY_FILE = DATA_DIR / "history.json"

# RSS設定
QIITA_RSS_URL = "https://qiita.com/popular-items/feed.atom"
ZENN_RSS_URL = "https://zenn.dev/feed"
HN_RSS_URL = "https://hnrss.org/frontpage"

# タイムアウト設定（秒）
RSS_TIMEOUT = 30
NOTIFICATION_TIMEOUT = 30

# APIキー
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")


def validate_config() -> Tuple[bool, List[str]]:
    """設定のバリデーションを行う

    Returns:
        (検証成功かどうか, 警告メッセージリスト)
    """
    warnings: List[str] = []

    # Resend APIキーチェック
    if not RESEND_API_KEY:
        warnings.append("RESEND_API_KEY が未設定です。通知機能は無効になります。")
    elif not RESEND_API_KEY.startswith("re_"):
        warnings.append("RESEND_API_KEY のフォーマットが不正の可能性があります（re_で始まる必要があります）。")

    # 通知先メールチェック
    if RESEND_API_KEY and not NOTIFICATION_EMAIL:
        warnings.append("NOTIFICATION_EMAIL が未設定です。通知機能は無効になります。")
    elif NOTIFICATION_EMAIL and "@" not in NOTIFICATION_EMAIL:
        warnings.append("NOTIFICATION_EMAIL のフォーマットが不正です。")

    # ディレクトリ存在チェック・作成
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    # 重大なエラーがない限りTrueを返す（警告のみの場合も続行可能）
    return True, warnings
