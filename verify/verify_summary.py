from huggingface_hub import HfApi
import requests
from bs4 import BeautifulSoup

def test_fetch_summary(paper_id):
    print(f"Testing summary fetch for {paper_id}...")

    url = f"https://huggingface.co/papers/{paper_id}"
    print(f"Scraping {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Debug: Print title to confirm page
            title = soup.find('h1')
            print(f"Page Title: {title.get_text(strip=True) if title else 'Not found'}")

            # Find Abstract
            # Looking for typical abstract containers.
            # Often it's a <p> following "Abstract" or just a large block of text.
            # Let's inspect the text content of the first few paragraphs in the main section.

            main_content = soup.find('main')
            if main_content:
                paragraphs = main_content.find_all('p')
                print(f"Found {len(paragraphs)} paragraphs in main.")
                for i, p in enumerate(paragraphs[:5]):
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        print(f"--- Paragraph {i} ---")
                        print(text[:200] + "...")

            # Specific check for abstract div if known
            # <div class="pb-8"> ... <p class="text-gray-700"> ?

        else:
            print(f"Failed: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Use a known ID from previous API list
    test_fetch_summary("2512.23705")
