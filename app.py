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
    Scrape **Technology, Business, and Sales** events from Eventbrite across major US cities.
    Enrich them with AI-generated summaries and lead scores. 🚀
""")

# 📍 State-to-City mapping
city_map = {
    "CA": ["San Francisco", "Los Angeles", "San Diego"],
    "MA": ["Boston", "Cambridge"],
    "NY": ["New York", "Brooklyn"],
    "WA": ["Seattle"],
    "TX": ["Austin", "Dallas", "Houston"]
}

# State and City selection
st.subheader("⚙️ Configure EventMind Pipeline")

# Initialize session state
if "selected_state" not in st.session_state:
    st.session_state.selected_state = "CA"
if "selected_city" not in st.session_state:
    st.session_state.selected_city = city_map[st.session_state.selected_state][0]

# Handle state selection
new_state = st.selectbox(
    "State",
    list(city_map.keys()),
    index=list(city_map.keys()).index(st.session_state.selected_state),
    help="Select a state to filter cities.",
    key="state_select"
)

if new_state != st.session_state.selected_state:
    st.session_state.selected_state = new_state
    st.session_state.selected_city = city_map[new_state][0]
    st.rerun()  # Force rerender to refresh city dropdown

# Handle city selection
city = st.selectbox(
    "City",
    city_map[st.session_state.selected_state],
    index=city_map[st.session_state.selected_state].index(st.session_state.selected_city),
    help="Select a city within the chosen state.",
    key="city_select"
)
st.session_state.selected_city = city

# Debug output (remove after testing)
st.write(f"Debug: Selected State = {st.session_state.selected_state}, Selected City = {st.session_state.selected_city}, Available Cities = {city_map[st.session_state.selected_state]}")

# Reset session state (remove after testing)
if st.button("Reset Session State"):
    for key in st.session_state:
        del st.session_state[key]
    st.rerun()

# 📄 FORM for other inputs and submission
with st.form("pipeline_form"):
    category = st.selectbox(
        "Category",
        ["tech", "business", "sales"],
        help="Choose the event category.",
        key="category_select"
    )
    max_events = st.slider(
        "Maximum Number of Events",
        min_value=1,
        max_value=100,
        value=20,
        help="Set the maximum number of events to scrape.",
        key="max_events_slider"
    )
    submitted = st.form_submit_button("🚀 Run Pipeline")

# Handle pipeline execution
if submitted:
    with st.spinner("Running EventMind pipeline..."):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            if "pipeline_logs" not in st.session_state:
                st.session_state.pipeline_logs = {"scraping": "", "summarization": ""}
            
            status_text.write("🔍 Scraping events from Eventbrite...")
            run_cmd = [
                "python", "run.py",
                "--city", st.session_state.selected_city,
                "--state", st.session_state.selected_state,
                "--category", category,
                "--max-events", str(max_events)
            ]
            run_result = subprocess.run(run_cmd, capture_output=True, text=True)
            st.session_state.pipeline_logs["scraping"] = run_result.stdout
            progress_bar.progress(50)
            
            status_text.write("Generating summaries and lead scores...")
            sum_cmd = ["python", "sum_agent.py"]
            sum_result = subprocess.run(sum_cmd, capture_output=True, text=True)
            st.session_state.pipeline_logs["summarization"] = sum_result.stdout
            progress_bar.progress(100)
            status_text.write("✅ Pipeline completed!")
            
            st.subheader("Pipeline Output")
            if run_result.returncode == 0 and sum_result.returncode == 0:
                st.success("🎉 Pipeline completed successfully!")
                with st.expander("Scraping Logs (run.py)", expanded=True):
                    st.text_area("Scraping Logs", run_result.stdout, height=300)
                    if run_result.stderr:
                        st.text_area("Scraping Warnings/Errors", run_result.stderr, height=100)
                with st.expander("Summarization Logs (sum_agent.py)", expanded=True):
                    st.text_area("Summarization Logs", sum_result.stdout, height=300)
                    if sum_result.stderr:
                        st.text_area("Summarization Warnings/Errors", sum_result.stderr, height=100)
            else:
                st.error("⚠️ Pipeline failed.")
                if run_result.returncode != 0:
                    with st.expander("Scraping Error Logs"):
                        st.text_area("Errors", run_result.stderr, height=300)
                if sum_result.returncode != 0:
                    with st.expander("Summarization Error Logs"):
                        st.text_area("Errors", sum_result.stderr, height=300)
        except Exception as e:
            st.error(f"❌ Error running pipeline: {str(e)}")

# Display existing events on load
st.subheader("🗂 Current Events in Database")
if os.path.exists("data/events.db"):
    conn = sqlite3.connect("data/events.db")
    df = pd.read_sql_query("""
        SELECT id, name, city, category_name, summary, lead_score
        FROM events
        ORDER BY lead_score DESC
    """, conn)
    conn.close()
    st.dataframe(df)
else:
    st.info("No database found. Run the pipeline to populate events.")