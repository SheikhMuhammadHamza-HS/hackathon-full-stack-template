import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('D:/testing/hackathon-full-stack-template/backend/.env')

# Get database URL from environment
database_url = os.getenv('DATABASE_URL')
if not database_url:
    print("DATABASE_URL not found in .env file")
    exit(1)

print(f"Connecting to database: {database_url}")

try:
    # Parse the database URL
    import urllib.parse
    parsed_url = urllib.parse.urlparse(database_url)

    # Connect to the database
    conn = psycopg2.connect(
        host=parsed_url.hostname,
        port=parsed_url.port,
        database=parsed_url.path[1:],  # Remove the leading '/'
        user=parsed_url.username,
        password=parsed_url.password
    )

    # Create a cursor
    cur = conn.cursor()

    # Count tasks in the database
    cur.execute("SELECT COUNT(*) FROM tasks;")
    task_count = cur.fetchone()[0]

    print(f"Total tasks in database: {task_count}")

    # If there are tasks, show their details
    if task_count > 0:
        cur.execute("SELECT id, user_id, title, description, completed, created_at FROM tasks ORDER BY created_at;")
        tasks = cur.fetchall()

        print("\nTask details:")
        print("ID | User ID | Title | Description | Completed | Created At")
        print("-" * 100)
        for task in tasks:
            print(f"{task[0]} | {task[1][:8]}... | {task[2][:20]}... | {task[3][:20] if task[3] else 'None'}... | {task[4]} | {task[5]}")
    else:
        print("No tasks found in the database.")

    # Close connections
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error connecting to database: {e}")