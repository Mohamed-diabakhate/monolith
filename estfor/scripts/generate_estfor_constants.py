#!/usr/bin/env python3
"""
Generate Python constants and enums from EstFor TypeScript definitions.
This script parses the TypeScript files and creates Python equivalents.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

def parse_typescript_enum(content: str) -> Dict[str, List[Tuple[str, int]]]:
    """Parse TypeScript enum definitions."""
    enums = {}
    
    # Find all enum definitions
    enum_pattern = r'export\s+enum\s+(\w+)\s*\{([^}]+)\}'
    matches = re.findall(enum_pattern, content, re.DOTALL)
    
    for enum_name, enum_body in matches:
        items = []
        current_value = 0
        
        # Parse enum items
        lines = enum_body.strip().split('\n')
        for line in lines:
            line = line.strip().rstrip(',')
            if not line or line.startswith('//'):
                continue
                
            # Remove inline comments
            if '//' in line:
                line = line.split('//')[0].strip()
            
            # Handle explicit values
            if '=' in line:
                parts = line.split('=')
                name = parts[0].strip()
                value = parts[1].strip()
                try:
                    current_value = int(value)
                except ValueError:
                    # Skip non-numeric values for now
                    continue
            else:
                name = line.strip().rstrip(',')
            
            if name:
                items.append((name, current_value))
                current_value += 1
        
        enums[enum_name] = items
    
    return enums

def parse_typescript_constants(content: str) -> Dict[str, any]:
    """Parse TypeScript constant definitions."""
    constants = {}
    
    # Parse simple numeric constants
    const_pattern = r'export\s+const\s+(\w+)\s*=\s*([^;\n]+)'
    matches = re.findall(const_pattern, content)
    
    # First pass: collect simple numeric values
    for name, value in matches:
        value = value.strip()
        
        # Skip complex expressions and imports
        if 'import' in value or '{' in value or '[' in value:
            continue
            
        # Handle numeric values
        try:
            if value.isdigit():
                constants[name] = int(value)
            elif value.startswith('0x'):
                constants[name] = int(value, 16)
        except ValueError:
            pass
    
    # Second pass: resolve references and expressions
    for name, value in matches:
        value = value.strip()
        
        # Skip if already processed or complex
        if name in constants or 'import' in value or '{' in value or '[' in value:
            continue
        
        # Handle variable references (e.g., BRONZE_HELMET = HEAD_BASE)
        if value in constants:
            constants[name] = constants[value]
        # Handle simple addition expressions
        elif ' + ' in value:
            parts = value.split(' + ')
            if len(parts) == 2:
                base = parts[0].strip()
                offset = parts[1].strip()
                if base in constants and offset.isdigit():
                    constants[name] = constants[base] + int(offset)
        # Handle simple subtraction expressions  
        elif ' - ' in value:
            parts = value.split(' - ')
            if len(parts) == 2:
                base = parts[0].strip()
                offset = parts[1].strip()
                if base in constants and offset.isdigit():
                    constants[name] = constants[base] - int(offset)
    
    return constants

def parse_class_definition(content: str) -> Dict[str, List[Tuple[str, str, any]]]:
    """Parse TypeScript class definitions."""
    classes = {}
    
    # Find class definitions
    class_pattern = r'export\s+class\s+(\w+)\s*\{([^}]+)\}'
    matches = re.findall(class_pattern, content, re.DOTALL)
    
    for class_name, class_body in matches:
        fields = []
        
        # Parse class fields
        field_pattern = r'(\w+):\s*(\w+(?:\[\])?)\s*=\s*([^;\n]+)'
        field_matches = re.findall(field_pattern, class_body)
        
        for field_name, field_type, default_value in field_matches:
            default_value = default_value.strip()
            
            # Convert TypeScript types to Python types
            if field_type == 'u16' or field_type == 'number':
                py_type = 'int'
                default = 0
            elif field_type == 'string':
                py_type = 'str'
                default = '""'
            elif field_type == 'boolean':
                py_type = 'bool'
                default = 'False'
            else:
                py_type = 'Any'
                default = 'None'
            
            try:
                if default_value.isdigit():
                    default = int(default_value)
            except:
                pass
                
            fields.append((field_name, py_type, default))
        
        classes[class_name] = fields
    
    return classes

def generate_python_enum(enum_name: str, items: List[Tuple[str, int]]) -> str:
    """Generate Python enum code."""
    code = f"class {enum_name}(IntEnum):\n"
    code += '    """Auto-generated from TypeScript definitions."""\n'
    
    for name, value in items:
        code += f"    {name} = {value}\n"
    
    return code

def generate_python_class(class_name: str, fields: List[Tuple[str, str, any]]) -> str:
    """Generate Python dataclass code."""
    code = f"@dataclass\n"
    code += f"class {class_name}:\n"
    code += '    """Auto-generated from TypeScript definitions."""\n'
    
    for field_name, field_type, default in fields:
        code += f"    {field_name}: {field_type} = {default}\n"
    
    return code

def generate_python_constants(constants: Dict[str, any]) -> str:
    """Generate Python constant definitions."""
    code = "# Game Constants\n"
    
    # Group constants by prefix
    grouped = {}
    for name, value in sorted(constants.items()):
        if '_' in name:
            prefix = name.split('_')[0]
            if prefix not in grouped:
                grouped[prefix] = []
            grouped[prefix].append((name, value))
        else:
            if 'MISC' not in grouped:
                grouped['MISC'] = []
            grouped['MISC'].append((name, value))
    
    # Generate grouped constants
    for group, items in sorted(grouped.items()):
        if group != 'MISC':
            code += f"\n# {group.title()} Items\n"
        else:
            code += f"\n# Miscellaneous\n"
            
        for name, value in items:
            code += f"{name} = {value}\n"
    
    return code

def main():
    """Main function to generate Python constants from TypeScript."""
    # Paths
    ts_base_path = Path("/Users/mo/Library/Mobile Documents/com~apple~CloudDocs/cloud_agent/puppy/monolith/estfor/estfor-definitions/src")
    output_path = Path("/Users/mo/Library/Mobile Documents/com~apple~CloudDocs/cloud_agent/puppy/monolith/estfor/app/game_constants.py")
    
    # Read TypeScript files
    types_content = (ts_base_path / "types.ts").read_text()
    constants_content = (ts_base_path / "constants.ts").read_text()
    
    # Parse TypeScript definitions
    print("Parsing TypeScript enums...")
    enums = parse_typescript_enum(types_content)
    
    print("Parsing TypeScript constants...")
    constants = parse_typescript_constants(constants_content)
    
    print("Parsing TypeScript classes...")
    classes = parse_class_definition(types_content)
    
    # Generate Python code
    python_code = '''"""
EstFor Kingdom Game Constants and Enums
Auto-generated from TypeScript definitions in estfor-definitions/

DO NOT EDIT THIS FILE DIRECTLY!
Run scripts/generate_estfor_constants.py to regenerate.
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Any

'''
    
    # Add enums
    python_code += "# Game Enums\n\n"
    for enum_name, items in enums.items():
        python_code += generate_python_enum(enum_name, items)
        python_code += "\n\n"
    
    # Add classes
    if classes:
        python_code += "# Game Classes\n\n"
        for class_name, fields in classes.items():
            python_code += generate_python_class(class_name, fields)
            python_code += "\n\n"
    
    # Add constants
    python_code += generate_python_constants(constants)
    
    # Write to file
    output_path.write_text(python_code)
    print(f"Generated Python constants at: {output_path}")
    
    # Print summary
    print(f"\nGenerated:")
    print(f"  - {len(enums)} enums")
    print(f"  - {len(classes)} classes")
    print(f"  - {len(constants)} constants")
    
    return output_path

if __name__ == "__main__":
    main()