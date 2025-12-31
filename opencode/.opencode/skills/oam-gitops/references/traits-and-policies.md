# OAM Traits and Policies Reference

## Traits

Traits are operational capabilities attached to components.

### ingress
Configure ingress routing with TLS support.

```yaml
traits:
  - type: ingress
    properties:
      domain: "api.example.com"
      path: "/api"
      tls: true
      class: "nginx"  # nginx|istio|traefik
      annotations:
        nginx.ingress.kubernetes.io/rewrite-target: "/"
```

### autoscaler
Horizontal Pod Autoscaler with CPU/memory targets.

```yaml
traits:
  - type: autoscaler
    properties:
      min: 2
      max: 10
      cpuTarget: 70
      memoryTarget: 80
```

### scaler
Fixed replica count scaling.

```yaml
traits:
  - type: scaler
    properties:
      replicas: 3
```

### gateway
API gateway exposure (KubeVela native).

```yaml
traits:
  - type: gateway
    properties:
      domain: "gateway.example.com"
      http:
        "/api/v1": 8080
        "/health": 8080
```

### sidecar
Inject sidecar containers.

```yaml
traits:
  - type: sidecar
    properties:
      name: "logging-agent"
      image: "fluent/fluent-bit:latest"
      volumes:
        - name: "varlog"
          path: "/var/log"
```

### kafka-producer
Configure application as Kafka producer.

```yaml
traits:
  - type: kafka-producer
    properties:
      topic: "events"
      brokers: "kafka-cluster:9092"
      acks: "all"
      compression: "gzip"
```

### kafka-consumer
Configure application as Kafka consumer.

```yaml
traits:
  - type: kafka-consumer
    properties:
      topic: "events"
      groupId: "my-consumer-group"
      brokers: "kafka-cluster:9092"
      autoOffsetReset: "earliest"
```

### resource
Override resource limits.

```yaml
traits:
  - type: resource
    properties:
      cpu: "1000m"
      memory: "1Gi"
      requests:
        cpu: "200m"
        memory: "256Mi"
```

### labels
Add Kubernetes labels.

```yaml
traits:
  - type: labels
    properties:
      "app.kubernetes.io/team": "platform"
      "app.kubernetes.io/cost-center": "engineering"
```

### annotations
Add Kubernetes annotations.

```yaml
traits:
  - type: annotations
    properties:
      "prometheus.io/scrape": "true"
      "prometheus.io/port": "8080"
```

## Policies

Policies apply cross-cutting concerns across components.

### health
Health checking policy for applications.

```yaml
policies:
  - name: health-policy
    type: health
    properties:
      probeTimeout: 60
      probeInterval: 10
```

### security-policy
Network policies and access control.

```yaml
policies:
  - name: network-policy
    type: security-policy
    properties:
      networkPolicy:
        ingress:
          - from:
              - namespaceSelector:
                  matchLabels:
                    name: allowed-namespace
        egress:
          - to:
              - namespaceSelector:
                  matchLabels:
                    name: allowed-namespace
```

### override
Selective component configuration overrides.

```yaml
policies:
  - name: prod-override
    type: override
    properties:
      components:
        - name: "web-service"
          properties:
            resources:
              cpu: "2000m"
              memory: "2Gi"
```

### env-binding
Environment-specific configuration for multi-cluster deployment.

```yaml
policies:
  - name: env-binding
    type: env-binding
    properties:
      envs:
        - name: staging
          placement:
            namespaceSelector:
              matchLabels:
                env: staging
        - name: production
          placement:
            namespaceSelector:
              matchLabels:
                env: production
```

### garbage-collect
Garbage collection policy for orphaned resources.

```yaml
policies:
  - name: gc-policy
    type: garbage-collect
    properties:
      keepLegacyResource: false
```

### topology
Topology spread constraints for high availability.

```yaml
policies:
  - name: topology-spread
    type: topology
    properties:
      clusterLabelSelector:
        region: "us-east-1"
      namespaceSelector:
        matchLabels:
          app: "my-app"
```

## Workflow Steps

Workflow steps define deployment sequence.

### deploy
Deploy components with policies.

```yaml
workflow:
  steps:
    - name: deploy-infra
      type: deploy
      properties:
        policies: ["env-binding"]
        env: staging
```

### suspend
Manual approval gate.

```yaml
workflow:
  steps:
    - name: manual-approval
      type: suspend
      properties:
        duration: "24h"  # Auto-resume after duration
```

### notification
Send notifications.

```yaml
workflow:
  steps:
    - name: notify-slack
      type: notification
      properties:
        slack:
          channel: "#deployments"
          message: "Deployment started for {{ .AppName }}"
```

### apply-component
Apply specific components.

```yaml
workflow:
  steps:
    - name: deploy-database
      type: apply-component
      properties:
        component: "database"
```
