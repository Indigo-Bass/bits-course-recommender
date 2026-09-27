import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Add the root directory to the path so we can import our engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.rules import get_eligible_courses

# Load the API key from the .env file
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# The strict system prompt mandated by the project brief
SYSTEM_PROMPT = """You are a BITS course-recommendation assistant. You may only state a course property, eligibility result, or policy fact if it was returned by a tool call this turn. If asked about a property not present in the tool output, say explicitly that it could not be verified from the source data — never guess. Always cite the source file and page or clause for every claim. For subjective words like 'lenient' or 'flexible', quote or closely paraphrase the retrieved policy text and let the student judge, rather than asserting your own boolean."""

def process_query(user_query, student_profile):
    """
    Takes a user query, lets Gemini call our SQLite database via Python tools,
    and returns a formatted, sourced response.
    """
    
    # We wrap our tool so Gemini doesn't have to guess the student profile
    def get_eligible_courses_tool(category: str = None, no_midsem: bool = False):
        """
        Return courses the student is eligible for, filtered by category and structural properties. 
        Never returns unverified data.
        """
        return get_eligible_courses(category=category, no_midsem=no_midsem, profile=student_profile)

    # Initialize a chat session using the new SDK and gemini-2.5-flash
    chat = client.chats.create(
        model="gemini-3.8-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[get_eligible_courses_tool],
            temperature=0.0 # Keep responses highly deterministic
        )
    )
    
    # Send the message; the SDK handles the tool calling loop automatically
    response = chat.send_message(user_query)
    
    return response.text

if __name__ == "__main__":
    # Let's test the agent with the exact queries from the brief!
    mock_student = {
        "degree": "B.E. Computer Science",
        "completed_courses": ["CS F111", "CS F212"]
    }
    
    print("--- Waking up the Agent ---\n")
    
    query1 = "Suggest DELs related to AI or Machine learning."
    print(f"USER: {query1}")
    print(f"AGENT: {process_query(query1, mock_student)}\n")
    print("-" * 50)
    
    query2 = "I want an OPEL with no attendance requirement."
    print(f"USER: {query2}")
    print(f"AGENT: {process_query(query2, mock_student)}\n")