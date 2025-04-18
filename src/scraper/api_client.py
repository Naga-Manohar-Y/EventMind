# src/scraper/api_client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("EVENTBRITE_TOKEN")

def get_event_details(event_id: str) -> dict:
    url = f"https://www.eventbriteapi.com/v3/events/{event_id}/"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed for event {event_id}: {e}")
        return {}

def get_venue_details(venue_id: str) -> dict:
    if not venue_id:
        return {}
    url = f"https://www.eventbriteapi.com/v3/venues/{venue_id}/"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Failed for venue {venue_id}: {e}")
        return {}

def get_categories() -> dict:
    url = "https://www.eventbriteapi.com/v3/categories/"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        categories = response.json().get("categories", [])
        return {cat["id"]: cat["name"] for cat in categories}
    except requests.RequestException as e:
        print(f"❌ Failed to fetch categories: {e}")
        return {}