import sqlite3
import os

# Ensure the processed data directory exists
os.makedirs('data_processed', exist_ok=True)

# Connect to the SQLite database (this creates the file if it doesn't exist)
conn = sqlite3.connect('data_processed/app.db')
cursor = conn.cursor()

# Define and execute the schema
schema = """
CREATE TABLE IF NOT EXISTS Course (
  course_code TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  department TEXT,
  units INTEGER NOT NULL,
  category TEXT CHECK(category IN ('CDC','DEL','HUEL','OPEL')) NOT NULL,
  topics TEXT,
  prerequisites TEXT, 
  restrictions TEXT
);

CREATE TABLE IF NOT EXISTS Handout_Data (
  course_code TEXT REFERENCES Course(course_code),
  attendance_policy TEXT,
  midsem_date TEXT,
  compre_date TEXT,
  evaluation_components TEXT,
  makeup_policy TEXT,
  instructor TEXT,
  syllabus TEXT
);

CREATE TABLE IF NOT EXISTS Timetable (
  course_code TEXT REFERENCES Course(course_code),
  section TEXT,
  instructor TEXT,
  days TEXT,
  hours TEXT,
  room TEXT,
  midsem_slot TEXT,
  compre_slot TEXT
);

CREATE TABLE IF NOT EXISTS Student (
  id TEXT PRIMARY KEY,
  campus TEXT,
  batch INTEGER,
  degree TEXT,
  current_semester INTEGER,
  completed_courses TEXT,
  current_courses TEXT,
  minor TEXT,
  interests TEXT
);

CREATE TABLE IF NOT EXISTS Source_Metadata (
  entity_id TEXT, 
  source_document TEXT,
  page_section_reference TEXT,
  extraction_confidence REAL
);
"""

cursor.executescript(schema)
conn.commit()
conn.close()

print("Database initialized successfully at data_processed/app.db!")