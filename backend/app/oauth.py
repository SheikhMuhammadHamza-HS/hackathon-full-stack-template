"""OAuth 2.0 client configuration for Google and GitHub authentication."""
import os
from authlib.integrations.starlette_client import OAuth
from typing import Optional
import secrets

# Initialize OAuth registry
oauth = OAuth()

# OAuth Configuration from environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8000/api/auth")

def generate_state_token() -> str:
    """Generate a secure random state token for CSRF protection.

    Returns:
        str: A 32-character URL-safe random token
    """
    return secrets.token_urlsafe(32)


# Register Google OAuth client
if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
            'prompt': 'select_account'
        }
    )

# Register GitHub OAuth client
if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    oauth.register(
        name='github',
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        authorize_params=None,
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )


def is_oauth_configured(provider: str) -> bool:
    """Check if OAuth provider is properly configured.

    Args:
        provider: OAuth provider name ('google' or 'github')

    Returns:
        bool: True if provider is configured, False otherwise
    """
    if provider == 'google':
        return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    elif provider == 'github':
        return bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET)
    return False
