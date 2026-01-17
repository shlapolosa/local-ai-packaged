#!/usr/bin/env python3
"""
json-to-archimate.py - Transform LLM JSON output to ArchiMate XML

This script takes JSON input (from LLM) describing ArchiMate elements and
relationships, and uses pyArchimate to generate valid Archi-compatible XML.

Usage:
    python json-to-archimate.py input.json output.archimate
    cat input.json | python json-to-archimate.py - output.archimate
    echo '{"name": "Model", ...}' | python json-to-archimate.py

JSON Schema:
{
    "name": "Model Name",
    "layer": "business|application|technology|all",
    "elements": [
        {
            "id": "unique-id",
            "type": "BusinessActor|BusinessProcess|ApplicationComponent|...",
            "name": "Element Name",
            "description": "Optional description"
        }
    ],
    "relationships": [
        {
            "type": "Serving|Realization|Assignment|Flow|Access|Composition|Aggregation|Triggering",
            "source": "source-element-id",
            "target": "target-element-id",
            "description": "Optional description"
        }
    ]
}
"""

import json
import sys
import argparse
from typing import Dict, Any, Optional
import uuid

try:
    from pyArchimate import Model, ArchiType, Writers
    PYARCHIMATE_AVAILABLE = True
except ImportError:
    PYARCHIMATE_AVAILABLE = False
    print("Warning: pyArchimate not installed. Using template-based output.", file=sys.stderr)

# Mapping from JSON type names to ArchiType enum values
TYPE_MAPPING = {
    # Business Layer
    "BusinessActor": "BusinessActor",
    "BusinessRole": "BusinessRole",
    "BusinessCollaboration": "BusinessCollaboration",
    "BusinessInterface": "BusinessInterface",
    "BusinessProcess": "BusinessProcess",
    "BusinessFunction": "BusinessFunction",
    "BusinessInteraction": "BusinessInteraction",
    "BusinessEvent": "BusinessEvent",
    "BusinessService": "BusinessService",
    "BusinessObject": "BusinessObject",
    "Contract": "Contract",
    "Representation": "Representation",
    "Product": "Product",

    # Application Layer
    "ApplicationComponent": "ApplicationComponent",
    "ApplicationCollaboration": "ApplicationCollaboration",
    "ApplicationInterface": "ApplicationInterface",
    "ApplicationFunction": "ApplicationFunction",
    "ApplicationInteraction": "ApplicationInteraction",
    "ApplicationProcess": "ApplicationProcess",
    "ApplicationEvent": "ApplicationEvent",
    "ApplicationService": "ApplicationService",
    "DataObject": "DataObject",

    # Technology Layer
    "Node": "Node",
    "Device": "Device",
    "SystemSoftware": "SystemSoftware",
    "TechnologyCollaboration": "TechnologyCollaboration",
    "TechnologyInterface": "TechnologyInterface",
    "Path": "Path",
    "CommunicationNetwork": "CommunicationNetwork",
    "TechnologyFunction": "TechnologyFunction",
    "TechnologyProcess": "TechnologyProcess",
    "TechnologyInteraction": "TechnologyInteraction",
    "TechnologyEvent": "TechnologyEvent",
    "TechnologyService": "TechnologyService",
    "Artifact": "Artifact",

    # Motivation Layer
    "Stakeholder": "Stakeholder",
    "Driver": "Driver",
    "Assessment": "Assessment",
    "Goal": "Goal",
    "Outcome": "Outcome",
    "Principle": "Principle",
    "Requirement": "Requirement",
    "Constraint": "Constraint",
    "Meaning": "Meaning",
    "Value": "Value",

    # Strategy Layer
    "Resource": "Resource",
    "Capability": "Capability",
    "CourseOfAction": "CourseOfAction",

    # Implementation Layer
    "WorkPackage": "WorkPackage",
    "Deliverable": "Deliverable",
    "ImplementationEvent": "ImplementationEvent",
    "Plateau": "Plateau",
    "Gap": "Gap",
}

# Relationship type mapping
RELATIONSHIP_MAPPING = {
    "Serving": "ServingRelationship",
    "Realization": "RealizationRelationship",
    "Assignment": "AssignmentRelationship",
    "Flow": "FlowRelationship",
    "Access": "AccessRelationship",
    "Composition": "CompositionRelationship",
    "Aggregation": "AggregationRelationship",
    "Triggering": "TriggeringRelationship",
    "Influence": "InfluenceRelationship",
    "Specialization": "SpecializationRelationship",
    "Association": "AssociationRelationship",
}

# Layer to folder type mapping
LAYER_FOLDER_TYPE = {
    "business": "business",
    "application": "application",
    "technology": "technology",
    "motivation": "motivation",
    "strategy": "strategy",
    "implementation": "implementation_migration",
}


def get_element_layer(element_type: str) -> str:
    """Determine which layer an element belongs to."""
    business_types = ["BusinessActor", "BusinessRole", "BusinessCollaboration",
                      "BusinessInterface", "BusinessProcess", "BusinessFunction",
                      "BusinessInteraction", "BusinessEvent", "BusinessService",
                      "BusinessObject", "Contract", "Representation", "Product"]
    app_types = ["ApplicationComponent", "ApplicationCollaboration",
                 "ApplicationInterface", "ApplicationFunction", "ApplicationInteraction",
                 "ApplicationProcess", "ApplicationEvent", "ApplicationService", "DataObject"]
    tech_types = ["Node", "Device", "SystemSoftware", "TechnologyCollaboration",
                  "TechnologyInterface", "Path", "CommunicationNetwork",
                  "TechnologyFunction", "TechnologyProcess", "TechnologyInteraction",
                  "TechnologyEvent", "TechnologyService", "Artifact"]
    motivation_types = ["Stakeholder", "Driver", "Assessment", "Goal", "Outcome",
                        "Principle", "Requirement", "Constraint", "Meaning", "Value"]
    strategy_types = ["Resource", "Capability", "CourseOfAction"]
    impl_types = ["WorkPackage", "Deliverable", "ImplementationEvent", "Plateau", "Gap"]

    if element_type in business_types:
        return "business"
    elif element_type in app_types:
        return "application"
    elif element_type in tech_types:
        return "technology"
    elif element_type in motivation_types:
        return "motivation"
    elif element_type in strategy_types:
        return "strategy"
    elif element_type in impl_types:
        return "implementation"
    return "other"


def generate_id(prefix: str = "id") -> str:
    """Generate a unique ID."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def transform_with_pyarchimate(data: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """Transform JSON to ArchiMate using pyArchimate library."""
    model = Model(name=data.get("name", "Generated Model"))

    # Track elements by their JSON ID for relationship linking
    element_map: Dict[str, Any] = {}

    # Add elements
    for elem in data.get("elements", []):
        elem_type = elem.get("type", "BusinessObject")
        elem_name = elem.get("name", "Unnamed")
        elem_desc = elem.get("description", "")
        elem_id = elem.get("id", generate_id())

        # Get ArchiType enum value
        if hasattr(ArchiType, elem_type):
            archi_type = getattr(ArchiType, elem_type)
        else:
            print(f"Warning: Unknown type {elem_type}, defaulting to BusinessObject", file=sys.stderr)
            archi_type = ArchiType.BusinessObject

        element = model.add(concept_type=archi_type, name=elem_name, desc=elem_desc)
        element_map[elem_id] = element

    # Add relationships
    for rel in data.get("relationships", []):
        rel_type = rel.get("type", "Association")
        source_id = rel.get("source")
        target_id = rel.get("target")
        rel_desc = rel.get("description", "")

        if source_id not in element_map:
            print(f"Warning: Source element '{source_id}' not found, skipping relationship", file=sys.stderr)
            continue
        if target_id not in element_map:
            print(f"Warning: Target element '{target_id}' not found, skipping relationship", file=sys.stderr)
            continue

        # Get relationship type
        rel_type_name = RELATIONSHIP_MAPPING.get(rel_type, "AssociationRelationship")
        if hasattr(ArchiType, rel_type_name.replace("Relationship", "")):
            archi_rel_type = getattr(ArchiType, rel_type_name.replace("Relationship", ""))
        elif hasattr(ArchiType, rel_type):
            archi_rel_type = getattr(ArchiType, rel_type)
        else:
            print(f"Warning: Unknown relationship type {rel_type}, using Association", file=sys.stderr)
            archi_rel_type = ArchiType.Association

        model.add_relationship(
            rel_type=archi_rel_type,
            source=element_map[source_id],
            target=element_map[target_id],
            desc=rel_desc
        )

    # Write to file or return XML string
    if output_path:
        model.write(output_path, writer=Writers.archimate)
        with open(output_path, 'r') as f:
            return f.read()
    else:
        # Write to temp file and read back
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', suffix='.archimate', delete=False) as f:
            temp_path = f.name
        model.write(temp_path, writer=Writers.archimate)
        with open(temp_path, 'r') as f:
            xml_content = f.read()
        os.unlink(temp_path)
        return xml_content


def transform_with_template(data: Dict[str, Any]) -> str:
    """Transform JSON to ArchiMate using template-based approach (fallback)."""
    model_name = data.get("name", "Generated Model")
    model_id = generate_id("model")

    # Group elements by layer
    elements_by_layer: Dict[str, list] = {
        "business": [],
        "application": [],
        "technology": [],
        "motivation": [],
        "strategy": [],
        "implementation": [],
        "other": [],
    }

    element_ids: Dict[str, str] = {}  # Map JSON id to generated XML id

    for elem in data.get("elements", []):
        elem_type = elem.get("type", "BusinessObject")
        layer = get_element_layer(elem_type)
        json_id = elem.get("id", generate_id())
        xml_id = generate_id(f"id-{elem_type[:3].lower()}")
        element_ids[json_id] = xml_id

        elements_by_layer[layer].append({
            "id": xml_id,
            "type": elem_type,
            "name": elem.get("name", "Unnamed"),
            "description": elem.get("description", ""),
        })

    # Build XML
    xml_parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<archimate:model xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        f'    xmlns:archimate="http://www.archimatetool.com/archimate"',
        f'    name="{escape_xml(model_name)}"',
        f'    id="{model_id}" version="5.0.0">',
    ]

    # Add element folders
    for layer, elements in elements_by_layer.items():
        if not elements:
            continue

        folder_type = LAYER_FOLDER_TYPE.get(layer, layer)
        folder_id = generate_id(f"folder-{layer}")
        folder_name = layer.capitalize() if layer != "implementation" else "Implementation & Migration"

        xml_parts.append(f'  <folder name="{folder_name}" id="{folder_id}" type="{folder_type}">')

        for elem in elements:
            xml_parts.append(f'    <element xsi:type="archimate:{elem["type"]}" name="{escape_xml(elem["name"])}" id="{elem["id"]}">')
            if elem["description"]:
                xml_parts.append(f'      <documentation>{escape_xml(elem["description"])}</documentation>')
            xml_parts.append(f'    </element>')

        xml_parts.append(f'  </folder>')

    # Add relationships folder
    relationships = data.get("relationships", [])
    if relationships:
        rel_folder_id = generate_id("folder-relations")
        xml_parts.append(f'  <folder name="Relations" id="{rel_folder_id}" type="relations">')

        for i, rel in enumerate(relationships):
            rel_type = RELATIONSHIP_MAPPING.get(rel.get("type", "Association"), "AssociationRelationship")
            rel_id = generate_id(f"rel-{i:03d}")
            source_id = element_ids.get(rel.get("source", ""), "unknown")
            target_id = element_ids.get(rel.get("target", ""), "unknown")

            if source_id == "unknown" or target_id == "unknown":
                print(f"Warning: Skipping relationship with missing source/target", file=sys.stderr)
                continue

            xml_parts.append(f'    <element xsi:type="archimate:{rel_type}"')
            xml_parts.append(f'        id="{rel_id}" source="{source_id}" target="{target_id}"/>')

        xml_parts.append(f'  </folder>')

    xml_parts.append('</archimate:model>')

    return '\n'.join(xml_parts)


def escape_xml(text: str) -> str:
    """Escape XML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def main():
    parser = argparse.ArgumentParser(
        description="Transform LLM JSON output to ArchiMate XML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input JSON file (use - for stdin)")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output ArchiMate file (prints to stdout if not specified)")
    parser.add_argument("--use-template", action="store_true",
                        help="Force template-based output even if pyArchimate is available")

    args = parser.parse_args()

    # Read input
    if args.input == "-":
        json_input = sys.stdin.read()
    else:
        with open(args.input, 'r') as f:
            json_input = f.read()

    # Parse JSON
    try:
        data = json.loads(json_input)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    # Transform
    if PYARCHIMATE_AVAILABLE and not args.use_template:
        xml_output = transform_with_pyarchimate(data, args.output)
    else:
        xml_output = transform_with_template(data)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(xml_output)

    # Output
    if not args.output:
        print(xml_output)


if __name__ == "__main__":
    main()
