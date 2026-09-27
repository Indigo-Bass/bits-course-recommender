import sqlite3
import pdfplumber
import re
import os

def parse_timetable():
    db_path = 'data_processed/app.db'
    pdf_path = 'data_raw/timetable.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"Error: Could not find {pdf_path}. Please make sure it is in the data_raw folder.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the list of our seed courses to filter the massive timetable
    cursor.execute("SELECT course_code FROM Course")
    seed_courses = [row[0] for row in cursor.fetchall()]

    print(f"Scanning timetable for {len(seed_courses)} seed courses... This may take a minute.")

    # Regex to catch Day/Hour codes like "M W F 10" or "T Th 2"
    time_pattern = re.compile(r'\b([M|T|W|Th|F|S]{1,2}(?:\s+[M|T|W|Th|F|S]{1,2})*)\s+([\d\s]+)\b')

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            for line in lines:
                # Filter out cancelled sections immediately
                if "CANCLED" in line:
                    continue
                
                # Check if this line belongs to one of our seed courses
                for course in seed_courses:
                    if course in line:
                        # Extract the days and hours
                        time_match = time_pattern.search(line)
                        days = time_match.group(1).strip() if time_match else "TBA"
                        hours = time_match.group(2).strip() if time_match else "TBA"
                        
                        # Identify if it's a Lecture (L), Practical (P), or Tutorial (T)
                        section = "Unknown"
                        if " L" in line: section = "Lecture"
                        elif " P" in line: section = "Practical"
                        elif " T" in line: section = "Tutorial"

                        cursor.execute('''
                            INSERT INTO Timetable (course_code, section, instructor, days, hours, room, midsem_slot, compre_slot)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (course, section, "See PDF", days, hours, "TBA", "TBA", "TBA"))
                        break # Move to next line once a course is found

    conn.commit()
    conn.close()
    print("Timetable parsed and saved to database successfully!")

if __name__ == "__main__":
    parse_timetable()