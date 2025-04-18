# run_benchmark.py

import time
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Pool
from CrewAI.Event_Finder_v2.tests.benchmark import summarize_event

DB_PATH = "data/events.db"

def get_events(n=10):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, url FROM events WHERE summary IS NULL LIMIT ?", (n,))
    rows = c.fetchall()
    conn.close()
    return rows


def benchmark_threads(events, workers=3):
    print("\n🧵 Starting Thread benchmark...")
    start = time.time()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(summarize_event, event) for event in events]
        for f in as_completed(futures):
            f.result()
    print(f"✅ Threads finished in {time.time() - start:.2f}s")


def benchmark_processes(events, workers=3):
    print("\n🔀 Starting Multiprocessing benchmark...")
    start = time.time()
    with Pool(processes=workers) as pool:
        pool.map(summarize_event, events)
    print(f"✅ Processes finished in {time.time() - start:.2f}s")


if __name__ == "__main__":
    events = get_events(n=10)  # Change this to 20, 50, 100 as needed

    benchmark_threads(events, workers=3)
    benchmark_processes(events, workers=3)
