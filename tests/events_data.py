
# import sqlite3

# DB_PATH = "../data/events.db"


# def print_events():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     c.execute("""
#     SELECT * FROM events"""
#     )
    
#     records = c.fetchall()
    
#     if records:
#         for record in records:
#             print(record)
#     else:
#         print("No records found.")

#     conn.commit()
#     conn.close()
    
    
# if __name__ == "__main__":
#     print_events()
    
# '''

# '''

import requests
import json

EVENT_ID = '1290155242059'
TOKEN = ''  # Replace with your actual token

url = f'https://www.eventbriteapi.com/v3/events/{EVENT_ID}/'
headers = {
    'Authorization': f'Bearer {TOKEN}'
}

response = requests.get(url, headers=headers)

# Print all JSON keys/values nicely
event_data = response.json()
print(json.dumps(event_data, indent=2))

print("\n\n")

VENUE_ID = '261139373'  

url = f'https://www.eventbriteapi.com/v3/venues/{VENUE_ID}/'
headers = {
    'Authorization': f'Bearer {TOKEN}'
}

response = requests.get(url, headers=headers)

# Print all JSON keys/values nicely
venue_data = response.json()
print(json.dumps(venue_data, indent=2))
print("\n\n")


ORG_ID = '58039330153'
url = f'https://www.eventbriteapi.com/v3/organizations/{ORG_ID}/'
headers = {
    'Authorization': f'Bearer {TOKEN}'
}

response = requests.get(url, headers=headers)

# Print all JSON keys/values nicely
org_members_data = response.json()
print(json.dumps(org_members_data, indent=2))