#!/usr/bin/env python3
"""
Add first_name and last_name fields to all authors in by_country files.
Extracts from publication data where available, or parses the full name.
"""

import json
import re
from pathlib import Path
from datetime import datetime

def extract_names_from_publications(author_data):
    """
    Extract first and last name from author's publication records.
    Returns (first_name, last_name, source) or (None, None, None)
    """
    # Check all publications for this author
    all_pubs = author_data.get('all_publications', [])
    author_id = author_data.get('author_id')
    
    for pub in all_pubs:
        pub_authors = pub.get('authors', [])
        for pub_author in pub_authors:
            # Match by author ID
            if str(pub_author.get('id')) == str(author_id):
                first_name = pub_author.get('first_name')
                last_name = pub_author.get('last_name')
                if first_name and last_name:
                    return first_name, last_name, 'publication_data'
    
    return None, None, None

def parse_full_name(full_name):
    """
    Parse full name into first and last name.
    Handles various formats like:
    - "John Smith" -> first: John, last: Smith
    - "John Michael Smith" -> first: John, last: Smith
    - "Jean-Pierre Dubois" -> first: Jean-Pierre, last: Dubois
    - "von Neumann" -> first: von, last: Neumann (best effort)
    """
    if not full_name:
        return None, None
    
    # Clean the name
    name = full_name.strip()
    
    # Remove titles and suffixes
    titles = r'\b(Dr\.|Prof\.|PhD|Ph\.D\.|M\.Sc\.|B\.Sc\.|Jr\.|Sr\.|II|III|IV)\b'
    name = re.sub(titles, '', name, flags=re.IGNORECASE).strip()
    
    # Split by spaces
    parts = [p for p in name.split() if p]
    
    if not parts:
        return None, None
    elif len(parts) == 1:
        # Only one name - use as last name
        return None, parts[0]
    elif len(parts) == 2:
        # Simple case: first last
        return parts[0], parts[1]
    else:
        # Multiple parts: first name is first part, last name is everything else
        # This handles cases like "Jean-Pierre" or "Mary Anne" as first names
        # and compound last names like "von Neumann" or "de la Cruz"
        return parts[0], ' '.join(parts[1:])

def add_names_to_author(author_data):
    """
    Add first_name and last_name fields to author data.
    Returns updated author data and metadata about the source.
    """
    # Try to get from publications first
    first_name, last_name, source = extract_names_from_publications(author_data)
    
    # Fallback to parsing full name
    if not first_name or not last_name:
        full_name = author_data.get('name')
        first_name_parsed, last_name_parsed = parse_full_name(full_name)
        
        # Use parsed values for missing fields
        if not first_name:
            first_name = first_name_parsed
        if not last_name:
            last_name = last_name_parsed
        
        source = 'name_parsing' if (first_name or last_name) else 'none'
    
    # Add to author data
    author_data['first_name'] = first_name
    author_data['last_name'] = last_name
    author_data['name_source'] = source
    
    return author_data, source

def process_country_file(file_path):
    """Process a single country file and add first/last names to all authors"""
    print(f"\nProcessing: {file_path.name}")
    
    # Load data
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_authors = len(data['authors'])
    print(f"  Total authors: {total_authors}")
    
    # Track statistics
    stats = {
        'publication_data': 0,
        'name_parsing': 0,
        'none': 0
    }
    
    # Process each author
    updated_authors = {}
    for author_id, author_data in data['authors'].items():
        updated_author, source = add_names_to_author(author_data)
        updated_authors[author_id] = updated_author
        stats[source] += 1
    
    # Update data
    data['authors'] = updated_authors
    
    # Update metadata
    if 'data_enhancements' not in data['metadata']:
        data['metadata']['data_enhancements'] = []
    
    data['metadata']['data_enhancements'].append({
        'date': datetime.now().isoformat(),
        'enhancement': 'Added first_name and last_name fields',
        'sources': {
            'from_publications': stats['publication_data'],
            'from_name_parsing': stats['name_parsing'],
            'unavailable': stats['none']
        }
    })
    
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save updated data
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    print(f"  ✓ Updated: {total_authors} authors")
    print(f"    - From publications: {stats['publication_data']}")
    print(f"    - From name parsing: {stats['name_parsing']}")
    if stats['none'] > 0:
        print(f"    - Unavailable: {stats['none']}")
    
    return stats

def main():
    by_country_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    print("="*80)
    print("Adding First and Last Names to All By-Country Files")
    print("="*80)
    
    # Get all JSON files
    json_files = sorted(by_country_dir.glob('european_authors_*.json'))
    
    if not json_files:
        print("⚠ No country files found!")
        return
    
    print(f"\nFound {len(json_files)} country files")
    
    # Track overall statistics
    overall_stats = {
        'publication_data': 0,
        'name_parsing': 0,
        'none': 0
    }
    total_authors = 0
    files_processed = 0
    
    # Process each file
    for file_path in json_files:
        try:
            stats = process_country_file(file_path)
            
            # Update overall stats
            for key in overall_stats:
                overall_stats[key] += stats[key]
            total_authors += sum(stats.values())
            files_processed += 1
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:     {files_processed}/{len(json_files)}")
    print(f"Total authors:       {total_authors}")
    print(f"\nName sources:")
    print(f"  From publications: {overall_stats['publication_data']:5d} ({(overall_stats['publication_data']/total_authors)*100:5.1f}%)")
    print(f"  From name parsing: {overall_stats['name_parsing']:5d} ({(overall_stats['name_parsing']/total_authors)*100:5.1f}%)")
    if overall_stats['none'] > 0:
        print(f"  Unavailable:       {overall_stats['none']:5d} ({(overall_stats['none']/total_authors)*100:5.1f}%)")
    
    print(f"\n{'='*80}")
    print("✓ All files updated successfully!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

