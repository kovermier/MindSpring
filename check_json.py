import json
from collections import defaultdict
from typing import Any, Dict, List, Set
import os

def analyze_json_structure(file_path: str) -> Dict[str, Any]:
    """
    Analyzes the structure of a JSON file and returns detailed information about it.
    
    Args:
        file_path: Path to the JSON file to analyze
        
    Returns:
        Dictionary containing structure information including:
        - type: The top-level type (list or dict)
        - size: File size in MB
        - count: Number of top-level elements if list
        - keys: Common keys if dictionary
        - sample: Sample of first few elements
    """
    try:
        # Get file size
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        structure = {
            'file_name': os.path.basename(file_path),
            'file_size_mb': round(file_size, 2),
            'top_level_type': type(data).__name__
        }
        
        # Analyze based on top-level type
        if isinstance(data, list):
            structure.update({
                'element_count': len(data),
                'first_element_type': type(data[0]).__name__ if data else None,
                'sample': data[:3] if len(data) > 0 else [],
            })
            
            # If elements are dicts, get common keys
            if data and isinstance(data[0], dict):
                common_keys = set(data[0].keys())
                for item in data[1:10]:  # Check first 10 items
                    if isinstance(item, dict):
                        common_keys &= set(item.keys())
                structure['common_keys'] = list(common_keys)
                
        elif isinstance(data, dict):
            structure.update({
                'top_level_keys': list(data.keys()),
                'sample': {k: data[k] for k in list(data.keys())[:3]}
            })
            
        return structure
        
    except json.JSONDecodeError as e:
        return {
            'file_name': os.path.basename(file_path),
            'error': f'Invalid JSON: {str(e)}'
        }
    except Exception as e:
        return {
            'file_name': os.path.basename(file_path),
            'error': f'Analysis failed: {str(e)}'
        }

def pretty_print_structure(structure: Dict[str, Any]) -> None:
    """
    Prints the JSON structure analysis in a readable format.
    """
    print(f"\n=== {structure['file_name']} Analysis ===")
    print(f"File Size: {structure['file_size_mb']} MB")
    print(f"Top-level Type: {structure['top_level_type']}")
    
    if 'error' in structure:
        print(f"Error: {structure['error']}")
        return
        
    if structure['top_level_type'] == 'list':
        print(f"Number of Elements: {structure['element_count']}")
        print(f"First Element Type: {structure['first_element_type']}")
        if 'common_keys' in structure:
            print("\nCommon Keys in Dictionary Elements:")
            for key in structure['common_keys']:
                print(f"  - {key}")
    else:
        print("\nTop-level Keys:")
        for key in structure['top_level_keys']:
            print(f"  - {key}")
    
    print("\nSample Data:")
    print(json.dumps(structure['sample'], indent=2)[:500] + "...")

def main():
    files = [os.path.abspath('./conversations.json'), os.path.abspath('./claude_conversations.json')]
    
    for file_path in files:
        if not os.path.exists(file_path):
            print(f"\nError: File not found: {file_path}")
            continue
            
        structure = analyze_json_structure(file_path)
        pretty_print_structure(structure)

if __name__ == "__main__":
    main()
