import requests
from bs4 import BeautifulSoup
import sys

# Set encoding to utf-8 for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def inspect_upvotes():
    url = "https://huggingface.co/papers"
    print(f"Fetching {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all('article')

            print(f"Found {len(articles)} articles.")

            for i, article in enumerate(articles[:10]):
                title = article.find('h3').get_text(strip=True) if article.find('h3') else "No Title"

                # Try to find upvotes
                # Often in HF papers it's a number next to a heart icon or similar
                # Looking for text that is purely numeric and near the bottom/top
                upvote_count = "N/A"

                # Check for div/span with numeric content
                # Based on previous one-liner output, '58' appeared after the author
                all_text = article.get_text(separator=' | ', strip=True)
                print(f"\n--- Article {i+1} : {title} ---")
                print(f"Text Snippet: {all_text[:150]}...")

                # Try to find exactly where the number is
                # Usually it's in a specific div class
                upvote_div = article.find('div', string=lambda x: x and x.strip().isdigit())
                if upvote_div:
                    upvote_count = upvote_div.get_text(strip=True)
                else:
                    # Look for span
                    upvote_span = article.find('span', string=lambda x: x and x.strip().isdigit())
                    if upvote_span:
                        upvote_count = upvote_span.get_text(strip=True)

                print(f"Detected Upvotes: {upvote_count}")

        else:
            print(f"Failed: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_upvotes()
