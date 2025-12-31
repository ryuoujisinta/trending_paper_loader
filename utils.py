"""
ユーティリティ関数

このモジュールは論文データの取得・保存に関するユーティリティ関数を提供します。
"""

# 標準ライブラリ
import datetime
import json
import logging
import os
import random
import time
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

# サードパーティライブラリ
import requests
from bs4 import BeautifulSoup

# ローカルモジュール
from config import config
from exceptions import (
    InvalidURLError,
    RateLimitError,
    UpvoteFetchError,
)

# ログディレクトリの作成
if not os.path.exists(config.LOG_DIR):
    os.makedirs(config.LOG_DIR)

# ログファイルのパス
log_file_path = os.path.join(config.LOG_DIR, config.LOG_FILE)

# ロガーの設定
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def load_data(date_str: str) -> Optional[List[Dict[str, Any]]]:
    """
    ローカルJSONファイルからデータを読み込む

    Args:
        date_str: 日付文字列（YYYY-MM-DD形式）

    Returns:
        論文データのリスト、ファイルが存在しない場合はNone
    """
    file_path = os.path.join(config.DATA_DIR, f"{date_str}.json")
    if os.path.exists(file_path):
        logger.info(f"データ読み込み: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    logger.info(f"対象日付のデータファイルが未取得です（パス: {file_path}）")
    return None


def save_data(date_str: str, data: List[Dict[str, Any]]) -> None:
    """
    ローカルJSONファイルにデータを保存する

    Args:
        date_str: 日付文字列（YYYY-MM-DD形式）
        data: 保存する論文データのリスト
    """
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR)
        logger.info(f"ディレクトリ作成: {config.DATA_DIR}")

    file_path = os.path.join(config.DATA_DIR, f"{date_str}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"データ保存: {file_path} ({len(data)} 件)")


def request_with_retry(
    url: str,
    retries: int = config.DEFAULT_RETRIES,
    delay: int = config.DEFAULT_RETRY_DELAY,
) -> Optional[requests.Response]:
    """
    リトライロジック付きHTTPリクエスト

    429エラー（レート制限）の場合のみリトライを行います。
    その他のエラーの場合は例外を発生させます。

    Args:
        url: リクエスト先URL
        retries: リトライ回数（デフォルト: config.DEFAULT_RETRIES）
        delay: リトライ遅延時間（秒、デフォルト: config.DEFAULT_RETRY_DELAY）

    Returns:
        HTTPレスポンス、リトライ上限に達した場合はNone

    Raises:
        RateLimitError: リトライ上限に達した場合
        requests.exceptions.RequestException: その他のHTTPエラー
    """
    for i in range(retries):
        try:
            response = requests.get(url, timeout=config.REQUEST_TIMEOUT)
            if response.status_code == 429:
                wait_time = delay * (2**i) + random.uniform(0, 1)
                logger.warning(f"429 レート制限エラー。{wait_time:.2f}秒待機中...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            logger.info(f"リクエスト成功: {url}")
            return response
        except requests.exceptions.RequestException as e:
            if (
                isinstance(e, requests.exceptions.HTTPError)
                and e.response.status_code == 429
            ):
                if i < retries - 1:
                    continue
                logger.error(f"リトライ上限に達しました: {url}")
                raise RateLimitError(f"リトライ上限に達しました: {url}") from e

            logger.error(f"リクエストエラー: {url}, エラー: {e}")
            raise e
    return None


def _validate_url(url: str) -> None:
    """
    URLの形式を検証する

    Args:
        url: 検証するURL

    Raises:
        InvalidURLError: URLが無効な形式の場合
    """
    if not url:
        raise InvalidURLError("URLが空です")

    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise InvalidURLError(f"無効なURL形式: {url}")
    except ValueError as e:
        raise InvalidURLError(f"URL解析エラー: {url}") from e

    # Hugging Faceドメインの検証（オプション）
    if "huggingface.co" not in result.netloc:
        logger.warning(f"Hugging Face以外のドメイン: {url}")


def get_paper_summary(paper_url: str) -> str:
    """
    論文詳細ページから要約（Abstract）を取得する

    Args:
        paper_url: 論文ページのURL

    Returns:
        論文の要約テキスト、取得できない場合はエラーメッセージ

    Raises:
        SummaryFetchError: 要約の取得に失敗した場合
    """
    if not paper_url:
        return "URLなし"

    try:
        _validate_url(paper_url)
    except InvalidURLError as e:
        logger.warning(f"無効なURL: {paper_url}, エラー: {e}")
        return f"無効なURL: {e}"

    try:
        # レート制限回避のための遅延
        time.sleep(config.RATE_LIMIT_DELAY)

        response = request_with_retry(paper_url)
        if response:
            soup = BeautifulSoup(response.content, "html.parser")
            main_content = soup.find("main")
            if main_content:
                paragraphs = main_content.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 100:
                        logger.info(f"要約取得成功: {paper_url}")
                        return text
            logger.warning(f"要約が見つかりませんでした: {paper_url}")
            return "要約が見つかりませんでした。"
        return "要約取得失敗 (Retry limit)"
    except Exception as e:
        logger.error(f"要約取得エラー: {paper_url}, エラー: {e}")
        return f"要約取得エラー: {e}"


def _extract_upvotes(article: BeautifulSoup) -> str:
    """
    articleタグからUpvote数を抽出する

    Args:
        article: BeautifulSoupのarticle要素

    Returns:
        Upvote数の文字列、見つからない場合は"0"
    """
    upvote_tag = article.find("div", string=lambda x: x and x.strip().isdigit())
    if not upvote_tag:
        upvote_tag = article.find("span", string=lambda x: x and x.strip().isdigit())
    return upvote_tag.get_text(strip=True) if upvote_tag else "0"


def get_upvotes_map(target_date: datetime.date) -> Dict[str, str]:
    """
    指定日のUpvote数を高速にスクレイピングする

    Args:
        target_date: 取得対象の日付

    Returns:
        論文IDをキー、Upvote数を値とする辞書

    Raises:
        UpvoteFetchError: Upvote取得中にエラーが発生した場合
    """
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"{config.BASE_URL}?date={date_str}"

    logger.info(f"Upvote取得開始: {date_str}")

    try:
        response = request_with_retry(url)
        if not response:
            logger.warning(f"Upvote取得失敗: {date_str}")
            return {}

        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("article")

        upvotes_map = {}
        for article in articles:
            # IDを取得
            link_tag = article.find("a", href=True)
            if not link_tag:
                continue
            paper_id = link_tag["href"].split("/")[-1]

            # Upvotesを取得
            upvotes = _extract_upvotes(article)
            upvotes_map[paper_id] = upvotes

        logger.info(f"Upvote取得完了: {date_str} ({len(upvotes_map)} 件)")
        return upvotes_map
    except Exception as e:
        logger.error(f"Upvote取得エラー: {date_str}, エラー: {e}")
        raise UpvoteFetchError(f"Upvote取得中にエラーが発生しました: {e}") from e


def fetch_daily_papers_from_hf(
    target_date: datetime.date,
    progress_callback: Optional[Callable[[float], None]] = None,
) -> List[Dict[str, Any]]:
    """
    指定日のHugging Face Trending Papersをスクレイピングする

    Args:
        target_date: 取得対象の日付
        progress_callback: 進捗を通知するコールバック関数（0.0〜1.0）

    Returns:
        論文情報の辞書のリスト。各辞書には以下のキーが含まれる:
            - title: 論文タイトル
            - summary: 要約
            - link: 論文へのリンク
            - date: 日付文字列（YYYY-MM-DD）
            - id: 論文ID
            - thumbnail: サムネイルURL
            - upvotes: Upvote数（文字列）

    Raises:
        Exception: データ取得中にエラーが発生した場合

    Examples:
        >>> from datetime import date
        >>> papers = fetch_daily_papers_from_hf(date(2025, 12, 31))
        >>> len(papers) > 0
        True
    """
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"{config.BASE_URL}?date={date_str}"

    logger.info(f"論文データ取得開始: {date_str}")

    try:
        response = request_with_retry(url)
        if not response:
            logger.warning(f"論文データ取得失敗: {date_str}")
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all("article")

        results = []
        total_articles = len(articles)
        logger.info(f"{total_articles} 件の論文を発見: {date_str}")

        for i, article in enumerate(articles):
            if progress_callback:
                progress_callback(i / total_articles if total_articles > 0 else 0)

            # タイトル
            title_tag = article.find("h3")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # リンク
            link_tag = article.find("a", href=True)
            link = f"https://huggingface.co{link_tag['href']}" if link_tag else ""

            # ID
            paper_id = link_tag["href"].split("/")[-1] if link_tag else ""

            # サムネイル
            thumbnail = config.CDN_THUMBNAIL_URL_TEMPLATE.format(paper_id=paper_id)

            # 詳細な要約を取得
            summary = get_paper_summary(link)

            # Upvotes
            upvotes = _extract_upvotes(article)

            results.append(
                {
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "date": date_str,
                    "id": paper_id,
                    "thumbnail": thumbnail,
                    "upvotes": upvotes,
                }
            )

        if progress_callback:
            progress_callback(1.0)

        logger.info(f"論文データ取得完了: {date_str} ({len(results)} 件)")
        return results

    except Exception as e:
        logger.error(f"論文データ取得エラー: {date_str}, エラー: {e}")
        raise Exception(f"{date_str} の論文取得中にエラーが発生しました: {e}") from e
