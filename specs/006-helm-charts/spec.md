# Feature Specification: Helm Charts for Local Kubernetes Deployment

**Feature Branch**: `006-helm-charts`
**Created**: 2025-12-24
**Status**: Draft
**Input**: User description: "Scaffold a production-ready Helm Chart at k8s/helm/todo-app/ that orchestrates both Frontend and Backend containers for Phase IV Local Kubernetes deployment."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Application to Local Kubernetes (Priority: P1)

As a developer, I want to deploy the complete Todo application (backend and frontend) to my local Kubernetes cluster using a single command, so that I can test the application in a production-like environment.

**Why this priority**: Core deployment capability - without this, no other features can be tested in Kubernetes. This proves the containers work together in an orchestrated environment.

**Independent Test**: Run `helm install todo-app k8s/helm/todo-app/` and verify both frontend and backend pods are running and accessible.

**Acceptance Scenarios**:

1. **Given** the Helm chart is configured with default values, **When** I run the install command, **Then** both backend and frontend deployments are created with 2 replicas each.
2. **Given** the application is deployed, **When** I check the services, **Then** backend is accessible via internal cluster IP and frontend is accessible via LoadBalancer/NodePort.
3. **Given** the pods are running, **When** I access the frontend service URL, **Then** the Todo application loads and can communicate with the backend.

---

### User Story 2 - Configure Application Through Values (Priority: P1)

As a developer, I want to customize deployment settings (replicas, image tags, service types) through a centralized configuration file, so that I can adapt the deployment to different environments without modifying templates.

**Why this priority**: Essential for environment flexibility - allows same charts to work across dev, staging, and production with different configurations.

**Independent Test**: Modify values.yaml to change replica count, reinstall, and verify the new replica count is applied.

**Acceptance Scenarios**:

1. **Given** values.yaml has replicaCount set to 3, **When** I deploy the chart, **Then** both deployments have 3 replicas.
2. **Given** values.yaml has custom image tags, **When** I deploy the chart, **Then** pods use the specified image versions.
3. **Given** values.yaml has frontend service type set to NodePort, **When** I deploy, **Then** frontend service is created as NodePort type.

---

### User Story 3 - Health Monitoring for Backend (Priority: P2)

As an operator, I want Kubernetes to automatically monitor backend container health and restart unhealthy instances, so that the application maintains high availability.

**Why this priority**: Critical for production reliability - ensures self-healing behavior without manual intervention.

**Independent Test**: Deploy application, kill the backend process in a pod, verify Kubernetes detects failure and restarts the pod.

**Acceptance Scenarios**:

1. **Given** backend pods are running, **When** the health check endpoint returns success, **Then** the pod remains in Ready state.
2. **Given** a backend pod becomes unhealthy, **When** the liveness probe fails, **Then** Kubernetes restarts the container.
3. **Given** a backend pod is starting, **When** readiness probe fails, **Then** the pod does not receive traffic until ready.

---

### User Story 4 - Secure Secret Management (Priority: P2)

As a security-conscious developer, I want sensitive configuration (database credentials, API keys) to be loaded from Kubernetes Secrets rather than hardcoded in configuration files, so that secrets are not exposed in version control.

**Why this priority**: Security requirement - prevents credential leakage and follows security best practices.

**Independent Test**: Create Kubernetes secret manually, deploy chart, verify pods can access secret values as environment variables.

**Acceptance Scenarios**:

1. **Given** a Kubernetes secret named "todo-secrets" exists, **When** backend pods start, **Then** they have access to secret values as environment variables.
2. **Given** values.yaml is committed to version control, **When** reviewed, **Then** no actual secret values are present.
3. **Given** secrets are not created, **When** pods try to start, **Then** they fail with clear error message about missing secrets.

---

### User Story 5 - Non-Sensitive Configuration via ConfigMap (Priority: P3)

As a developer, I want non-sensitive environment variables to be managed through ConfigMaps, so that I can update configuration without rebuilding images.

**Why this priority**: Operational convenience - enables runtime configuration changes for non-sensitive values.

**Independent Test**: Update ConfigMap value, restart pods, verify new configuration is applied.

**Acceptance Scenarios**:

1. **Given** ConfigMap contains environment variables, **When** pods start, **Then** they receive ConfigMap values as environment variables.
2. **Given** ConfigMap is updated, **When** pods are restarted, **Then** they receive the updated values.

---

### Edge Cases

- What happens when the Kubernetes cluster runs out of resources to schedule pods?
- How does the system handle when required secrets are not created before deployment?
- What happens when backend service is unavailable but frontend pods are running?
- How does the system behave when local Docker images are not available in the cluster?

## Requirements *(mandatory)*

### Functional Requirements

**Chart Structure**
- **FR-001**: System MUST provide a Helm chart at location `k8s/helm/todo-app/` with standard directory structure
- **FR-002**: Chart MUST include Chart.yaml with name "todo-app" and version "0.1.0"
- **FR-003**: Chart MUST include values.yaml with all configurable parameters
- **FR-004**: Chart MUST include templates directory with deployment and service manifests

**Backend Deployment**
- **FR-005**: System MUST create a backend Deployment with configurable replica count (default: 2)
- **FR-006**: Backend pods MUST use configurable container image (default: todo-backend:latest)
- **FR-007**: Backend pods MUST have liveness probe checking health endpoint on port 8000
- **FR-008**: Backend pods MUST have readiness probe checking ready endpoint on port 8000
- **FR-009**: Backend pods MUST receive environment variables from both ConfigMap and Secrets
- **FR-010**: System MUST create a ClusterIP Service for backend on port 8000

**Frontend Deployment**
- **FR-011**: System MUST create a frontend Deployment with configurable replica count (default: 2)
- **FR-012**: Frontend pods MUST use configurable container image (default: todo-frontend:latest)
- **FR-013**: Frontend pods MUST receive API URL configuration to connect to backend service
- **FR-014**: System MUST create a Service for frontend on port 3000 with configurable type (default: LoadBalancer)

**Configuration Management**
- **FR-015**: System MUST provide ConfigMap for non-sensitive environment variables
- **FR-016**: System MUST support loading secrets from external Kubernetes Secret (name: todo-secrets)
- **FR-017**: System MUST NOT include actual secret values in values.yaml or any chart files
- **FR-018**: Image pull policy MUST be configurable (default: Never for local images)

**Service Discovery**
- **FR-019**: Backend Service MUST be discoverable by frontend via Kubernetes DNS
- **FR-020**: Labels MUST be consistent between Deployments and Services for proper selector matching

### Key Entities

- **Deployment**: Kubernetes workload resource managing pod replicas and updates
- **Service**: Network abstraction providing stable endpoint for pod communication
- **ConfigMap**: Storage for non-sensitive configuration data as key-value pairs
- **Secret**: Reference to external Kubernetes Secret containing sensitive credentials
- **Pod**: Running instance of containerized application with health probes

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Application deploys successfully with a single `helm install` command in under 2 minutes
- **SC-002**: Both frontend and backend maintain 2 running replicas after deployment
- **SC-003**: Backend health checks pass within 30 seconds of pod startup
- **SC-004**: Frontend is accessible via browser within 60 seconds of deployment completion
- **SC-005**: Pod restart occurs automatically within 60 seconds when health check fails
- **SC-006**: Configuration changes via values.yaml take effect on helm upgrade without template modifications
- **SC-007**: No secrets are visible in any version-controlled chart files
- **SC-008**: All pods run as expected when proper secrets are pre-created in the cluster

## Assumptions

- Docker Desktop Kubernetes or Minikube is running and configured as the active kubectl context
- Docker images (todo-backend:latest, todo-frontend:latest) are already built and available locally
- Helm 3+ is installed on the developer's machine
- User has kubectl access to create secrets manually before deployment
- Local Kubernetes cluster has LoadBalancer support (Docker Desktop) or will use NodePort fallback

## Out of Scope

- Ingress controller configuration
- TLS/SSL certificate management
- Horizontal Pod Autoscaler (HPA) configuration
- Persistent Volume Claims for data storage
- Production cloud deployment configurations
- CI/CD pipeline integration
- Helm chart repository publishing
