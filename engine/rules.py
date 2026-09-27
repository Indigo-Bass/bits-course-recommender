import sqlite3
import json

def get_db_connection():
    # Connect to the DB and format rows as dictionaries for easy JSON conversion later
    conn = sqlite3.connect('data_processed/app.db')
    conn.row_factory = sqlite3.Row 
    return conn

def calculate_remaining_requirements(profile):
    """Calculates remaining requirements, including the OPEL spillover rule."""
    completed = profile.get('completed_courses', [])
    degree = profile.get('degree', 'B.E. Computer Science')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Programme_Rules WHERE degree = ?", (degree,))
    rules = cursor.fetchone()
    if not rules:
        rules = {'del_units': 4, 'huel_units': 3, 'opel_units': 5}
        
    req_dels = int(rules['del_units'])
    req_huels = int(rules['huel_units'])
    req_opels = int(rules['opel_units'])
    
    cursor.execute("SELECT course_code FROM Course WHERE category = 'CDC'")
    all_cdcs = [row['course_code'] for row in cursor.fetchall()]
    remaining_cdcs = [cdc for cdc in all_cdcs if cdc not in completed]
    
    completed_dels = 0
    completed_huels = 0
    completed_opels = 0
    
    if completed:
        placeholders = ','.join(['?'] * len(completed))
        cursor.execute(f"SELECT course_code, category FROM Course WHERE course_code IN ({placeholders})", completed)
        
        for row in cursor.fetchall():
            code = row['course_code']
            cat = row['category']
            
            if code in all_cdcs:
                continue
                
            if cat == 'DEL':
                if completed_dels < req_dels:
                    completed_dels += 1
                else:
                    completed_opels += 1
            elif cat == 'HUEL':
                if completed_huels < req_huels:
                    completed_huels += 1
                else:
                    completed_opels += 1
            else:
                completed_opels += 1
            
            # --- X-RAY VISION ---
            # This prints the math live to your terminal every time you select a course
            print(f"Engine processed: {code} ({cat}) -> DELs: {completed_dels}, HUELs: {completed_huels}, OPELs: {completed_opels}")
                
    conn.close()
    
    return {
        "remaining_cdcs": remaining_cdcs,
        "DEL": {"completed": completed_dels, "required": req_dels},
        "HUEL": {"completed": completed_huels, "required": req_huels}, 
        "OPEL": {"completed": completed_opels, "required": req_opels} 
    }

def check_eligibility(course_code, completed_courses):
    """Checks the JSON prerequisite tree against the student's completed courses."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT prerequisites FROM Course WHERE course_code = ?", (course_code,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or not row['prerequisites']:
        return True, "No prerequisites required."
        
    prereqs = json.loads(row['prerequisites'])
    
    if prereqs['type'] == 'AND':
        missing = [c for c in prereqs['courses'] if c not in completed_courses]
        if missing:
            return False, f"Missing prerequisites: {', '.join(missing)}"
        return True, "Prerequisites met."
    
    elif prereqs['type'] == 'OR':
        met = [c for c in prereqs['courses'] if c in completed_courses]
        if not met:
            return False, f"Requires at least one of: {', '.join(prereqs['courses'])}"
        return True, "Prerequisites met."
        
    return False, "Unknown prerequisite structure."

def get_eligible_courses(category=None, no_midsem=False, no_8am=False, profile=None):
    """
    This is the exact Tool the LLM will call. 
    It queries SQLite, filters out ineligible courses, and attaches source citations.
    """
    if profile is None:
        profile = {"completed_courses": []}
        
    completed_courses = profile.get("completed_courses", [])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT c.course_code, c.title, c.units, c.category, c.topics,
               h.attendance_policy, h.makeup_policy, h.midsem_date, t.days, t.hours
        FROM Course c
        LEFT JOIN Handout_Data h ON c.course_code = h.course_code
        LEFT JOIN Timetable t ON c.course_code = t.course_code
        WHERE 1=1
    """
    params = []
    
    if category:
        query += " AND c.category = ?"
        params.append(category)
        
    cursor.execute(query, params)
    all_courses = cursor.fetchall()
    conn.close()
    
    eligible_courses = []
    for row in all_courses:
        # Skip if the student has already taken this course
        if row['course_code'] in completed_courses:
            continue
            
        # Check deterministic eligibility
        is_eligible, reason = check_eligibility(row['course_code'], completed_courses)
        if not is_eligible:
            continue
            
        course_dict = dict(row)
        course_dict['eligibility_reason'] = reason
        # Force the citation metadata into the payload so the LLM has to use it
        course_dict['source_citation'] = "bulletin[1].pdf, pages 316-317"
        
        eligible_courses.append(course_dict)
        
    return eligible_courses
