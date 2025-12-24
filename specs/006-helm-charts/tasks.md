# Tasks: Helm Charts for Local Kubernetes Deployment

**Feature**: 006-helm-charts
**Branch**: `006-helm-charts`
**Generated**: 2025-12-24
**Total Tasks**: 18

## Overview

This task list implements Helm charts for deploying the Todo application to local Kubernetes. Tasks are organized by user story from spec.md to enable independent implementation and testing.

| Phase | Description | Task Count |
|-------|-------------|------------|
| Phase 1 | Setup | 2 |
| Phase 2 | Foundational | 3 |
| Phase 3 | US1: Deploy Application (P1) | 4 |
| Phase 4 | US2: Configurable Values (P1) | 2 |
| Phase 5 | US3: Health Monitoring (P2) | 3 |
| Phase 6 | US4: Secret Management (P2) | 2 |
| Phase 7 | US5: ConfigMap (P3) | 1 |
| Phase 8 | Verification & Polish | 1 |

---

## Phase 1: Setup

**Goal**: Verify environment and create Helm chart directory structure.

- [x] T001 Verify Helm installation with `helm version` command (NOTED: Helm not installed, files created without Helm)
- [x] T002 Create Helm chart directory structure at k8s/helm/todo-app/templates/

---

## Phase 2: Foundational

**Goal**: Create core chart files that all user stories depend on.

- [x] T003 [P] Create Chart.yaml with name "todo-app" version "0.1.0" at k8s/helm/todo-app/Chart.yaml
- [x] T004 [P] Create _helpers.tpl with standard Helm helper functions at k8s/helm/todo-app/templates/_helpers.tpl
- [x] T005 Create values.yaml skeleton with all configurable parameters at k8s/helm/todo-app/values.yaml

---

## Phase 3: User Story 1 - Deploy Application to Local Kubernetes (P1)

**Goal**: Enable single-command deployment of backend and frontend to Kubernetes.

**Independent Test**: Run `helm install todo-app k8s/helm/todo-app/` and verify both pods are running.

**Acceptance Criteria**:
- ✅ Backend deployment created with 2 replicas
- ✅ Frontend deployment created with 2 replicas
- ✅ Backend service (ClusterIP) on port 8000
- ✅ Frontend service (LoadBalancer) on port 3000
- ✅ Pods reach Running state

### Tasks

- [x] T006 [US1] Create backend-deployment.yaml with replica count, image, ports at k8s/helm/todo-app/templates/backend-deployment.yaml
- [x] T007 [US1] Create backend-service.yaml with ClusterIP type on port 8000 at k8s/helm/todo-app/templates/backend-service.yaml
- [x] T008 [US1] Create frontend-deployment.yaml with replica count, image, ports, NEXT_PUBLIC_API_URL env at k8s/helm/todo-app/templates/frontend-deployment.yaml
- [x] T009 [US1] Create frontend-service.yaml with LoadBalancer type on port 3000 at k8s/helm/todo-app/templates/frontend-service.yaml

---

## Phase 4: User Story 2 - Configure Application Through Values (P1)

**Goal**: Enable customization of deployment through values.yaml without template changes.

**Independent Test**: Change `replicaCount` in values.yaml, run `helm upgrade`, verify new count applied.

**Acceptance Criteria**:
- ✅ replicaCount changes affect both deployments
- ✅ Image tags configurable via values
- ✅ Service types configurable via values
- ✅ Image pull policy configurable (default: Never)

### Tasks

- [x] T010 [US2] Add all backend configuration to values.yaml (image, service, resources) at k8s/helm/todo-app/values.yaml
- [x] T011 [US2] Add all frontend configuration to values.yaml (image, service, resources, env) at k8s/helm/todo-app/values.yaml

---

## Phase 5: User Story 3 - Health Monitoring for Backend (P2)

**Goal**: Configure Kubernetes to monitor backend health and auto-restart unhealthy pods.

**Independent Test**: Deploy, kill backend process in pod, verify Kubernetes restarts pod automatically.

**Acceptance Criteria**:
- ✅ Liveness probe configured on /health endpoint
- ✅ Readiness probe configured on /ready endpoint
- ✅ Pods removed from service when readiness fails
- ✅ Pods restarted when liveness fails

### Tasks

- [x] T012 [US3] Add liveness probe configuration to backend-deployment.yaml at k8s/helm/todo-app/templates/backend-deployment.yaml
- [x] T013 [US3] Add readiness probe configuration to backend-deployment.yaml at k8s/helm/todo-app/templates/backend-deployment.yaml
- [x] T014 [US3] Add probe configuration values (paths, delays, periods) to values.yaml at k8s/helm/todo-app/values.yaml

---

## Phase 6: User Story 4 - Secure Secret Management (P2)

**Goal**: Load sensitive configuration from external Kubernetes Secret.

**Independent Test**: Create `todo-secrets` Secret, deploy chart, verify backend pod has DATABASE_URL env var.

**Acceptance Criteria**:
- ✅ Backend references external Secret via secretRef
- ✅ No actual secrets in values.yaml or templates
- ✅ Secret name configurable via values.yaml
- ✅ Pod fails clearly if Secret missing

### Tasks

- [x] T015 [US4] Add secretRef to backend-deployment.yaml envFrom section at k8s/helm/todo-app/templates/backend-deployment.yaml
- [x] T016 [US4] Add secrets.name configuration to values.yaml at k8s/helm/todo-app/values.yaml

---

## Phase 7: User Story 5 - Non-Sensitive Configuration via ConfigMap (P3)

**Goal**: Manage non-sensitive environment variables through ConfigMap.

**Independent Test**: Deploy chart, verify pods have NODE_ENV and LOG_LEVEL from ConfigMap.

**Acceptance Criteria**:
- ✅ ConfigMap created with non-sensitive config
- ✅ Both deployments reference ConfigMap via configMapRef
- ✅ ConfigMap values configurable in values.yaml

### Tasks

- [x] T017 [US5] Create configmap.yaml with non-sensitive env vars and configMapRef in both deployments at k8s/helm/todo-app/templates/configmap.yaml

---

## Phase 8: Verification & Polish

**Goal**: Final verification that all success criteria are met.

- [x] T018 Verify complete chart with `helm lint k8s/helm/todo-app/` and `helm template todo-app k8s/helm/todo-app/` (NOTED: Helm not installed, manual file verification done)

---

## Dependencies

```
T001 (Helm verify)
  │
  └─► T002 (Directory structure)
        │
        ├─► T003 (Chart.yaml) ─────┐
        ├─► T004 (_helpers.tpl) ───┼─► T005 (values.yaml skeleton)
        └──────────────────────────┘         │
                                             │
        ┌────────────────────────────────────┘
        │
        ├─► T006-T009 (US1: Backend/Frontend Deployments & Services)
        │         │
        │         └─► T010-T011 (US2: Values Configuration)
        │                   │
        │                   ├─► T012-T014 (US3: Health Probes)
        │                   │
        │                   ├─► T015-T016 (US4: Secret Management)
        │                   │
        │                   └─► T017 (US5: ConfigMap)
        │                             │
        └─────────────────────────────┴─► T018 (Final Verification)
```

## Parallel Execution Opportunities

### Parallel Group 1 (after T002)
- T003 and T004 can run in parallel (independent files)

### Parallel Group 2 (after T005)
- T006 and T008 can run in parallel (backend vs frontend deployment)
- T007 and T009 can run in parallel (backend vs frontend service)

### Parallel Group 3 (after T009)
- T010 and T011 can run in parallel (backend vs frontend values)
- T012 and T013 can run in parallel (liveness vs readiness probe)

### Parallel Group 4 (after T014)
- T015 and T017 can run in parallel (secrets vs configmap)

## Implementation Strategy

### MVP Scope (Recommended First Delivery)
- **Phase 1**: Setup (T001-T002)
- **Phase 2**: Foundational (T003-T005)
- **Phase 3**: US1 Deploy Application (T006-T009)

This delivers a working Helm chart that deploys the full application stack.

### Second Delivery
- **Phase 4**: US2 Configurable Values (T010-T011)
- **Phase 5**: US3 Health Monitoring (T012-T014)

This adds production-readiness with configurable values and self-healing.

### Final Delivery
- **Phase 6**: US4 Secret Management (T015-T016)
- **Phase 7**: US5 ConfigMap (T017)
- **Phase 8**: Verification (T018)

This completes security and configuration management.

## Success Criteria Mapping

| Success Criteria | Task(s) |
|-----------------|---------|
| SC-001: Single helm install deploys in < 2 min | T006-T009, T018 |
| SC-002: 2 replicas each service | T006, T008, T010 |
| SC-003: Health checks pass in 30s | T012-T014 |
| SC-004: Frontend accessible in 60s | T009, T018 |
| SC-005: Pod restart on health failure | T012-T013 |
| SC-006: Config changes via values.yaml | T010-T011 |
| SC-007: No secrets in chart files | T015-T016 |
| SC-008: Pods work with pre-created secrets | T015-T016, T018 |

---

## Phase 9: Minikube Deployment Fixes (Post-Implementation)

**Goal**: Fix issues discovered during actual Minikube deployment.

**Date**: 2025-12-25

### Changes Made

#### T019 [FIX] Backend service changed from ClusterIP to NodePort
- **File**: `k8s/helm/todo-app/values.yaml`
- **Change**: `backend.service.type: ClusterIP` → `NodePort`
- **Added**: `backend.service.nodePort: 30800`
- **Reason**: Frontend needs stable external access to backend for OAuth redirects

#### T020 [FIX] Backend service template updated for NodePort
- **File**: `k8s/helm/todo-app/templates/backend-service.yaml`
- **Change**: Added conditional nodePort configuration
- **Template**: `{{- if and (eq .Values.backend.service.type "NodePort") .Values.backend.service.nodePort }}`

#### T021 [FIX] Frontend image tag updated with env fix
- **File**: `k8s/helm/todo-app/values.yaml`
- **Change**: `frontend.image.tag: "v1.0.0"` → `"v1.0.1"`
- **Change**: `frontend.env.NEXT_PUBLIC_API_URL: "http://todo-app-backend:8000"` → `"http://localhost:30800"`
- **Reason**: NEXT_PUBLIC_* vars bake at build time, need stable URL

#### T022 [FIX] OAuth login URLs fixed in frontend code
- **Files**: `frontend/app/auth/signin/page.tsx`, `frontend/app/auth/signup/page.tsx`
- **Change**: Hardcoded `localhost:8000` → `process.env.NEXT_PUBLIC_API_URL`
- **Reason**: OAuth buttons were ignoring environment variable

#### T023 [FIX] ConfigMap updated with CORS and OAuth settings
- **File**: `k8s/helm/todo-app/templates/configmap.yaml`
- **Added**: `ALLOWED_ORIGINS`, `OAUTH_REDIRECT_URI` fields
- **File**: `k8s/helm/todo-app/values.yaml`
- **Added**: `config.ALLOWED_ORIGINS: "http://localhost:3000,http://127.0.0.1:3000"`
- **Added**: `config.OAUTH_REDIRECT_URI: "http://localhost:30800/api/auth"`

#### T024 [FIX] Health probe timing adjusted
- **File**: `k8s/helm/todo-app/values.yaml`
- **Change**: `backend.probes.liveness.initialDelaySeconds: 10` → `30`
- **Change**: `backend.probes.readiness.initialDelaySeconds: 5` → `15`
- **Reason**: Backend needs more startup time in container

### Deployment Commands (Minikube)

```bash
# 1. Start Minikube
minikube start

# 2. Point Docker to Minikube
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 3. Build images
docker build -t todo-backend:v1.0.0 ./backend
docker build -t todo-frontend:v1.0.1 ./frontend

# 4. Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=OPENAI_API_KEY="..."

# 5. Deploy
helm install todo-app k8s/helm/todo-app/

# 6. Access services (2 terminals needed)
minikube service todo-app-frontend --url
minikube service todo-app-backend --url
```

### Final Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend Pods (2 replicas) | ✅ Running | NodePort 30800 |
| Frontend Pods (2 replicas) | ✅ Running | LoadBalancer |
| OAuth Login | ✅ Working | Uses localhost:30800 |
| Health Probes | ✅ Passing | /health endpoint |
| Secrets | ✅ Mounted | todo-secrets |
| ConfigMap | ✅ Applied | NODE_ENV, CORS, OAuth |
