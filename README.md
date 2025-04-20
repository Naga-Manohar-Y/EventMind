# EventMind

EventMind is an automated pipeline that scrapes tech and professional events from Eventbrite, stores them in a SQLite database, and enriches them with AI-generated summaries and lead scores for B2B SaaS lead generation. It efficiently processes \~20 events in \~25-35 seconds, skips duplicates, preserves historical data, and identifies high-value events for targeted sales outreach.

## Architecture

![Architecture](https://github.com/Naga-Manohar-Y/EventMind/blob/main/src/Architecture.jpeg)
The pipeline uses a modular design:

- **Scraper**: Collects events via Eventbrite API and Selenium (`src/scraper/`).
- **Storage**: Saves events to `data/events.db` (`src/storage/`).
- **AI Enrichment**: Summarizes and scores events using AI agents (`sum_agent.py`).
- **Docker**: Ensures consistent execution (`Dockerfile`, `docker-compose.yml`).

## Features

- **Event Scraping**: Collects tech and professional events from Eventbrite using API and Selenium (`src/scraper/api_client.py`, `src/scraper/selenium_scraper.py`).
- **SQLite Storage**: Stores events in `data/events.db` with fields like `id`, `name`, `city`, `summary`, and `lead_score` (`src/storage/database.py`).
- **Duplicate Skipping**: Prevents redundant entries, preserving historical data.
- **AI Enrichment**: Generates concise summaries and lead scores (e.g., 8 for high-value events) using AI agents (`sum_agent.py`).
- **Fast & Scalable**: Processes \~20 events in \~25-35s, scalable to \~40 events (\~110-140s).
- **Testing Suite**: Includes benchmarking and unit tests (`tests/benchmark.py`, `tests/scraping_test.py`, `tests/summary_test.py`).
- **Dockerized**: Runs consistently via Docker (`Dockerfile`, `docker-compose.yml`).

## Project Structure

```
EventMind/
├── data/                    # SQLite database (events.db, ignored)
├── src/                     # Source code
│   ├── scraper/             # Scraping logic
│   │   ├── api_client.py
│   │   └── selenium_scraper.py
│   ├── storage/             # Database handling
│   │   └── database.py
│   ├── Architecture.jpeg    # Architecture diagram
├── tests/                   # Benchmarking and unit tests
│   ├── benchmark.py
│   ├── events_data.py
│   ├── run_benchmark.py
│   ├── scraping_test.py
│   ├── summary_test.py
├── Dockerfile               # Docker image configuration
├── docker-compose.yml       # Docker Compose setup
├── requirements.txt         # Python dependencies
├── app.py                   # Streamlit app (if applicable)
├── run.py                   # Main pipeline script
├── run.sh                   # Shell script for running pipeline
├── sum_agent.py             # AI summarization and lead scoring
├── .gitignore               # Ignores .env, data/events.db, __pycache__
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

Follow these steps to set up and run the EventMind pipeline:

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Naga-Manohar-Y/EventMind.git
   cd EventMind
   ```

2. **Set Up Environment Variables**: Create a `.env` file in the root directory:

   ```bash
   touch .env
   ```

   Add the following API keys (replace with your own):

   ```
   EVENTBRITE_TOKEN=your_eventbrite_token
   NVIDIA_NIM_API_KEY=your_nvidia_nim_api_key
   SERPER_API_KEY=your_serper_api_key
   ```

   Ensure `.env` is not committed (already ignored in `.gitignore`).

3. **Install Docker**: Download and install Docker Desktop. Verify installation:

   ```bash
   docker --version
   ```

4. **Build and Run the Pipeline**: Build the Docker image and start the container:

   ```bash
   docker-compose up --build
   ```

   Expected output in logs:

   - Event collection: `✅ Collected 20 event IDs`
   - Duplicate skipping: `ℹ️ Skipped event 1267735524079: Already exists`
   - Summarization and scoring: `✅ Stored: Tech Weekend May 2025`The container exits after completion (exit code 0).

5. **Verify Results**: Check the SQLite database (`data/events.db`):

   ```bash
   sqlite3 data/events.db
   ```

   Query total events:

   ```sql
   SELECT COUNT(*) FROM events;
   ```

   View high-value events:

   ```sql
   SELECT name, city, summary, lead_score
   FROM events
   WHERE lead_score >= 7
   ORDER BY lead_score DESC;
   ```

   Exit:

   ```sql
   .exit
   ```

6. **Clean Up (Optional)**: Stop and remove containers:

   ```bash
   docker-compose down
   ```

## Testing

Run the test suite to verify functionality:

```bash
docker-compose run --rm eventmind python -m unittest discover tests
```

- **Benchmarking**: `tests/benchmark.py`, `tests/run_benchmark.py`
- **Scraping Tests**: `tests/scraping_test.py`
- **Summary Tests**: `tests/summary_test.py`

## License

MIT License

Copyright (c) \[YEAR\] \[COPYRIGHT HOLDER\]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contact

For questions or contributions, reach out via GitHub or open an issue on the EventMind repository.
