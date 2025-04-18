# src/benchmark.py

import os
from dotenv import load_dotenv
from crewai_tools import SerperDevTool
from src.storage.database import update_event_summary

# Make sure .env vars are loaded even in multiprocessing
load_dotenv()



search_tool = SerperDevTool()

def summarize_event(event):
    from crewai import Agent, Task, Crew, Process, LLM
    from crewai_tools import SerperDevTool
    
    # Initialize LLM
    
    llm = LLM(
    model="nvidia_nim/meta/llama-3.1-8b-instruct",
    api_key=os.getenv("NVIDIA_NIM_API_KEY"),
    temperature=0.7,
    max_tokens=500)

    event_id, event_url = event
    print(f"🧠 Processing event {event_id}")

    researcher = Agent(
        role="Researcher",
        goal="Find details from event URL",
        backstory="Web search specialist",
        tools=[SerperDevTool()],
        verbose=False,
        llm=llm
    )

    analyzer = Agent(
        role="Analyzer",
        goal="Summarize for sales insights",
        backstory="Creates 2–3 line descriptions",
        verbose=False,
        llm=llm
    )

    research_task = Task(
        description=f"Find and summarize info from {event_url}",
        expected_output="Short event insight",
        agent=researcher
    )

    summary_task = Task(
        description="Summarize event in 2–3 lines for a sales team",
        expected_output="Concise sales summary",
        agent=analyzer,
        context=[research_task]
    )

    crew = Crew(
        agents=[researcher, analyzer],
        tasks=[research_task, summary_task],
        process=Process.sequential
    )

    result = crew.kickoff()
    update_event_summary(event_id, str(result))
    print(f"✅ Done {event_id}")
