# Quickstart: Dapr Pub/Sub Event System

**Feature**: 009-dapr-pubsub-events
**Date**: 2025-12-25

## Prerequisites

- Dapr CLI installed (`dapr --version`)
- Kubernetes cluster with Dapr initialized (`dapr init -k`)
- Kafka running (Strimzi or managed)
- Backend application running

## Local Development Setup

### 1. Start Kafka (Docker Compose)

```yaml
# docker-compose.kafka.yml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
```

```bash
docker-compose -f docker-compose.kafka.yml up -d
```

### 2. Create Dapr Pub/Sub Component (Local)

Create `~/.dapr/components/kafka-pubsub.yaml`:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:9092"
  - name: authType
    value: "none"
  - name: consumerGroup
    value: "todo-backend"
```

### 3. Create Kafka Topics

```bash
# Using Kafka CLI
docker exec -it kafka kafka-topics --create \
  --topic tasks \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

docker exec -it kafka kafka-topics --create \
  --topic reminders \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

docker exec -it kafka kafka-topics --create \
  --topic tasks-dlq \
  --partitions 1 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092
```

### 4. Run Backend with Dapr

```bash
cd backend

# Run with Dapr sidecar
dapr run --app-id backend --app-port 8000 --dapr-http-port 3500 -- python -m uvicorn app.main:app --reload
```

### 5. Test Event Publishing

```bash
# Publish test event
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/tasks \
  -H "Content-Type: application/cloudevents+json" \
  -d '{
    "specversion": "1.0",
    "type": "task.created",
    "source": "test",
    "id": "test-001",
    "time": "2025-12-25T10:00:00Z",
    "partitionkey": "user-test",
    "data": {
      "task_id": 1,
      "user_id": "user-test",
      "title": "Test Task"
    }
  }'
```

### 6. Verify Subscription

Check backend logs for event receipt:
```
INFO: Received task.created event for task 1
```

## Kubernetes Deployment

### 1. Deploy Strimzi Operator

```bash
# Install Strimzi Operator
kubectl create namespace kafka
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka -n kafka
```

### 2. Create Kafka Cluster

```yaml
# k8s/kafka/strimzi/kafka-cluster.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
  namespace: kafka
spec:
  kafka:
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    storage:
      type: ephemeral
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
```

```bash
kubectl apply -f k8s/kafka/strimzi/kafka-cluster.yaml
```

### 3. Create Topics

```yaml
# k8s/kafka/strimzi/kafka-topics.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: tasks
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: tasks-dlq
  namespace: kafka
  labels:
    strimzi.io/cluster: my-cluster
spec:
  partitions: 1
  replicas: 1
  config:
    retention.ms: 2592000000  # 30 days
```

```bash
kubectl apply -f k8s/kafka/strimzi/kafka-topics.yaml
```

### 4. Create Dapr Component

```yaml
# k8s/dapr-components/kafka-pubsub.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
  - name: authType
    value: "none"
  - name: consumerGroup
    value: "todo-backend"
```

```bash
kubectl apply -f k8s/dapr-components/kafka-pubsub.yaml
```

### 5. Verify Dapr Component

```bash
dapr components -k -n todo-app | grep kafka-pubsub
```

### 6. Update Backend Deployment

```yaml
# Add Dapr annotations
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "backend"
    dapr.io/app-port: "8000"
```

## Testing the Event Flow

### 1. Create a Task

```bash
curl -X POST http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test recurring task",
    "priority": "high",
    "due_date": "2025-12-26T18:00:00Z",
    "is_recurring": true,
    "recurring_interval": "daily"
  }'
```

### 2. Verify Event Published

Check backend logs:
```
INFO: Published task.created event for task 42
```

### 3. Complete the Task

```bash
curl -X POST http://localhost:8000/api/{user_id}/tasks/42/complete \
  -H "Authorization: Bearer {token}"
```

### 4. Verify Recurring Instance Created

Check backend logs:
```
INFO: Received task.completed event for task 42
INFO: Created next recurring instance: 43
```

### 5. Check New Task

```bash
curl http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer {token}"
```

## Monitoring Events

### View Kafka Topics

```bash
# List topics
kubectl exec -it my-cluster-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# View messages
kubectl exec -it my-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh --topic tasks \
  --from-beginning --bootstrap-server localhost:9092
```

### View Dapr Logs

```bash
kubectl logs -l app=backend -c daprd -n todo-app --tail=100
```

## Troubleshooting

### Events Not Publishing

1. Check Dapr sidecar is running:
```bash
kubectl get pods -l app=backend -n todo-app
```

2. Check Dapr component:
```bash
dapr components -k -n todo-app
```

3. Check Kafka connectivity:
```bash
kubectl run kafka-test -it --rm --image=confluentinc/cp-kafka:7.5.0 -- \
  kafka-topics --list --bootstrap-server my-cluster-kafka-bootstrap.kafka:9092
```

### Events Not Received

1. Check subscription endpoint:
```bash
curl http://localhost:8000/dapr/subscribe
```

2. Check handler is registered in FastAPI

3. Check Dapr subscription logs:
```bash
kubectl logs -l app=backend -c daprd -n todo-app | grep subscribe
```

### Dead Letter Queue Growing

1. Check handler errors:
```bash
kubectl logs -l app=backend -c backend -n todo-app | grep ERROR
```

2. View DLQ messages:
```bash
kubectl exec -it my-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh --topic tasks-dlq \
  --from-beginning --bootstrap-server localhost:9092
```
