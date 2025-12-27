<!--
Sync Impact Report:
- Version Change: 4.1.0 → 5.0.0 (MAJOR)
- Rationale: Fundamental architecture shift from synchronous HTTP to event-driven Dapr+Kafka. Introduces breaking changes in service communication patterns, deployment targets (local → cloud), and infrastructure automation (manual → CI/CD).
- Modified Principles:
  * I. Production-Ready Architecture → Extended to Event-Driven & Sidecar Pattern
  * XII. Cloud-Native Deployment → Minikube → Cloud (DOKS/AKS/GKE)
  * XVII. Container-First Architecture → Added Dapr sidecar annotations
  * XXI. Health Checks and Observability → Added Dapr observability integration
- New Principles Added:
  * XXII. Event-Driven Architecture (Pub/Sub via Dapr+Kafka)
  * XXIII. Sidecar Pattern with Dapr Abstraction
  * XXIV. Infrastructure Independence and Portability
  * XXV. Automated Delivery with CI/CD
  * XXVI. Advanced Task Management Features
- Removed Sections: None (all Phase IV principles remain valid)
- Templates Requiring Updates:
  ⚠ plan-template.md (Must include Dapr components, Kafka topics, event flows)
  ⚠ spec-template.md (Must include event definitions, async workflows)
  ⚠ tasks-template.md (Must include Dapr setup, Kafka deployment, CI/CD tasks)
- Follow-up TODOs:
  * Create Dapr component YAML templates (pubsub, statestore, secretstore)
  * Create GitHub Actions workflow templates
  * Create cloud provider deployment guides (DOKS, AKS)
  * Document Kafka/Redpanda setup procedures
  * Create event schema documentation template
-->

# Phase V Cloud Deployment & Event-Driven Architecture Constitution

## Phase Transition Context

**Phase I (Console App)**: Established fundamental CRUD operations, clean code practices, and spec-driven development methodology using in-memory storage and console interface.

**Phase II (Full-Stack Web App)**: Transitioned to production-ready, multi-user web application with persistent database, authentication, REST API, responsive UI, and cloud deployment on localhost. Built the foundational Web App Layer.

**Phase III (AI-Powered Chatbot)**: Introduced the **Intelligence Layer** with AI agents, MCP tools, and conversational interface. Users can interact via natural language while traditional GUI remains functional. MCP bridges AI and application logic.

**Phase IV (Local Kubernetes Deployment)**: Transitioned from localhost development to **containerized, orchestrated deployment** on local Kubernetes (Minikube). Applications packaged as Docker containers, deployed as Kubernetes pods, managed through declarative manifests. Demonstrated cloud-native patterns: immutable infrastructure, horizontal scaling, self-healing.

**Phase V (Cloud Deployment & Event-Driven Architecture)**: Transforms the application into a **distributed, event-driven system** deployed on real cloud infrastructure. Introduces the **Architecture of Intelligence** through Dapr sidecars and Kafka event streaming. Services communicate asynchronously through events instead of synchronous HTTP calls. Automated CI/CD pipelines replace manual deployments. Advanced task features (recurring tasks, reminders, priorities) leverage event-driven patterns.

**Why This Transition Matters**: Modern distributed systems use event-driven architectures for scalability, resilience, and decoupling. Dapr provides infrastructure abstractions (Pub/Sub, State, Secrets) that work across any cloud provider. Kafka enables asynchronous processing, event sourcing, and real-time data pipelines. CI/CD automation ensures reliable, repeatable deployments. This is the architecture used by production systems at scale (Netflix, Uber, LinkedIn).

## Architecture Overview

```
┌───────────────────────────────────────────────────────────────────────┐
│                    CLOUD KUBERNETES CLUSTER (DOKS/AKS/GKE)            │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │  Namespace: todo-app                                              │ │
│  │                                                                    │ │
│  │  ┌─────────────────────┐           ┌─────────────────────┐        │ │
│  │  │ Frontend Deployment │           │ Backend Deployment  │        │ │
│  │  │ (2+ replicas)       │           │ (2+ replicas)       │        │ │
│  │  │                     │           │                     │        │ │
│  │  │ ┌────────────────┐  │           │ ┌────────────────┐  │        │ │
│  │  │ │ Pod 1          │  │           │ │ Pod 1          │  │        │ │
│  │  │ │ ┌────────────┐ │  │           │ │ ┌────────────┐ │  │        │ │
│  │  │ │ │ Next.js    │ │  │           │ │ │ FastAPI    │ │  │        │ │
│  │  │ │ │ Container  │ │  │           │ │ │ Container  │ │  │        │ │
│  │  │ │ └────────────┘ │  │           │ │ └────────────┘ │  │        │ │
│  │  │ │ ┌────────────┐ │  │           │ │ ┌────────────┐ │  │        │ │
│  │  │ │ │ Dapr       │ │  │           │ │ │ Dapr       │ │  │        │ │
│  │  │ │ │ Sidecar    │ │  │◄──────────┼─┼─┤ Sidecar    │ │  │        │ │
│  │  │ │ └────────────┘ │  │  Service  │ │ └────────────┘ │  │        │ │
│  │  │ └────────┬───────┘  │ Invocation│ └────────┬───────┘  │        │ │
│  │  │          │          │           │          │          │        │ │
│  │  └──────────┼──────────┘           └──────────┼──────────┘        │ │
│  │             │                                  │                   │ │
│  │             │         ┌────────────────────┐   │                   │ │
│  │             │         │ Kafka / Redpanda   │   │                   │ │
│  │             └────────►│ Event Streaming    │◄──┘                   │ │
│  │                       │                    │                       │ │
│  │                       │ Topics:            │                       │ │
│  │                       │ - task-events      │                       │ │
│  │                       │ - reminders        │                       │ │
│  │                       │ - task-updates     │                       │ │
│  │                       └────────────────────┘                       │ │
│  │                                                                    │ │
│  │  ┌──────────────────┐        ┌──────────────────┐                 │ │
│  │  │ frontend-service │        │ backend-service  │                 │ │
│  │  │ (LoadBalancer)   │        │ (ClusterIP)      │                 │ │
│  │  └────────┬─────────┘        └────────┬─────────┘                 │ │
│  │           │                           │                           │ │
│  └───────────┼───────────────────────────┼───────────────────────────┘ │
│              │                           │                             │
└──────────────┼───────────────────────────┼─────────────────────────────┘
               │                           │
               ▼                           ▼
         Public IP/Domain           External Database
       (LoadBalancer URL)          (Neon PostgreSQL)

Phase IV Flow: LoadBalancer → Pod → ClusterIP → Pod → Neon
Phase V Flow: LoadBalancer → Dapr → Kafka → Dapr → Pod → Neon
```

**Key Changes from Phase IV**:
- **Dapr sidecars** run alongside application containers (sidecar pattern)
- **Kafka/Redpanda** handles event streaming (asynchronous communication)
- Services communicate via **Dapr Pub/Sub** (not direct HTTP for async operations)
- **Service Invocation** through Dapr (resilience, retries, circuit breakers)
- **State management** via Dapr State Store (chatbot session history)
- **Secrets** fetched via Dapr Secret Store (not direct Kubernetes Secrets)
- Deployed on **real cloud cluster** (DigitalOcean, Azure, or GCP)
- **CI/CD automation** (GitHub Actions) replaces manual deployments

## Core Principles (Phases I-III - Still Valid)

All principles from Phases I-III remain in effect. Phase V adds event-driven architecture, Dapr integration, cloud deployment, and CI/CD automation while preserving application security, data integrity, and development methodology.

### I. Production-Ready Event-Driven Architecture

Phase V extends the architecture with event-driven patterns using Dapr and Kafka. The Web App Layer and Intelligence Layer from Phase III now communicate asynchronously through events. Applications remain containerized (Phase IV) but add Dapr sidecars for infrastructure abstraction.

**Rationale**: Event-driven architecture decouples services, enabling independent scaling, fault tolerance, and asynchronous processing. Dapr provides portable abstractions (Pub/Sub, State, Secrets) that work across any cloud provider or infrastructure. Kafka enables event streaming, event sourcing, and real-time data pipelines. Sidecar pattern separates infrastructure concerns (retries, circuit breakers, observability) from application logic.

**Rules**:
- All Phase I-IV architecture rules remain in effect
- Services MUST communicate asynchronously for non-blocking operations (task creation triggers events)
- Synchronous HTTP calls MUST go through Dapr Service Invocation (not direct service URLs)
- Event-driven workflows MUST use Dapr Pub/Sub (not direct Kafka clients)
- Application code MUST NOT contain cloud-specific APIs (use Dapr abstractions)
- Dapr sidecars MUST run alongside every application container
- Event schemas MUST be documented and version-controlled
- Dead letter queues MUST handle failed event processing

### II. Spec-Driven Development (NON-NEGOTIABLE)

All code, infrastructure, and event schemas MUST be preceded by written specifications. Phase V extends this to include event definitions, Dapr component specs, and CI/CD pipeline specs.

**Rationale**: Event-driven systems are harder to debug than synchronous systems. Events travel through multiple services asynchronously. Without specifications, debugging becomes impossible. Dapr components (Pub/Sub, State Store) are infrastructure-as-code and must be spec-driven.

**Rules**:
- All Phase I-IV spec-driven rules remain in effect
- Event schemas MUST be documented in spec before implementation
- Dapr component YAML MUST be spec-driven (pubsub, statestore, secretstore)
- Event flows MUST be documented (which service publishes, which subscribes)
- CI/CD pipeline changes MUST be spec-driven (documented before implementation)
- Async workflows MUST have acceptance criteria (eventual consistency documented)

### III. Test-First Development

Tests MUST be written or defined before implementation code. Phase V extends this to include event testing (publish/subscribe), Dapr component testing, and cloud deployment testing.

**Rationale**: Event-driven systems require integration testing across services. Unit tests alone are insufficient. Dapr components must be tested in realistic environment.

**Rules**:
- All Phase I-IV testing rules remain in effect
- Event publishing MUST be tested (message reaches topic)
- Event subscription MUST be tested (handler processes message)
- Dapr Pub/Sub MUST be tested (end-to-end flow)
- Dapr State Store MUST be tested (save/retrieve state)
- CI/CD pipeline MUST be tested (deploy succeeds)
- Cloud deployment MUST be tested (pods reach Running state)
- Event ordering MUST be tested if required
- Idempotency MUST be tested (duplicate events handled)

### IV. Data Model Integrity with User Isolation and Conversation Persistence

Database schema MUST maintain referential integrity, enforce user isolation, and support stateless AI conversations. Phase V adds task management fields for advanced features (priority, tags, recurring tasks, reminders).

**Rationale**: Event-driven task management requires additional metadata. Recurring tasks need interval specification. Reminders need due dates. Priority and tags enable advanced organization.

**Rules**:
- All Phase I-IV data model rules remain in effect
- Tasks table MUST add: `priority` (enum: Low, Medium, High)
- Tasks table MUST add: `tags` (JSON array for multiple tags)
- Tasks table MUST add: `due_date` (timestamp for reminders)
- Tasks table MUST add: `is_recurring` (boolean flag)
- Tasks table MUST add: `recurring_interval` (string: daily, weekly, monthly)
- Database migrations MUST be version-controlled (Alembic)
- User isolation MUST apply to all new fields (user_id foreign key)

### V. Input Validation and Error Handling

All user input MUST be validated at BOTH frontend and backend. API endpoints MUST use Pydantic models for request validation. Errors MUST be handled gracefully. Phase V adds event validation and dead letter queue handling.

**Rationale**: Invalid events can poison message queues. Events must be validated before publishing. Failed event processing must be retried or moved to dead letter queue.

**Rules**:
- All Phase I-IV validation rules remain in effect
- Event payloads MUST be validated with Pydantic models before publishing
- Event handlers MUST validate messages before processing
- Failed events MUST be retried (configurable retry policy)
- Permanently failed events MUST go to dead letter queue
- Event schema violations MUST be logged and alerted

### VI. Clean Code and Multi-Language Standards

Code MUST follow language-specific conventions and clean code principles. Phase V adds event handler standards and Dapr component configuration standards.

**Rationale**: Event handlers are code and must be maintainable. Dapr components are configuration-as-code and must be documented.

**Rules**:
- All Phase I-IV code quality rules remain in effect
- Event handlers MUST be idempotent (safe to process same event multiple times)
- Event payloads MUST use strong types (Pydantic models)
- Dapr component YAML MUST have comments explaining configuration
- CI/CD pipeline YAML MUST have comments for each step
- Event topics MUST have naming convention (kebab-case, noun-based)

### VII. Windows via WSL 2 or Docker Desktop

Windows users MUST use either WSL 2 with Ubuntu OR Docker Desktop with Kubernetes enabled. Phase V unchanged.

**Rules**:
- All Phase I-IV rules remain in effect

### VIII. User Isolation and Data Security

Every API endpoint MUST require JWT authentication. Users MUST only access their own data. Phase V adds event-level user isolation and Dapr secret management.

**Rationale**: Events must carry user context. Event handlers must enforce user isolation. Dapr Secret Store provides encrypted secret management.

**Rules**:
- All Phase I-IV security rules remain in effect
- Events MUST include user_id in payload (for user-scoped processing)
- Event handlers MUST enforce user isolation (verify user_id)
- Secrets MUST be fetched via Dapr Secret Store API (not direct Kubernetes Secrets)
- Dapr components MUST use `secretstores.kubernetes` component
- API keys and tokens MUST NOT be in Dapr component YAML (reference secrets by name)

### IX. RESTful API Design

API MUST follow RESTful conventions. Phase V adds Dapr Service Invocation for inter-service calls and maintains REST for external clients.

**Rationale**: Frontend still uses REST API (browser compatibility). Backend-to-backend calls use Dapr Service Invocation for resilience and observability.

**Rules**:
- All Phase I-IV REST rules remain in effect
- External clients (browser) MUST use REST API
- Internal service calls MUST use Dapr Service Invocation
- Dapr Service Invocation URL pattern: `http://localhost:3500/v1.0/invoke/<app-id>/method/<endpoint>`
- Services MUST be registered with Dapr app-id annotation

### X. Authentication-First Approach

Authentication and authorization MUST be designed and implemented BEFORE building features. Phase V ensures auth works across event-driven flows.

**Rationale**: Events carry user context. Authentication tokens must be validated in event handlers.

**Rules**:
- All Phase I-IV auth rules remain in effect
- Event payloads MUST include authentication context (user_id)
- Event handlers MUST validate user permissions before processing
- JWT tokens MUST work across Dapr sidecar requests

### XI. Mobile-First Responsive Design

UI MUST be responsive and functional on mobile and desktop. Phase V unchanged.

**Rules**:
- All Phase I-IV responsive design rules remain in effect

### XII. Cloud-Native Deployment with Production Kubernetes

Application MUST be deployed on production-grade cloud Kubernetes (DigitalOcean DOKS, Azure AKS, or Google GKE). All services containerized, orchestrated through Kubernetes, with Dapr runtime installed cluster-wide.

**Rationale**: Minikube is for learning; production systems run on managed Kubernetes services. Cloud providers handle cluster upgrades, node scaling, and infrastructure reliability. Dapr installed cluster-wide (dapr-system namespace) provides runtime for all applications.

**Rules**:
- All Phase IV Kubernetes rules remain in effect
- Cluster MUST be on cloud provider (DigitalOcean, Azure, or GCP - NOT Minikube)
- Dapr MUST be installed cluster-wide (`dapr init -k`)
- Dapr components MUST be defined (pubsub.yaml, statestore.yaml, secretstore.yaml)
- Kafka/Redpanda MUST be deployed (Strimzi Operator or managed service)
- Ingress controller MUST be configured (expose services externally)
- TLS certificates MUST be provisioned (Let's Encrypt or cloud cert manager)
- DNS MUST point to LoadBalancer IP (custom domain or cloud provider subdomain)
- Horizontal Pod Autoscaler (HPA) SHOULD be configured (scale based on CPU/memory)

## Phase III Principles (Intelligence Layer - Still Valid)

All Phase III principles (XIII-XVI) remain in effect. The Intelligence Layer (AI agent, MCP tools, chat interface) now runs in containers on cloud Kubernetes with Dapr sidecars.

### XIII. MCP-First Architecture

All task operations MUST be exposed as MCP Tools. Phase V adds event publishing to MCP tool execution.

**Rules**:
- All Phase III MCP rules remain in effect
- MCP tools MAY publish events after task operations (e.g., add_task publishes task-created event)

### XIV. Stateless AI with Database Persistence

Agents MUST be stateless. Conversation history stored in database. Phase V adds Dapr State Store as alternative storage for session state.

**Rationale**: Dapr State Store provides key-value storage abstraction. Can be backed by PostgreSQL, Redis, or cloud provider state stores.

**Rules**:
- All Phase III stateless rules remain in effect
- Chatbot session state MAY use Dapr State Store API
- Long-term conversation history MUST remain in PostgreSQL (searchable, queryable)

### XV. Agentic Workflow

Use OpenAI Agents SDK for intent recognition. No manual parsing. Phase V unchanged.

**Rules**: All Phase III agentic workflow rules remain in effect.

### XVI. Agent Security and Instruction Safety

Agent boundaries enforced, prompt injection prevented. Phase V unchanged.

**Rules**: All Phase III security rules remain in effect.

## Phase IV Principles (Deployment & Infrastructure - Still Valid)

All Phase IV containerization and Kubernetes principles remain in effect. Phase V builds on this foundation by adding Dapr sidecars, event-driven communication, and cloud deployment.

### XVII. Container-First Architecture with Dapr Sidecars

All application components MUST be packaged as Docker containers with Dapr sidecars. Containers provide isolation; Dapr provides infrastructure abstraction.

**Rationale**: Dapr sidecar pattern separates infrastructure logic (Pub/Sub, State, Secrets) from application logic. Application code remains simple HTTP calls to localhost:3500 (Dapr sidecar). Dapr handles retry logic, circuit breakers, and observability.

**Rules**:
- All Phase IV container rules remain in effect
- Kubernetes Deployments MUST have Dapr annotations:
  ```yaml
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "backend"          # Service identifier
    dapr.io/app-port: "8000"           # Application port
    dapr.io/log-level: "info"
  ```
- Containers MUST NOT include Kafka client libraries (use Dapr Pub/Sub API)
- Containers MUST NOT access Kubernetes Secrets directly (use Dapr Secret Store API)

### XVIII. Declarative Infrastructure

All infrastructure MUST be defined through declarative configuration files. Phase V adds Dapr components and CI/CD pipelines to declarative requirements.

**Rationale**: Dapr components (Pub/Sub, State Store, Secret Store) are infrastructure and must be version-controlled. GitHub Actions workflows are infrastructure-as-code.

**Rules**:
- All Phase IV declarative rules remain in effect
- Dapr components MUST be defined in YAML (components/ directory)
- CI/CD pipelines MUST be defined in .github/workflows/
- Kafka topics MUST be created declaratively (not manual kafka-topics.sh)
- Infrastructure changes MUST go through Git (GitOps workflow)

### XIX. Immutable Infrastructure

Containers are immutable and disposable. Phase V unchanged - extends to event handlers.

**Rationale**: Event handlers are stateless functions. Pods can be killed mid-processing; events will be redelivered.

**Rules**:
- All Phase IV immutability rules remain in effect
- Event handlers MUST be stateless (no local variables persisted across events)
- In-flight events MUST be safe to reprocess after pod restart (idempotency)

### XX. Cloud-Native Patterns and 12-Factor App

Application MUST follow 12-factor app principles. Phase V emphasizes backing services (Kafka as attached resource) and concurrency (event-driven scaling).

**Rules**:
- All Phase IV 12-factor rules remain in effect
- Kafka MUST be treated as attached resource (connection URL in env var)
- Concurrency MUST be achieved via event partitions and consumer groups (not threads)

### XXI. Health Checks and Observability

All services MUST implement health check endpoints. Phase V adds Dapr observability integration (distributed tracing, metrics).

**Rationale**: Dapr automatically exports metrics (Prometheus), traces (Zipkin/Jaeger), and logs. Health checks must verify Dapr sidecar is ready.

**Rules**:
- All Phase IV health check rules remain in effect
- Health endpoint MAY check Dapr sidecar health (`http://localhost:3500/v1.0/healthz`)
- Dapr observability MUST be enabled (Prometheus, Zipkin/Jaeger)
- Distributed tracing MUST track events across services

## Phase V Principles (Event-Driven & Cloud Deployment)

### XXII. Event-Driven Architecture (NEW)

Application MUST use event-driven patterns for asynchronous operations. Task creation, updates, and deletions MUST publish events. Reminders and recurring tasks MUST be triggered by events. Services MUST communicate via Dapr Pub/Sub for async workflows.

**Rationale**: Event-driven architecture enables loose coupling (services don't know about each other), scalability (add consumers without changing producers), resilience (events buffered in Kafka during outages), and real-time processing (react to events as they occur). Synchronous HTTP calls block; events are fire-and-forget. Recurring tasks and reminders are inherently asynchronous and fit event-driven model.

**Rules**:
- Task CRUD operations MUST publish events to `task-events` topic
  - Events: `task.created`, `task.updated`, `task.completed`, `task.deleted`
- Reminder system MUST subscribe to `task-events` and publish to `reminders` topic
- Recurring task scheduler MUST publish events based on interval
- Event payloads MUST include: `event_type`, `user_id`, `task_id`, `timestamp`, `data`
- Events MUST be published via Dapr Pub/Sub API (`POST http://localhost:3500/v1.0/publish/<pubsub>/<topic>`)
- Event subscriptions MUST be registered via Dapr (`/dapr/subscribe` endpoint)
- Event handlers MUST be idempotent (safe to process duplicate events)
- Event processing failures MUST be logged and retried
- Kafka topics MUST have retention policy (7 days minimum for debugging)

**Event Schema Pattern**:
```python
# backend/app/events/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class TaskCreatedEvent(BaseModel):
    event_type: Literal["task.created"] = "task.created"
    user_id: int
    task_id: int
    timestamp: datetime
    data: dict  # Task details

# Publishing event via Dapr
import httpx

async def publish_task_created(user_id: int, task: Task):
    event = TaskCreatedEvent(
        user_id=user_id,
        task_id=task.id,
        timestamp=datetime.utcnow(),
        data=task.dict()
    )

    async with httpx.AsyncClient() as client:
        await client.post(
            "http://localhost:3500/v1.0/publish/pubsub-kafka/task-events",
            json=event.dict()
        )
```

**Event Subscription Pattern**:
```python
# backend/app/main.py
@app.get("/dapr/subscribe")
async def subscribe():
    """Dapr subscription endpoint"""
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-events",
            "route": "/events/task-events"
        }
    ]

@app.post("/events/task-events")
async def handle_task_event(event: TaskCreatedEvent):
    """Process task events"""
    # Idempotent processing logic
    if event.event_type == "task.created" and event.data.get("is_recurring"):
        # Schedule next occurrence
        await schedule_recurring_task(event.task_id, event.data["recurring_interval"])
    return {"status": "ok"}
```

### XXIII. Sidecar Pattern with Dapr Abstraction (NEW)

Application code MUST NOT directly access infrastructure (Kafka, Secrets, State Storage). All infrastructure interactions MUST go through Dapr sidecar via HTTP API or Dapr SDK. Dapr handles retries, circuit breakers, and observability.

**Rationale**: Dapr abstracts infrastructure. Switching from Kafka to RabbitMQ requires changing Dapr component YAML only (no application code changes). Switching from Azure to DigitalOcean requires zero code changes. Dapr provides: automatic retries, circuit breakers, distributed tracing, metrics export, secret encryption, and state management - all without application code.

**Rules**:
- Application code MUST call Dapr sidecar API (localhost:3500) for infrastructure
- Application code MUST NOT import kafka-python, redis-py, or cloud-specific SDKs
- Dapr SDK MAY be used for convenience (still calls localhost:3500 internally)
- Pub/Sub MUST use Dapr API: `POST /v1.0/publish/<pubsub>/<topic>`
- State MUST use Dapr API: `POST /v1.0/state/<store>/<key>`
- Secrets MUST use Dapr API: `GET /v1.0/secrets/<store>/<secret>`
- Service-to-service calls MUST use Dapr Service Invocation: `POST /v1.0/invoke/<app-id>/method/<endpoint>`
- Dapr app-id MUST be unique per service (backend, frontend, reminder-worker)

**Dapr Pub/Sub Pattern**:
```python
# WRONG: Direct Kafka client (tightly coupled)
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='kafka:9092')
producer.send('task-events', event_json)

# CORRECT: Dapr Pub/Sub API (infrastructure-independent)
import httpx
async with httpx.AsyncClient() as client:
    await client.post(
        "http://localhost:3500/v1.0/publish/pubsub-kafka/task-events",
        json=event_dict
    )
```

**Dapr Service Invocation Pattern**:
```typescript
// Frontend calling Backend via Dapr (resilience, retries, tracing)
const response = await fetch(
  "http://localhost:3500/v1.0/invoke/backend/method/api/tasks",
  { method: "GET", headers: { "Authorization": `Bearer ${token}` } }
);
```

### XXIV. Infrastructure Independence and Portability (NEW)

Application code MUST be cloud-agnostic. Code MUST NOT know if it's running on DigitalOcean, Azure, or GCP. Dapr provides portability layer. Switching cloud providers MUST require zero application code changes.

**Rationale**: Vendor lock-in is expensive. Dapr components abstract infrastructure. Same application code runs on any Kubernetes cluster. Cloud-specific configurations live in Dapr component YAML, not application code.

**Rules**:
- Application code MUST NOT import cloud-specific SDKs (AWS SDK, Azure SDK, GCP SDK)
- Application code MUST use Dapr abstractions (Pub/Sub, State, Secrets)
- Cloud-specific configuration MUST be in Dapr component YAML only
- Switching cloud providers MUST only require Dapr component YAML changes
- Infrastructure provider MUST be configurable via Helm values (deployment-time choice)

**Portability Example**:
```yaml
# Dapr pubsub component - DigitalOcean with Redpanda
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "redpanda.example.com:9092"

# Same component - Azure with Event Hubs (just change metadata)
# Application code unchanged!
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "my-eventhub.servicebus.windows.net:9093"
```

### XXV. Automated Delivery with CI/CD (NEW)

Deployments MUST be automated through CI/CD pipelines. No manual `kubectl apply` or `helm install` in production. GitHub Actions MUST build images, push to registry, and deploy to cluster on every merge to main.

**Rationale**: Manual deployments are error-prone and not auditable. CI/CD ensures every deployment is tested, versioned, and rollback-capable. Automated pipelines enable continuous delivery (deploy multiple times per day safely).

**Rules**:
- Production deployments MUST go through CI/CD pipeline (no manual kubectl)
- GitHub Actions MUST build Docker images on every commit
- Images MUST be tagged with git commit SHA or semantic version
- Images MUST be pushed to container registry (GitHub Container Registry, Docker Hub, or cloud registry)
- Helm charts MUST be upgraded automatically after image push
- Deployment MUST run automated tests before production promotion
- Rollback MUST be automated (previous Helm release)
- Secrets MUST be injected via GitHub Secrets (not committed)

**GitHub Actions Pipeline Pattern**:
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud
on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Backend
        run: docker build -t ghcr.io/username/todo-backend:${{ github.sha }} ./backend

      - name: Push to Registry
        run: docker push ghcr.io/username/todo-backend:${{ github.sha }}

      - name: Deploy via Helm
        run: |
          helm upgrade todo-app ./k8s/helm/todo-app \
            --set backend.image.tag=${{ github.sha }} \
            --namespace todo-app
```

### XXVI. Advanced Task Management Features (NEW)

Application MUST support production-grade task management: priorities, tags, due dates, recurring tasks, and reminders. These features MUST leverage event-driven architecture (not synchronous processing).

**Rationale**: Users need advanced organization (priorities, tags). Recurring tasks require background scheduling. Reminders require time-based triggers. Event-driven architecture fits these async workflows naturally.

**Rules**:
- Tasks MUST support priority levels (Low, Medium, High) - filterable and sortable
- Tasks MUST support tags (multiple per task) - searchable
- Tasks MUST support due dates (timestamp) - reminder trigger
- Tasks MUST support recurring intervals (daily, weekly, monthly)
- Recurring tasks MUST auto-create next instance via events (not cron in application)
- Reminders MUST be triggered via Dapr Jobs API (scheduled events)
- Tag search MUST be efficient (database index on tags column)
- Priority filtering MUST be performant (index on priority column)

**Recurring Task Event Flow**:
```
1. User creates task with is_recurring=true, interval="daily"
2. Backend publishes task.created event
3. Recurring Task Scheduler (subscribes to task.created) schedules next occurrence
4. Dapr Jobs API triggers event at scheduled time
5. Event creates next task instance
6. Repeat step 2-5
```

**Reminder Event Flow**:
```
1. User sets due_date on task
2. Backend publishes task.updated event
3. Reminder Service (subscribes to task.updated) schedules reminder
4. Dapr Jobs API triggers reminder event at due_date
5. Reminder Service publishes reminder.triggered event
6. Frontend/Email Service handles notification
```

## Phase V Principles (Event-Driven Architecture & Cloud)

### XXII. Event-Driven Architecture
(Documented above)

### XXIII. Sidecar Pattern with Dapr Abstraction
(Documented above)

### XXIV. Infrastructure Independence and Portability
(Documented above)

### XXV. Automated Delivery with CI/CD
(Documented above)

### XXVI. Advanced Task Management Features
(Documented above)

## Scope and Constraints

### In Scope (Phase V)
- All Phase I-IV scope remains (containerized Kubernetes deployment)
- Dapr runtime installation on cloud Kubernetes
- Dapr components (Pub/Sub, State Store, Secret Store, Service Invocation)
- Kafka or Redpanda deployment (event streaming)
- Event schemas and handlers (task-events, reminders, task-updates)
- Recurring task scheduling via events
- Reminder system via Dapr Jobs API
- Advanced task features (priority, tags, due dates)
- Cloud Kubernetes deployment (DigitalOcean DOKS, Azure AKS, or GKE)
- CI/CD pipeline (GitHub Actions)
- Container registry integration (GHCR, Docker Hub, or cloud registry)
- Ingress controller and TLS
- Custom domain DNS configuration
- Horizontal Pod Autoscaler (optional)

### Out of Scope (Future or Optional)
- Service mesh (Istio, Linkerd) - Dapr provides sufficient abstraction
- Monitoring infrastructure (Prometheus, Grafana) - use cloud provider monitoring
- Persistent volumes (StatefulSets) - stateless architecture maintained
- Multi-cluster deployment (single cloud cluster sufficient)
- Event sourcing pattern (CQRS) - optional advanced pattern
- Saga pattern for distributed transactions - simple workflows only

### Technology Constraints (Phase V Additions)
- All Phase I-IV constraints remain
- Dapr Runtime: v1.12+
- Kafka: Strimzi Operator or Redpanda Cloud (free tier)
- Cloud Provider: DigitalOcean (DOKS), Azure (AKS), or Google Cloud (GKE)
- CI/CD: GitHub Actions (repository-integrated)
- Container Registry: GitHub Container Registry (GHCR) or Docker Hub
- NO direct Kafka clients (kafka-python) - use Dapr only
- NO cloud-specific SDKs (boto3, azure-sdk) - use Dapr abstractions

## Project Structure (Phase V Additions)

Phase V adds Dapr components, CI/CD workflows, and event handlers to Phase IV structure:

```
hackathon-full-stack-template/
├── backend/
│   ├── app/
│   │   ├── events/               # NEW: Event handlers and schemas
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py        # Pydantic event models
│   │   │   ├── publishers.py    # Event publishing utilities
│   │   │   └── handlers.py       # Event subscription handlers
│   │   └── ...
│   ├── Dockerfile
│   └── ...
├── frontend/
│   ├── Dockerfile
│   └── ...
├── k8s/
│   ├── helm/
│   │   └── todo-app/
│   │       ├── Chart.yaml
│   │       ├── values.yaml
│   │       └── templates/
│   │           ├── deployment.yaml        # Updated with Dapr annotations
│   │           └── service.yaml
│   ├── dapr-components/           # NEW: Dapr configuration
│   │   ├── pubsub-kafka.yaml     # Kafka Pub/Sub component
│   │   ├── statestore.yaml        # PostgreSQL state store
│   │   └── secretstore.yaml       # Kubernetes secret store
│   └── kafka/                     # NEW: Kafka deployment
│       └── strimzi/               # Strimzi Operator manifests (if self-hosted)
├── .github/                       # NEW: CI/CD automation
│   └── workflows/
│       ├── deploy-backend.yml
│       ├── deploy-frontend.yml
│       └── test.yml
└── ...
```

## Development Workflow (Phase V Additions)

### Event-Driven Development Phase
1. Define event schema in spec.md
2. Create Pydantic model in events/schemas.py
3. Implement event publisher (after CRUD operations)
4. Implement event handler (subscriber)
5. Test locally with Dapr CLI: `dapr run --app-id backend --app-port 8000 -- python -m app.main`
6. Verify event flow with `dapr logs`

### Dapr Setup Phase
1. Install Dapr CLI: `curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash`
2. Initialize Dapr on Kubernetes: `dapr init -k`
3. Create Dapr components (pubsub, statestore, secretstore)
4. Apply components: `kubectl apply -f k8s/dapr-components/`
5. Verify: `dapr components -k`

### Kafka Deployment Phase
1. Choose Kafka provider:
   - Self-hosted: Deploy Strimzi Operator
   - Managed: Redpanda Cloud (free tier), Confluent Cloud, or cloud provider service
2. Create topics: `task-events`, `reminders`, `task-updates`
3. Configure Dapr Pub/Sub component with Kafka brokers
4. Test connection: publish test event via Dapr

### Cloud Deployment Phase
1. Create cloud Kubernetes cluster (DigitalOcean, Azure, or GCP)
2. Configure kubectl context: `kubectl config use-context <cloud-cluster>`
3. Install Dapr on cloud cluster: `dapr init -k`
4. Deploy Kafka (Strimzi or connect to managed service)
5. Create Kubernetes secrets (database, API keys)
6. Deploy Dapr components
7. Deploy application via Helm
8. Configure Ingress and DNS
9. Verify pods and services

### CI/CD Setup Phase
1. Create GitHub Actions workflows
2. Configure GitHub Secrets (registry credentials, kubeconfig)
3. Test workflow on feature branch
4. Merge to main triggers production deployment
5. Monitor deployment in GitHub Actions UI
6. Verify application accessible on public domain

## Success Criteria (Phase V)

Phase V is complete when ALL Phase I-IV criteria remain met AND:

### Event-Driven Architecture
- ✅ Dapr runtime installed on cloud Kubernetes cluster
- ✅ Dapr sidecars running alongside frontend and backend pods
- ✅ Kafka or Redpanda deployed and accessible
- ✅ Dapr Pub/Sub component configured (pubsub-kafka)
- ✅ Dapr State Store component configured (PostgreSQL)
- ✅ Dapr Secret Store component configured (Kubernetes secrets)
- ✅ Event schemas defined (task.created, task.updated, etc.)
- ✅ Event publishers implemented (task CRUD publishes events)
- ✅ Event subscribers implemented (handlers process events)
- ✅ End-to-end event flow tested (publish → Kafka → subscribe → process)

### Advanced Task Features
- ✅ Priority field added to tasks (Low, Medium, High)
- ✅ Tags field added to tasks (JSON array)
- ✅ Due date field added to tasks (timestamp)
- ✅ Recurring task fields added (is_recurring, recurring_interval)
- ✅ Recurring tasks auto-create next instance via events
- ✅ Reminders triggered via Dapr Jobs API
- ✅ Priority filtering works in UI
- ✅ Tag search works in UI
- ✅ Database indexes created (priority, tags, due_date)

### Cloud Deployment
- ✅ Application deployed on cloud Kubernetes (DigitalOcean, Azure, or GCP)
- ✅ Dapr components deployed and working
- ✅ Kafka/Redpanda deployed and accessible
- ✅ Ingress controller configured
- ✅ TLS certificates provisioned (HTTPS working)
- ✅ Custom domain DNS configured (or cloud provider subdomain)
- ✅ All pods in Running state on cloud cluster
- ✅ LoadBalancer has public IP
- ✅ Application accessible from internet

### CI/CD Automation
- ✅ GitHub Actions workflows created
- ✅ Workflow builds Docker images on commit
- ✅ Images tagged with git SHA or version
- ✅ Images pushed to container registry
- ✅ Helm chart upgraded automatically
- ✅ Deployment succeeds without manual intervention
- ✅ Pipeline runs on every merge to main
- ✅ Failed deployments alert (GitHub notifications)

### Observability
- ✅ Dapr metrics exported (Prometheus endpoint)
- ✅ Distributed tracing working (Zipkin or Jaeger)
- ✅ Logs aggregated (cloud provider logging or ELK stack)
- ✅ Event processing visible in traces
- ✅ Failed events logged to dead letter queue

### Application Functionality
- ✅ All Phase I-IV features work on cloud
- ✅ User signup/signin works on public domain
- ✅ Task CRUD operations work and publish events
- ✅ AI chatbot works with cloud deployment
- ✅ Recurring tasks create next instance automatically
- ✅ Reminders trigger at due date
- ✅ Priority and tag filtering works
- ✅ OAuth authentication works with cloud URLs

### Documentation
- ✅ Dapr architecture diagram created
- ✅ Event flow diagrams documented
- ✅ Deployment guide updated for cloud providers
- ✅ CI/CD pipeline documented
- ✅ Troubleshooting guide includes event debugging
- ✅ README updated with Phase V architecture

## Governance

### Amendment Process
Constitution changes MUST be documented with:
- Clear rationale for the change
- Version increment following semantic versioning
- Update to dependent templates (spec, plan, tasks)
- Sync Impact Report (HTML comment at top of file)
- Approval before taking effect

### Version Semantics
- MAJOR: Principle removal, fundamental architectural change (Phase IV → Phase V: synchronous → event-driven)
- MINOR: New principle added, significant expansion
- PATCH: Clarifications, examples, formatting

### Compliance
- All spec.md files MUST reference relevant constitution principles
- All plan.md files MUST include "Constitution Check" section
- All code reviews MUST verify constitutional compliance
- Infrastructure changes MUST comply with deployment principles (XII, XVII-XXVI)
- Event schemas MUST be reviewed for compliance with Principle XXII

### Compliance Review Checklist (Phase V Additions)
Before marking Phase V complete, verify:
- [ ] All Phase IV compliance items (containers, Kubernetes, health checks)
- [ ] Dapr installed on cloud cluster (Principle XXIII)
- [ ] Dapr sidecars running (Principle XXIII)
- [ ] Dapr components deployed (Principle XXII)
- [ ] Kafka/Redpanda deployed (Principle XXII)
- [ ] Event schemas documented (Principle II)
- [ ] Event publishers implemented (Principle XXII)
- [ ] Event subscribers implemented (Principle XXII)
- [ ] Application uses Dapr APIs only (Principle XXIII)
- [ ] No cloud-specific SDKs in code (Principle XXIV)
- [ ] CI/CD pipeline working (Principle XXV)
- [ ] Automated deployments tested (Principle XXV)
- [ ] Advanced task features working (Principle XXVI)
- [ ] Application accessible on public domain
- [ ] TLS certificates valid
- [ ] No secrets in Git or container images

**Version**: 5.0.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-25
