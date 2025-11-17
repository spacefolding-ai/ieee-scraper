#!/usr/bin/env python3
"""
Enhanced pattern matching for biographies with more flexible patterns.
"""

import json
import re
from pathlib import Path

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

# Enhanced patterns - more flexible
ENHANCED_PATTERNS = {
    "Professor": [
        r'\bprofessor\b',
        r'\bprof\.\b',
        r'\bfull\s+professor\b',
        r'\bordinary\s+professor\b',
        r'\bhonor[a]?ry\s+professor\b',
        r'\bvisiting\s+professor\b',
        r'\badjunct\s+professor\b',
        r'\bclinical\s+professor\b',
        r'\bemeritus\s+professor\b',
        r'\btitular\s+professor\b'  # Spanish/Portuguese
    ],
    "Researcher": [
        r'\bresearcher\b',
        r'\bscientist\b',
        r'\bresearch\s+scientist\b',
        r'\bresearch\s+engineer\b',
        r'\bresearch\s+associate\b',
        r'\bscientific\s+collaborator\b',
        r'\bscientific\s+employee\b',
        r'\bfellow\b(?!.*research)',  # Generic fellow
        r'\bstaff\s+scientist\b',
        r'\bstaff\s+researcher\b',
        r'\bM\.S\.\s+degree.*(?:working|employed)',  # Has MS and is working
        r'\bPh\.D\.\s+(?:student|candidate)\b',  # PhD student
        r'\bdoctoral\s+(?:student|candidate|researcher)\b'
    ],
    "Senior Researcher": [
        r'\bsenior\s+(?:research|scientist)',
        r'\bprincipal\s+(?:research|scientist)',
        r'\bhead\s+of\s+research',
        r'\blead\s+(?:research|scientist)'
    ],
    "Research fellow": [
        r'\bresearch\s+fellow\b',
        r'\bpostdoc(?:toral)?\b',
        r'\bpost-doc(?:toral)?\b',
        r'\bpostdoctoral\s+(?:research|fellow)',
        r'\bmarie\s+curie\s+fellow\b'  # EU fellowship
    ],
    "Lecturer (teaching)": [
        r'\blecturer\b',
        r'\bsenior\s+lecturer\b',
        r'\bteaching\s+fellow\b',
        r'\binstructor\b',
        r'\bteacher\b'
    ],
    "Teaching Assistant": [
        r'\bteaching\s+assistant\b',
        r'\bgraduate\s+assistant\b',
        r'\bTA\b'
    ]
}

def extract_author_type_enhanced(biography: str) -> str:
    """Enhanced extraction with more flexible patterns."""
    if not biography:
        return None
    
    for author_type, patterns in ENHANCED_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, biography, re.IGNORECASE):
                return author_type
    
    return None

def main():
    print("="*80)
    print("ENHANCED PATTERN MATCHING FOR BIOGRAPHIES")
    print("="*80)
    print()
    
    # Load authors without type
    with open(RESULTS_DIR / "authors_without_type.json", 'r') as f:
        authors_without_type = json.load(f)
    
    # Filter those with biographies
    with_bio = [a for a in authors_without_type if a['biography']]
    
    print(f"Checking {len(with_bio)} authors with biographies...")
    print()
    
    found_types = {}
    
    for author in with_bio:
        author_type = extract_author_type_enhanced(author['biography'])
        if author_type:
            found_types[author['author_id']] = {
                'name': author['name'],
                'author_type': author_type,
                'country': author['country']
            }
    
    print(f"✅ Found {len(found_types)} additional author types from biographies!")
    print()
    
    if found_types:
        print("Examples:")
        print("-"*80)
        for i, (author_id, data) in enumerate(list(found_types.items())[:10], 1):
            print(f"{i}. {data['name']}: {data['author_type']}")
        print()
    
    # Save results
    output = RESULTS_DIR / "enhanced_pattern_results.json"
    with open(output, 'w') as f:
        json.dump(found_types, f, indent=2)
    
    print(f"Results saved to: {output}")
    print(f"\nPotential additional coverage: {len(found_types)}/{len(with_bio)} ({len(found_types)/len(with_bio)*100:.1f}%)")

if __name__ == "__main__":
    main()

