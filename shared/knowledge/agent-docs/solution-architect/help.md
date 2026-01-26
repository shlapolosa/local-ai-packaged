# Solution Architect Agent

## What I Do
I design technical solutions including API specifications, integration patterns, database schemas, and event-driven architectures. I produce OpenAPI, AsyncAPI, Avro schemas, and SQL DDL.

## Commands
- `solution:help` - Show this help
- `solution:status` - Check my knowledge status
- `solution:list` - List my knowledge collections
- `solution:query <question>` - Ask me about API design, integration patterns, or schemas
- `solution:upload` - Add knowledge to my collection (attach a file)
- `solution:reload` - Refresh my knowledge from source files

## Examples
- "Design APIs for an e-commerce platform" - Full solution package
- "solution:query what are best practices for REST API versioning?"
- "solution:query when should I use event-driven vs request-response?"
- "solution:upload" + attach API specifications or integration patterns

## My Knowledge Topics
- OpenAPI 3.0/3.1 specification
- AsyncAPI 2.0 for event-driven APIs
- REST API design patterns
- GraphQL design patterns
- Event-driven architecture
- Cloud Events specification
- Apache Avro schemas
- Database schema design
- Integration patterns (EIP)
- API security (OAuth, JWT)

## Output Artifacts
When I execute a solution design, I produce:
- Solution Architecture Markdown
- OpenAPI YAML specification (for REST)
- AsyncAPI YAML specification (for events)
- Avro schemas JSON (for event payloads)
- Cloud Events documentation
- SQL DDL schema

## Integration Style Detection
I automatically detect the best integration approach:
- **REST-only**: Traditional request-response APIs
- **Events-only**: Fully event-driven architecture
- **Hybrid**: Combination of REST and events

## Integration
I work with other agents in the architecture pipeline:
- I receive architecture designs from **Architect**
- **Software Delivery** uses my specs for code generation
- **Test Strategist** creates API tests from my specs
