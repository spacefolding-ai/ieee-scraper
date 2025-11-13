#!/usr/bin/env python3
"""
Restructure author data to remove the separate 'abstracts' array.
All abstracts should be stored directly in their publication objects.
"""

import json
from pathlib import Path
from datetime import datetime

def restructure_author_abstracts(author_data):
    """
    Remove the separate 'abstracts' array since abstracts are now
    stored directly in publication objects.
    """
    # Remove the abstracts array if it exists
    if 'abstracts' in author_data:
        del author_data['abstracts']
    
    # Also remove publication_titles, publication_years, publication_dois
    # since this info is in the full publication objects
    fields_to_remove = [
        'publication_titles',
        'publication_years', 
        'publication_dois'
    ]
    
    for field in fields_to_remove:
        if field in author_data:
            del author_data[field]
    
    return author_data

def update_country_file(file_path):
    """
    Update a single country file to restructure abstracts.
    """
    print(f"\n📄 Processing: {file_path.name}")
    
    # Load file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_authors = len(data['authors'])
    
    # Update each author
    for author_id, author in data['authors'].items():
        restructure_author_abstracts(author)
    
    # Update metadata
    if 'data_enhancements' not in data['metadata']:
        data['metadata']['data_enhancements'] = []
    
    data['metadata']['data_enhancements'].append({
        'date': datetime.now().isoformat(),
        'enhancement': 'Restructured data: removed separate abstracts/titles/years/dois arrays',
        'reason': 'All publication details (including abstracts) are now in publication objects',
        'authors_updated': total_authors
    })
    
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Updated: {total_authors} authors")
    
    return total_authors

def main():
    by_country_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    print("="*80)
    print("Restructuring By-Country Files: Moving Abstracts to Publication Objects")
    print("="*80)
    
    # Get all country files
    json_files = sorted(by_country_dir.glob('european_authors_*.json'))
    
    if not json_files:
        print("\n⚠ No country files found!")
        return
    
    # Exclude summary file
    json_files = [f for f in json_files if f.name != 'countries_summary.json']
    
    print(f"\nFound {len(json_files)} country files to process")
    
    # Track statistics
    files_processed = 0
    total_authors = 0
    
    # Process each file
    for file_path in json_files:
        try:
            authors_updated = update_country_file(file_path)
            files_processed += 1
            total_authors += authors_updated
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:    {files_processed}/{len(json_files)}")
    print(f"Authors updated:    {total_authors}")
    print(f"\nChanges made:")
    print(f"  ✓ Removed 'abstracts' array (abstracts now in publication objects)")
    print(f"  ✓ Removed 'publication_titles' array (titles in publication objects)")
    print(f"  ✓ Removed 'publication_years' array (years in publication objects)")
    print(f"  ✓ Removed 'publication_dois' array (dois in publication objects)")
    print(f"\nResult: Cleaner structure with all publication data grouped together")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

