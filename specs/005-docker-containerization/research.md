# Research: Docker Containerization

**Feature**: 005-docker-containerization
**Date**: 2025-12-24
**Status**: Complete

## Research Summary

All technical decisions for Docker containerization have been resolved. No NEEDS CLARIFICATION items existed in the specification - user provided detailed requirements upfront.

## Decision 1: Python Package Manager in Docker

**Decision**: Use `uv` package manager with `uv sync --frozen --no-install-project`

**Rationale**:
- Project already uses `uv` (per CLAUDE.md and project standards)
- `uv` is significantly faster than pip (10-100x in benchmarks)
- `--frozen` ensures reproducible builds from lock file
- `--no-install-project` installs only dependencies, not the project itself (needed for copy-based Docker workflow)

**Alternatives Considered**:
- `pip install -r requirements.txt` - Slower, no lock file guarantee
- `poetry install` - Would require adding Poetry, not current project standard
- `pip-tools` - Extra compilation step, more complex

## Decision 2: Python Base Image

**Decision**: Use `python:3.13-slim`

**Rationale**:
- Matches project Python version (3.13 per constitution)
- `slim` variant removes unnecessary packages (~150MB smaller than full)
- Debian-based (better compatibility than Alpine for Python)
- Official image with security updates

**Alternatives Considered**:
- `python:3.13-alpine` - Musl libc causes issues with some Python packages
- `python:3.13` - Full image ~900MB, unnecessary bloat
- `python:3.13-bookworm` - Same as default, too large

## Decision 3: Node.js Base Image

**Decision**: Use `node:20-alpine`

**Rationale**:
- Node.js 20 is LTS (Long Term Support)
- Alpine variant is ~5x smaller than Debian (~50MB vs ~250MB)
- Node.js works well with Alpine (unlike Python)
- Sufficient for running standalone Next.js server

**Alternatives Considered**:
- `node:20-slim` - Larger than alpine, no benefit for Next.js
- `node:20` - Full image ~1GB, unnecessary
- `node:22` - Not LTS yet

## Decision 4: Next.js Output Mode

**Decision**: Use `output: 'standalone'` in next.config.ts

**Rationale**:
- Reduces image size from ~1GB to <200MB
- Creates self-contained server.js with minimal dependencies
- Official Next.js recommendation for Docker deployment
- Automatically traces and includes only needed node_modules

**Alternatives Considered**:
- Default output - Requires copying entire node_modules (~500MB+)
- Static export - Not suitable for dynamic routes/API routes
- Custom server - More complexity, standalone is sufficient

## Decision 5: Non-Root User UIDs

**Decision**: Backend `appuser` (UID 10001), Frontend `nextjs` (UID 1001)

**Rationale**:
- UID > 10000 for backend follows Kubernetes best practices (avoids system UIDs)
- UID 1001 for frontend follows Next.js documentation example
- Different names make container logs distinguishable
- Non-root is security requirement per constitution

**Alternatives Considered**:
- Same UID for both - Works but harder to identify in logs
- UID 1000 - Common user UID, potential collision
- Named user without explicit UID - UID assignment varies by base image

## Decision 6: Health Check Implementation

**Decision**: HEALTHCHECK instruction using curl to /health endpoint

**Rationale**:
- Docker native health checking (works without Kubernetes)
- `/health` endpoint already exists in FastAPI backend
- Simple curl command is reliable and fast
- Kubernetes will use its own probes, but HEALTHCHECK provides fallback

**Alternatives Considered**:
- wget instead of curl - Alpine doesn't have curl by default (need to install)
- Python script for health check - Overkill, curl is sufficient
- No HEALTHCHECK - Would lose Docker-level health monitoring

**Note for Alpine**: Frontend will need to install curl or use wget for health check.

## Decision 7: .dockerignore Strategy

**Decision**: Separate .dockerignore per service directory

**Rationale**:
- Each service has different exclusion needs
- Keeps exclusions close to Dockerfile (easier to maintain)
- Follows Docker convention for monorepo structures

**Alternatives Considered**:
- Root-level .dockerignore - Would need complex patterns for subdirectories
- No .dockerignore - Build context would include GB of unnecessary files

## Best Practices Applied

### Multi-Stage Build Pattern
```dockerfile
# Stage 1: Build environment with all tools
FROM base AS builder
# Install build dependencies, compile, etc.

# Stage 2: Runtime environment (minimal)
FROM base AS runtime
# Copy only artifacts needed to run
```

### Layer Caching Optimization
1. Copy dependency files first (package.json, pyproject.toml)
2. Install dependencies (cached if files unchanged)
3. Copy source code last (changes frequently)

### Security Hardening
1. Non-root user execution
2. No secrets in build args or ENV
3. Minimal base images
4. Specific version tags (no :latest)

## References

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Next.js Docker Example](https://github.com/vercel/next.js/tree/canary/examples/with-docker)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Constitution v4.1.0 - Phase IV Principles](../../.specify/memory/constitution.md)
