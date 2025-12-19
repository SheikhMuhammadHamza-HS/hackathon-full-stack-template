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

    # Count users in the database
    cur.execute("SELECT COUNT(*) FROM users;")
    user_count = cur.fetchone()[0]

    print(f"Total users in database: {user_count}")

    # If there are users, show their details (excluding password hashes for security)
    if user_count > 0:
        cur.execute("SELECT id, email, name, created_at, updated_at FROM users ORDER BY created_at;")
        users = cur.fetchall()

        print("\nUser details:")
        print("ID | Email | Name | Created At | Updated At")
        print("-" * 80)
        for user in users:
            print(f"{user[0][:8]}... | {user[1]} | {user[2]} | {user[3]} | {user[4]}")

    # Also check tasks
    cur.execute("SELECT COUNT(*) FROM tasks;")
    task_count = cur.fetchone()[0]
    print(f"\nTotal tasks in database: {task_count}")

    if task_count > 0:
        cur.execute("SELECT id, user_id, title, completed, created_at FROM tasks ORDER BY created_at;")
        tasks = cur.fetchall()

        print("\nTask details:")
        print("ID | User ID | Title | Completed | Created At")
        print("-" * 80)
        for task in tasks:
            print(f"{task[0]} | {task[1][:8]}... | {task[2][:20]}... | {task[3]} | {task[4]}")

    # Ask for confirmation before deleting
    if user_count > 0 or task_count > 0:
        response = input(f"\nDo you want to delete all {user_count} users and {task_count} tasks? (yes/no): ")
        if response.lower() == 'yes':
            # First, delete all related tasks
            cur.execute("DELETE FROM tasks;")
            print("Deleted all tasks...")

            # Then delete all users
            cur.execute("DELETE FROM users;")
            conn.commit()
            print(f"\nAll data has been deleted from the database.")

            # Verify the deletion
            cur.execute("SELECT COUNT(*) FROM users;")
            new_user_count = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM tasks;")
            new_task_count = cur.fetchone()[0]

            print(f"Users remaining in database: {new_user_count}")
            print(f"Tasks remaining in database: {new_task_count}")
        else:
            print("Deletion cancelled.")
    else:
        print("No users or tasks to delete.")

    # Close connections
    cur.close()
    conn.close()

except Exception as e:
    print(f"Error connecting to database: {e}")