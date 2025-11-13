#!/usr/bin/env python3
"""
Create simplified JSON files with arrays of authors containing only specified fields.
Output files: european_authors_<country>_simple.json
"""

import json
from pathlib import Path
from datetime import datetime

# Fields to extract (in order)
FIELDS_TO_EXTRACT = [
    'author_id',
    'first_name',
    'last_name',
    'name',
    'ieee_profile_url',
    'email',
    'email_source',
    'email_citations',
    'primary_affiliation',
    'all_affiliations',
    'biography',
    'first_author_count',  # Assuming this was meant instead of "first_author"
    'all_publications',
    'publications_as_first_author',
    'publications_as_non_first_author'
]

def extract_author_fields(author_data):
    """Extract only the specified fields from author data"""
    simplified_author = {}
    
    for field in FIELDS_TO_EXTRACT:
        # Get the value, defaulting to appropriate empty value if missing
        if field in author_data:
            simplified_author[field] = author_data[field]
        else:
            # Provide sensible defaults
            if field.endswith('_count') or field.endswith('_pubs'):
                simplified_author[field] = 0
            elif field in ['email', 'name', 'ieee_profile_url', 'email_source', 
                          'primary_affiliation', 'biography', 'author_id',
                          'first_name', 'last_name']:
                simplified_author[field] = author_data.get(field)
            else:  # Arrays
                simplified_author[field] = []
    
    return simplified_author

def create_simplified_file(input_path):
    """Create a simplified version of a country file"""
    print(f"\n📄 Processing: {input_path.name}")
    
    # Load file
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract authors into array
    simplified_authors = []
    for author_id, author_data in data['authors'].items():
        simplified_author = extract_author_fields(author_data)
        simplified_authors.append(simplified_author)
    
    # Create output structure (just an array)
    output_data = {
        'metadata': {
            'source_file': input_path.name,
            'created_date': datetime.now().isoformat(),
            'total_authors': len(simplified_authors),
            'fields': FIELDS_TO_EXTRACT,
            'description': 'Simplified author data with selected fields only'
        },
        'authors': simplified_authors
    }
    
    # Create output filename
    base_name = input_path.stem  # e.g., "european_authors_germany"
    output_filename = f"{base_name}_simple.json"
    output_path = input_path.parent / output_filename
    
    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Get file sizes
    input_size = input_path.stat().st_size / (1024 * 1024)  # MB
    output_size = output_path.stat().st_size / (1024 * 1024)  # MB
    
    print(f"  ✓ Created: {output_filename}")
    print(f"    Authors: {len(simplified_authors)}")
    print(f"    Size: {output_size:.1f} MB (original: {input_size:.1f} MB)")
    
    return {
        'file': output_filename,
        'authors': len(simplified_authors),
        'size_mb': output_size
    }

def main():
    by_country_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    print("="*80)
    print("Creating Simplified Author Array Files")
    print("="*80)
    print(f"\nFields to extract: {len(FIELDS_TO_EXTRACT)}")
    for i, field in enumerate(FIELDS_TO_EXTRACT, 1):
        print(f"  {i:2d}. {field}")
    
    # Get all country files
    json_files = sorted(by_country_dir.glob('european_authors_*.json'))
    
    # Exclude already simplified files and summary
    json_files = [f for f in json_files 
                  if not f.name.endswith('_simple.json') 
                  and f.name != 'countries_summary.json']
    
    print(f"\nFound {len(json_files)} files to process")
    
    # Track statistics
    overall_stats = {
        'files_processed': 0,
        'total_authors': 0,
        'total_size_mb': 0
    }
    
    results = []
    
    # Process each file
    for file_path in json_files:
        try:
            stats = create_simplified_file(file_path)
            results.append(stats)
            
            overall_stats['files_processed'] += 1
            overall_stats['total_authors'] += stats['authors']
            overall_stats['total_size_mb'] += stats['size_mb']
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files created:      {overall_stats['files_processed']}")
    print(f"Total authors:      {overall_stats['total_authors']}")
    print(f"Total size:         {overall_stats['total_size_mb']:.1f} MB")
    
    # Show largest files
    if results:
        print(f"\nLargest simplified files:")
        sorted_results = sorted(results, key=lambda x: x['size_mb'], reverse=True)
        for i, result in enumerate(sorted_results[:5], 1):
            print(f"  {i}. {result['file']:45s} {result['size_mb']:6.1f} MB ({result['authors']} authors)")
    
    print(f"\n{'='*80}")
    print("✓ All simplified files created!")
    print(f"  Location: {by_country_dir}/")
    print(f"  Naming: european_authors_<country>_simple.json")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

