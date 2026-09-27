import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.rules import calculate_remaining_requirements, get_eligible_courses

# Create a mock student who has completed CS F111 (the prerequisite we set for Data Structures)
mock_student = {
    "degree": "B.E. Computer Science",
    "completed_courses": ["CS F111", "CS F212"]
}

print("--- Testing Requirement Math ---")
reqs = calculate_remaining_requirements(mock_student)
print(f"Remaining CDCs: {len(reqs['remaining_cdcs'])}")
print(f"DEL Status: {reqs['DEL']}")
print("\n--- Testing Eligible Course Retrieval (Looking for DELs) ---")
eligible_dels = get_eligible_courses(category="DEL", profile=mock_student)
print(f"Found {len(eligible_dels)} eligible DELs.")
if eligible_dels:
    print(f"Example course returned: {eligible_dels[0]['course_code']} - {eligible_dels[0]['title']}")