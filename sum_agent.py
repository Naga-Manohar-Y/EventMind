#sum_agent.py

import sqlite3
import os
import time
from multiprocessing import Pool
from crewai import Agent, Crew, Process, Task, LLM
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def update_event_summary(event_id, data):
    """Update event with summary, lead_score, and retry logic."""
    for _ in range(3):
        try:
            conn = sqlite3.connect("data/events.db")
            c = conn.cursor()
            c.execute("""
                UPDATE events
                SET summary = ?, lead_score = ?
                WHERE id = ?
            """, (
                data.get('summary', ''),
                data.get('lead_score', None),
                event_id
            ))
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(0.1)
            else:
                raise
        finally:
            conn.close()
    raise sqlite3.OperationalError("Failed to update after retries")

def fetch_event_data(event_id):
    """Fetch event data from SQLite database."""
    data = {}
    try:
        conn = sqlite3.connect("data/events.db")
        c = conn.cursor()
        c.execute("""
            SELECT name, url, city, is_free, venue_name, category_name
            FROM events
            WHERE id = ?
        """, (event_id,))
        result = c.fetchone()
        if result:
            data['name'] = result[0]
            data['url'] = result[1]
            data['city'] = result[2]
            data['is_free'] = result[3]
            data['venue_name'] = result[4]
            data['category_name'] = result[5]
        else:
            logger.error(f"❌ No data found for event {event_id}")
            # print(f"❌ No data found for event {event_id}")
    except sqlite3.Error as e:
        logger.error(f"❌ Failed to fetch data for {event_id}: {e}")
        # print(f"❌ Failed to fetch data for {event_id}: {e}")
    finally:
        conn.close()
    return data

def summarize_event(event):
    """Summarize and score one event."""
 #   from crewai import Agent, Task, Crew, Process, LLM
    from crewai_tools import SerperDevTool
    from dotenv import load_dotenv

    load_dotenv()
    event_id, event_url = event
    print(f"🧠 Processing event: {event_id}")

    try:
        # Fetch event data from database
        data = fetch_event_data(event_id)
        if not data:
            logger.error(f"❌ Skipping event {event_id}: No data")
            #print(f"❌ Skipping event {event_id}: No data")
            return event_id, False

        # CrewAI setup
        search_tool = SerperDevTool()
        llm = LLM(
            model="nvidia_nim/meta/llama-3.2-3b-instruct",
            api_key=os.getenv("NVIDIA_NIM_API_KEY"),
            temperature=0.6,
            max_tokens=500
        )
        
    
        researcher = Agent(
            role="Event Researcher",
            goal="Gather event context from web using its URL",
            backstory="""You're a senior event intelligence analyst with years of experience researching professional and tech conferences.
            You specialize in using advanced search techniques to uncover detailed information about event audiences, industries, and speaker intent.
            You know how to dig deeper into event listings, uncovering the business potential behind each gathering.""",
            tools=[search_tool],
            verbose=False,
            llm=llm
        )

        analyzer = Agent(
            role="Event Analyzer",
            goal="Summarize events for sales teams in 2-3 crisp lines",
            backstory="""You're a B2B content strategist with a sharp ability to condense complex event data into sales-focused summaries.
            You've worked with sales enablement teams at SaaS companies and know exactly what makes an event valuable for outbound engagement.
            You help sales teams quickly identify which events are worth pursuing by distilling value propositions clearly.""",
            verbose=False,
            llm=llm
        )

        lead_scorer = Agent(
            role="Lead Scoring Analyst",
            goal="Evaluate event potential for sales lead generation",
            backstory="""You're a growth strategist specializing in B2B SaaS pipeline development. 
            You've built lead scoring models used by SDR and GTM teams to prioritize outreach opportunities from events. 
            Your strength is evaluating how well an event aligns with key buyer personas, company ICPs, and intent signals. 
            You think like a sales leader who only wants to invest time in high-yield events.""",
            verbose=False,
            llm=llm
        )

        research_task = Task(
            description=(
                f"Use the URL to search for details about this event: {event_url}. "
                f"Event: {data.get('name', 'Unknown')}, City: {data.get('city', 'Unknown')}, "
                f"Free: {'Yes' if data.get('is_free', 0) else 'No'}. "
                "Focus on sales-relevant insights (audience, purpose)."
            ),
            expected_output="Key event details: theme, target audience, purpose.",
            agent=researcher
        )

        summary_task = Task(
            description="Summarize the event into 2–3 concise sales-focused lines.",
            expected_output="Sales-oriented event summary.",
            agent=analyzer,
            context=[research_task]
        )

        scoring_task = Task(
            description=(
                f"Rate this event from 1 to 10 as a lead generation opportunity for a B2B SaaS company targeting tech buyers.\n\n"
                f"Use the following data:\n"
                f"- Is Free: {'Yes' if data.get('is_free', 0) else 'No'}\n"
                f"- City: {data.get('city', 'Unknown')}\n"
                f"- Venue: {data.get('venue_name', 'Unknown')}\n"
                f"- Category: {data.get('category_name', 'Unknown')}\n"
                f"- Summary: \"{data.get('summary', 'No summary available')}\"\n\n"
                f"Respond only with the number (1-10)."
            ),
            expected_output="A single number from 1 to 10",
            agent=lead_scorer,
            context=[summary_task]
        )

        crew = Crew(
            agents=[researcher, analyzer, lead_scorer],
            tasks=[research_task, summary_task, scoring_task],
            process=Process.sequential,
            verbose=False
        )

        time.sleep(1)  # Serper rate limit
        logger.info(f"Kicking off CrewAI for event {event_id}")
        results = crew.kickoff()

        # Parse results safely
        try:
            summary_result = results.tasks_output[1].raw if len(results.tasks_output) > 1 else ''
            score_result = results.tasks_output[2].raw if len(results.tasks_output) > 2 else ''
        except (IndexError, AttributeError) as e:
            logger.error(f"❌ Failed to parse results for {event_id}: {e}")
            #print(f"❌ Failed to parse results for {event_id}: {e}")
            return event_id, False

        data['summary'] = summary_result.strip()
        try:
            score = int(score_result.strip())
            if 1 <= score <= 10:
                data['lead_score'] = score
                logger.info(f"Assigned lead score {score} for event {event_id}")
            else:
                logger.error(f"❌ Invalid score {score} for {event_id}, skipping")
                # print(f"❌ Invalid score {score} for {event_id}, skipping")
                data['lead_score'] = None
        except ValueError:
            logger.error(f"❌ Invalid score format '{score_result}' for {event_id}, skipping")
            # print(f"❌ Invalid score format '{score_result}' for {event_id}, skipping")
            data['lead_score'] = None

        # Update database
        update_event_summary(event_id, data)
        # print(f"✅ Stored summary and score for {event_id}")
        logger.info(f"✅ Stored summary and score for event {event_id}")
        return event_id, True

    except Exception as e:
        logger.error(f"❌ Failed event {event_id}: {e}")
        # print(f"❌ Failed event {event_id}: {e}")
        return event_id, False

def run_summary_for_events():
    """Run summarization and scoring for all unsummarized events."""
    logger.info("Starting EventMind summarization pipeline...")
    
    conn = sqlite3.connect("data/events.db")
    c = conn.cursor()
    c.execute("SELECT id, url FROM events WHERE summary IS NULL LIMIT 50")
    events = c.fetchall()
    conn.close()

    if not events:
        # print("📭 No events to summarize.")
        logger.info("📭 No events to summarize.")
        return

    # print(f"📦 Found {len(events)} events to summarize and score.")
    logger.info(f"📦 Found {len(events)} events to summarize and score.")

    with Pool(processes=4) as pool:
        results = pool.map(summarize_event, events)

    for event_id, success in results:
        status = "✅ Completed" if success else "❌ Failed"
        # print(f"{status} event {event_id}")
        logger.info(f"{status} event {event_id}")
        
    logger.info("EventMind summarization pipeline completed")

if __name__ == "__main__":
    run_summary_for_events()