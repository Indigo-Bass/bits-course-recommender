```markdown
# BITS Academic Course Recommender

An agentic, LLM-powered course recommendation system for BITS Pilani students. This application processes institutional academic data (Bulletin, Timetable, Handouts, Regulations) into a structured SQLite database, utilizing a deterministic rule engine for academic policy validation and an LLM for natural language preference matching.

## Setup and Execution

**1. Environment Setup**
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

```

**2. Configure API Keys**
Create a `.env` file in the root directory and add your Google Gemini API key:

```text
GEMINI_API_KEY=your_api_key_here

```

**3. Data Ingestion Pipeline**
Place the raw PDFs (`bulletin[1].pdf`, `timetable[1].pdf`, `Academic-Regulations-2023[1].pdf`, and the course handouts) into the `/data_raw/` directory, then execute the ingestion pipeline:

```powershell
python ingestion/init_db.py
python ingestion/load_seed_data.py
python ingestion/parse_timetable.py
python ingestion/parse_handouts.py

```

**4. Run the Dashboard**

```powershell
streamlit run dashboard/app.py

```

## System Architecture & Implementation Alignment

This system was architected specifically to adhere to the rigid constraints of the project brief, ensuring the LLM never hallucinates academic policies or course properties.

* **Pre-processed Structured Records:** Raw PDFs are not passed to the LLM at runtime. They are processed via an offline pipeline (using `pdfplumber` and regex) into a structured SQLite database. The recommendation layer queries this clean schema.
* **Deterministic Academic-Rule Checking:** Requirement calculations (CDC/DEL/OPEL unit tracking) and eligibility checks (prerequisite validation) are written in pure Python (`engine/rules.py`). The LLM is restricted from performing academic math.
* **Agentic Orchestration:** The LLM is used strictly for user-intent understanding and semantic interest matching. It translates natural language queries into structured tool calls (e.g., `get_eligible_courses(category="DEL", no_midsem=True)`), which execute against the deterministic Python engine.
* **Source Traceability:** Every data point extracted during the ingestion pipeline carries source metadata. The LLM is system-prompted to append these citations (e.g., *Source: bulletin[1].pdf, pages 316-317*) to every recommendation, ensuring complete traceability back to the supplied documents.
* **Strict Verification Fallbacks:** During handout ingestion, if an explicit attendance or makeup policy cannot be found via regex, the pipeline inserts `"Unverified"` into the database rather than guessing, fulfilling the strict accuracy requirement.
* **Decoupled Ingestion:** The architecture separates the `/ingestion/` pipeline from the `/engine/` and `/agent/`. A new semester's timetable or updated handouts can be dropped into `/data_raw/` and re-ingested without altering a single line of the recommendation logic.

## Known Scope Limits (MVP Version)

To deliver a robust, fully functional end-to-end prototype within a one-day development sprint, the following deliberate scope limits were applied:

1. **Programme Scope:** The database is currently seeded with the B.E. Computer Science curriculum (14 CDCs, 20 DELs) and their corresponding handouts. The ingestion scripts are built to scale to all 540 courses once the full bulletin department tables are parsed into the `Course` table.
2. **Timetable Intelligence:** The timetable parser successfully extracts and structures section, day, and hour data into the SQLite database. However, the stretch-goal logic for active clash-detection and section-swapping during the recommendation phase was deferred to prioritize the core deterministic eligibility flow.

```

```