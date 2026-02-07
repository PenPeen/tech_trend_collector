"""HN記事タイトル翻訳モジュール"""

import json
from typing import Any

import google.generativeai as genai

from src.utils.config import GEMINI_API_KEY
from src.utils.logger import get_logger

logger = get_logger("services.translator")

TRANSLATION_PROMPT = """\
以下の英語の記事タイトルを自然な日本語に翻訳してください。
JSON配列形式で、翻訳後のタイトルのみを入力と同じ順序で返してください。
余計な説明やコードブロックは不要です。JSON配列のみを出力してください。

{titles_json}"""


def translate_hn_titles(articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Hacker News記事のタイトルを日本語に一括翻訳する

    Gemini APIを1回だけ呼び出し、全タイトルをまとめて翻訳する。
    翻訳失敗時は英語タイトルのままフォールバックする。

    Args:
        articles: HN記事リスト

    Returns:
        タイトルが翻訳された記事リスト（失敗時は元のまま）
    """
    if not articles:
        return articles

    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY が未設定のため翻訳をスキップ")
        return articles

    titles = [a["title"] for a in articles]

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        prompt = TRANSLATION_PROMPT.format(
            titles_json=json.dumps(titles, ensure_ascii=False)
        )

        response = model.generate_content(prompt)

        translated = _parse_response(response.text, len(titles))

        if translated:
            for article, translated_title in zip(articles, translated):
                article["title"] = translated_title
            logger.info(f"HN記事タイトル {len(translated)}件の翻訳完了")
        else:
            logger.warning("翻訳結果のパースに失敗したためフォールバック")

    except Exception as e:
        logger.error(f"タイトル翻訳に失敗（英語タイトルのまま続行）: {e}")

    return articles


def _parse_response(text: str, expected_count: int) -> list[str] | None:
    """Geminiのレスポンスからタイトルリストをパースする

    Args:
        text: Geminiレスポンステキスト
        expected_count: 期待するタイトル数

    Returns:
        翻訳タイトルリスト。パース失敗や件数不一致の場合はNone
    """
    cleaned = text.strip()

    # ```json ... ``` のコードブロックを除去
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1]).strip()

    try:
        result = json.loads(cleaned)
        if isinstance(result, list) and len(result) == expected_count:
            return [str(t) for t in result]
        logger.warning(
            f"翻訳結果の件数が不一致 (期待: {expected_count}, 実際: {len(result) if isinstance(result, list) else 'N/A'})"
        )
    except json.JSONDecodeError as e:
        logger.warning(f"翻訳結果のJSONパースエラー: {e}")

    return None
