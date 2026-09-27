import sqlite3
import os
import pdfplumber
import re
import glob

def parse_handouts():
    conn = sqlite3.connect('data_processed/app.db')
    cursor = conn.cursor()

    cursor.execute("SELECT course_code FROM Course")
    courses = [row[0] for row in cursor.fetchall()]

    print(f"Scanning handouts for {len(courses)} courses...")

    for course in courses:
        # Format "CS F317" to "CS_F317"
        course_formatted = course.replace(' ', '_')
        
        # Use glob to find files like "165_CS_F317.pdf" (ignores the numbers at the start)
        search_pattern = f"data_raw/*_{course_formatted}.pdf"
        matches = glob.glob(search_pattern)
        
        # Fallback just in case some don't have the number prefix
        if not matches:
            matches = glob.glob(f"data_raw/{course_formatted}.pdf")
            
        filepath = matches[0] if matches else None
        
        attendance_policy = "Unverified"
        makeup_policy = "Unverified"
        midsem_date = "Unverified"
        
        if filepath:
            print(f"Found handout for {course}: {filepath}")
            with pdfplumber.open(filepath) as pdf:
                text = "".join([page.extract_text() for page in pdf.pages if page.extract_text()])
                
                # Check for explicit mention of attendance
                if re.search(r'attendance', text, re.IGNORECASE):
                    attendance_policy = "Mentioned in handout (See PDF)"
                    
                # Extract makeup policy text for the LLM to analyze later
                makeup_match = re.search(r'(make-?up.*?)(?=\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
                if makeup_match:
                    makeup_policy = makeup_match.group(1).strip()[:200] + "..." # Truncate for DB
                    
        # Update the database
        cursor.execute('''
            UPDATE Handout_Data 
            SET attendance_policy = ?, makeup_policy = ?, midsem_date = ?
            WHERE course_code = ?
        ''', (attendance_policy, makeup_policy, midsem_date, course))

    conn.commit()
    conn.close()
    print("Handouts parsed and saved to database successfully!")

if __name__ == "__main__":
    parse_handouts()