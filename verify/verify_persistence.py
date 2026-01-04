from utils import fetch_daily_papers_from_hf, save_data, load_data
import datetime
import os

def test_persistence():
    print("Testing Persistence Logic...")

    # 1. Fetch
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    print(f"Fetching for {date_str}...")

    papers = fetch_daily_papers_from_hf(today)
    print(f"Fetched {len(papers)} papers.")
    if len(papers) > 0:
        print(f"Sample Title: {papers[0]['title']}")
        print(f"Sample Summary: {papers[0]['summary'][:100]}...")

    # 2. Save
    print("Saving data...")
    save_data(date_str, papers)
    if os.path.exists(f"data/{date_str}.json"):
        print("File created successfully.")
    else:
        print("Error: File not created.")
        return

    # 3. Load
    print("Loading data...")
    loaded_papers = load_data(date_str)
    if loaded_papers:
        print(f"Loaded {len(loaded_papers)} papers.")
        print("Success!")
    else:
        print("Error: Could not load data.")

if __name__ == "__main__":
    test_persistence()
