import sqlite3
import pdfplumber
import re
import json

def update_huels_and_prereqs():
    conn = sqlite3.connect('data_processed/app.db')
    cursor = conn.cursor()

    print("1. Scraping timetable.pdf for all HUELs...")
    
    with pdfplumber.open("data_raw/timetable.pdf") as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            for line in text.split('\n'):
                # BITS humanities electives always start with HSS F or GS F
                if "HSS F" in line or "GS F" in line:
                    # Regex to capture Code and Title, ignoring the timetable slots/instructors
                    match = re.search(r'(HSS F\d{3}|GS F\d{3})\s+([A-Z\s\&\-\,]+?)\s+(\d+)\s+([LTP]\d|CANCLED|\d+)', line)
                    if match:
                        code = match.group(1)
                        title = match.group(2).strip()
                        
                        cursor.execute('''
                            INSERT OR IGNORE INTO Course (course_code, title, department, units, category)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (code, title, 'HSS', 3, 'HUEL'))

    cursor.execute("SELECT COUNT(*) FROM Course WHERE category = 'HUEL'")
    print(f"-> Successfully extracted {cursor.fetchone()[0]} HUELs into the database!\n")

    print("2. Scanning bulletin.pdf for real prerequisites...")
    cursor.execute("SELECT course_code FROM Course")
    courses = [row[0] for row in cursor.fetchall()]

    with pdfplumber.open("data_raw/bulletin.pdf") as pdf:
        # Search the course description pages (roughly 100-500)
        for page in pdf.pages[100:500]:
            text = page.extract_text()
            if not text:
                continue
                
            for course in courses:
                # Look for "Prerequisite(s):" immediately following a course code
                pattern = rf"{course}.*?Prerequisite\(s\):\s*([A-Z\s\d/]+)(?=\n)"
                match = re.search(pattern, text, re.DOTALL)
                
                if match:
                    prereq_raw = match.group(1).strip()
                    req_codes = re.findall(r'[A-Z]{2,4}\s+F\d{3}', prereq_raw)
                    if req_codes:
                        prereq_json = json.dumps({"type": "AND", "courses": req_codes})
                        cursor.execute("UPDATE Course SET prerequisites = ? WHERE course_code = ?", (prereq_json, course))
                        print(f"-> Linked {course} with prerequisites: {req_codes}")

    conn.commit()
    conn.close()
    print("\nDatabase upgrade complete!")

if __name__ == "__main__":
    update_huels_and_prereqs()