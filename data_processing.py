"""
データ処理関数

このモジュールは論文データの処理（重複排除、ソート、フィルタリング）を行う関数を提供します。
"""

from typing import Any, Dict, List


def get_numeric_upvotes(paper: Dict[str, Any]) -> int:
    """
    論文のUpvote数を整数として取得する

    Args:
        paper: 論文データの辞書

    Returns:
        Upvote数の整数値、変換できない場合は0
    """
    try:
        return int(paper.get("upvotes", 0))
    except (ValueError, TypeError):
        return 0


def deduplicate_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    論文リストから重複を排除する

    最新の日付または最も高いUpvote数を持つものを優先します。

    Args:
        papers: 論文データのリスト

    Returns:
        重複排除された論文リスト
    """
    unique_papers = {}
    for p in papers:
        key = p.get("id") or p.get("title")
        if not key:
            continue

        current_upvotes = get_numeric_upvotes(p)

        if key not in unique_papers:
            unique_papers[key] = p
        else:
            prev_p = unique_papers[key]
            prev_upvotes = get_numeric_upvotes(prev_p)

            # 新しい日付または高いUpvote数を優先
            if p["date"] > prev_p["date"] or current_upvotes > prev_upvotes:
                unique_papers[key] = p

    return list(unique_papers.values())


def sort_papers_by_date(
    papers: List[Dict[str, Any]], reverse: bool = True
) -> List[Dict[str, Any]]:
    """
    論文リストを日付順にソートする

    Args:
        papers: 論文データのリスト
        reverse: Trueの場合は新しい順、Falseの場合は古い順

    Returns:
        ソートされた論文リスト
    """
    return sorted(papers, key=lambda x: x["date"], reverse=reverse)


def sort_papers_by_upvotes(
    papers: List[Dict[str, Any]], reverse: bool = True
) -> List[Dict[str, Any]]:
    """
    論文リストをUpvote数順にソートする

    Args:
        papers: 論文データのリスト
        reverse: Trueの場合は多い順、Falseの場合は少ない順

    Returns:
        ソートされた論文リスト
    """
    return sorted(papers, key=get_numeric_upvotes, reverse=reverse)


def filter_papers(papers: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    キーワードで論文をフィルタリングする

    タイトルまたは要約にクエリが含まれる論文を抽出します（大文字小文字を区別しない）。

    Args:
        papers: 論文データのリスト
        query: 検索キーワード

    Returns:
        フィルタリングされた論文リスト
    """
    if not query:
        return papers

    query_lower = query.lower()
    filtered = []

    for p in papers:
        title = p.get("title", "").lower()
        summary = p.get("summary", "").lower()

        if query_lower in title or query_lower in summary:
            filtered.append(p)

    return filtered
