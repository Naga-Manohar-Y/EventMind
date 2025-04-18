import sqlite3
conn = sqlite3.connect("data/events.db")
c = conn.cursor()
c.execute("SELECT lead_score FROM events")
print(c.fetchall())
conn.close()


'''
sqlite3 data/events.db
'''