import sys
import traceback

print(f"Python executable: {sys.executable}")

try:
    print("Attempting to import sqlite3...")
    import sqlite3
    print(f"sqlite3 version: {sqlite3.version}")
except:
    traceback.print_exc()

try:
    print("Attempting to import pypdf...")
    import pypdf
    print(f"pypdf version: {pypdf.__version__}")
except:
    traceback.print_exc()

try:
    print("Attempting to import uuid...")
    import uuid
    print("uuid imported")
except:
    traceback.print_exc()
