# OAM Component Definitions Reference

This document contains ALL valid component types for OAM Applications. **Never use a component type not defined here.**

## Infrastructure Components

### vcluster
Virtual Kubernetes environment with optional components.

```yaml
type: vcluster
properties:
  name: string              # Required: vCluster name
  istio: boolean            # Enable Istio service mesh
  knative: boolean          # Enable Knative serving
  argocd: boolean           # Enable ArgoCD
  observability: boolean    # Enable observability stack
  highAvailability: boolean # Enable HA mode
```

### neon-postgres
Neon PostgreSQL managed database.

```yaml
type: neon-postgres
properties:
  name: string       # Required: Database name
  namespace: string  # Required: Target namespace
  size: string       # Database size: small|medium|large
```

### postgresql
PostgreSQL database (standard).

```yaml
type: postgresql
properties:
  name: string           # Required: Database name
  namespace: string      # Required: Target namespace
  storage: string        # Storage size (e.g., "10Gi")
  version: string        # PostgreSQL version
```

### auth0-idp
Auth0 identity provider integration.

```yaml
type: auth0-idp
properties:
  name: string       # Required: IDP name
  namespace: string  # Required: Target namespace
  audience: string   # API audience URL
  domain: string     # Auth0 domain
```

### aws-apigateway
AWS API Gateway for external service access.

```yaml
type: aws-apigateway
properties:
  name: string          # Required: Gateway name
  namespace: string     # Required: Target namespace
  stage: string         # API stage (dev|staging|prod)
  cors: boolean         # Enable CORS
  throttling:
    rateLimit: number   # Requests per second
    burstLimit: number  # Burst limit
```

### karpenter-nodepool
Dynamic compute provisioning with Karpenter.

```yaml
type: karpenter-nodepool
properties:
  name: string               # Required: Nodepool name
  instanceTypes: [string]    # EC2 instance types
  capacityType: string       # on-demand|spot
  minNodes: number           # Minimum nodes
  maxNodes: number           # Maximum nodes
```

### snowflake-datawarehouse
Snowflake data warehouse.

```yaml
type: snowflake-datawarehouse
properties:
  name: string       # Required: Warehouse name
  namespace: string  # Required: Target namespace
  size: string       # Warehouse size: XSMALL|SMALL|MEDIUM|LARGE
  autoSuspend: number # Auto-suspend minutes
```

## Application Components

### webservice
Web applications with Knative serving.

```yaml
type: webservice
properties:
  name: string              # Component name (from metadata)
  image: string             # Required: Container image
  port: number              # Required: Container port (default: 8080)
  language: string          # Programming language (typescript|python|go|java)
  framework: string         # Framework (fastapi|express|gin|spring)
  version: string           # Application version
  targetEnvironment: string # Target vCluster name
  resources:
    cpu: string             # CPU limit (e.g., "500m")
    memory: string          # Memory limit (e.g., "512Mi")
  environment:              # Environment variables
    KEY: string
  healthPath: string        # Health check path (default: "/health")
  realtime: string          # Realtime platform name for integration
  enableGraphQLFederation: boolean  # Enable GraphQL federation
  openApiPath: string       # OpenAPI spec path for GraphQL
  registrySecret: string    # Image pull secret name
  envFrom:                  # Environment from secrets/configmaps
    - secretRef:
        name: string
```

### kafka
Apache Kafka event streaming platform.

```yaml
type: kafka
properties:
  name: string           # Required: Kafka cluster name
  namespace: string      # Required: Target namespace
  replicas: number       # Number of brokers (default: 3)
  storage: string        # Storage per broker (e.g., "100Gi")
  topics:                # Pre-created topics
    - name: string
      partitions: number
      replicationFactor: number
```

### redis
Redis in-memory data store.

```yaml
type: redis
properties:
  name: string       # Required: Redis name
  namespace: string  # Required: Target namespace
  mode: string       # standalone|cluster|sentinel
  memory: string     # Memory limit (e.g., "256Mi")
  persistence: boolean # Enable persistence
```

### mongodb
MongoDB document database.

```yaml
type: mongodb
properties:
  name: string       # Required: MongoDB name
  namespace: string  # Required: Target namespace
  replicas: number   # Replica set size
  storage: string    # Storage size (e.g., "10Gi")
  version: string    # MongoDB version
```

### graphql-gateway
GraphQL federation gateway (Hasura-based).

```yaml
type: graphql-gateway
properties:
  name: string                  # Component name
  serviceSelector:              # Service discovery labels
    labelKey: string
  autoSchema: boolean           # Auto-generate schema from services
  schemaRefreshInterval: string # Schema refresh interval (e.g., "5m")
  exposeIntrospection: boolean  # Enable GraphQL introspection
  enableConsole: boolean        # Enable Hasura console
  enableAllowList: boolean      # Enable query allowlist
  adminSecret: string           # Admin secret key
  customResolvers:              # Custom resolver endpoints
    - name: string
      endpoint: string
      headers:
        headerKey: string
  language: string              # For repo creation (typescript|go)
  framework: string             # For repo creation (apollo-server|gqlgen)
  repository: string            # Repository name to create
  resources:
    cpu: string
    memory: string
  targetEnvironment: string     # Target vCluster
```

### realtime-platform
Real-time data platform with Kafka, MQTT, ClickHouse.

```yaml
type: realtime-platform
properties:
  name: string             # Required: Platform name
  namespace: string        # Required: Target namespace
  kafka:
    enabled: boolean
    replicas: number
    storage: string
  mqtt:
    enabled: boolean
    replicas: number
  clickhouse:
    enabled: boolean
    shards: number
    storage: string
  metabase:
    enabled: boolean
  lenses:
    enabled: boolean
```

### rasa-chatbot
Rasa conversational AI platform.

```yaml
type: rasa-chatbot
properties:
  name: string           # Required: Chatbot name
  namespace: string      # Required: Target namespace
  model: string          # Model name/path
  replicas: number       # Number of replicas
  tracker:
    type: string         # redis|postgresql|mongodb
  actions:
    image: string        # Custom actions image
```

### camunda-orchestrator
Camunda process orchestration.

```yaml
type: camunda-orchestrator
properties:
  name: string           # Required: Orchestrator name
  namespace: string      # Required: Target namespace
  version: string        # Camunda version
  database:
    type: string         # postgresql|h2
    host: string
    name: string
  identity:
    enabled: boolean
    keycloak:
      enabled: boolean
```

### identity-service
Identity management service.

```yaml
type: identity-service
properties:
  name: string           # Required: Service name
  namespace: string      # Required: Target namespace
  provider: string       # auth0|keycloak|okta
  database:
    type: string
    host: string
```

## Traits Reference

### ingress
```yaml
type: ingress
properties:
  domain: string      # Required: Domain name
  path: string        # URL path (default: "/")
  tls: boolean        # Enable TLS
  class: string       # Ingress class (nginx|istio|traefik)
```

### autoscaler
```yaml
type: autoscaler
properties:
  min: number         # Minimum replicas
  max: number         # Maximum replicas
  cpuTarget: number   # CPU utilization target (%)
  memoryTarget: number # Memory utilization target (%)
```

### scaler
```yaml
type: scaler
properties:
  replicas: number    # Fixed replica count
```

### gateway
```yaml
type: gateway
properties:
  domain: string
  http:
    "/path": number   # Path to port mapping
```

### sidecar
```yaml
type: sidecar
properties:
  name: string        # Sidecar name
  image: string       # Sidecar image
```

### kafka-producer
```yaml
type: kafka-producer
properties:
  topic: string       # Kafka topic
  brokers: string     # Broker addresses
  acks: string        # Acknowledgment mode (all|1|0)
```

### kafka-consumer
```yaml
type: kafka-consumer
properties:
  topic: string       # Kafka topic
  groupId: string     # Consumer group ID
  brokers: string     # Broker addresses
```
