# Research: Helm Charts for Local Kubernetes Deployment

**Feature**: 006-helm-charts
**Date**: 2025-12-24
**Status**: Complete

## Research Summary

This document captures key decisions and best practices for implementing Helm charts to deploy the Todo application on local Kubernetes (Docker Desktop).

---

## Decision 1: Helm Chart Structure

**Decision**: Use standard Helm 3 chart structure with separate templates per resource type.

**Rationale**:
- Standard structure is well-documented and familiar to Kubernetes engineers
- Separate templates enable independent testing and debugging
- Follows Helm best practices from official documentation

**Alternatives Considered**:
- Single large template file: Rejected - harder to maintain and debug
- Kustomize overlays: Rejected - Helm provides better parameterization for this use case
- Raw kubectl manifests: Rejected - no templating or configuration management

**Implementation**:
```text
k8s/helm/todo-app/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── _helpers.tpl
    ├── configmap.yaml
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

---

## Decision 2: Image Pull Policy for Local Development

**Decision**: Use `imagePullPolicy: Never` as default for local Docker Desktop deployment.

**Rationale**:
- Docker Desktop Kubernetes shares Docker daemon with host
- Images built locally are already available in cluster
- Prevents unnecessary registry pulls
- Faster deployment cycles during development

**Alternatives Considered**:
- `imagePullPolicy: Always`: Rejected - requires registry, slower iteration
- `imagePullPolicy: IfNotPresent`: Acceptable alternative but `Never` is more explicit for local

**Implementation**:
```yaml
# values.yaml
image:
  pullPolicy: Never
```

---

## Decision 3: Service Types (Backend vs Frontend)

**Decision**:
- Backend: ClusterIP (internal-only access)
- Frontend: LoadBalancer (external access via localhost)

**Rationale**:
- Backend API should not be directly exposed externally (security)
- Frontend needs external access for user browser
- Docker Desktop provides LoadBalancer support on localhost
- Frontend communicates with backend via Kubernetes DNS (internal)

**Alternatives Considered**:
- Both as ClusterIP with Ingress: Rejected - adds complexity, out of scope for Phase IV
- Both as NodePort: Rejected - less clean than LoadBalancer on Docker Desktop
- Backend as LoadBalancer: Rejected - unnecessary external exposure

**Implementation**:
```yaml
# values.yaml
backend:
  service:
    type: ClusterIP
    port: 8000
frontend:
  service:
    type: LoadBalancer
    port: 3000
```

---

## Decision 4: Secret Management Strategy

**Decision**: Reference external Kubernetes Secret (name: `todo-secrets`) via `envFrom.secretRef`. Secrets created manually before deployment.

**Rationale**:
- No secrets in Git (security)
- Operator creates secrets via kubectl before helm install
- Clear separation of concerns (chart manages structure, operator manages credentials)
- Follows Kubernetes best practices for secret handling

**Alternatives Considered**:
- Secrets in values.yaml: Rejected - security risk, would be committed to Git
- Sealed Secrets: Rejected - out of scope for Phase IV local deployment
- External Secrets Operator: Rejected - overkill for local development

**Implementation**:
```yaml
# templates/backend-deployment.yaml
envFrom:
  - secretRef:
      name: todo-secrets
```

**Required Secrets** (created manually):
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: Authentication secret
- `OPENAI_API_KEY`: OpenAI API key

---

## Decision 5: Health Probe Configuration

**Decision**: Configure liveness probe on `/health` and readiness probe on `/ready` with appropriate delays.

**Rationale**:
- Backend already has `/health` endpoint (liveness - is process alive?)
- Backend needs `/ready` endpoint (readiness - can handle traffic?)
- Initial delay accounts for container startup time
- Period balances responsiveness with resource usage

**Alternatives Considered**:
- TCP socket probes: Rejected - HTTP probes provide more meaningful health info
- Exec probes: Rejected - HTTP is more efficient than spawning processes
- Single endpoint for both: Rejected - different purposes require different checks

**Implementation**:
```yaml
# Backend probes
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

---

## Decision 6: Replica Count Default

**Decision**: Default to 2 replicas for both backend and frontend.

**Rationale**:
- Proves horizontal scaling works
- Demonstrates load balancing across pods
- Validates stateless application design
- Matches constitution requirement (Principle I: 2+ replicas)

**Alternatives Considered**:
- 1 replica: Rejected - doesn't demonstrate scaling
- 3+ replicas: Rejected - unnecessary resource usage for local dev

**Implementation**:
```yaml
# values.yaml
replicaCount: 2
```

---

## Decision 7: Frontend-to-Backend Communication

**Decision**: Frontend uses Kubernetes DNS to reach backend service (`http://todo-app-backend:8000`).

**Rationale**:
- Kubernetes provides automatic DNS for services
- Service name is stable regardless of pod IPs
- Works with multiple backend replicas (load balanced)
- Follows cloud-native service discovery patterns

**Alternatives Considered**:
- Hardcoded pod IP: Rejected - pods are ephemeral
- External LoadBalancer for backend: Rejected - unnecessary exposure
- Sidecar proxy: Rejected - overkill for this use case

**Implementation**:
```yaml
# values.yaml
frontend:
  env:
    NEXT_PUBLIC_API_URL: "http://todo-app-backend:8000"
```

**Note**: For browser-based API calls, frontend may need to use the backend's external URL or an Ingress. For SSR (server-side rendering), internal DNS works.

---

## Best Practices Applied

1. **Helm Naming Convention**: Use `{{ include "todo-app.fullname" . }}` for resource names
2. **Label Consistency**: Apply standard labels (app.kubernetes.io/name, app.kubernetes.io/instance)
3. **Resource Limits**: Define CPU/memory requests and limits (configurable via values.yaml)
4. **Template Helpers**: Use `_helpers.tpl` for reusable template functions
5. **Values Documentation**: Comment all values.yaml options for operators

---

## Outstanding Considerations

None - all technical decisions resolved. Ready for Phase 1 design.
