#!/usr/bin/env python3
"""
ADOIT Import File Validator

Validates Excel files before importing to ADOIT to catch common issues:
- Duplicate element names
- Invalid relationship references
- Missing required columns
- ArchiMate compliance issues
"""

import pandas as pd
import sys
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import re

class ADOITValidator:
    """Validates ADOIT import Excel files"""
    
    # Valid ArchiMate element types
    VALID_ELEMENT_TYPES = {
        "Application Collaboration", "Application Component", "Application Event",
        "Application Function", "Application Interaction", "Application Interface",
        "Application Process", "Application Service", "Artifact", "Assessment",
        "Business Actor", "Business Collaboration", "Business Event", "Business Function",
        "Business Interaction", "Business Interface", "Business Object", "Business Process",
        "Business Role", "Business Service", "Capability", "Communication Network",
        "Constraint", "Contract", "Course of Action", "Data Object", "Deliverable",
        "Device", "Distribution Network", "Driver", "Equipment", "Facility", "Gap",
        "Goal", "Grouping", "Implementation Event", "Junction", "Location", "Material",
        "Meaning", "Node", "Outcome", "Path", "Plateau", "Principle", "Product",
        "Representation", "Requirement", "Resource", "Stakeholder", "System Software",
        "Technology Collaboration", "Technology Event", "Technology Function",
        "Technology Interaction", "Technology Interface", "Technology Process",
        "Technology Service", "Value", "Value Stream", "Work Package"
    }
    
    VALID_RELATIONSHIPS = {
        "Composition", "Aggregation", "Assignment", "Realization", "Serving",
        "Access", "Influence", "Triggering", "Flow", "Specialization", "Association"
    }
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.all_element_names: Dict[str, Set[str]] = defaultdict(set)
        
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validations.
        Returns (is_valid, errors, warnings)
        """
        try:
            xlsx = pd.ExcelFile(self.filepath)
        except Exception as e:
            self.errors.append(f"Cannot read file: {e}")
            return False, self.errors, self.warnings
        
        # First pass: collect all element names
        for sheet_name in xlsx.sheet_names:
            if sheet_name in ['Overview', 'Instructions']:
                continue
            
            df = pd.read_excel(xlsx, sheet_name=sheet_name)
            if 'Name (simple)' in df.columns:
                names = df['Name (simple)'].dropna().tolist()
                for name in names:
                    self.all_element_names[sheet_name].add(str(name))
        
        # Second pass: validate each sheet
        for sheet_name in xlsx.sheet_names:
            if sheet_name in ['Overview', 'Instructions']:
                continue
                
            self._validate_sheet(xlsx, sheet_name)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_sheet(self, xlsx: pd.ExcelFile, sheet_name: str):
        """Validate a single sheet"""
        
        # Check if valid element type
        if sheet_name not in self.VALID_ELEMENT_TYPES:
            self.warnings.append(f"Sheet '{sheet_name}' is not a standard ArchiMate element type")
            return
        
        df = pd.read_excel(xlsx, sheet_name=sheet_name)
        
        if df.empty:
            return
        
        # Check required columns
        if 'Name (simple)' not in df.columns:
            self.errors.append(f"Sheet '{sheet_name}': Missing required column 'Name (simple)'")
            return
        
        # Check for duplicates within sheet
        names = df['Name (simple)'].dropna()
        duplicates = names[names.duplicated()].unique()
        if len(duplicates) > 0:
            for dup in duplicates:
                self.errors.append(f"Sheet '{sheet_name}': Duplicate element name '{dup}'")
        
        # Validate relationship columns
        for col in df.columns:
            self._validate_relationship_column(sheet_name, col, df)
    
    def _validate_relationship_column(self, sheet_name: str, col_name: str, df: pd.DataFrame):
        """Validate a relationship column"""
        
        # Check if this is a relationship column
        rel_match = re.match(r'(\w+(?:\s+\w+)?)\s+\((->|<-)(\w+(?:\s+\w+)?)\)', col_name)
        if not rel_match:
            return
        
        rel_type = rel_match.group(1)
        direction = rel_match.group(2)
        target_type = rel_match.group(3)
        
        # Validate relationship type
        if rel_type not in self.VALID_RELATIONSHIPS:
            self.warnings.append(
                f"Sheet '{sheet_name}', Column '{col_name}': "
                f"'{rel_type}' is not a standard ArchiMate relationship"
            )
        
        # Validate target type
        if target_type not in self.VALID_ELEMENT_TYPES:
            self.warnings.append(
                f"Sheet '{sheet_name}', Column '{col_name}': "
                f"'{target_type}' is not a standard ArchiMate element type"
            )
        
        # Check relationship targets exist
        for idx, row in df.iterrows():
            cell_value = row.get(col_name)
            if pd.isna(cell_value):
                continue
            
            # Targets can be semicolon-separated
            targets = [t.strip() for t in str(cell_value).split(';')]
            for target in targets:
                if target and target not in self.all_element_names.get(target_type, set()):
                    # This could be a warning - target might exist in repository
                    self.warnings.append(
                        f"Sheet '{sheet_name}', Row {idx+2}: "
                        f"Relationship target '{target}' not found in import file"
                    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_import.py <excel_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"Validating: {filepath}")
    print("=" * 60)
    
    validator = ADOITValidator(filepath)
    is_valid, errors, warnings = validator.validate()
    
    if errors:
        print("\n❌ ERRORS (must fix before import):")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print("\n⚠️  WARNINGS (review recommended):")
        for warning in warnings[:20]:  # Limit output
            print(f"  • {warning}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more warnings")
    
    print("\n" + "=" * 60)
    if is_valid:
        print("✅ Validation PASSED - file is ready for import")
    else:
        print("❌ Validation FAILED - fix errors before importing")
    
    # Summary
    print(f"\nSummary:")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
