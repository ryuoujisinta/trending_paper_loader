import os
import json
import requests
from bs4 import BeautifulSoup
import datetime
import time
import random

# Constants
DATA_DIR = "data"

def load_data(date_str):
    """Load data from local JSON file."""
    file_path = os.path.join(DATA_DIR, f"{date_str}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_data(date_str, data):
    """Save data to local JSON file."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    file_path = os.path.join(DATA_DIR, f"{date_str}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def request_with_retry(url, retries=3, delay=180):
    """
    Request with retry logic ONLY for 429 errors.
    For other errors, it stops and raises an exception.
    """
    for i in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 429:
                wait_time = delay * (2 ** i) + random.uniform(0, 1) # Exponential backoff + jitter
                print(f"429 Limit hit. Waiting {wait_time:.2f}s...")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            # If it's a 429, we already 'continue'd above, so this catch handles other RequestExceptions
            # or the case where we've exhausted retries for 429.
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 429:
                if i < retries - 1:
                    continue

            # For 429 exhausted or any other error, raise it
            raise e
    return None

def get_paper_summary(paper_url):
    """
    Fetch the summary (abstract) from the paper detail page.
    """
    if not paper_url:
        return "URLなし"

    try:
        # Rate limit prevention: small delay between summary fetches
        time.sleep(0.5)

        response = request_with_retry(paper_url)
        if response:
            soup = BeautifulSoup(response.content, "html.parser")
            main_content = soup.find('main')
            if main_content:
                paragraphs = main_content.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 100:
                        return text
            return "要約が見つかりませんでした。"
        return "要約取得失敗 (Retry limit)"
    except Exception as e:
        # Re-raise so the high-level fetch can stop if needed, or return error string?
        # User asked to stop execution and return error message.
        # For individual summaries, maybe we just return the error string to show in UI.
        return f"要約取得エラー: {e}"

def get_upvotes_map(target_date):
    """
    Quickly scrape upvote counts for papers on a specific date.
    Returns a dict: {paper_id: upvote_count_str}
    """
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"https://huggingface.co/papers?date={date_str}"

    try:
        response = request_with_retry(url)
        if not response:
            return {}

        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all('article')

        upvotes_map = {}
        for article in articles:
            # Get ID from link
            link_tag = article.find('a', href=True)
            if not link_tag:
                continue
            paper_id = link_tag['href'].split('/')[-1]

            # Get Upvotes
            upvote_tag = article.find('div', string=lambda x: x and x.strip().isdigit())
            if not upvote_tag:
                upvote_tag = article.find('span', string=lambda x: x and x.strip().isdigit())

            upvotes = upvote_tag.get_text(strip=True) if upvote_tag else "0"
            upvotes_map[paper_id] = upvotes

        return upvotes_map
    except Exception as e:
        # Propagate the error so app.py can catch it
        raise Exception(f"Upvote取得中にエラーが発生しました: {e}")

def fetch_daily_papers_from_hf(target_date, progress_callback=None):
    """
    Scrape trending papers from Hugging Face for a specific date.
    URL pattern: https://huggingface.co/papers?date=YYYY-MM-DD
    """
    date_str = target_date.strftime("%Y-%m-%d")
    url = f"https://huggingface.co/papers?date={date_str}"

    try:
        response = request_with_retry(url)
        if not response:
            return []

        soup = BeautifulSoup(response.content, "html.parser")
        articles = soup.find_all('article')

        results = []
        total_articles = len(articles)

        for i, article in enumerate(articles):
            if progress_callback:
                progress_callback(i / total_articles if total_articles > 0 else 0)

            # Title
            title_tag = article.find('h3')
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)

            # Link
            link_tag = article.find('a', href=True)
            link = f"https://huggingface.co{link_tag['href']}" if link_tag else ""

            # ID
            paper_id = link_tag['href'].split('/')[-1] if link_tag else ""

            # Thumbnail
            # Use deterministic CDN URL format: https://cdn-thumbnails.huggingface.co/social-thumbnails/papers/{arxiv_number}.png
            thumbnail = f"https://cdn-thumbnails.huggingface.co/social-thumbnails/papers/{paper_id}.png"

            # Fetch Detailed Summary
            summary = get_paper_summary(link)

            # Upvotes
            upvote_tag = article.find('div', string=lambda x: x and x.strip().isdigit())
            if not upvote_tag:
                upvote_tag = article.find('span', string=lambda x: x and x.strip().isdigit())
            upvotes = upvote_tag.get_text(strip=True) if upvote_tag else "0"

            results.append({
                "title": title,
                "summary": summary,
                "link": link,
                "date": date_str,
                "id": paper_id,
                "thumbnail": thumbnail,
                "upvotes": upvotes
            })

        if progress_callback:
            progress_callback(1.0)

        return results

    except Exception as e:
        # Propagate error message to UI
        raise Exception(f"{date_str} の論文取得中にエラーが発生しました: {e}")
