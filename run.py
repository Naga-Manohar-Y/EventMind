# run.py
    
from src.scraper.selenium_scraper import get_event_ids
from src.scraper.api_client import get_event_details, get_venue_details, get_categories
from src.storage.database import init_db, save_event
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main(args):
    
    logger.info("Initializing EventMind pipeline...")
    
    # Initialize database
    init_db()
    
    # Prepare query parameters
    query_params = {
        "state": args.state,
        "city": args.city,
        "category": args.category,
        "max_events": args.max_events
    }
    
    logger.info(f"Scraping events with parameters: {query_params}")
    
    # Fetch event IDs using Selenium scraper
    event_ids = get_event_ids(query_params)
    
    logger.info(f"Collected {len(event_ids)} event IDs")

    # Fetch categories once
    logger.info("Fetching event categories...")
    category_map = get_categories()
    logger.info(f"Retrieved {len(category_map)} categories")

    for eid in event_ids:
        event = get_event_details(eid)
        if not event or not event.get("id"):
            print(f"❌ Skipped event {eid}: No data")
            continue
        if event.get("online_event", False) or not event.get("venue_id"):
            print(f"ℹ️ Skipped event {eid}: Online event")
            continue

        # Fetch venue details
        logger.info(f"Fetching venue details for venue ID: {event['venue_id']}")
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
        logger.info(f"Saving event: {event_data['name']} ({event_data['city']})")
        save_event(event_data)
        logger.info(f"Saved event ID: {eid}")
    
    logger.info("EventMind scraping pipeline completed")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="EventMind: Scrape events from Eventbrite")
    parser.add_argument("--state", default="CA", help="State (e.g., CA, MA)")
    parser.add_argument("--city", default="San Francisco", help="City (e.g., San Francisco, Boston)")
    parser.add_argument("--category", default="tech", help="Category (e.g., tech, business)")
    parser.add_argument("--max-events", type=int, default=20, help="Maximum number of events to scrape")
    args = parser.parse_args()
    main(args)
