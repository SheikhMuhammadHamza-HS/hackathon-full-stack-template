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

    # Show the orphaned task before deletion
    cur.execute("SELECT id, user_id, title, description, completed, created_at FROM tasks;")
    tasks = cur.fetchall()

    print(f"Found {len(tasks)} task(s) in database:")
    for task in tasks:
        print(f"  Task ID: {task[0]}, User ID: {task[1]}, Title: {task[2]}")

    # Delete all tasks
    cur.execute("DELETE FROM tasks;")
    conn.commit()

    print(f"\nAll tasks have been deleted from the database.")

    # Verify the deletion
    cur.execute("SELECT COUNT(*) FROM tasks;")
    new_task_count = cur.fetchone()[0]
    print(f"Tasks remaining in database: {new_task_count}")

    # Also verify users count
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count = cur.fetchone()[0]
    print(f"Users remaining in database: {user_count}")

    # Close connections
    cur.close()
    conn.close()

    print("\nDatabase cleanup completed successfully!")

except Exception as e:
    print(f"Error connecting to database: {e}")