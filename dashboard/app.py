import streamlit as st
import sqlite3
import sys
import os

# Ensure the app can import our custom modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.rules import calculate_remaining_requirements
from agent.orchestrator import process_query

st.set_page_config(page_title="BITS Course Recommender", layout="wide")

# Helper function to fetch all courses for the multiselect dropdown
@st.cache_data
def get_all_courses():
    if not os.path.exists('data_processed/app.db'):
        return []
    conn = sqlite3.connect('data_processed/app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT course_code, title FROM Course")
    courses = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
    conn.close()
    return courses

st.title("🎓 BITS Academic Course Recommender")

# --- SIDEBAR: STUDENT PROFILE ---
st.sidebar.header("Student Profile")
campus = st.sidebar.selectbox("Campus", ["Pilani", "Goa", "Hyderabad", "Dubai"])
batch = st.sidebar.number_input("Batch Year", min_value=2020, max_value=2026, value=2023)
degree = st.sidebar.selectbox("Degree", ["B.E. Computer Science"])
current_semester = st.sidebar.number_input("Current Semester", min_value=1, max_value=8, value=5)

all_courses = get_all_courses()
completed = st.sidebar.multiselect("Completed Courses", all_courses)
# Extract just the course codes from the dropdown selection
completed_codes = [c.split(" - ")[0] for c in completed]

interests = st.sidebar.text_area("Academic Interests", "e.g., Machine Learning, Systems, Finance...")

# Build the profile dictionary to pass to our engine
student_profile = {
    "campus": campus,
    "batch": batch,
    "degree": degree,
    "current_semester": current_semester,
    "completed_courses": completed_codes,
    "interests": interests
}

# --- TOP MAIN: PROGRESS BARS ---
st.subheader("Academic Progress")
try:
    reqs = calculate_remaining_requirements(student_profile)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Remaining CDCs", len(reqs.get("remaining_cdcs", [])))
    with col2:
        del_comp = reqs["DEL"]["completed"]
        del_req = reqs["DEL"]["required"]
        st.progress(min(del_comp / del_req, 1.0) if del_req > 0 else 1.0, text=f"DELs: {del_comp}/{del_req} Completed")
    with col3:
        opel_comp = reqs["OPEL"]["completed"]
        opel_req = reqs["OPEL"]["required"]
        st.progress(min(opel_comp / opel_req, 1.0) if opel_req > 0 else 1.0, text=f"OPELs: {opel_comp}/{opel_req} Completed")
except Exception as e:
    st.warning("Please ensure the database is initialized. Run `python ingestion/init_db.py` and `python ingestion/load_seed_data.py`.")

st.divider()

# --- BOTTOM MAIN: CHAT INTERFACE ---
st.subheader("Course Advisor")

# Initialize chat history in Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about courses (e.g., 'Suggest DELs related to AI with no midsem')"):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Analyzing requirements and searching courses..."):
            try:
                # We silently append the user's interests to the prompt so the LLM has context
                contextual_prompt = f"[User Interests: {interests}]\n\nUser Query: {prompt}"
                
                # Call the orchestrator
                response = process_query(contextual_prompt, student_profile)
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                # Gracefully catch 503s or other API errors
                error_msg = f"**Network Error:** The AI server is currently busy or unavailable. Please try again in a few moments.\n\n*(Error details: {e})*"
                st.error(error_msg)