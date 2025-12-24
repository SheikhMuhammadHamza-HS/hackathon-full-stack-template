#!/bin/sh
# =============================================================================
# Frontend Docker Entrypoint - Runtime Environment Variable Injection
# =============================================================================
# Purpose: Inject NEXT_PUBLIC_* environment variables at container runtime
#
# Why this is needed:
# Next.js bakes NEXT_PUBLIC_* variables into the JavaScript bundle at BUILD time.
# This means changing env vars in Kubernetes won't affect the frontend without
# rebuilding the image. This script performs a runtime find-and-replace to inject
# the actual API URL from the Kubernetes environment into the already-built bundle.
#
# How it works:
# 1. Find all JavaScript files in .next/static
# 2. Replace placeholder string with actual NEXT_PUBLIC_API_URL value
# 3. Start the Next.js server
#
# Security: Safe because we're replacing our own placeholder, not arbitrary content
# =============================================================================

set -e

# Default API URL (used if environment variable not set)
DEFAULT_API_URL="http://localhost:8000"

# Get the API URL from environment or use default
API_URL="${NEXT_PUBLIC_API_URL:-$DEFAULT_API_URL}"

echo "========================================"
echo "Frontend Container Startup"
echo "========================================"
echo "Injecting runtime environment variables..."
echo "NEXT_PUBLIC_API_URL: $API_URL"
echo "========================================"

# Find and replace in all JavaScript chunks
# This replaces the placeholder with the actual runtime value
if [ -d ".next/static" ]; then
    echo "Searching for JavaScript files to update..."

    # Find all .js files and replace the placeholder
    # Using sed -i for in-place editing
    find .next/static -type f -name "*.js" -exec sed -i \
        "s|RUNTIME_API_URL_PLACEHOLDER|$API_URL|g" {} \;

    echo "Environment variable injection complete."
else
    echo "Warning: .next/static directory not found. Skipping injection."
fi

echo "========================================"
echo "Starting Next.js server..."
echo "========================================"

# Execute the CMD (node server.js)
exec "$@"
