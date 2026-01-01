from huggingface_hub import HfApi
import datetime

api = HfApi()
target_date = datetime.date(2026, 1, 1).strftime("%Y-%m-%d")
try:
    papers = list(api.list_daily_papers(date=target_date))
    print(f"Successfully fetched {len(papers)} papers for {target_date}")
    if papers:
        print(f"First paper: {papers[0].title}")
except AttributeError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Other error: {e}")
