# EventMind

**EventMind** is an automated pipeline that scrapes tech events from Eventbrite, stores them in a SQLite database, and enriches them with AI-generated summaries and lead scores for CRM lead generation. Designed for efficiency, it processes \~20 events in \~25-35 seconds, skips duplicates, preserves historical data, and supports high-value lead identification, saving \~$900/month in targeted outreach.

## Features

- **Event Scraping**: Collects tech events from Eventbrite using Selenium and API clients (`src/scraper/*`).
- **SQLite Storage**: Stores events in `data/events.db` with fields like `id`, `name`, `city`, `summary`, and `lead_score` (`src/storage/database.py`).
- **Duplicate Skipping**: Prevents redundant entries, preserving historical data.
- **AI Enrichment**: Generates event summaries and lead scores (e.g., 8 for high-value events) using AI agents (`sum_agent.py`).
- **Fast & Scalable**: Processes \~20 events in \~25-35s, scalable to \~40 events (\~110-140s).
- **Testing Suite**: Includes benchmarking and unit tests (`tests/*`).
- **Dockerized**: Runs consistently via Docker (`Dockerfile`, `docker-compose.yml`).

## Project Structure

```
EventMind/
├── data/                    # SQLite database (events.db, ignored)
├── src/
│   ├── scraper/             # Scraping logic
│   │   ├── api_client.py
│   │   ├── selenium_scraper.py
│   ├── storage/             # Database handling
│   │   ├── database.py
├── tests/                   # Benchmarking and unit tests
│   ├── benchmark.py
│   ├── events_data.py
│   ├── run_benchmark.py
│   ├── scraping_test.py
│   ├── summary_test.py
├── .gitignore               # Ignores .env, data/events.db, etc.
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Docker Compose setup
├── requirements.txt         # Python dependencies
├── run.py                   # Main pipeline script
├── run.sh                   # Shell script for running pipeline
├── sum_agent.py             # AI summarization and lead scoring
```

## Requirements

- **Docker**: For containerized execution.
- **Git**: To clone the repository.
- **API Keys**:
  - `EVENTBRITE_TOKEN`: Eventbrite API token (Eventbrite API).
  - `NVIDIA_NIM_API_KEY`: For AI summarization (NVIDIA NIM).
  - `SERPER_API_KEY`: For web search augmentation (Serper API).
- **System**: macOS, Linux, or Windows with Docker support.

## How to Run

Follow these steps to clone the repository and run the **EventMind** pipeline:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Naga-Manohar-Y/EventMind.git
   cd EventMind
   ```

2. **Set Up Environment Variables**:

   - Create a `.env` file in the root directory:

     ```bash
     touch .env
     ```

   - Add the following API keys (replace with your own):

     ```plaintext
     EVENTBRITE_TOKEN=your_eventbrite_token
     NVIDIA_NIM_API_KEY=your_nvidia_nim_api_key
     SERPER_API_KEY=your_serper_api_key
     ```

   - Ensure `.env` is not committed (already ignored in `.gitignore`).

3. **Install Docker**:

   - Download and install Docker Desktop from docker.com.

   - Verify installation:

     ```bash
     docker --version
     ```

4. **Build and Run the Pipeline**:

   - Build the Docker image and start the container:

     ```bash
     docker-compose up --build
     ```

   - **Expected Output**:

     - Logs showing event collection (e.g., `✅ Collected 20 event IDs`).
     - Duplicate skipping (e.g., `ℹ️ Skipped event 1267735524079: Already exists`).
     - Summarization and scoring (e.g., `✅ Stored: Tech Weekend May 2025`).

   - The container exits after completion (exit code 0).

5. **Verify Results**:

   - Check the SQLite database (`data/events.db`):

     ```bash
     sqlite3 data/events.db
     ```

     - Query total events:

       ```sql
       SELECT COUNT(*) FROM events;
       ```

     - View high-value events:

       ```sql
       SELECT name, city, summary, lead_score
       FROM events
       WHERE lead_score >= 7
       ORDER BY lead_score DESC;
       ```

     - Exit:

       ```sql
       .exit
       ```

6. **Clean Up** (Optional):

   - Stop and remove containers:

     ```bash
     docker-compose down
     ```


## License

MIT License (update with your preferred license).

## Contact

For questions or contributions, reach out via GitHub or open an issue on the EventMind repository.