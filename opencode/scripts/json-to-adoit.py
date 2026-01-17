#!/usr/bin/env python3
"""
json-to-adoit.py - Transform LLM JSON output to ADOIT Excel import format

This script takes JSON input (from LLM) describing ArchiMate elements and
relationships, and generates an ADOIT-compatible Excel import file.

Usage:
    python json-to-adoit.py input.json output.xlsx
    cat input.json | python json-to-adoit.py - output.xlsx
    echo '{"name": "Model", ...}' | python json-to-adoit.py

JSON Schema:
{
    "name": "Model Name",
    "elements": [
        {
            "id": "unique-id",
            "type": "Capability|ApplicationComponent|BusinessProcess|...",
            "name": "Element Name",
            "description": "Optional description",
            "relationships": {
                "composition": ["child-id-1", "child-id-2"],
                "realization": ["target-id"],
                "serving": ["consumer-id"]
            }
        }
    ]
}

Note: This script converts ArchiMate JSON to ADOIT Excel format.
The JSON relationship structure uses element IDs, which are resolved
to element names for ADOIT import.
"""

import json
import sys
import argparse
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add the ADOIT skill scripts path
sys.path.insert(0, os.path.join(os.path.dirname(__file__),
    '../.opencode/skills/adoit-archimate/scripts'))

try:
    from adoit_excel_generator import ADOITExcelGenerator
    ADOIT_GENERATOR_AVAILABLE = True
except ImportError:
    ADOIT_GENERATOR_AVAILABLE = False
    print("Warning: adoit_excel_generator not available. Using built-in generator.", file=sys.stderr)


# Mapping from JSON type names (camelCase) to ADOIT sheet names (Title Case)
TYPE_MAPPING = {
    # Strategy Layer
    "Resource": "Resource",
    "Capability": "Capability",
    "ValueStream": "Value Stream",
    "CourseOfAction": "Course of Action",

    # Business Layer
    "BusinessActor": "Business Actor",
    "BusinessRole": "Business Role",
    "BusinessCollaboration": "Business Collaboration",
    "BusinessInterface": "Business Interface",
    "BusinessProcess": "Business Process",
    "BusinessFunction": "Business Function",
    "BusinessInteraction": "Business Interaction",
    "BusinessEvent": "Business Event",
    "BusinessService": "Business Service",
    "BusinessObject": "Business Object",
    "Contract": "Contract",
    "Representation": "Representation",
    "Product": "Product",

    # Application Layer
    "ApplicationComponent": "Application Component",
    "ApplicationCollaboration": "Application Collaboration",
    "ApplicationInterface": "Application Interface",
    "ApplicationFunction": "Application Function",
    "ApplicationInteraction": "Application Interaction",
    "ApplicationProcess": "Application Process",
    "ApplicationEvent": "Application Event",
    "ApplicationService": "Application Service",
    "DataObject": "Data Object",

    # Technology Layer
    "Node": "Node",
    "Device": "Device",
    "SystemSoftware": "System Software",
    "TechnologyCollaboration": "Technology Collaboration",
    "TechnologyInterface": "Technology Interface",
    "Path": "Path",
    "CommunicationNetwork": "Communication Network",
    "DistributionNetwork": "Distribution Network",
    "TechnologyFunction": "Technology Function",
    "TechnologyProcess": "Technology Process",
    "TechnologyInteraction": "Technology Interaction",
    "TechnologyEvent": "Technology Event",
    "TechnologyService": "Technology Service",
    "Artifact": "Artifact",
    "Equipment": "Equipment",
    "Facility": "Facility",
    "Material": "Material",

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

    # Implementation Layer
    "WorkPackage": "Work Package",
    "Deliverable": "Deliverable",
    "ImplementationEvent": "Implementation Event",
    "Plateau": "Plateau",
    "Gap": "Gap",

    # Other
    "Location": "Location",
    "Grouping": "Grouping",
    "Junction": "Junction",
}

# Relationship type mapping
RELATIONSHIP_MAPPING = {
    "composition": "Composition",
    "aggregation": "Aggregation",
    "assignment": "Assignment",
    "realization": "Realization",
    "serving": "Serving",
    "access": "Access",
    "influence": "Influence",
    "triggering": "Triggering",
    "flow": "Flow",
    "specialization": "Specialization",
    "association": "Association",
}


def get_adoit_type(json_type: str) -> str:
    """Convert JSON type name to ADOIT type name."""
    return TYPE_MAPPING.get(json_type, json_type)


def build_id_to_name_map(elements: List[Dict[str, Any]]) -> Dict[str, str]:
    """Build a mapping from element IDs to names."""
    return {elem.get("id", elem.get("name", "")): elem.get("name", "")
            for elem in elements}


def build_id_to_type_map(elements: List[Dict[str, Any]]) -> Dict[str, str]:
    """Build a mapping from element IDs to their ADOIT types."""
    return {elem.get("id", elem.get("name", "")): get_adoit_type(elem.get("type", ""))
            for elem in elements}


def resolve_relationship_targets(targets: List[str], id_to_name: Dict[str, str]) -> List[str]:
    """Resolve element IDs to names for relationship targets."""
    resolved = []
    for target in targets:
        # Try to resolve as ID first, fall back to using as name
        resolved.append(id_to_name.get(target, target))
    return resolved


def transform_with_generator(data: Dict[str, Any], output_path: Optional[str] = None) -> bool:
    """Transform JSON to ADOIT Excel using the generator library."""
    gen = ADOITExcelGenerator()

    elements = data.get("elements", [])
    id_to_name = build_id_to_name_map(elements)
    id_to_type = build_id_to_type_map(elements)

    for elem in elements:
        elem_type = get_adoit_type(elem.get("type", "Capability"))
        elem_name = elem.get("name", "Unnamed")
        elem_id = elem.get("id", "")
        elem_desc = elem.get("description", "")

        # Build relationship kwargs
        rel_kwargs = {}
        relationships = elem.get("relationships", {})

        for rel_type, targets in relationships.items():
            if rel_type not in RELATIONSHIP_MAPPING:
                continue

            adoit_rel = RELATIONSHIP_MAPPING[rel_type].lower()

            if isinstance(targets, str):
                targets = [targets]

            # Resolve IDs to names
            resolved_targets = resolve_relationship_targets(targets, id_to_name)

            if not resolved_targets:
                continue

            # Group targets by their type
            targets_by_type: Dict[str, List[str]] = {}
            for target in targets:
                target_type = id_to_type.get(target, "Capability")
                if target_type not in targets_by_type:
                    targets_by_type[target_type] = []
                # Use resolved name
                resolved_name = id_to_name.get(target, target)
                targets_by_type[target_type].append(resolved_name)

            # Create kwargs for each target type
            for target_type, target_names in targets_by_type.items():
                # Convert to snake_case for kwargs
                kwarg_name = f"{adoit_rel}_{target_type.lower().replace(' ', '_')}"
                rel_kwargs[kwarg_name] = target_names

        # Add element with relationships
        gen.add_element(
            element_type=elem_type,
            name=elem_name,
            id=elem_id,
            description=elem_desc,
            **rel_kwargs
        )

    # Save the file
    if output_path:
        gen.save(output_path, use_template=False)
        return True

    return False


def transform_with_pandas(data: Dict[str, Any], output_path: str) -> bool:
    """Transform JSON to ADOIT Excel using pandas (fallback)."""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas is required. Install with: pip install pandas openpyxl", file=sys.stderr)
        return False

    elements = data.get("elements", [])
    id_to_name = build_id_to_name_map(elements)
    id_to_type = build_id_to_type_map(elements)

    # Group elements by type
    elements_by_type: Dict[str, List[Dict[str, Any]]] = {}

    for elem in elements:
        elem_type = get_adoit_type(elem.get("type", "Capability"))
        if elem_type not in elements_by_type:
            elements_by_type[elem_type] = []
        elements_by_type[elem_type].append(elem)

    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Create Overview sheet
        overview_data = {
            "ADOIT Import File": [f"Generated from: {data.get('name', 'Model')}"],
            "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "Total Elements": [len(elements)]
        }
        pd.DataFrame(overview_data).to_excel(writer, sheet_name="Overview", index=False)

        # Create sheet for each element type
        for elem_type, type_elements in elements_by_type.items():
            rows = []

            for elem in type_elements:
                row = {
                    "Name (simple)": elem.get("name", ""),
                    "ID (simple)": elem.get("id", ""),
                    "Description (simple)": elem.get("description", ""),
                }

                # Process relationships
                relationships = elem.get("relationships", {})
                for rel_type, targets in relationships.items():
                    if rel_type not in RELATIONSHIP_MAPPING:
                        continue

                    adoit_rel = RELATIONSHIP_MAPPING[rel_type]

                    if isinstance(targets, str):
                        targets = [targets]

                    # Group by target type
                    targets_by_type: Dict[str, List[str]] = {}
                    for target in targets:
                        target_type = id_to_type.get(target, elem_type)
                        if target_type not in targets_by_type:
                            targets_by_type[target_type] = []
                        resolved_name = id_to_name.get(target, target)
                        targets_by_type[target_type].append(resolved_name)

                    # Create relationship columns
                    for target_type, target_names in targets_by_type.items():
                        col_name = f"{adoit_rel} (->{target_type})"
                        row[col_name] = ";".join(target_names)

                rows.append(row)

            if rows:
                df = pd.DataFrame(rows)
                df.to_excel(writer, sheet_name=elem_type[:31], index=False)  # Excel limits sheet names to 31 chars

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Transform LLM JSON output to ADOIT Excel import format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input JSON file (use - for stdin)")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output Excel file (required)")

    args = parser.parse_args()

    if not args.output:
        print("Error: Output file path is required", file=sys.stderr)
        print("Usage: python json-to-adoit.py input.json output.xlsx", file=sys.stderr)
        sys.exit(1)

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
    if ADOIT_GENERATOR_AVAILABLE:
        success = transform_with_generator(data, args.output)
    else:
        success = transform_with_pandas(data, args.output)

    if success:
        print(f"ADOIT Excel file written to {args.output}", file=sys.stderr)
    else:
        print("Error: Failed to generate ADOIT Excel file", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
