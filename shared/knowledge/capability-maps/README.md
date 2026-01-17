# Capability Maps

This folder contains organization capability models.

## Content Types
- Business capability maps (L1-L4 hierarchies)
- Value stream definitions
- Business process models

## File Formats
- `.json` - Structured capability data (recommended)
- `.md` - Markdown documentation
- `.txt` - Plain text documents

## Qdrant Collection
- **Collection Name:** `capability-maps`
- **Consumers:** business-architect

## Example Structure
```json
{
  "id": "cap-1",
  "level": 1,
  "capability": "Brand Management",
  "definition": "The ability to...",
  "subcapabilities": [...]
}
```
