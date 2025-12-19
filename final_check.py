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

    # Check users
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count = cur.fetchone()[0]
    print(f"Users in database: {user_count}")

    if user_count > 0:
        cur.execute("SELECT id, email, name, created_at FROM users ORDER BY created_at;")
        users = cur.fetchall()
        print("\nUser details:")
        for user in users:
            print(f"  ID: {user[0][:8]}..., Email: {user[1]}, Name: {user[2]}, Created: {user[3]}")

    # Check tasks
    cur.execute("SELECT COUNT(*) FROM tasks;")
    task_count = cur.fetchone()[0]
    print(f"\nTasks in database: {task_count}")

    # Clean up everything
    print(f"\nCleaning up database...")
    cur.execute("DELETE FROM tasks;")
    cur.execute("DELETE FROM users;")
    conn.commit()

    # Verify cleanup
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count_after = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tasks;")
    task_count_after = cur.fetchone()[0]

    print(f"Users after cleanup: {user_count_after}")
    print(f"Tasks after cleanup: {task_count_after}")
    print(f"Database is now completely clean!")

    # Close connections
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error connecting to database: {e}")