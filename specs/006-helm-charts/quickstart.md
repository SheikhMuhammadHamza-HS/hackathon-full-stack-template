# Quickstart: Helm Charts Deployment

**Feature**: 006-helm-charts
**Date**: 2025-12-24

## Prerequisites

Before deploying, ensure the following are in place:

- [ ] Docker Desktop installed and running
- [ ] Kubernetes enabled in Docker Desktop (Settings → Kubernetes → Enable)
- [ ] Helm 3+ installed (`helm version`)
- [ ] kubectl configured for Docker Desktop (`kubectl config use-context docker-desktop`)
- [ ] Docker images built locally:
  - `todo-backend:latest` (or specific tag)
  - `todo-frontend:latest` (or specific tag)

---

## Quick Deploy (5 Commands)

```bash
# 1. Verify Kubernetes is running
kubectl cluster-info

# 2. Create secrets (replace with your actual values)
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="your-neon-connection-string" \
  --from-literal=BETTER_AUTH_SECRET="your-auth-secret" \
  --from-literal=OPENAI_API_KEY="your-openai-key"

# 3. Install the Helm chart
helm install todo-app k8s/helm/todo-app/

# 4. Wait for pods to be ready
kubectl get pods -w

# 5. Access the application
kubectl get svc todo-app-frontend
# Open the EXTERNAL-IP in your browser (localhost on Docker Desktop)
```

---

## Detailed Deployment Steps

### Step 1: Verify Environment

```bash
# Check Kubernetes cluster
kubectl cluster-info
# Expected: Kubernetes control plane running at https://kubernetes.docker.internal:6443

# Check Helm
helm version
# Expected: version.BuildInfo{Version:"v3.x.x", ...}

# Check local images exist
docker images | grep todo
# Expected: todo-backend and todo-frontend images listed
```

### Step 2: Create Kubernetes Secret

**Option A: From literal values**
```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host/db?sslmode=require" \
  --from-literal=BETTER_AUTH_SECRET="your-32-char-secret-here" \
  --from-literal=OPENAI_API_KEY="sk-your-openai-key"
```

**Option B: From .env file (create secret.env first)**
```bash
# Create secret.env file (DO NOT COMMIT)
cat > secret.env << EOF
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
BETTER_AUTH_SECRET=your-32-char-secret-here
OPENAI_API_KEY=sk-your-openai-key
EOF

# Create secret from file
kubectl create secret generic todo-secrets --from-env-file=secret.env

# Delete the file
rm secret.env
```

### Step 3: Install Helm Chart

```bash
# Install with default values
helm install todo-app k8s/helm/todo-app/

# OR install with custom values
helm install todo-app k8s/helm/todo-app/ \
  --set replicaCount=3 \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0
```

### Step 4: Verify Deployment

```bash
# Check all resources
kubectl get all -l app.kubernetes.io/instance=todo-app

# Check pods are running
kubectl get pods
# Expected: 2 backend pods, 2 frontend pods, all Running

# Check services
kubectl get svc
# Expected: todo-app-backend (ClusterIP), todo-app-frontend (LoadBalancer)

# Check pod logs (if issues)
kubectl logs -l app.kubernetes.io/component=backend
kubectl logs -l app.kubernetes.io/component=frontend
```

### Step 5: Access Application

```bash
# Get frontend service URL
kubectl get svc todo-app-frontend
# EXTERNAL-IP will be localhost on Docker Desktop

# Open in browser
# http://localhost:3000
```

---

## Common Operations

### Upgrade Deployment

```bash
# Upgrade with new values
helm upgrade todo-app k8s/helm/todo-app/ --set replicaCount=3

# Upgrade with new image tag
helm upgrade todo-app k8s/helm/todo-app/ \
  --set backend.image.tag=v1.1.0 \
  --set frontend.image.tag=v1.1.0
```

### Scale Replicas

```bash
# Via Helm
helm upgrade todo-app k8s/helm/todo-app/ --set replicaCount=4

# Via kubectl (temporary, will be overwritten by Helm)
kubectl scale deployment todo-app-backend --replicas=4
```

### View Pod Logs

```bash
# Backend logs
kubectl logs -f deployment/todo-app-backend

# Frontend logs
kubectl logs -f deployment/todo-app-frontend

# All pods with label
kubectl logs -l app.kubernetes.io/name=todo-app --all-containers
```

### Restart Deployment

```bash
kubectl rollout restart deployment/todo-app-backend
kubectl rollout restart deployment/todo-app-frontend
```

### Uninstall

```bash
# Remove Helm release
helm uninstall todo-app

# Remove secret (optional)
kubectl delete secret todo-secrets
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Common issues:
# - ImagePullBackOff: Image not found locally (check docker images)
# - CrashLoopBackOff: Container crashing (check logs)
# - Pending: No resources (check resource limits)
```

### Secret Not Found

```bash
# Verify secret exists
kubectl get secret todo-secrets

# Check secret contents (base64 encoded)
kubectl get secret todo-secrets -o yaml
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints todo-app-frontend

# Port forward for debugging
kubectl port-forward svc/todo-app-frontend 3000:3000
```

### Health Check Failures

```bash
# Check probe status
kubectl describe pod <pod-name> | grep -A 5 "Liveness\|Readiness"

# Test health endpoint manually
kubectl exec -it <pod-name> -- curl localhost:8000/health
```

---

## Build and Deploy Flow

Complete flow from code to deployment:

```bash
# 1. Build Docker images
docker build -t todo-backend:v1.0.0 backend/
docker build -t todo-frontend:v1.0.0 frontend/

# 2. Create secret (first time only)
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=OPENAI_API_KEY="..."

# 3. Install or upgrade
helm upgrade --install todo-app k8s/helm/todo-app/ \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.tag=v1.0.0

# 4. Verify
kubectl get pods -w
```
