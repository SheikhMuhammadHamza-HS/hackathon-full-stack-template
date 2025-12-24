# Data Model: Helm Chart Structure

**Feature**: 006-helm-charts
**Date**: 2025-12-24

## Overview

This document defines the structure and schema for the Helm chart artifacts. Since this is an infrastructure feature, "data model" refers to the Helm values schema and Kubernetes resource definitions.

---

## Helm Chart Artifact Structure

```text
k8s/helm/todo-app/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Configurable values
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── configmap.yaml      # ConfigMap resource
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-deployment.yaml
    └── frontend-service.yaml
```

---

## Chart.yaml Schema

```yaml
apiVersion: v2
name: todo-app
description: Helm chart for Todo application deployment
type: application
version: 0.1.0
appVersion: "1.0.0"
```

| Field | Type | Description |
|-------|------|-------------|
| apiVersion | string | Helm chart API version (v2 for Helm 3) |
| name | string | Chart name |
| description | string | Human-readable description |
| type | string | application or library |
| version | string | Chart version (SemVer) |
| appVersion | string | Application version being deployed |

---

## values.yaml Schema

```yaml
# Global settings
replicaCount: 2

# Backend configuration
backend:
  image:
    repository: todo-backend
    tag: "latest"
    pullPolicy: Never
  service:
    type: ClusterIP
    port: 8000
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  probes:
    liveness:
      path: /health
      initialDelaySeconds: 10
      periodSeconds: 30
    readiness:
      path: /ready
      initialDelaySeconds: 5
      periodSeconds: 10

# Frontend configuration
frontend:
  image:
    repository: todo-frontend
    tag: "latest"
    pullPolicy: Never
  service:
    type: LoadBalancer
    port: 3000
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "300m"
  env:
    NEXT_PUBLIC_API_URL: "http://todo-app-backend:8000"

# ConfigMap data (non-sensitive)
config:
  NODE_ENV: "production"
  LOG_LEVEL: "info"

# Secret reference (created externally)
secrets:
  name: todo-secrets
```

### Values Schema Documentation

| Path | Type | Default | Description |
|------|------|---------|-------------|
| `replicaCount` | int | 2 | Number of replicas for both deployments |
| `backend.image.repository` | string | todo-backend | Backend image name |
| `backend.image.tag` | string | latest | Backend image tag |
| `backend.image.pullPolicy` | string | Never | Image pull policy |
| `backend.service.type` | string | ClusterIP | Backend service type |
| `backend.service.port` | int | 8000 | Backend service port |
| `backend.resources.requests.memory` | string | 256Mi | Memory request |
| `backend.resources.requests.cpu` | string | 100m | CPU request |
| `backend.resources.limits.memory` | string | 512Mi | Memory limit |
| `backend.resources.limits.cpu` | string | 500m | CPU limit |
| `frontend.image.repository` | string | todo-frontend | Frontend image name |
| `frontend.image.tag` | string | latest | Frontend image tag |
| `frontend.image.pullPolicy` | string | Never | Image pull policy |
| `frontend.service.type` | string | LoadBalancer | Frontend service type |
| `frontend.service.port` | int | 3000 | Frontend service port |
| `frontend.env.NEXT_PUBLIC_API_URL` | string | http://todo-app-backend:8000 | Backend API URL |
| `config.NODE_ENV` | string | production | Environment mode |
| `secrets.name` | string | todo-secrets | Name of external Secret |

---

## Kubernetes Resource Definitions

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "todo-app.fullname" . }}-config
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
data:
  NODE_ENV: {{ .Values.config.NODE_ENV | quote }}
  LOG_LEVEL: {{ .Values.config.LOG_LEVEL | quote }}
```

### Backend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      containers:
        - name: backend
          image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
          imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: {{ include "todo-app.fullname" . }}-config
            - secretRef:
                name: {{ .Values.secrets.name }}
          resources:
            {{- toYaml .Values.backend.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: {{ .Values.backend.probes.liveness.path }}
              port: 8000
            initialDelaySeconds: {{ .Values.backend.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.backend.probes.liveness.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.backend.probes.readiness.path }}
              port: 8000
            initialDelaySeconds: {{ .Values.backend.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.backend.probes.readiness.periodSeconds }}
```

### Backend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-backend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  type: {{ .Values.backend.service.type }}
  ports:
    - port: {{ .Values.backend.service.port }}
      targetPort: 8000
      protocol: TCP
  selector:
    {{- include "todo-app.selectorLabels" . | nindent 4 }}
    app.kubernetes.io/component: backend
```

### Frontend Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "todo-app.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: frontend
  template:
    metadata:
      labels:
        {{- include "todo-app.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: frontend
    spec:
      containers:
        - name: frontend
          image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
          imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
          ports:
            - containerPort: 3000
          env:
            - name: NEXT_PUBLIC_API_URL
              value: {{ .Values.frontend.env.NEXT_PUBLIC_API_URL | quote }}
          envFrom:
            - configMapRef:
                name: {{ include "todo-app.fullname" . }}-config
          resources:
            {{- toYaml .Values.frontend.resources | nindent 12 }}
```

### Frontend Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "todo-app.fullname" . }}-frontend
  labels:
    {{- include "todo-app.labels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
    - port: {{ .Values.frontend.service.port }}
      targetPort: 3000
      protocol: TCP
  selector:
    {{- include "todo-app.selectorLabels" . | nindent 4 }}
    app.kubernetes.io/component: frontend
```

---

## Label Standards

All resources use consistent labeling:

| Label | Value | Purpose |
|-------|-------|---------|
| `app.kubernetes.io/name` | todo-app | Application name |
| `app.kubernetes.io/instance` | {{ .Release.Name }} | Helm release name |
| `app.kubernetes.io/version` | {{ .Chart.AppVersion }} | Application version |
| `app.kubernetes.io/managed-by` | Helm | Resource manager |
| `app.kubernetes.io/component` | backend/frontend | Service component |

---

## External Dependencies

### Required Secret: `todo-secrets`

Must be created before `helm install`:

```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=BETTER_AUTH_SECRET="..." \
  --from-literal=OPENAI_API_KEY="sk-..."
```

| Key | Description | Required |
|-----|-------------|----------|
| DATABASE_URL | Neon PostgreSQL connection string | Yes |
| BETTER_AUTH_SECRET | Authentication secret | Yes |
| OPENAI_API_KEY | OpenAI API key for AI features | Yes |
