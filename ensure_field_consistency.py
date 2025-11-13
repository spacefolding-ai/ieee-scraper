#!/usr/bin/env python3
"""
Ensure all authors have consistent fields with appropriate default values.
Adds missing fields to authors so all have the same structure.
"""

import json
from pathlib import Path
from datetime import datetime

# Define the complete schema with default values
AUTHOR_SCHEMA = {
    # Basic identity
    'author_id': '',
    'name': '',
    'first_name': None,
    'last_name': None,
    'name_source': None,
    'all_names': [],
    'normalized_names': [],
    'aliases': [],
    
    # IEEE profile
    'ieee_profile_url': '',
    
    # Contact info
    'email': '',
    'email_found': False,
    'email_source': None,
    'email_citations': [],
    'email_retry_info': None,
    
    # Affiliation
    'primary_affiliation': '',
    'all_affiliations': [],
    
    # Biography
    'biography': None,
    
    # Publications summary
    'publications_as_first_author': [],
    'total_first_author_pubs': 0,
    'first_author_count': 0,
    'total_publications': 0,
    'total_non_first_author_pubs': 0,
    
    # Citations and downloads
    'total_citations': 0,
    'total_downloads': 0,
    
    # Publication details
    'all_publications': [],
    'publications_as_non_first_author': []
}

def ensure_field_consistency(author_data):
    """
    Ensure author has all fields from schema.
    Adds missing fields with default values.
    """
    fields_added = []
    
    for field, default_value in AUTHOR_SCHEMA.items():
        if field not in author_data:
            # Special case: don't override author_id if it exists
            if field == 'author_id':
                continue
            
            author_data[field] = default_value
            fields_added.append(field)
    
    return author_data, fields_added

def update_country_file(file_path):
    """
    Update a single country file to ensure field consistency.
    """
    print(f"\n📄 Processing: {file_path.name}")
    
    # Load file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_authors = len(data['authors'])
    authors_updated = 0
    total_fields_added = 0
    field_stats = {}
    
    # Update each author
    for author_id, author in data['authors'].items():
        author, fields_added = ensure_field_consistency(author)
        
        if fields_added:
            authors_updated += 1
            total_fields_added += len(fields_added)
            
            for field in fields_added:
                field_stats[field] = field_stats.get(field, 0) + 1
    
    # Update metadata
    if 'data_enhancements' not in data['metadata']:
        data['metadata']['data_enhancements'] = []
    
    data['metadata']['data_enhancements'].append({
        'date': datetime.now().isoformat(),
        'enhancement': 'Ensured field consistency across all authors',
        'authors_updated': authors_updated,
        'total_fields_added': total_fields_added,
        'most_common_missing_fields': sorted(field_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    })
    
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Updated: {authors_updated}/{total_authors} authors")
    if total_fields_added > 0:
        print(f"     Added {total_fields_added} missing fields")
        if field_stats:
            top_missing = sorted(field_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            for field, count in top_missing:
                print(f"       - {field}: {count} authors")
    else:
        print(f"     All authors already have consistent fields")
    
    return {
        'total_authors': total_authors,
        'authors_updated': authors_updated,
        'fields_added': total_fields_added,
        'field_stats': field_stats
    }

def main():
    by_country_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    print("="*80)
    print("Ensuring Field Consistency Across All By-Country Files")
    print("="*80)
    
    # Get all country files
    json_files = sorted(by_country_dir.glob('european_authors_*.json'))
    
    if not json_files:
        print("\n⚠ No country files found!")
        return
    
    # Exclude summary file
    json_files = [f for f in json_files if f.name != 'countries_summary.json']
    
    print(f"\nFound {len(json_files)} country files to process")
    print(f"\nFields that will be added if missing:")
    for field, default in list(AUTHOR_SCHEMA.items())[:10]:
        print(f"  - {field}: {type(default).__name__} = {default}")
    print(f"  ... and {len(AUTHOR_SCHEMA) - 10} more fields")
    
    # Track statistics
    overall_stats = {
        'files_processed': 0,
        'total_authors': 0,
        'authors_updated': 0,
        'fields_added': 0,
        'field_stats': {}
    }
    
    # Process each file
    for file_path in json_files:
        try:
            stats = update_country_file(file_path)
            
            overall_stats['files_processed'] += 1
            overall_stats['total_authors'] += stats['total_authors']
            overall_stats['authors_updated'] += stats['authors_updated']
            overall_stats['fields_added'] += stats['fields_added']
            
            # Merge field stats
            for field, count in stats['field_stats'].items():
                overall_stats['field_stats'][field] = overall_stats['field_stats'].get(field, 0) + count
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:       {overall_stats['files_processed']}/{len(json_files)}")
    print(f"Total authors:         {overall_stats['total_authors']}")
    print(f"Authors updated:       {overall_stats['authors_updated']}")
    print(f"Total fields added:    {overall_stats['fields_added']}")
    
    if overall_stats['field_stats']:
        print(f"\nMost commonly missing fields:")
        top_missing = sorted(overall_stats['field_stats'].items(), key=lambda x: x[1], reverse=True)[:10]
        for field, count in top_missing:
            print(f"  - {field}: {count} authors ({(count/overall_stats['total_authors'])*100:.1f}%)")
    
    print(f"\n{'='*80}")
    print("✓ All authors now have consistent field structure!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

