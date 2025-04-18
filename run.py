# run.py
    
from src.scraper.selenium_scraper import get_event_ids
from src.scraper.api_client import get_event_details, get_venue_details, get_categories
from src.storage.database import init_db, save_event

def main():
    init_db()
    event_ids = get_event_ids(city="san-francisco", max_events=30)

    # Fetch categories once
    category_map = get_categories()

    for eid in event_ids:
        event = get_event_details(eid)
        if not event or not event.get("id"):
            print(f"❌ Skipped event {eid}: No data")
            continue
        if event.get("online_event", False) or not event.get("venue_id"):
            print(f"ℹ️ Skipped event {eid}: Online event")
            continue

        # Fetch venue details
        venue = get_venue_details(event["venue_id"])
        event_data = {
            "id": event["id"],
            "name": event["name"]["text"],
            "url": event["url"],
            "start_utc": event["start"]["utc"],
            "city": venue.get("address", {}).get("city", ""),
            "country": venue.get("address", {}).get("country", ""),
            "is_free": 1 if event["is_free"] else 0,
            "venue_name": venue.get("name", ""),
            "category_name": category_map.get(event.get("category_id", ""), "")
        }

        save_event(event_data)

if __name__ == "__main__":
    main()
