import requests
from bs4 import BeautifulSoup

def inspect_images():
    url = "https://huggingface.co/papers"
    print(f"Fetching {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            articles = soup.find_all('article')

            print(f"Found {len(articles)} articles.")

            for i, article in enumerate(articles):
                title = article.find('h3').get_text(strip=True) if article.find('h3') else "No Title"

                # Check current logic
                thumbnail = ""
                images = article.find_all('img')
                for img in images:
                    classes = img.get('class', [])
                    src = img.get('src', '')
                    # Our current stricter logic
                    if 'object-cover' in classes and 'rounded-full' not in classes:
                         thumbnail = src
                         break
                    if not thumbnail and '/avatars/' not in src and 'rounded-full' not in classes:
                         thumbnail = src

                # Check video tags
                videos = article.find_all('video')

                # Report if missing or video-only
                if not thumbnail:
                    if videos:
                         print(f"\n--- [VIDEO ONLY] Article {i+1} : {title} ---")
                         for v in videos:
                             print(f"    Video poster: {v.get('poster')}, class={v.get('class')}")
                    else:
                         print(f"\n--- [MISSING] Article {i+1} : {title} ---")
                         print("  No suitable img found. All images:")
                         for j, img in enumerate(images):
                              print(f"    Img {j}: src={img.get('src')}, class={img.get('class')}")
                else:
                    # Optional: Print successful ones if needed, but keeping log clean for errors
                    pass

        else:
            print(f"Failed: {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_images()
