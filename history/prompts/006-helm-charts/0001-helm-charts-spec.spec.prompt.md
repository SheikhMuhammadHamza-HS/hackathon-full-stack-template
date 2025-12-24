---
id: "0001"
title: "Helm Charts Specification"
stage: spec
date: 2025-12-24
surface: agent
model: claude-sonnet-4-5-20250929
feature: 006-helm-charts
branch: 006-helm-charts
user: SheikhMuhammadHamza
command: /sp.specify
labels: ["helm", "kubernetes", "phase-iv", "spec", "deployment"]
links:
  spec: specs/006-helm-charts/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-helm-charts/spec.md
  - specs/006-helm-charts/checklists/requirements.md
tests:
  - Checklist validation PASS (16/16 items)
---

## Prompt

/sp.specify you have docker agent (or System: Act as the Deployment & Orchestration Architect) Dockerfiles are complete. Now, generate the **Helm Chart** structure for Phase IV (Local Kubernetes on Minikube).

## Your Goal
Scaffold a production-ready Helm Chart at `k8s/helm/todo-app/` that orchestrates both Frontend and Backend containers.

## Requirements

### 1. Chart Structure
Create the following file structure:
```text
k8s/helm/todo-app/
├── Chart.yaml          # Metadata (Name: todo-app, Version: 0.1.0)
├── values.yaml         # Default configuration (Define images, replicas, ports)
└── templates/
    ├── _helpers.tpl    # Standard helpers (optional but good)
    ├── configmap.yaml  # Non-sensitive env vars
    ├── secrets.yaml    # (Optional) Or reference to external secret
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

### 2. values.yaml Configuration
- ReplicaCount: 2
- Images: todo-backend:latest, todo-frontend:latest
- PullPolicy: Never (for local images)
- Backend: ClusterIP on Port 8000
- Frontend: LoadBalancer/NodePort on Port 3000

### 3. Template Logic
- Backend with liveness/readiness probes (/health, /ready)
- Environment variables from ConfigMap and Secrets
- Frontend with NEXT_PUBLIC_API_URL configuration

### 4. Constraints
- No hardcoded secrets
- Proper label matching for Service selectors

## Response snapshot

Created comprehensive Helm Charts specification with:

**5 User Stories (P1-P3)**:
1. Deploy Application to Local Kubernetes (P1)
2. Configure Application Through Values (P1)
3. Health Monitoring for Backend (P2)
4. Secure Secret Management (P2)
5. Non-Sensitive Configuration via ConfigMap (P3)

**20 Functional Requirements** covering:
- Chart structure (FR-001 to FR-004)
- Backend deployment (FR-005 to FR-010)
- Frontend deployment (FR-011 to FR-014)
- Configuration management (FR-015 to FR-018)
- Service discovery (FR-019 to FR-020)

**8 Success Criteria** with measurable outcomes:
- Single command deployment under 2 minutes
- 2 replicas maintained for each service
- Health checks pass within 30 seconds
- No secrets in version control

## Outcome

- ✅ Impact: Complete specification for Helm charts ready for planning phase
- 🧪 Tests: Checklist validation PASS (16/16 items)
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: /sp.clarify or /sp.plan
- 🧠 Reflection: Spec follows technology-agnostic principles while capturing all Helm chart requirements

## Evaluation notes (flywheel)

- Failure modes observed: None - all checklist items passed
- Graders run and results (PASS/FAIL): Checklist PASS (16/16)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase
