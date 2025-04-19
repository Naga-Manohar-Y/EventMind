import streamlit as st
import subprocess
import sqlite3
import pandas as pd
import os

# Streamlit page configuration
st.set_page_config(page_title="EventMind", page_icon="🎉", layout="wide")

# Title and description
st.title("EventMind: Event Scraper & Lead Generator")
st.markdown("""
    Scrape Technology and Business events from Eventbrite in San Francisco, CA, or Boston, MA.
    Select your preferences below and run the pipeline!
""")

# Input form
with st.form("pipeline_form"):
    st.subheader("Configure Pipeline")
    
    # State dropdown
    state = st.selectbox("State", ["CA", "MA"])
    
    # City dropdown
    city = st.selectbox("City", ["San Francisco", "Boston"])
    
    # Category dropdown
    category = st.selectbox("Category", ["tech", "business"])
    
    # Max events slider
    max_events = st.slider("Maximum Number of Events", min_value=1, max_value=100, value=20)
    
    # Run button
    submitted = st.form_submit_button("Run Pipeline")

# Handle pipeline execution
if submitted:
    with st.spinner("Running EventMind pipeline..."):
        try:
            # Initialize progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Stage 1: Run run.py (scraping and storing events)
            status_text.write("Scraping events from Eventbrite...")
            # Prepare command to run run.py with parameters
            run_cmd = [
                "python", "run.py",
                "--city", city,
                "--state", state,
                "--category", category,
                "--max-events", str(max_events)
            ]
            # Run run.py (scraping and storing events)
            run_result = subprocess.run(run_cmd, capture_output=True, text=True)
            progress_bar.progress(50)  # 50% complete after scraping
            
            # Stage 2: Run sum_agent.py (summarization and lead scoring)
            status_text.write("Generating summaries and lead scores...")
            
            # Prepare command to run sum_agent.py
            sum_cmd = ["python", "sum_agent.py"]
            # Run sum_agent.py (summarization and lead scoring)
            sum_result = subprocess.run(sum_cmd, capture_output=True, text=True)
            progress_bar.progress(100)  # 100% complete after summarization
            status_text.write("Pipeline completed!")
            
            # Display output
            st.subheader("Pipeline Output")
            if run_result.returncode == 0 and sum_result.returncode == 0:
                st.success("Pipeline completed successfully!")
                
                # Display scraping logs
                with st.expander("Scraping Logs (run.py)", expanded=True):
                    st.text_area("Scraping Logs", run_result.stdout, height=300)
                
                # Display summarization logs
                with st.expander("Summarization Logs (sum_agent.py)", expanded=True):
                    st.text_area("Summarization Logs", sum_result.stdout, height=300)
                
                # Display results from database
                conn = sqlite3.connect("data/events.db")
                query = "SELECT id, name, city, category_name, summary, lead_score FROM events ORDER BY lead_score DESC LIMIT 5"
                df = pd.read_sql_query(query, conn)
                conn.close()
                
                st.subheader("Sample Events (Top 5 by Lead Score)")
                st.dataframe(df)
                
                # Show total events
                conn = sqlite3.connect("data/events.db")
                total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
                conn.close()
                st.metric("Total Events in Database", total_events)
            else:
                st.error("Pipeline failed.")
                if run_result.returncode != 0:
                    with st.expander("Scraping Error Logs (run.py)", expanded=True):
                        st.text_area("Scraping Errors", run_result.stderr, height=300)
                if sum_result.returncode != 0:
                    with st.expander("Summarization Error Logs (sum_agent.py)", expanded=True):
                        st.text_area("Summarization Errors", sum_result.stderr, height=300)
        except Exception as e:
            st.error(f"Error running pipeline: {str(e)}")

# Display existing events on load
st.subheader("Current Events in Database")
if os.path.exists("data/events.db"):
    conn = sqlite3.connect("data/events.db")
    query = "SELECT id, name, city, category_name, summary, lead_score FROM events ORDER BY lead_score DESC LIMIT 5"
    df = pd.read_sql_query(query, conn)
    conn.close()
    st.dataframe(df)
else:
    st.info("No events database found. Run the pipeline to populate events.")