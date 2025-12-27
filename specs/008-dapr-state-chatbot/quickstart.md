# Quickstart: Dapr State Store for Chatbot

**Feature**: 008-dapr-state-chatbot
**Date**: 2025-12-25

## Prerequisites

- Dapr CLI installed (`dapr --version`)
- Kubernetes cluster with Dapr initialized (`dapr init -k`)
- PostgreSQL database (Neon) accessible
- Backend application running

## Local Development Setup

### 1. Install Dapr CLI

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify
dapr --version
```

### 2. Initialize Dapr (Standalone Mode)

```bash
dapr init

# Verify components
dapr components list
```

### 3. Create State Store Component (Local)

Create `~/.dapr/components/statestore.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    value: "host=localhost user=postgres password=xxx dbname=todo sslmode=disable"
```

### 4. Run Backend with Dapr

```bash
cd backend

# Run with Dapr sidecar
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 -- python -m uvicorn app.main:app --reload
```

### 5. Test State Store

```bash
# Save state
curl -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key": "test-key", "value": {"message": "Hello Dapr!"}}]'

# Get state
curl http://localhost:3500/v1.0/state/statestore/test-key

# Delete state
curl -X DELETE http://localhost:3500/v1.0/state/statestore/test-key
```

## Kubernetes Deployment

### 1. Create Dapr Component

```yaml
# k8s/dapr-components/statestore.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: database-credentials
      key: connection-string
```

### 2. Apply Component

```bash
kubectl apply -f k8s/dapr-components/statestore.yaml
```

### 3. Verify Component

```bash
dapr components -k -n todo-app
```

### 4. Update Backend Deployment

Add Dapr annotations:

```yaml
# k8s/helm/todo-app/templates/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DAPR_HTTP_PORT | 3500 | Dapr sidecar port |
| CHAT_MESSAGE_WINDOW | 50 | Messages for AI context |
| CHAT_MAX_MESSAGES | 200 | Max messages before truncation |
| CHAT_STATE_TTL | 2592000 | State TTL (30 days in seconds) |

## Testing the Integration

### 1. Start a Chat

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "conversation_id": null}'
```

### 2. Verify State Saved

```bash
# Check state in Dapr
curl http://localhost:3500/v1.0/state/statestore/chat:{user_id}:{conv_id}
```

### 3. Continue Conversation

```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: Buy groceries", "conversation_id": 1}'
```

## Troubleshooting

### State Store Not Found

```bash
# Check Dapr sidecar logs
kubectl logs -l app=backend -c daprd -n todo-app

# Verify component
dapr components -k -n todo-app | grep statestore
```

### Connection String Issues

```bash
# Test PostgreSQL connection
kubectl run -it --rm debug --image=postgres:15 --restart=Never -- \
  psql "postgres://user:pass@host:5432/db?sslmode=require"
```

### Degraded Mode Active

If `X-Chat-Degraded: true` header appears:
1. Check Dapr sidecar is running
2. Verify state store component is applied
3. Check PostgreSQL connectivity

## Migration from Database

```bash
# Run migration script (one-time)
cd backend
python -m app.scripts.migrate_to_state_store

# Verify migration
curl http://localhost:3500/v1.0/state/statestore/chat:{user_id}:{conv_id}
```
