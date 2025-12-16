---
name: docker
description: Docker containerization skill for building, running, and managing containers. Use when working with Dockerfiles, docker-compose, container deployment, or any containerization tasks. Triggers on keywords like docker, container, image, Dockerfile, compose, deployment.
---

# Docker Containerization Skill

## Overview

Docker is an open platform for developing, shipping, and running applications. It uses containers which are lightweight, portable, and isolated environments that package applications with all their dependencies.

## Core Concepts

### What is a Container?

A container is an isolated process that packages an application with all its dependencies.

**Key Properties:**
- **Self-contained**: Everything is included, no pre-installed dependencies needed on host
- **Isolated**: Operates independently, enhancing security
- **Independent**: Can be managed individually
- **Portable**: Runs identically on laptop, server, or cloud

### Container vs Virtual Machine

| Feature | Container | Virtual Machine |
|---------|-----------|-----------------|
| Size | Lightweight (MBs) | Heavy (GBs) |
| Startup | Seconds | Minutes |
| OS | Shared kernel | Full OS required |
| Resources | Efficient | More overhead |

### Docker Architecture

```
┌─────────────────────────────────────────────┐
│              Docker Client (CLI)            │
│                  docker                      │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│              Docker Daemon                   │
│                 dockerd                      │
├─────────────────────────────────────────────┤
│  Images  │  Containers  │  Networks  │ Vol  │
└─────────────────────────────────────────────┘
```

## Essential Docker Commands

### Container Management

```bash
# Run a container
docker run <image>                    # Basic run
docker run -d <image>                 # Detached mode (background)
docker run -it <image> /bin/bash      # Interactive terminal
docker run -p 8080:80 <image>         # Port mapping (host:container)
docker run -v /host/path:/container/path <image>  # Volume mount
docker run --name mycontainer <image> # Named container
docker run -e VAR=value <image>       # Environment variable
docker run --rm <image>               # Auto-remove after exit

# View running containers
docker ps                             # Running containers
docker ps -a                          # All containers (including stopped)

# Container operations
docker stop <container>               # Gracefully stop
docker start <container>              # Start stopped container
docker restart <container>            # Restart
docker kill <container>               # Force stop
docker rm <container>                 # Delete container
docker rm -f <container>              # Force delete running container

# Execute commands in container
docker exec -it <container> /bin/bash # Shell access
docker exec <container> <command>     # Single command

# View logs
docker logs <container>               # All logs
docker logs -f <container>            # Follow logs (live)
docker logs --tail 100 <container>    # Last 100 lines

# Inspect container
docker inspect <container>            # Detailed JSON info
docker stats                          # Live resource usage
docker top <container>                # Running processes
```

### Image Management

```bash
# View images
docker images                         # List all images
docker images -a                      # Include intermediate

# Pull/push images
docker pull <image>:<tag>             # Download from registry
docker push <image>:<tag>             # Upload to registry

# Build images
docker build -t <name>:<tag> .        # Build from Dockerfile
docker build -t <name> -f custom.Dockerfile .  # Custom file
docker build --no-cache -t <name> .   # Fresh build

# Image operations
docker tag <image> <new-name>:<tag>   # Rename/tag
docker rmi <image>                    # Delete image
docker image prune                    # Remove unused images
docker image prune -a                 # Remove all unused
```

### System Commands

```bash
# System info
docker version                        # Version info
docker info                           # System-wide info
docker system df                      # Disk usage

# Cleanup
docker system prune                   # Remove unused data
docker system prune -a                # Aggressive cleanup
docker volume prune                   # Remove unused volumes
docker network prune                  # Remove unused networks
```

### Network Commands

```bash
# Network management
docker network ls                     # List networks
docker network create <name>          # Create network
docker network connect <network> <container>    # Connect
docker network disconnect <network> <container> # Disconnect
docker network inspect <network>      # Network details
```

### Volume Commands

```bash
# Volume management
docker volume ls                      # List volumes
docker volume create <name>           # Create volume
docker volume inspect <name>          # Volume details
docker volume rm <name>               # Delete volume
```

## Dockerfile Reference

### Basic Structure

```dockerfile
# Base image (REQUIRED - always first)
FROM node:18-alpine

# Metadata
LABEL maintainer="your@email.com"
LABEL version="1.0"

# Environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Set working directory
WORKDIR /app

# Copy files
COPY package*.json ./
COPY . .

# Run commands (build time)
RUN npm install --production
RUN npm run build

# Expose port (documentation)
EXPOSE 3000

# Default command (runtime)
CMD ["node", "server.js"]
```

### All Dockerfile Instructions

| Instruction | Purpose | Example |
|-------------|---------|---------|
| `FROM` | Base image | `FROM node:18-alpine` |
| `RUN` | Build-time commands | `RUN npm install` |
| `CMD` | Default runtime command | `CMD ["npm", "start"]` |
| `ENTRYPOINT` | Fixed executable | `ENTRYPOINT ["python"]` |
| `COPY` | Copy files | `COPY src/ /app/src/` |
| `ADD` | Copy + extract/download | `ADD app.tar.gz /app/` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `ENV` | Environment variable | `ENV PORT=3000` |
| `ARG` | Build-time variable | `ARG VERSION=1.0` |
| `EXPOSE` | Document port | `EXPOSE 8080` |
| `VOLUME` | Mount point | `VOLUME /data` |
| `USER` | Set user | `USER node` |
| `LABEL` | Metadata | `LABEL version="1.0"` |
| `HEALTHCHECK` | Container health | `HEALTHCHECK CMD curl -f http://localhost/` |
| `SHELL` | Default shell | `SHELL ["/bin/bash", "-c"]` |
| `STOPSIGNAL` | Stop signal | `STOPSIGNAL SIGTERM` |
| `ONBUILD` | Trigger for child images | `ONBUILD RUN npm install` |

### Multi-Stage Build Example

```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production (smaller image)
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Dockerfile Best Practices

```dockerfile
# 1. Use specific tags (not :latest)
FROM node:18.19.0-alpine3.19

# 2. Combine RUN commands (reduce layers)
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy package files first (leverage cache)
COPY package*.json ./
RUN npm ci --production
COPY . .

# 4. Use .dockerignore
# Create .dockerignore file:
# node_modules
# .git
# *.log
# .env

# 5. Run as non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup
USER appuser

# 6. Use HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# 7. Set proper permissions
RUN chown -R appuser:appgroup /app
```

## Docker Compose

### Basic docker-compose.yml

```yaml
version: '3.8'

services:
  # Web application
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgres://db:5432/mydb
    depends_on:
      - db
    volumes:
      - ./src:/app/src
    networks:
      - app-network
    restart: unless-stopped

  # Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: mydb
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    networks:
      - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres-data:
```

### Docker Compose Commands

```bash
# Basic operations
docker compose up                     # Start all services
docker compose up -d                  # Detached mode
docker compose up --build             # Rebuild images
docker compose down                   # Stop and remove
docker compose down -v                # Also remove volumes

# Service management
docker compose start                  # Start existing containers
docker compose stop                   # Stop containers
docker compose restart                # Restart all
docker compose pause                  # Pause containers
docker compose unpause                # Unpause

# Logs and status
docker compose logs                   # All logs
docker compose logs -f <service>      # Follow specific service
docker compose ps                     # List containers
docker compose top                    # Running processes

# Scaling
docker compose up -d --scale web=3    # Run 3 web instances

# Execute commands
docker compose exec <service> <cmd>   # Run in service
docker compose run <service> <cmd>    # Run new container
```

### Advanced Compose Features

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
      args:
        - BUILD_ENV=production

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M

    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    # Logging
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

    # Environment from file
    env_file:
      - .env
      - .env.local
```

## Common Patterns

### Node.js Application

```dockerfile
FROM node:18-alpine

# Security: run as non-root
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

WORKDIR /app

# Dependencies first (cache optimization)
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY --chown=nextjs:nodejs . .

USER nextjs
EXPOSE 3000

CMD ["node", "server.js"]
```

### Python Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### FastAPI with PostgreSQL (Compose)

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

## Troubleshooting

### Common Issues

```bash
# Container crashing
docker logs <container>               # Check logs
docker inspect <container>            # Check exit code

# Port already in use
docker ps                             # Check which container is using it
lsof -i :8080                         # Check port (Linux/Mac)
netstat -ano | findstr :8080          # Check port (Windows)

# Disk space full
docker system prune -a                # Cleanup
docker volume prune                   # Remove unused volumes

# Permission denied
# In Dockerfile: USER root temporarily
# Or: RUN chmod +x script.sh

# Slow image build
# Create .dockerignore file
# Optimize layer ordering (dependencies first)
```

### Debug Commands

```bash
# Container shell access
docker exec -it <container> /bin/sh   # Alpine
docker exec -it <container> /bin/bash # Ubuntu/Debian

# Explore file system
docker cp <container>:/path/file ./local  # Copy from container
docker diff <container>               # Changed files

# Network debug
docker network inspect bridge         # Network details
docker exec <container> ping <other>  # Connectivity test
```

## Security Best Practices

1. **Use official images** - From Docker Hub verified publishers
2. **Use specific tags** - Avoid `:latest`
3. **Non-root user** - Use `USER` instruction
4. **Mount secrets** - Don't hardcode in environment
5. **Scan for vulnerabilities** - Use `docker scout`
6. **Minimal base images** - Prefer Alpine
7. **Regular updates** - Keep base images updated
8. **Read-only containers** - Use `--read-only` flag when possible

## Quick Reference Card

```bash
# Most used commands
docker run -d -p 8080:80 --name web nginx    # Run nginx
docker exec -it web /bin/bash                 # Shell access
docker logs -f web                            # Follow logs
docker stop web && docker rm web              # Cleanup

# Build and push
docker build -t myapp:1.0 .                   # Build
docker tag myapp:1.0 registry/myapp:1.0       # Tag
docker push registry/myapp:1.0                # Push

# Compose workflow
docker compose up -d --build                  # Start fresh
docker compose logs -f                        # Watch logs
docker compose down -v                        # Full cleanup
```

## Additional Resources

- [Docker Official Docs](https://docs.docker.com/)
- [Dockerfile Reference](https://docs.docker.com/reference/dockerfile/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Best Practices](https://docs.docker.com/build/building/best-practices/)
