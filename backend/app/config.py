"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

# Admin Configuration
# Only these emails have admin access to delete users and view stats
ADMIN_EMAILS = [
    "sheikhmhamza37@gmail.com",  # Your admin email
]

# Admin Credentials (pre-defined password for admin email)
ADMIN_CREDENTIALS = {
    "sheikhmhamza37@gmail.com": "Hamza@890"  # Admin email and password
}

# Get from environment or use default
ADMIN_EMAILS_ENV = os.getenv("ADMIN_EMAILS", "").split(",")
if ADMIN_EMAILS_ENV and ADMIN_EMAILS_ENV[0]:
    ADMIN_EMAILS = [email.strip() for email in ADMIN_EMAILS_ENV if email.strip()]
