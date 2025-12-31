---
name: oam-gitops
description: "OAM Application generation with GitOps deployment. Use when: (1) Creating KubeVela OAM Application specs, (2) Deploying to GitOps repositories, (3) Working with Crossplane-backed infrastructure. CRITICAL: Only generate OAM Applications using component types defined in the references folder. Never invent new component types."
---

# OAM GitOps Skill

This skill enables the solution-architect agent to generate compliant OAM Application specifications and deploy them to GitOps repositories.

## CRITICAL CONSTRAINT

**You MUST only use component types that are defined in the reference files.**

Available component types (from `references/component-definitions.md`):
- `webservice` - Web applications with Knative serving
- `kafka` - Apache Kafka event streaming
- `redis` - Redis in-memory data store
- `mongodb` - MongoDB document database
- `vcluster` - Virtual Kubernetes environments
- `neon-postgres` - Neon PostgreSQL managed database
- `auth0-idp` - Auth0 identity provider
- `aws-apigateway` - AWS API Gateway
- `karpenter-nodepool` - Dynamic compute provisioning
- `snowflake-datawarehouse` - Snowflake data warehouse
- `graphql-gateway` - GraphQL federation gateway
- `realtime-platform` - Real-time data platform (Kafka, MQTT, ClickHouse)
- `rasa-chatbot` - Rasa conversational AI
- `camunda-orchestrator` - Camunda process orchestration
- `postgresql` - PostgreSQL database
- `identity-service` - Identity management service

**DO NOT create OAM Applications with component types not in this list.**

## OAM Application Structure

```yaml
apiVersion: core.oam.dev/v1beta1
kind: Application
metadata:
  name: <service-name>
  namespace: <namespace>
spec:
  components:
    - name: <component-name>
      type: <component-type>  # MUST be from the list above
      properties:
        # Component-specific properties from references
      traits:
        - type: <trait-type>
          properties:
            # Trait properties
  policies:
    - name: <policy-name>
      type: <policy-type>
      properties:
        # Policy properties
  workflow:
    steps:
      - name: <step-name>
        type: <step-type>
        properties:
          # Step properties
```

## Available Traits

From `references/traits-and-policies.md`:
- `ingress` - Configure ingress routing with TLS
- `autoscaler` - Horizontal Pod Autoscaler
- `kafka-producer` - Kafka producer configuration
- `kafka-consumer` - Kafka consumer configuration
- `gateway` - API gateway exposure
- `scaler` - Replica scaling
- `sidecar` - Sidecar container injection

## Available Policies

- `health` - Health checking policy
- `security-policy` - Network policies and access control
- `override` - Selective component configuration overrides
- `env-binding` - Environment-specific configuration

## GitOps Deployment

### Target Repository Structure

```
<repo-name>-gitops/
├── apps/
│   └── oam-application.yaml    # OAM Application spec (YOU UPDATE THIS)
├── base/
│   └── kustomization.yaml
└── overlays/
    ├── dev/
    ├── staging/
    └── production/
```

### Deployment via GitHub API

The n8n workflow handles GitHub commits. Your output should include:

```json
{
  "artifacts": {
    "apps/oam-application.yaml": "<yaml-content>"
  },
  "gitops": {
    "repository": "<org>/<repo-name>-gitops",
    "branch": "main",
    "commitMessage": "feat(<service>): Update OAM Application spec"
  }
}
```

## Example: Compliant OAM Application

```yaml
apiVersion: core.oam.dev/v1beta1
kind: Application
metadata:
  name: patient-portal
  namespace: healthcare
spec:
  components:
    # Web service component
    - name: patient-api
      type: webservice
      properties:
        image: ghcr.io/org/patient-api:latest
        port: 8080
        language: typescript
        framework: fastapi
        version: "1.0.0"
        resources:
          cpu: "500m"
          memory: "512Mi"
        environment:
          NODE_ENV: "production"
          LOG_LEVEL: "info"
        healthPath: "/health"
      traits:
        - type: ingress
          properties:
            domain: patient-portal.example.com
            path: /api
            tls: true
        - type: autoscaler
          properties:
            min: 2
            max: 10
            cpuTarget: 70

    # Database component
    - name: patient-db
      type: neon-postgres
      properties:
        name: patient-db
        namespace: healthcare
        size: "small"

    # Identity provider
    - name: patient-auth
      type: auth0-idp
      properties:
        name: patient-auth
        namespace: healthcare
        audience: "https://patient-portal.example.com"

  policies:
    - name: health-policy
      type: health
      properties:
        probeTimeout: 60

    - name: env-binding
      type: env-binding
      properties:
        envs:
          - name: production
            placement:
              namespaceSelector:
                matchLabels:
                  env: production

  workflow:
    steps:
      - name: deploy-infra
        type: deploy
        properties:
          policies: ["env-binding"]

      - name: deploy-app
        type: deploy
        properties:
          policies: ["health-policy"]
```

## Validation Checklist

Before outputting an OAM Application:

1. [ ] All component types exist in the reference definitions
2. [ ] All properties match the component's schema
3. [ ] All traits are from the available traits list
4. [ ] Namespace is specified
5. [ ] Resource limits are defined for webservice components
6. [ ] Health paths are configured for webservice components

## Output Format

Always return your OAM Application in this JSON structure:

```json
{
  "artifacts": {
    "apps/oam-application.yaml": "apiVersion: core.oam.dev/v1beta1\nkind: Application\n..."
  },
  "gitops": {
    "repository": "<org>/<repo-name>-gitops",
    "branch": "main",
    "commitMessage": "feat(<service>): <description>"
  }
}
```
