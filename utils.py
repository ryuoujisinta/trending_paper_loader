"""
ユーティリティ関数

このモジュールは論文データの取得・保存に関するユーティリティ関数を提供します。
"""

# 標準ライブラリ
import datetime
import json
import logging
import os
from collections.abc import Callable
from logging.handlers import RotatingFileHandler
from typing import Any

# サードパーティライブラリ
from huggingface_hub import HfApi

# ローカルモジュール
from config import config

# ログディレクトリの作成
if not os.path.exists(config.LOG_DIR):
    os.makedirs(config.LOG_DIR)

# ログファイルのパス
log_file_path = os.path.join(config.LOG_DIR, config.LOG_FILE)

# ロガーの設定
logger = logging.getLogger("trending_papers")
logger.setLevel(getattr(logging, config.LOG_LEVEL))
logger.propagate = False  # ルートロガーへの伝播を停止（外部ライブラリのログ混入防止）

# Hugging Face APIクライアント
hf_api = HfApi()

if not logger.handlers:
    # ログフォーマッタ
    formatter = logging.Formatter(config.LOG_FORMAT)

    # ファイルハンドラ（ローテーション設定付き）
    file_handler = RotatingFileHandler(
        log_file_path,
        encoding="utf-8",
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # コンソールハンドラ
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def load_data(date_str: str) -> list[dict[str, Any]] | None:
    """
    ローカルJSONファイルからデータを読み込む

    Args:
        date_str: 日付文字列（YYYY-MM-DD形式）

    Returns:
        論文データのリスト、ファイルが存在しない場合はNone
    """
    file_path = os.path.join(config.DATA_DIR, f"{date_str}.json")
    if os.path.exists(file_path):
        logger.debug(f"データ読み込み: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    logger.info(f"対象日付のデータファイルが未取得です（パス: {file_path}）")
    return None


def save_data(date_str: str, data: list[dict[str, Any]]) -> None:
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


def get_upvotes_map(target_date: datetime.date) -> dict[str, str]:
    """
    指定日のUpvote数をAPI経由で取得する

    Args:
        target_date: 取得対象の日付

    Returns:
        論文IDをキー、Upvote数を値とする辞書
    """
    date_str = target_date.strftime("%Y-%m-%d")
    logger.info(f"Upvote取得開始: {date_str}")

    try:
        papers = list(hf_api.list_daily_papers(date=date_str))
        upvotes_map = {paper.id: str(paper.upvotes) for paper in papers}
        logger.info(f"Upvote取得完了: {date_str} ({len(upvotes_map)} 件)")
        return upvotes_map
    except Exception as e:
        logger.error(f"Upvote取得エラー: {date_str}, エラー: {e}")
        # APIエラー時は空の辞書を返して処理を続行させる
        return {}


def fetch_daily_papers_from_hf(
    target_date: datetime.date,
    progress_callback: Callable[[float], None] | None = None,
) -> list[dict[str, Any]]:
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
    logger.info(f"論文データ取得開始: {date_str}")

    try:
        # APIを使用して論文リストを取得
        papers = list(hf_api.list_daily_papers(date=date_str))

        results = []
        total_articles = len(papers)
        logger.info(f"{total_articles} 件の論文を発見: {date_str}")

        for i, paper in enumerate(papers):
            if progress_callback:
                progress_callback(i / total_articles if total_articles > 0 else 0)

            # 必要な情報を抽出
            title = paper.title
            paper_id = paper.id
            link = f"https://huggingface.co/papers/{paper_id}"

            # サムネイル
            thumbnail = config.CDN_THUMBNAIL_URL_TEMPLATE.format(paper_id=paper_id)

            # 要約 (APIの結果にsummaryが含まれている場合はそれを使用)
            summary = paper.summary if hasattr(paper, 'summary') and paper.summary else "要約なし"

            # Upvotes
            upvotes = str(paper.upvotes) if hasattr(paper, 'upvotes') else "0"

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
