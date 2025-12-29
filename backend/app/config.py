"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()

# Admin Configuration
# Only these emails have admin access to delete users and view stats
# Set via environment variable: ADMIN_EMAILS=admin1@example.com,admin2@example.com
_admin_emails_env = os.getenv("ADMIN_EMAILS", "")
ADMIN_EMAILS = [
    email.strip()
    for email in _admin_emails_env.split(",")
    if email.strip()
]

# Admin Credentials (for initial admin user creation)
# SECURITY: Always set these via environment variables, never hardcode!
# Set via environment variables:
#   ADMIN_EMAIL=admin@example.com
#   ADMIN_PASSWORD=SecurePassword123!
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Build credentials dict only if both are set
ADMIN_CREDENTIALS = {}
if ADMIN_EMAIL and ADMIN_PASSWORD:
    ADMIN_CREDENTIALS[ADMIN_EMAIL] = ADMIN_PASSWORD
    # Auto-add admin email to ADMIN_EMAILS list if not already present
    if ADMIN_EMAIL not in ADMIN_EMAILS:
        ADMIN_EMAILS.append(ADMIN_EMAIL)

# Frontend URL for OAuth redirects
# Falls back to the first allowed origin or localhost
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
FRONTEND_URL = os.getenv("FRONTEND_URL", _allowed_origins[0].strip())
