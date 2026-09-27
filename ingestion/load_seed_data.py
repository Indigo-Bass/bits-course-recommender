import sqlite3
import json

# Verified seed data for B.E. Computer Science
seed_data = {
    "programme": "B.E. Computer Science",
    "cdc_courses": [
        {"code": "CS F211", "title": "Data Structures & Algorithms", "L": 3, "P": 1, "U": 4},
        {"code": "CS F212", "title": "Database Systems", "L": 3, "P": 1, "U": 4},
        {"code": "CS F213", "title": "Object Oriented Programming", "L": 3, "P": 1, "U": 4},
        {"code": "CS F214", "title": "Logic in Computer Science", "L": 3, "P": 0, "U": 3},
        {"code": "CS F215", "title": "Digital Design", "L": 3, "P": 1, "U": 4},
        {"code": "CS F222", "title": "Discrete Structures for Computer Science", "L": 3, "P": 0, "U": 3},
        {"code": "CS F241", "title": "Microprocessors & Interfacing", "L": 3, "P": 1, "U": 4},
        {"code": "CS F301", "title": "Principles of Programming Languages", "L": 2, "P": 0, "U": 2},
        {"code": "CS F303", "title": "Computer Networks", "L": 3, "P": 1, "U": 4},
        {"code": "CS F342", "title": "Computer Architecture", "L": 3, "P": 0, "U": 3},
        {"code": "CS F351", "title": "Theory of Computation", "L": 3, "P": 0, "U": 3},
        {"code": "CS F363", "title": "Compiler Construction", "L": 2, "P": 1, "U": 3},
        {"code": "CS F364", "title": "Design & Analysis of Algorithms", "L": 3, "P": 0, "U": 3},
        {"code": "CS F372", "title": "Operating Systems", "L": 3, "P": 0, "U": 3}
    ],
    "del_pool": [
        {"code": "BITS F311", "title": "Image Processing", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F312", "title": "Neural Networks and Fuzzy Logic", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F343", "title": "Fuzzy Logic and Applications", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F364", "title": "Human-Computer Interaction", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F386", "title": "Quantum Information and Computation", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F452", "title": "Blockchain Technology", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F453", "title": "Computational Learning Theory", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F454", "title": "Bio-Inspired Intelligence: Algorithms and Applications", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F459", "title": "Computer Vision", "L": 3, "P": 1, "U": 4},
        {"code": "BITS F463", "title": "Cryptography", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F464", "title": "Machine Learning", "L": 3, "P": 0, "U": 3},
        {"code": "BITS F465", "title": "Enterprise Computing", "L": 3, "P": 1, "U": 4},
        {"code": "BITS F466", "title": "Service Oriented Computing", "L": 3, "P": 1, "U": 4},
        {"code": "BITS F471", "title": "Introduction to Large Language Models", "L": 3, "P": 0, "U": 3},
        {"code": "CS F314", "title": "Software Development for Portable Devices", "L": 2, "P": 1, "U": 3},
        {"code": "CS F315", "title": "Information and Communication Technologies and Development", "L": 3, "P": 0, "U": 3},
        {"code": "CS F316", "title": "Quantum Architecture and Programming", "L": 3, "P": 0, "U": 3},
        {"code": "CS F317", "title": "Reinforcement Learning", "L": 3, "P": 0, "U": 3},
        {"code": "CS F320", "title": "Foundations of Data Science", "L": 3, "P": 0, "U": 3},
        {"code": "CS F321", "title": "System Security", "L": 3, "P": 0, "U": 3}
    ]
}

def load_courses():
    conn = sqlite3.connect('data_processed/app.db')
    cursor = conn.cursor()
    
    # Insert CDCs
    for course in seed_data['cdc_courses']:
        # CS F211 has a prerequisite of CS F111 (Computer Programming). We will mock this one prerequisite for our engine tests.
        prereq = '{"type": "AND", "courses": ["CS F111"]}' if course['code'] == 'CS F211' else None
        
        cursor.execute('''
            INSERT OR REPLACE INTO Course (course_code, title, department, units, category, prerequisites)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (course['code'], course['title'], 'CS', course['U'], 'CDC', prereq))

    # Insert DELs
    for course in seed_data['del_pool']:
        cursor.execute('''
            INSERT OR REPLACE INTO Course (course_code, title, department, units, category, prerequisites)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (course['code'], course['title'], 'CS', course['U'], 'DEL', None))

    conn.commit()
    conn.close()
    print(f"Successfully loaded {len(seed_data['cdc_courses']) + len(seed_data['del_pool'])} seed courses into the database.")

if __name__ == "__main__":
    load_courses()