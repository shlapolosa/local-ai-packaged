#!/usr/bin/env python3
"""
json-to-markdown.py - Transform LLM JSON output to structured Markdown documents

This script takes JSON input describing document structure and generates
properly formatted Markdown (BRD, PRD, or general documents).

Usage:
    python json-to-markdown.py input.json output.md
    cat input.json | python json-to-markdown.py - output.md
    echo '{"title": "Doc", ...}' | python json-to-markdown.py

JSON Schema:
{
    "type": "brd|prd|general",
    "title": "Document Title",
    "version": "1.0.0",
    "date": "2024-01-15",
    "sections": [
        {
            "heading": "Section Title",
            "level": 2,
            "content": "Paragraph text...",
            "subsections": [...],
            "list": ["item1", "item2"],
            "table": {
                "headers": ["Col1", "Col2"],
                "rows": [["val1", "val2"]]
            }
        }
    ]
}
"""

import json
import sys
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime


def generate_table(table: Dict[str, Any]) -> str:
    """Generate markdown table from headers and rows."""
    headers = table.get("headers", [])
    rows = table.get("rows", [])

    if not headers:
        return ""

    lines = []

    # Header row
    lines.append("| " + " | ".join(headers) + " |")

    # Separator row
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    # Data rows
    for row in rows:
        # Ensure row has same number of columns as headers
        row_data = list(row) + [""] * (len(headers) - len(row))
        lines.append("| " + " | ".join(str(cell) for cell in row_data[:len(headers)]) + " |")

    return "\n".join(lines)


def generate_list(items: List[Any], ordered: bool = False, level: int = 0) -> str:
    """Generate markdown list (ordered or unordered)."""
    lines = []
    indent = "  " * level

    for i, item in enumerate(items):
        if isinstance(item, dict):
            # Nested item with potential sub-list
            text = item.get("text", "")
            prefix = f"{i+1}." if ordered else "-"
            lines.append(f"{indent}{prefix} {text}")

            if item.get("sublist"):
                lines.append(generate_list(item["sublist"], item.get("ordered", False), level + 1))
        elif isinstance(item, list):
            # Nested list
            lines.append(generate_list(item, ordered, level + 1))
        else:
            prefix = f"{i+1}." if ordered else "-"
            lines.append(f"{indent}{prefix} {item}")

    return "\n".join(lines)


def generate_section(section: Dict[str, Any], parent_level: int = 1) -> str:
    """Generate markdown for a section."""
    lines = []

    # Heading
    level = section.get("level", parent_level + 1)
    heading = section.get("heading", section.get("title", ""))
    if heading:
        lines.append(f"{'#' * level} {heading}")
        lines.append("")

    # Content (can be string or list of paragraphs)
    content = section.get("content", "")
    if isinstance(content, str) and content:
        lines.append(content)
        lines.append("")
    elif isinstance(content, list):
        for para in content:
            lines.append(para)
            lines.append("")

    # List
    if section.get("list"):
        ordered = section.get("ordered", False)
        lines.append(generate_list(section["list"], ordered))
        lines.append("")

    # Bullet points (alias for list)
    if section.get("bullets"):
        lines.append(generate_list(section["bullets"], False))
        lines.append("")

    # Numbered items (alias for ordered list)
    if section.get("numbered"):
        lines.append(generate_list(section["numbered"], True))
        lines.append("")

    # Table
    if section.get("table"):
        lines.append(generate_table(section["table"]))
        lines.append("")

    # Code block
    if section.get("code"):
        lang = section.get("language", "")
        lines.append(f"```{lang}")
        lines.append(section["code"])
        lines.append("```")
        lines.append("")

    # Subsections
    for subsection in section.get("subsections", []):
        lines.append(generate_section(subsection, level))

    return "\n".join(lines)


def generate_brd(data: Dict[str, Any]) -> str:
    """Generate BRD-specific markdown structure."""
    lines = []

    title = data.get("title", "Business Requirements Document")
    lines.append(f"# {title}")
    lines.append("")

    # Metadata
    if data.get("version") or data.get("date") or data.get("author"):
        lines.append(f"**Version:** {data.get('version', '1.0.0')}")
        lines.append(f"**Date:** {data.get('date', datetime.now().strftime('%Y-%m-%d'))}")
        if data.get("author"):
            lines.append(f"**Author:** {data['author']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Standard BRD sections
    sections = data.get("sections", [])

    # If sections provided, use them
    if sections:
        for section in sections:
            lines.append(generate_section(section, 1))
    else:
        # Use structured data for BRD
        if data.get("executiveSummary"):
            lines.append("## 1. Executive Summary")
            lines.append("")
            lines.append(data["executiveSummary"])
            lines.append("")

        if data.get("problemStatement"):
            lines.append("## 2. Problem Statement")
            lines.append("")
            ps = data["problemStatement"]
            if isinstance(ps, dict):
                if ps.get("currentState"):
                    lines.append("### Current State")
                    lines.append(ps["currentState"])
                    lines.append("")
                if ps.get("painPoints"):
                    lines.append("### Pain Points")
                    lines.append(generate_list(ps["painPoints"]))
                    lines.append("")
                if ps.get("impact"):
                    lines.append("### Impact")
                    lines.append(ps["impact"])
                    lines.append("")
            else:
                lines.append(ps)
                lines.append("")

        if data.get("businessObjectives"):
            lines.append("## 3. Business Objectives")
            lines.append("")
            objectives = data["businessObjectives"]
            if isinstance(objectives, list) and objectives and isinstance(objectives[0], dict):
                # Table format
                lines.append("| Objective | Description | Success Metric |")
                lines.append("|-----------|-------------|----------------|")
                for obj in objectives:
                    lines.append(f"| {obj.get('id', '')} | {obj.get('description', '')} | {obj.get('metric', '')} |")
            else:
                lines.append(generate_list(objectives))
            lines.append("")

        if data.get("stakeholders"):
            lines.append("## 4. Stakeholders")
            lines.append("")
            stakeholders = data["stakeholders"]
            if isinstance(stakeholders, list) and stakeholders and isinstance(stakeholders[0], dict):
                lines.append("| Role | Responsibilities | Concerns |")
                lines.append("|------|-----------------|----------|")
                for s in stakeholders:
                    lines.append(f"| {s.get('role', '')} | {s.get('responsibilities', '')} | {s.get('concerns', '')} |")
            else:
                lines.append(generate_list(stakeholders))
            lines.append("")

        if data.get("scope"):
            lines.append("## 5. Scope")
            lines.append("")
            scope = data["scope"]
            if isinstance(scope, dict):
                if scope.get("inScope"):
                    lines.append("### In Scope")
                    lines.append(generate_list(scope["inScope"]))
                    lines.append("")
                if scope.get("outOfScope"):
                    lines.append("### Out of Scope")
                    lines.append(generate_list(scope["outOfScope"]))
                    lines.append("")
            else:
                lines.append(scope)
                lines.append("")

        if data.get("constraints") or data.get("assumptions"):
            lines.append("## 6. Constraints & Assumptions")
            lines.append("")
            if data.get("constraints"):
                lines.append("### Constraints")
                lines.append(generate_list(data["constraints"]))
                lines.append("")
            if data.get("assumptions"):
                lines.append("### Assumptions")
                lines.append(generate_list(data["assumptions"]))
                lines.append("")

        if data.get("successCriteria"):
            lines.append("## 7. Success Criteria")
            lines.append("")
            lines.append(generate_list(data["successCriteria"]))
            lines.append("")

    return "\n".join(lines)


def generate_prd(data: Dict[str, Any]) -> str:
    """Generate PRD-specific markdown structure."""
    lines = []

    title = data.get("title", "Product Requirements Document")
    lines.append(f"# {title}")
    lines.append("")

    # Metadata
    if data.get("version") or data.get("date"):
        lines.append(f"**Version:** {data.get('version', '1.0.0')}")
        lines.append(f"**Date:** {data.get('date', datetime.now().strftime('%Y-%m-%d'))}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Standard PRD sections
    sections = data.get("sections", [])

    if sections:
        for section in sections:
            lines.append(generate_section(section, 1))
    else:
        # Use structured data for PRD
        if data.get("overview"):
            lines.append("## 1. Overview")
            lines.append("")
            overview = data["overview"]
            if isinstance(overview, dict):
                if overview.get("problemStatement"):
                    lines.append("### Problem Statement")
                    lines.append(overview["problemStatement"])
                    lines.append("")
                if overview.get("targetUsers"):
                    lines.append("### Target Users")
                    lines.append(generate_list(overview["targetUsers"]))
                    lines.append("")
                if overview.get("successMetrics"):
                    lines.append("### Success Metrics")
                    lines.append(generate_list(overview["successMetrics"]))
                    lines.append("")
            else:
                lines.append(overview)
                lines.append("")

        if data.get("features"):
            lines.append("## 2. Features")
            lines.append("")
            for feature in data["features"]:
                lines.append(f"### {feature.get('name', 'Feature')}")
                if feature.get("description"):
                    lines.append(f"**Description:** {feature['description']}")
                    lines.append("")
                if feature.get("inputs"):
                    lines.append("**Inputs:**")
                    lines.append(generate_list(feature["inputs"]))
                    lines.append("")
                if feature.get("outputs"):
                    lines.append("**Outputs:**")
                    lines.append(generate_list(feature["outputs"]))
                    lines.append("")
                if feature.get("behavior"):
                    lines.append("**Behavior:**")
                    lines.append(feature["behavior"])
                    lines.append("")

        if data.get("architecture"):
            lines.append("## 3. Architecture")
            lines.append("")
            arch = data["architecture"]
            if isinstance(arch, dict):
                if arch.get("components"):
                    lines.append("### System Components")
                    lines.append(generate_list(arch["components"]))
                    lines.append("")
                if arch.get("dataModels"):
                    lines.append("### Data Models")
                    lines.append(generate_list(arch["dataModels"]))
                    lines.append("")
                if arch.get("techStack"):
                    lines.append("### Technology Stack")
                    lines.append(generate_list(arch["techStack"]))
                    lines.append("")
            else:
                lines.append(arch)
                lines.append("")

        if data.get("roadmap"):
            lines.append("## 4. Implementation Roadmap")
            lines.append("")
            for phase in data["roadmap"]:
                lines.append(f"### Phase {phase.get('number', '?')}: {phase.get('name', 'Phase')}")
                if phase.get("goal"):
                    lines.append(f"**Goal:** {phase['goal']}")
                    lines.append("")
                if phase.get("tasks"):
                    lines.append("**Tasks:**")
                    lines.append(generate_list(phase["tasks"]))
                    lines.append("")
                if phase.get("deliverables"):
                    lines.append("**Delivers:** {phase['deliverables']}")
                    lines.append("")

    return "\n".join(lines)


def generate_general(data: Dict[str, Any]) -> str:
    """Generate general markdown document."""
    lines = []

    title = data.get("title", "Document")
    lines.append(f"# {title}")
    lines.append("")

    if data.get("description"):
        lines.append(data["description"])
        lines.append("")

    for section in data.get("sections", []):
        lines.append(generate_section(section, 1))

    return "\n".join(lines)


def transform_to_markdown(data: Dict[str, Any]) -> str:
    """Transform JSON to Markdown based on document type."""
    doc_type = data.get("type", "general").lower()

    if doc_type == "brd":
        return generate_brd(data)
    elif doc_type == "prd":
        return generate_prd(data)
    else:
        return generate_general(data)


def main():
    parser = argparse.ArgumentParser(
        description="Transform LLM JSON output to Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input JSON file (use - for stdin)")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output Markdown file (prints to stdout if not specified)")

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
    md_output = transform_to_markdown(data)

    # Output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(md_output)
        print(f"Markdown written to {args.output}", file=sys.stderr)
    else:
        print(md_output)


if __name__ == "__main__":
    main()
