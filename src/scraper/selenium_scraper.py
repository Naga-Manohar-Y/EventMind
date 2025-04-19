# src/scraper/selenium_scraper.py
    
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_event_ids(query_params):
    
    state = query_params.get("state").lower()
    city = query_params.get("city").lower().replace(" ", "-")
    category = query_params.get("category").lower()
    max_events = query_params.get("max_events", 20)
    
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    event_ids = set()
    page = 1

    #print(f"🔍 Scraping Eventbrite events in {city}...")
    logger.info(f"🔍 Scraping Eventbrite events in {city}, {state} for {category}...")

    while len(event_ids) < max_events:
        url = f"https://www.eventbrite.com/d/{state}--{city}/{category}--events/?page={page}"
        #print(f"🌐 Visiting page {page}: {url}")
        logger.info(f"🌐 Visiting page {page}: {url}")
        driver.get(url)
        time.sleep(3)  # wait for events to load

        links = driver.find_elements("xpath", "//a[contains(@href, '/e/')]")
        if not links:
            print("🚫 No more events found.")
            break

        for link in links:
            href = link.get_attribute("href")
            match = re.search(r'/e/.+-([0-9]+)', href)
            if match:
                event_ids.add(match.group(1))
                if len(event_ids) >= max_events:
                    break

        page += 1

    driver.quit()
    print(f"✅ Collected {len(event_ids)} event IDs.")
    return list(event_ids)

