import sqlite3
import json

conn = sqlite3.connect('drivers_data.db')
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Available tables:", [table[0] for table in tables])

# Check table structure
for table in tables:
    table_name = table[0]
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    print(f"\nTable {table_name} columns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")

# Get a sample of rides data
cursor.execute('SELECT * FROM drivers_data LIMIT 1')
columns = [description[0] for description in cursor.description]
result = cursor.fetchone()

if result:
    print("\nSample driver data columns:", columns)
    # Find rides_history column
    if 'rides_history' in columns:
        rides_index = columns.index('rides_history')
        rides_data = result[rides_index]
        if rides_data:
            try:
                rides = json.loads(rides_data)
                if rides:
                    print("Sample ride keys:", list(rides[0].keys()))
                    print("Sample ride:", json.dumps(rides[0], indent=2))
                else:
                    print("No rides found in history")
            except json.JSONDecodeError as e:
                print("JSON decode error:", e)
                print("Raw data (first 200 chars):", str(rides_data)[:200])
        else:
            print("rides_history is NULL")
    else:
        print("rides_history column not found")

conn.close()
