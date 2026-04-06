import sqlite3
import os

db_path = 'db.sqlite3'

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking current journal mode...")
    cursor.execute("PRAGMA journal_mode;")
    print(f"Current mode: {cursor.fetchone()[0]}")
    
    print("Enabling WAL mode...")
    cursor.execute("PRAGMA journal_mode=WAL;")
    new_mode = cursor.fetchone()[0]
    print(f"New mode: {new_mode}")
    
    print("Setting synchronous to NORMAL...")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    
    conn.close()
    if new_mode.upper() == 'WAL':
        print("✅ SUCCESS: WAL mode enabled. SQLite is now optimized for concurrency.")
    else:
        print("❌ FAILED: Could not enable WAL mode.")
else:
    print(f"❌ ERROR: {db_path} not found.")
