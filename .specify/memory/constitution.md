<!--
Sync Impact Report:
- Version Change: 4.0.0 → 4.1.0 (MINOR)
- Rationale: Enhanced Phase IV constitution with concrete examples, corrected Python version, added missing patterns
- Modified Principles:
  * XVII. Container-First Architecture → Updated Python version 3.11→3.13, added graceful shutdown example, updated image size target
  * XIX. Immutable Infrastructure → Added graceful shutdown code example
  * XXI. Health Checks and Observability → Added frontend health check example, added resource limits example
- New Sections Added:
  * Graceful shutdown pattern with Python code example
  * Frontend health check example (Next.js API route)
  * Resource limits example with concrete values
  * Secret management production recommendation
- Removed Sections: None
- Templates Requiring Updates:
  ⚠ plan-template.md (Must reference containerization, K8s deployment, health checks)
  ⚠ spec-template.md (Must include deployment requirements, resource limits)
  ⚠ tasks-template.md (Must include Docker build, K8s manifests, Helm chart tasks)
- Follow-up TODOs:
  * Create Dockerfile templates for backend and frontend
  * Create Kubernetes manifest templates
  * Create Helm chart structure template
  * Document Minikube setup and testing procedures
-->

# Phase IV Local Kubernetes Deployment Constitution

## Phase Transition Context

**Phase I (Console App)**: Established fundamental CRUD operations, clean code practices, and spec-driven development methodology using in-memory storage and console interface.

**Phase II (Full-Stack Web App)**: Transitioned to production-ready, multi-user web application with persistent database, authentication, REST API, responsive UI, and cloud deployment on localhost. Built the foundational Web App Layer.

**Phase III (AI-Powered Chatbot)**: Introduced the **Intelligence Layer** with AI agents, MCP tools, and conversational interface. Users can interact via natural language while traditional GUI remains functional. MCP bridges AI and application logic.

**Phase IV (Local Kubernetes Deployment)**: Transitions from localhost development to **containerized, orchestrated deployment** on local Kubernetes (Minikube). Applications are packaged as Docker containers, deployed as Kubernetes pods, and managed through declarative manifests. This phase teaches cloud-native patterns, container orchestration, horizontal scaling, and production deployment fundamentals.

**Why This Transition Matters**: Modern cloud applications run in containers orchestrated by Kubernetes, not on bare metal servers. Phase IV demonstrates production deployment patterns: immutable infrastructure (containers are disposable), declarative configuration (manifests define desired state), horizontal scaling (multiple replicas), self-healing (Kubernetes restarts failed pods), and infrastructure-as-code. These are essential skills for deploying applications to any cloud provider (AWS, GCP, Azure, DigitalOcean).

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER (Minikube)             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Namespace: todo-app                                    │ │
│  │                                                          │ │
│  │  ┌──────────────────────┐    ┌──────────────────────┐  │ │
│  │  │ Frontend Deployment  │    │ Backend Deployment    │  │ │
│  │  │ (2 replicas)         │    │ (2 replicas)         │  │ │
│  │  │                      │    │                      │  │ │
│  │  │ ┌────────┐ ┌────────┐│    │ ┌────────┐ ┌────────┐│  │ │
│  │  │ │Pod 1   │ │Pod 2   ││    │ │Pod 1   │ │Pod 2   ││  │ │
│  │  │ │Next.js │ │Next.js ││    │ │FastAPI │ │FastAPI ││  │ │
│  │  │ │Container│ │Container││    │ │Container│ │Container││  │ │
│  │  │ └────────┘ └────────┘│    │ └────────┘ └────────┘│  │ │
│  │  └──────────┬────────────┘    └──────────┬───────────┘  │ │
│  │             │                            │              │ │
│  │             ▼                            ▼              │ │
│  │  ┌──────────────────┐        ┌──────────────────┐      │ │
│  │  │ frontend-service │        │ backend-service  │      │ │
│  │  │ (LoadBalancer)   │        │ (ClusterIP)      │      │ │
│  │  └────────┬─────────┘        └────────┬─────────┘      │ │
│  │           │                           │                │ │
│  └───────────┼───────────────────────────┼────────────────┘ │
│              │                           │                  │
└──────────────┼───────────────────────────┼──────────────────┘
               │                           │
               ▼                           ▼
         External Access            External Database
      (localhost:XXXXX)           (Neon PostgreSQL)

Phase III Flow: localhost:3000 → localhost:8000 → Neon
Phase IV Flow: LoadBalancer → Pod → ClusterIP → Pod → Neon
```

**Key Changes**:
- Applications run in **Docker containers** (isolated, reproducible)
- Containers managed by **Kubernetes pods** (scheduling, restart)
- Pods grouped in **Deployments** (replicas, rolling updates)
- **Services** provide stable networking (load balancing)
- **ConfigMaps** and **Secrets** inject configuration
- Multiple replicas enable **horizontal scaling**

## Core Principles (Phases I-III - Still Valid)

All principles from Phases I-III remain in effect. Phase IV adds deployment and infrastructure principles while preserving application architecture, security, and development methodology.

### I. Production-Ready Container-Native Architecture

Phase IV extends the architecture with containerization and orchestration. Applications packaged as Docker containers, deployed on Kubernetes, managed through declarative manifests. The Web App Layer and Intelligence Layer from Phase III now run in containers with multiple replicas for scalability and resilience.

**Rationale**: Containers provide consistency across environments (dev, staging, prod), isolation from host system, and portability across clouds. Kubernetes orchestration enables horizontal scaling (add more pods), self-healing (restart failed pods), zero-downtime deployments (rolling updates), and declarative infrastructure (manifests define desired state).

**Rules**:
- All Phase I-III architecture rules remain in effect
- Applications MUST be packaged as Docker containers (no bare-metal deployment)
- Containers MUST use multi-stage builds (optimize image size)
- Containers MUST run as non-root users (security)
- Kubernetes MUST orchestrate all services (no manual process management)
- Deployments MUST have 2+ replicas (enable horizontal scaling)
- Services MUST provide stable endpoints (ClusterIP for internal, LoadBalancer for external)
- ConfigMaps MUST store non-sensitive configuration
- Secrets MUST store sensitive data (API keys, passwords)
- Health checks MUST be implemented (liveness and readiness probes)
- Resource limits MUST be defined (CPU, memory)

### II. Spec-Driven Development (NON-NEGOTIABLE)

All code and infrastructure MUST be preceded by written specifications. No implementation may begin without approved spec.md, plan.md, and tasks.md files. Phase IV extends this to include containerization specs and Kubernetes deployment specs.

**Rationale**: Infrastructure-as-code requires the same rigor as application code. Dockerfile and Kubernetes manifests are code and must be spec-driven. Deployment architecture decisions (resource limits, replica counts, probe configurations) have production impact and must be documented.

**Rules**:
- All Phase I-III spec-driven rules remain in effect
- Spec MUST document container requirements (base images, build stages, security)
- Spec MUST define Kubernetes architecture (deployments, services, probes)
- Spec MUST specify resource limits (CPU, memory requests and limits)
- Spec MUST include health check endpoints and probe configurations
- Dockerfile changes MUST be documented in spec before implementation
- Kubernetes manifest changes MUST be version-controlled with rationale

### III. Test-First Development

Tests MUST be written or defined before implementation code. Phase IV extends this to include container testing (image builds, container runs), Kubernetes testing (pods start, services route traffic), and deployment testing (rolling updates, rollbacks).

**Rationale**: Infrastructure failures are harder to debug than application bugs. Container and Kubernetes tests verify deployment succeeds before production.

**Rules**:
- All Phase I-III testing rules remain in effect
- Container MUST be tested locally before Kubernetes deployment
- Health check endpoints MUST be tested (return 200 OK)
- Kubernetes pods MUST reach Running state in tests
- Services MUST route traffic correctly in tests
- Rolling updates MUST be tested (zero-downtime verified)
- Resource limits MUST be tested (pods don't exceed limits)
- Multi-replica deployment MUST be tested (load distribution)

### IV. Data Model Integrity with User Isolation and Conversation Persistence

Database schema MUST maintain referential integrity, enforce user isolation, and support stateless AI conversations. Phase IV does not change data model but ensures database remains accessible from containerized applications.

**Rationale**: External database (Neon) accessed from Kubernetes pods requires proper connection string management via Secrets.

**Rules**:
- All Phase I-III data model rules remain in effect
- DATABASE_URL MUST be stored in Kubernetes Secret (not ConfigMap)
- Database connections MUST use connection pooling (multiple pods)
- Database MUST be accessible from Kubernetes cluster (network policies if needed)

### V. Input Validation and Error Handling

All user input MUST be validated at BOTH frontend and backend. API endpoints MUST use Pydantic models for request validation. Errors MUST be handled gracefully. Phase IV adds container health check validation.

**Rationale**: Kubernetes uses health checks to determine if container is healthy. Failed health checks trigger pod restarts.

**Rules**:
- All Phase I-III validation rules remain in effect
- Health check endpoint MUST validate critical dependencies (database connection)
- Readiness probe MUST return 503 if dependencies unavailable
- Container MUST fail gracefully if required environment variables missing

### VI. Clean Code and Multi-Language Standards

Code MUST follow language-specific conventions and clean code principles. Phase IV adds infrastructure-as-code standards for Dockerfiles and Kubernetes manifests.

**Rationale**: Infrastructure code is code and must be maintainable, readable, and well-documented.

**Rules**:
- All Phase I-III code quality rules remain in effect
- Dockerfiles MUST be commented (explain each stage)
- Kubernetes manifests MUST have metadata labels (app, version, component)
- Helm charts MUST have values.yaml documentation
- Infrastructure decisions MUST be documented in plan.md

### VII. Windows via WSL 2 or Docker Desktop

Windows users MUST use either WSL 2 with Ubuntu OR Docker Desktop with Kubernetes enabled. Phase IV adds Docker Desktop as acceptable alternative since it includes Kubernetes.

**Rationale**: Docker Desktop provides integrated Kubernetes on Windows, making setup easier while maintaining Linux container compatibility.

**Rules**:
- WSL 2 rules from Phase I-III remain valid
- OR Docker Desktop with Kubernetes enabled is acceptable
- All containers MUST be Linux-based (not Windows containers)
- Docker daemon MUST be accessible from command line

### VIII. User Isolation and Data Security

Every API endpoint MUST require JWT authentication. Users MUST only access their own data. Phase IV ensures security principles apply in containerized environment with secrets management.

**Rationale**: Secrets in Kubernetes are base64-encoded (not encrypted by default). Proper secret management prevents credential exposure.

**Rules**:
- All Phase I-III security rules remain in effect
- Secrets MUST be stored in Kubernetes Secret resources (not hardcoded in images)
- Secrets MUST NOT be committed to Git (use templates)
- Environment variables MUST be injected from Secrets/ConfigMaps at runtime
- Container images MUST NOT contain hardcoded credentials

**Production Secret Management Note**:
For production deployments, consider enhanced secret management solutions:
- **Sealed Secrets**: Encrypt secrets for safe Git storage (Bitnami Sealed Secrets)
- **External Secrets Operator**: Sync secrets from external vaults (AWS Secrets Manager, HashiCorp Vault)
- **SOPS**: Mozilla's secret encryption tool for GitOps workflows

Base64 encoding is NOT encryption. Never rely on it for security.

### IX. RESTful API Design

API MUST follow RESTful conventions. Phase IV ensures API remains accessible from containers with proper service networking.

**Rationale**: Container networking uses service names instead of localhost.

**Rules**:
- All Phase I-III REST rules remain in effect
- Frontend in container MUST use backend service name (not localhost)
- Service names MUST be DNS-resolvable within cluster

### X. Authentication-First Approach

Authentication and authorization MUST be designed and implemented BEFORE building features. Phase IV ensures auth works in containerized environment.

**Rationale**: JWT tokens must work across container restarts and pod scaling.

**Rules**:
- All Phase I-III auth rules remain in effect
- BETTER_AUTH_SECRET MUST be stored in Kubernetes Secret
- JWT verification MUST work across multiple backend replicas (stateless)

### XI. Mobile-First Responsive Design

UI MUST be responsive and functional on mobile and desktop. Phase IV does not change this.

**Rules**:
- All Phase I-III responsive design rules remain in effect

### XII. Cloud-Native Deployment with Kubernetes Orchestration

Application MUST be deployed on Kubernetes (Minikube for Phase IV, cloud for Phase V). All services containerized, orchestrated, and managed through declarative manifests.

**Rationale**: Kubernetes is the industry standard for container orchestration. Learning Kubernetes on Minikube (local) prepares for cloud deployment (AWS EKS, GCP GKE, Azure AKS, DigitalOcean Kubernetes). Declarative infrastructure (YAML manifests) enables GitOps, version control, and reproducible deployments.

**Rules**:
- All services MUST run in Docker containers
- Containers MUST be deployed on Kubernetes (Minikube for local)
- Deployments MUST be defined declaratively (YAML manifests)
- Services MUST expose applications (LoadBalancer for frontend, ClusterIP for backend)
- ConfigMaps MUST store non-sensitive configuration
- Secrets MUST store sensitive data (base64-encoded)
- Namespace MUST be used (todo-app) for resource isolation
- Resource requests and limits MUST be defined
- Health probes MUST be configured (liveness and readiness)
- Helm charts MUST be used for package management
- Images MUST be tagged with specific versions (not :latest in production)

## Phase III Principles (Intelligence Layer - Still Valid)

All Phase III principles (XIII-XVI) remain in effect. The Intelligence Layer (AI agent, MCP tools, chat interface) now runs in containers on Kubernetes.

### XIII. MCP-First Architecture

All task operations MUST be exposed as MCP Tools. Phase IV does not change MCP architecture.

**Rules**: All Phase III MCP rules remain in effect.

### XIV. Stateless AI with Database Persistence

Agents MUST be stateless. Conversation history fetched from database. Phase IV emphasizes this is critical for container orchestration - pods can be killed/restarted anytime.

**Rationale**: Stateless architecture enables Kubernetes to scale pods horizontally and restart them without data loss.

**Rules**: All Phase III stateless rules remain in effect.

### XV. Agentic Workflow

Use OpenAI Agents SDK for intent recognition. No manual parsing. Phase IV unchanged.

**Rules**: All Phase III agentic workflow rules remain in effect.

### XVI. Agent Security and Instruction Safety

Agent boundaries enforced, prompt injection prevented. Phase IV unchanged.

**Rules**: All Phase III security rules remain in effect.

## Phase IV Principles (Deployment & Infrastructure)

### XVII. Container-First Architecture (NEW)

All application components MUST be packaged as Docker containers. Containers provide isolation, consistency, and portability. Multi-stage builds MUST be used to optimize image size and security.

**Rationale**: Containers ensure "works on my machine" problems disappear. Same container image runs in dev, staging, and production. Multi-stage builds separate build-time dependencies from runtime, reducing attack surface and image size.

**Rules**:
- Every service MUST have a Dockerfile (backend, frontend)
- Dockerfiles MUST use multi-stage builds (minimum 2 stages: builder + runtime)
- Base images MUST use specific versions (python:3.13-slim, node:20-alpine, NOT :latest)
- Final stage MUST run as non-root user (create user with UID > 10000)
- Containers MUST expose single port (8000 for backend, 3000 for frontend)
- .dockerignore MUST exclude unnecessary files (node_modules, .git, tests)
- Health check MUST be defined in Dockerfile (HEALTHCHECK instruction)
- Images MUST be tagged with version (todo-backend:v1.0.0)
- Build process MUST be documented in README
- Images MUST be optimized (< 600MB backend, < 200MB frontend)

**Multi-Stage Dockerfile Pattern**:
```dockerfile
# Stage 1: Dependencies
FROM python:3.13-slim AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim
RUN useradd -m -u 10001 appuser
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY app/ /app/
USER appuser
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### XVIII. Declarative Infrastructure (NEW)

All infrastructure MUST be defined through declarative configuration files (Kubernetes YAML manifests, Helm charts). No manual kubectl create commands in production. Desired state defined in Git, Kubernetes reconciles actual state to match desired state.

**Rationale**: Declarative infrastructure enables GitOps (Git as single source of truth), version control for infrastructure, reproducible deployments, and rollback capability. Imperative commands (kubectl run, kubectl create) are not version-controlled and cannot be audited.

**Rules**:
- All Kubernetes resources MUST be defined in YAML manifests (no imperative kubectl commands)
- Manifests MUST be stored in k8s/ directory
- Namespace MUST be explicitly defined (not default)
- Labels MUST be applied (app: backend, version: v1.0.0, component: api)
- Helm charts MUST be used for templating (values.yaml for configuration)
- Changes to infrastructure MUST go through Git (no direct kubectl edit)
- Manifests MUST be validated before apply (kubectl apply --dry-run)

**Manifest Pattern**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-app
  labels:
    app: backend
    version: v1.0.0
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: todo-backend:v1.0.0
        ports:
        - containerPort: 8000
```

### XIX. Immutable Infrastructure (NEW)

Containers are immutable and disposable. Once built, container images MUST NOT be modified. Updates require building new image version. Kubernetes MUST be able to kill and restart pods at any time without data loss.

**Rationale**: Immutable infrastructure prevents configuration drift (production servers diverging from each other), enables safe rollbacks (just redeploy previous image), and simplifies debugging (exact image version known). Stateless pods can be killed/restarted freely, enabling self-healing and zero-downtime deployments.

**Rules**:
- Container images MUST be immutable (no runtime modifications)
- Configuration MUST be injected via environment variables (not baked into image)
- Updates MUST create new image with new tag (not overwrite existing tag)
- Pods MUST be stateless (no local file storage for user data)
- Persistent data MUST be stored externally (database, object storage)
- Kubernetes MUST be able to kill any pod at any time (application handles gracefully)
- Rolling updates MUST not cause data loss (database transactions atomic)

**Immutability Pattern**:
```bash
# BAD: Modify running container (changes lost on pod restart)
kubectl exec pod -- apt-get install curl

# GOOD: Update Dockerfile, rebuild image, deploy new version
# 1. Update Dockerfile to include curl
# 2. Build new image: docker build -t todo-backend:v1.0.1 .
# 3. Update manifest to use v1.0.1
# 4. Apply: kubectl apply -f deployment.yaml (rolling update)
```

**Graceful Shutdown Pattern**:
```python
# backend/app/main.py
from contextlib import asynccontextmanager
from sqlmodel.ext.asyncio.session import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    yield
    # Shutdown: Clean up resources gracefully
    await engine.dispose()  # Close all DB connections
    print("Graceful shutdown complete")

app = FastAPI(lifespan=lifespan)
```

Kubernetes sends SIGTERM before killing pods. Applications MUST handle this signal to close connections and complete in-flight requests within the terminationGracePeriodSeconds (default 30s).

### XX. Cloud-Native Patterns and 12-Factor App (NEW)

Application MUST follow 12-factor app principles: codebase in Git, dependencies declared explicitly, config in environment, backing services as attached resources, build/release/run separation, stateless processes, port binding, concurrency via process model, disposability, dev/prod parity, logs to stdout, admin processes.

**Rationale**: 12-factor methodology ensures applications are cloud-native, scalable, and maintainable. These patterns are industry best practices for modern web applications.

**Rules**:
- Codebase: Single Git repo, multiple deployments
- Dependencies: requirements.txt (Python), package.json (Node) version-locked
- Config: All configuration via environment variables (no hardcoded values)
- Backing Services: Database, OpenAI API treated as attached resources (URLs in env vars)
- Build/Release/Run: Strict separation (docker build → tag → kubectl apply)
- Processes: Stateless, share-nothing (no local sessions, conversation in database)
- Port Binding: Apps export services via port (8000, 3000)
- Concurrency: Scale via replicas (not threads)
- Disposability: Fast startup, graceful shutdown
- Dev/Prod Parity: Same containers in dev (Minikube) and prod (cloud)
- Logs: All logs to stdout/stderr (collected by Kubernetes)
- Admin: Admin tasks as one-off pods (kubectl run or jobs)

### XXI. Health Checks and Observability (NEW)

All services MUST implement health check endpoints. Kubernetes MUST monitor application health through liveness and readiness probes. Logs MUST go to stdout/stderr for Kubernetes collection.

**Rationale**: Health checks enable self-healing. If container becomes unresponsive, Kubernetes automatically restarts it. Readiness probes prevent traffic to unhealthy pods. Centralized logging (Kubernetes collects from stdout) enables debugging across multiple pods.

**Rules**:
- Backend MUST implement GET /health endpoint (returns 200 OK if healthy)
- Backend MUST implement GET /ready endpoint (returns 200 OK if ready for traffic)
- Health endpoint MUST check critical dependencies (database connection optional)
- Readiness endpoint MUST check ALL dependencies (database, OpenAI API if critical)
- Liveness probe MUST be configured in Kubernetes (restart pod if fails)
- Readiness probe MUST be configured in Kubernetes (remove from service if fails)
- Probe initial delay MUST account for startup time (5-10 seconds)
- All logs MUST go to stdout/stderr (no log files in container)
- Log format MUST be structured (JSON preferred for parsing)

**Backend Health Check Pattern**:
```python
# backend/app/main.py
@app.get("/health")
async def health_check():
    """Liveness probe - is process alive?"""
    return {"status": "ok"}

@app.get("/ready")
async def readiness_check():
    """Readiness probe - ready for traffic?"""
    # Check database connection
    try:
        await db.execute("SELECT 1")
        return {"status": "ready", "database": "connected"}
    except:
        raise HTTPException(503, "Database unavailable")
```

**Frontend Health Check Pattern (Next.js)**:
```typescript
// frontend/app/api/health/route.ts
export async function GET() {
  return Response.json({ status: "ok" });
}

// frontend/app/api/ready/route.ts
export async function GET() {
  // Check if backend API is reachable
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
    if (res.ok) {
      return Response.json({ status: "ready", backend: "connected" });
    }
    return Response.json({ status: "not_ready" }, { status: 503 });
  } catch {
    return Response.json({ status: "not_ready", backend: "unreachable" }, { status: 503 });
  }
}
```

**Kubernetes Probe Configuration**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

**Resource Limits Pattern**:
```yaml
# Backend container resources
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"

# Frontend container resources
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "300m"
```

Resource requests guarantee minimum allocation; limits cap maximum usage. Pods exceeding memory limits are OOMKilled. CPU limits cause throttling. Start conservative and adjust based on monitoring.

## Scope and Constraints

### In Scope (Phase IV)
- All Phase I-III scope remains (application features unchanged)
- Docker containerization (backend, frontend)
- Multi-stage Dockerfile builds
- docker-compose.yml for local orchestration
- Kubernetes deployment on Minikube
- Deployments with 2 replicas each
- Services (LoadBalancer, ClusterIP)
- ConfigMaps for configuration
- Secrets for sensitive data
- Health and readiness probes
- Resource limits and requests
- Helm chart structure
- Rolling update strategy
- Deployment documentation

### Out of Scope (Phase V or Future)
- Production cloud deployment (DigitalOcean/AWS/GCP)
- CI/CD pipelines (GitHub Actions)
- Ingress controller and TLS certificates
- Monitoring and logging infrastructure (Prometheus, Grafana)
- Event-driven architecture (Kafka, Dapr)
- Service mesh (Istio, Linkerd)
- Auto-scaling (HPA, VPA)
- Persistent volumes (StatefulSets)

### Technology Constraints (Phase IV Additions)
- All Phase I-III constraints remain
- Containerization: Docker, docker-compose
- Orchestration: Kubernetes (Minikube for local)
- Package Management: Helm 3+
- Base Images: python:3.13-slim, node:20-alpine
- NO Docker Swarm, Nomad, or other orchestrators
- NO custom container runtimes (use Docker)

## Project Structure (Phase IV Additions)

Phase IV adds deployment artifacts to the Phase I-III structure:

```
hackathon-full-stack-template/
├── backend/
│   ├── Dockerfile                  # NEW: Multi-stage backend container
│   ├── .dockerignore               # NEW: Exclude build context files
│   └── ...                         # Existing backend files
├── frontend/
│   ├── Dockerfile                  # NEW: Multi-stage frontend container
│   ├── .dockerignore               # NEW: Exclude build context files
│   └── ...                         # Existing frontend files
├── docker-compose.yml              # NEW: Local orchestration
├── k8s/                            # NEW: Kubernetes manifests
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml.template        # Template (actual secret not committed)
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   └── frontend-service.yaml
├── helm/                           # NEW: Helm chart
│   └── todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── deployment.yaml
│           └── service.yaml
├── DEPLOYMENT.md                   # NEW: Deployment guide
└── ...                             # Existing files
```

## Development Workflow (Phase IV Additions)

### Containerization Phase
1. Write Dockerfiles (multi-stage) for backend and frontend
2. Create .dockerignore files
3. Build images locally: `docker build -t todo-backend:v1.0.0 backend/`
4. Test containers: `docker run -p 8000:8000 todo-backend:v1.0.0`
5. Verify health endpoints work in container

### Local Orchestration Phase
1. Create docker-compose.yml
2. Define services (frontend, backend)
3. Configure networking
4. Test: `docker-compose up`
5. Verify multi-container communication

### Kubernetes Deployment Phase
1. Start Minikube: `minikube start`
2. Build images in Minikube context: `eval $(minikube docker-env)`
3. Create namespace: `kubectl create ns todo-app`
4. Apply ConfigMap and Secrets
5. Apply Deployments and Services
6. Verify pods: `kubectl get pods -n todo-app`
7. Access application: `minikube service frontend-service -n todo-app --url`

### Helm Chart Phase
1. Create Helm chart structure
2. Templatize manifests
3. Create values.yaml
4. Install: `helm install todo-app ./helm/todo-app`
5. Test upgrade: `helm upgrade todo-app ./helm/todo-app`

## Success Criteria (Phase IV)

Phase IV is complete when ALL Phase I-III criteria remain met AND:

### Containerization
- ✅ Backend Dockerfile builds successfully
- ✅ Frontend Dockerfile builds successfully
- ✅ Images use multi-stage builds (optimized size)
- ✅ Containers run as non-root users
- ✅ Health check endpoints implemented and working
- ✅ docker-compose brings up full stack locally
- ✅ .dockerignore files exclude unnecessary files

### Kubernetes Deployment
- ✅ Minikube cluster operational
- ✅ Namespace created (todo-app)
- ✅ ConfigMap applied with non-sensitive config
- ✅ Secrets applied with sensitive data
- ✅ Backend deployment created with 2 replicas
- ✅ Frontend deployment created with 2 replicas
- ✅ Backend service (ClusterIP) routing traffic
- ✅ Frontend service (LoadBalancer) accessible externally
- ✅ All pods in Running state
- ✅ Health probes configured and passing
- ✅ Resource limits defined (CPU, memory)

### Application Functionality
- ✅ All Phase I-III features work in Kubernetes
- ✅ User can signup/signin through LoadBalancer
- ✅ User can create/view/update/delete tasks
- ✅ AI chatbot works in containerized environment
- ✅ Database connection works from pods
- ✅ OpenAI API accessible from backend pods

### Helm Charts
- ✅ Helm chart structure created
- ✅ Chart.yaml with metadata
- ✅ values.yaml with parameterized config
- ✅ Templates for all resources
- ✅ Helm install succeeds
- ✅ Helm upgrade works (rolling update)

### Testing
- ✅ Container builds tested (no errors)
- ✅ Container runs tested (starts successfully)
- ✅ Pod deployment tested (reaches Running state)
- ✅ Service routing tested (traffic reaches pods)
- ✅ Health probes tested (return correct status)
- ✅ Rolling update tested (zero downtime)
- ✅ Pod restart tested (application recovers)
- ✅ Multi-replica load balancing tested

### Documentation
- ✅ DEPLOYMENT.md created with setup instructions
- ✅ Dockerfile comments explain each stage
- ✅ Kubernetes manifests have resource descriptions
- ✅ Helm values.yaml documented
- ✅ Troubleshooting guide included
- ✅ Architecture diagram updated with K8s components

## Governance

### Amendment Process
Constitution changes MUST be documented with:
- Clear rationale for the change
- Version increment following semantic versioning
- Update to dependent templates (spec, plan, tasks)
- Sync Impact Report (HTML comment at top of file)
- Approval before taking effect

### Version Semantics
- MAJOR: Principle removal, fundamental architectural change (e.g., Phase III → Phase IV deployment shift)
- MINOR: New principle added, significant expansion
- PATCH: Clarifications, examples, formatting

### Compliance
- All spec.md files MUST reference relevant constitution principles
- All plan.md files MUST include "Constitution Check" section
- All code reviews MUST verify constitutional compliance
- Infrastructure changes MUST comply with deployment principles (XVII-XXI)

### Compliance Review Checklist (Phase IV Additions)
Before marking Phase IV complete, verify:
- [ ] All services containerized with Dockerfiles (Principle XVII)
- [ ] Multi-stage builds used (Principle XVII)
- [ ] Kubernetes manifests declarative (Principle XVIII)
- [ ] Containers immutable (Principle XIX)
- [ ] 12-factor principles followed (Principle XX)
- [ ] Health endpoints implemented (Principle XXI)
- [ ] Liveness and readiness probes configured (Principle XXI)
- [ ] ConfigMaps and Secrets used (Principle XVIII)
- [ ] Resource limits defined (Principle XVIII)
- [ ] Helm chart created (Principle XVIII)
- [ ] All Phase I-III features work in Kubernetes
- [ ] No secrets committed to Git (Principle VIII)

**Version**: 4.1.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-24
