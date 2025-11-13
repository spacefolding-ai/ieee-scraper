#!/usr/bin/env python3
"""
Script to add author_type property to all authors in _simple.json and _simple.csv files.
Extracts the author type from the biography field.
"""

import json
import csv
import os
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict

# Increase CSV field size limit to handle large fields
csv.field_size_limit(sys.maxsize)

# Directory containing the files
RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

# Author types to search for (in order of priority)
AUTHOR_TYPES = [
    "Professor",
    "Associate Professor",
    "Assistant Professor",
    "Research fellow",
    "Researcher",
    "Senior Researcher",
    "Project Manager",
    "Research group manager",
    "Principal investigator",
    "Senior Lecturer",
    "Lecturer (teaching)",
    "Assistant Lecturer",
    "Teaching Assistant",
    "Demonstrator"
]

# Patterns for each author type (case-insensitive)
AUTHOR_TYPE_PATTERNS = {
    "Professor": [
        r'\bprofessor\b(?!\s+(?:associate|assistant))',
        r'\bprof\.\b(?!\s+(?:assoc|asst))',
        r'\bfull\s+professor\b',
        r'\bordinary\s+professor\b'
    ],
    "Associate Professor": [
        r'\bassociate\s+professor\b',
        r'\bassoc\.\s+prof\.\b',
        r'\bassoc\s+prof\b'
    ],
    "Assistant Professor": [
        r'\bassistant\s+professor\b',
        r'\basst\.\s+prof\.\b',
        r'\basst\s+prof\b'
    ],
    "Senior Lecturer": [
        r'\bsenior\s+lecturer\b',
        r'\bsr\.\s+lecturer\b'
    ],
    "Lecturer (teaching)": [
        r'\blecturer\b(?!\s+(?:senior|assistant))',
        r'\bteaching\s+fellow\b'
    ],
    "Assistant Lecturer": [
        r'\bassistant\s+lecturer\b',
        r'\basst\.\s+lecturer\b'
    ],
    "Principal investigator": [
        r'\bprincipal\s+investigator\b',
        r'\bPI\b',
        r'\bprincipal\s+researcher\b'
    ],
    "Research group manager": [
        r'\bresearch\s+group\s+(?:manager|leader|head)\b',
        r'\bgroup\s+leader\b',
        r'\bhead\s+of\s+(?:research\s+)?group\b'
    ],
    "Senior Researcher": [
        r'\bsenior\s+researcher\b',
        r'\bsenior\s+research\s+(?:scientist|fellow|associate)\b',
        r'\bsr\.\s+researcher\b'
    ],
    "Research fellow": [
        r'\bresearch\s+fellow\b',
        r'\bpostdoctoral\s+(?:research\s+)?fellow\b',
        r'\bpostdoc(?:toral)?\b'
    ],
    "Researcher": [
        r'\bresearcher\b(?!\s+(?:senior))',
        r'\bresearch\s+(?:scientist|associate)\b(?!\s+(?:senior))'
    ],
    "Project Manager": [
        r'\bproject\s+manager\b',
        r'\bprogram\s+manager\b'
    ],
    "Teaching Assistant": [
        r'\bteaching\s+assistant\b',
        r'\bTA\b'
    ],
    "Demonstrator": [
        r'\bdemonstrator\b'
    ]
}


def extract_author_type(biography: Optional[str]) -> Optional[str]:
    """
    Extract author type from biography text.
    Returns the first matching author type or None if no match found.
    """
    if not biography or not isinstance(biography, str):
        return None
    
    # Search for each author type in priority order
    for author_type in AUTHOR_TYPES:
        patterns = AUTHOR_TYPE_PATTERNS.get(author_type, [])
        for pattern in patterns:
            if re.search(pattern, biography, re.IGNORECASE):
                return author_type
    
    return None


def process_json_file(json_path: Path) -> int:
    """
    Process a JSON file and add author_type to each author.
    Returns the number of authors updated.
    """
    print(f"Processing {json_path.name}...")
    
    try:
        # Read the JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            authors = json.load(f)
        
        if not isinstance(authors, list):
            print(f"  ERROR: Expected list of authors, got {type(authors)}")
            return 0
        
        updated_count = 0
        with_type_count = 0
        
        # Process each author
        for author in authors:
            if not isinstance(author, dict):
                continue
            
            # Extract author type from biography
            author_type = extract_author_type(author.get('biography'))
            author['author_type'] = author_type
            
            if author_type:
                with_type_count += 1
            
            updated_count += 1
        
        # Write back to JSON file
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(authors, f, indent=2, ensure_ascii=False)
        
        print(f"  Updated {updated_count} authors ({with_type_count} with author_type)")
        return updated_count
        
    except Exception as e:
        print(f"  ERROR processing {json_path.name}: {e}")
        return 0


def process_csv_file(csv_path: Path, json_path: Path) -> int:
    """
    Process a CSV file and add author_type column.
    Uses the corresponding JSON file as the source of truth.
    Returns the number of authors updated.
    """
    print(f"Processing {csv_path.name}...")
    
    try:
        # Read the corresponding JSON file to get author_type mapping
        with open(json_path, 'r', encoding='utf-8') as f:
            authors = json.load(f)
        
        # Create a mapping from author_id to author_type
        author_type_map = {
            author['author_id']: author.get('author_type')
            for author in authors
            if isinstance(author, dict)
        }
        
        # Read CSV file
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)
        
        # Add author_type to fieldnames if not present
        if 'author_type' not in fieldnames:
            fieldnames = list(fieldnames)
            # Insert author_type after biography
            if 'biography' in fieldnames:
                bio_index = fieldnames.index('biography')
                fieldnames.insert(bio_index + 1, 'author_type')
            else:
                fieldnames.append('author_type')
        
        # Update each row with author_type
        updated_count = 0
        for row in rows:
            author_id = row.get('author_id')
            if author_id in author_type_map:
                row['author_type'] = author_type_map[author_id] or ''
                updated_count += 1
        
        # Write back to CSV file
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"  Updated {updated_count} authors in CSV")
        return updated_count
        
    except Exception as e:
        print(f"  ERROR processing {csv_path.name}: {e}")
        return 0


def main():
    """Main function to process all _simple.json and _simple.csv files."""
    
    if not RESULTS_DIR.exists():
        print(f"ERROR: Directory {RESULTS_DIR} does not exist")
        return
    
    # Find all _simple.json files
    json_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    if not json_files:
        print(f"No _simple.json files found in {RESULTS_DIR}")
        return
    
    print(f"Found {len(json_files)} JSON files to process\n")
    
    total_json_updated = 0
    total_csv_updated = 0
    
    # Process each JSON file and corresponding CSV file
    for json_path in json_files:
        # Process JSON file
        json_updated = process_json_file(json_path)
        total_json_updated += json_updated
        
        # Process corresponding CSV file
        csv_path = json_path.with_suffix('.csv')
        if csv_path.exists():
            csv_updated = process_csv_file(csv_path, json_path)
            total_csv_updated += csv_updated
        else:
            print(f"  WARNING: No corresponding CSV file found for {json_path.name}")
        
        print()  # Empty line for readability
    
    print("\n" + "="*60)
    print(f"SUMMARY:")
    print(f"  Total JSON files processed: {len(json_files)}")
    print(f"  Total authors updated in JSON: {total_json_updated}")
    print(f"  Total authors updated in CSV: {total_csv_updated}")
    print("="*60)


if __name__ == "__main__":
    main()

