```markdown
# BITS Academic Course Recommender

This is my submission for the course recommender project. It's an AI-powered dashboard that helps BITS students pick their courses. 

Instead of feeding massive PDFs to an LLM (which usually leads to hallucinated graduation rules), this project splits the work: a pure Python engine handles the strict academic math and database lookups, while the Gemini API handles the natural language chatting and preference matching.

## How to Run It

**1. Set up the environment**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

```

**2. Add your API Key**
Create a `.env` file in the main folder and add your Google Gemini key:

```text
GEMINI_API_KEY=your_api_key_here

```

**3. Build the Database**
Put the raw PDFs (`bulletin[1].pdf`, `timetable[1].pdf`, `Academic-Regulations-2023[1].pdf`, and your course handouts) into the `/data_raw/` folder. Then run these scripts in this exact order to build and link the SQLite database:

```powershell
python ingestion/init_db.py
python ingestion/load_seed_data.py
python ingestion/parse_rules.py
python ingestion/parse_timetable.py
python ingestion/parse_bulletin.py
python ingestion/parse_handouts.py

```

**4. Start the Dashboard**

```powershell
streamlit run dashboard/app.py

```

## How It Works (Architecture)

I wanted to make sure the AI never makes up academic rules, so the system is built with some strict boundaries:

* **No PDF Reading at Runtime:** All the PDFs are pre-processed offline into a clean SQLite database (`app.db`). The app only queries the database.
* **Deterministic Rule Engine:** The math for degree requirements (like CDC, DEL, and OPEL spillover) and prerequisite checking is done in standard Python (`engine/rules.py`). The LLM is not allowed to do academic math.
* **Tool Calling:** The LLM acts as an orchestrator. It figures out what the user is asking, then calls Python functions with specific filters (like `no_midsem=True`).
* **Source Citations:** Whenever data is pulled from the database, the source metadata is attached so the LLM can cite exactly where it found the information.
* **Safe Fallbacks:** If a handout doesn't explicitly mention an attendance policy, the script logs it as "Unverified" rather than trying to guess.

## Extra Features Implemented (Brownie Points)

* **8 AM Timetable Filter:** The engine parses the timetable and can successfully filter out courses that have 8:00 AM slots if the user asks for it.
* **Automated Prerequisites:** Instead of hardcoding, a script uses regex to scrape real prerequisites directly from the BITS Bulletin text and structures them so the engine can check them.
* **Smarter Handout Parsing:** The handout scraper looks for subjective grading terms like "class participation" in addition to standard attendance policies.
* **Dynamic OPEL Spillover:** The requirement tracker knows that taking a 4th HUEL or extra DEL automatically spills over to fill the OPEL bucket.

## Known Shortcomings & Limitations

To get a working end-to-end prototype finished within the sprint, I had to cut a few corners on the dataset:

* **Branch Limitations:** Even though the engine successfully parses the graduation math (CDC/DEL/OPEL units) for all 19 first-degree branches, **the database is currently only seeded with the CDCs and DELs for B.E. Computer Science**. If you select Chemical or Mechanical engineering in the UI, the progress bars will work, but the AI won't be able to recommend your specific branch courses yet.
* **Shallow Handout Scraping:** The handout parser is pretty basic right now. It flags attendance and grabs a text snippet for makeup policies, but it doesn't extract full evaluation schemes (like exact quiz counts or project weightings).
* **No Live Clash Detection:** While it can filter out 8 AMs, the system doesn't actively cross-check your selected courses to see if their timetable slots clash with each other.

```

```