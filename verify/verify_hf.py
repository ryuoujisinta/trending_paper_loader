from huggingface_hub import list_papers
import requests
from bs4 import BeautifulSoup
import datetime

print("1. Testing list_papers(query='...')...")
try:
    papers = list_papers(query="Artificial Intelligence")
    for i, paper in enumerate(papers):
        if i >= 3: break
        print(f"\n--- API Paper {i+1} ---")
        print(f"ID: {paper.id}")
        # Inspect attributes again
        print(f"Attr: {dir(paper)}")
except Exception as e:
    print(f"API Error: {e}")

print("\n2. Testing Scraping https://huggingface.co/papers ...")
try:
    url = "https://huggingface.co/papers"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        # Trying to find paper titles.
        # Structure changes often, but usually headers or articles.
        # Looking for h3 or specific classes.

        # Based on typical HF structure
        articles = soup.find_all('article')
        print(f"Found {len(articles)} articles via scraping.")

        for i, article in enumerate(articles):
            if i >= 3: break
            title_tag = article.find('h3')
            if title_tag:
                 print(f"--- Scraped Paper {i+1} ---")
                 print(f"Title: {title_tag.get_text(strip=True)}")
                 link = article.find('a', href=True)
                 if link:
                     print(f"Link: https://huggingface.co{link['href']}")
    else:
        print(f"Scraping Failed: {response.status_code}")
except Exception as e:
    print(f"Scraping Error: {e}")
