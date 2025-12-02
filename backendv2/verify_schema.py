import inspect
import sys
import os

# Add the parent directory to sys.path so we can import 'backend' 
# even if running this script directly from inside the backend/ folder.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db import models

def verify():
    print("🔍 Inspecting backend/db/models.py...")
    
    expected_tables = [
        "User", "Classroom", "Enrollment", 
        "Assignment", "Submission", "FileResource", 
        "Discussion", "DiscussionReply"
    ]
    
    found_tables = []
    for name, obj in inspect.getmembers(models):
        if inspect.isclass(obj) and hasattr(obj, "__tablename__"):
            found_tables.append(name)
            
    print(f"Found Tables: {found_tables}")
    
    missing = set(expected_tables) - set(found_tables)
    if not missing:
        print("✅ SUCCESS: All strict schema tables are present in the code!")
    else:
        print(f"❌ FAILURE: Missing tables: {missing}")

if __name__ == "__main__":
    verify()