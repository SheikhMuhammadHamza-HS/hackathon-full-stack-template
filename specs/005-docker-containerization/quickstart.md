# Quickstart: Docker Containerization

**Feature**: 005-docker-containerization
**Date**: 2025-12-24

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Access to project repository
- Environment variables configured in `.env` file

## Quick Build & Run

### Backend Container

```bash
# Navigate to backend directory
cd backend

# Build the image
docker build -t todo-backend:v1.0.0 .

# Run with environment variables
docker run -d \
  --name todo-backend \
  -p 8000:8000 \
  --env-file ../.env \
  todo-backend:v1.0.0

# Verify health
curl http://localhost:8000/health
# Expected: {"status": "ok"}

# Check logs
docker logs todo-backend

# Verify non-root user
docker exec todo-backend whoami
# Expected: appuser
```

### Frontend Container

```bash
# Navigate to frontend directory
cd frontend

# Build the image
docker build -t todo-frontend:v1.0.0 .

# Run the container
docker run -d \
  --name todo-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  todo-frontend:v1.0.0

# Verify running
curl http://localhost:3000
# Expected: HTML response

# Check logs
docker logs todo-frontend

# Verify non-root user
docker exec todo-frontend whoami
# Expected: nextjs
```

## Verify Image Sizes

```bash
docker images | grep todo

# Expected output (approximate):
# todo-backend    v1.0.0    <image-id>    <created>    ~400-600MB
# todo-frontend   v1.0.0    <image-id>    <created>    ~100-200MB
```

## Stop & Clean Up

```bash
# Stop containers
docker stop todo-backend todo-frontend

# Remove containers
docker rm todo-backend todo-frontend

# Remove images (optional)
docker rmi todo-backend:v1.0.0 todo-frontend:v1.0.0
```

## Troubleshooting

### Backend fails to start
1. Check environment variables: `docker logs todo-backend`
2. Verify DATABASE_URL is accessible from container
3. Ensure port 8000 is not in use: `netstat -an | grep 8000`

### Frontend shows blank page
1. Check NEXT_PUBLIC_API_URL is set correctly
2. Verify backend is running and accessible
3. Check browser console for errors

### Build fails
1. Ensure Docker daemon is running
2. Check .dockerignore isn't excluding required files
3. Verify base images are accessible (network issues)

### Image too large
1. Verify multi-stage build is working (check stages in Dockerfile)
2. Ensure .dockerignore excludes all unnecessary files
3. For frontend, confirm `output: 'standalone'` is in next.config.ts

## Development Workflow

```bash
# Rebuild after code changes
docker build -t todo-backend:dev .

# Run with volume mount for hot reload (development only)
docker run -d \
  --name todo-backend-dev \
  -p 8000:8000 \
  -v $(pwd)/app:/app/app \
  --env-file ../.env \
  todo-backend:dev
```

## Next Steps

After verifying containers work locally:
1. Run `/sp.tasks` to generate implementation tasks
2. Implement the Dockerfiles
3. Test with `docker build` and `docker run`
4. Proceed to Kubernetes deployment (Phase IV - next feature)
