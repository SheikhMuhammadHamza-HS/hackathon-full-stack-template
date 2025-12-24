# Implementation Plan: Helm Charts for Local Kubernetes Deployment

**Branch**: `006-helm-charts` | **Date**: 2025-12-24 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-helm-charts/spec.md`

## Summary

Create a production-ready Helm chart at `k8s/helm/todo-app/` to orchestrate the Todo application on local Kubernetes (Docker Desktop). The chart will manage both backend (FastAPI) and frontend (Next.js) deployments with ConfigMaps for non-sensitive config, external Secrets reference for credentials, health probes, and configurable replicas (default: 2 each).

## Technical Context

**Language/Version**: YAML (Helm templates with Go templating)
**Primary Dependencies**: Helm 3+, kubectl, Docker Desktop Kubernetes
**Storage**: N/A (chart manages deployment, not data persistence)
**Testing**: helm lint, helm template, kubectl apply --dry-run, manual pod verification
**Target Platform**: Kubernetes (Docker Desktop for Windows/Mac)
**Project Type**: Infrastructure-as-Code (Helm chart)
**Performance Goals**: Deployment completes in under 2 minutes, pods ready in 30 seconds
**Constraints**: Image pull policy "Never" for local images, no hardcoded secrets
**Scale/Scope**: 2 replicas each service, single namespace deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| XVII. Container-First Architecture | ✅ PASS | Helm chart deploys containerized applications |
| XVIII. Declarative Infrastructure | ✅ PASS | All resources defined in YAML templates |
| XIX. Immutable Infrastructure | ✅ PASS | Config injected via ConfigMap/Secret, not baked in |
| XX. Cloud-Native Patterns | ✅ PASS | 12-factor: config in env vars, stateless processes |
| XXI. Health Checks and Observability | ✅ PASS | Liveness/readiness probes in deployment templates |
| II. Spec-Driven Development | ✅ PASS | Spec completed and clarified before planning |
| VIII. User Isolation and Data Security | ✅ PASS | Secrets reference external Secret, not hardcoded |

**Gate Result**: PASS - No violations. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/006-helm-charts/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (Helm chart structure)
├── quickstart.md        # Phase 1 output (deployment commands)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
k8s/
└── helm/
    └── todo-app/
        ├── Chart.yaml              # Chart metadata
        ├── values.yaml             # Configurable defaults
        └── templates/
            ├── _helpers.tpl        # Template helpers
            ├── configmap.yaml      # Non-sensitive env vars
            ├── backend-deployment.yaml
            ├── backend-service.yaml
            ├── frontend-deployment.yaml
            └── frontend-service.yaml
```

**Structure Decision**: Option 1 (Single Infrastructure Project) - Helm chart is self-contained at `k8s/helm/todo-app/`. No application code changes needed.

## Complexity Tracking

No violations requiring justification. Helm chart follows standard structure with minimal complexity.
