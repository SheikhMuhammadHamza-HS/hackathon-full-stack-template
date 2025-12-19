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

    # Check if users table exists and structure
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position;
    """)
    user_columns = cur.fetchall()
    print(f"\nUsers table structure:")
    for col in user_columns:
        print(f"  {col[0]}: {col[1]}")

    # Check if tasks table exists and structure
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'tasks'
        ORDER BY ordinal_position;
    """)
    task_columns = cur.fetchall()
    print(f"\nTasks table structure:")
    for col in task_columns:
        print(f"  {col[0]}: {col[1]}")

    # Check current counts
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks;")
    task_count = cur.fetchone()[0]

    print(f"\nCurrent database state:")
    print(f"  Users: {user_count}")
    print(f"  Tasks: {task_count}")

    # Close connections
    cur.close()
    conn.close()

    print(f"\nDatabase is properly set up with both users and tasks tables!")

except Exception as e:
    print(f"Error connecting to database: {e}")