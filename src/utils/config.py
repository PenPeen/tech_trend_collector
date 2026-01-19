"""設定管理モジュール"""

import os
from pathlib import Path

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

# 取得件数
MAX_ARTICLES_PER_SOURCE = 5

# 将来の拡張用（Phase 2以降）
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")
