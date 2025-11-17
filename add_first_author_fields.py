#!/usr/bin/env python3
"""
Add is_first_author and most_recent_publication_title_as_first_author fields to CSV files.
"""

import json
import csv
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

def get_most_recent_first_author_publication(publications_as_first_author: List[Dict]) -> Optional[str]:
    """
    Get the title of the most recent publication where author was first author.
    Returns None if no first author publications.
    """
    if not publications_as_first_author:
        return None
    
    # Sort by year (descending), then by title
    # Note: publications_as_first_author uses 'article_title' and 'publication_year' fields
    sorted_pubs = sorted(
        publications_as_first_author,
        key=lambda p: (int(p.get('publication_year', p.get('year', 0))), p.get('article_title', p.get('title', ''))),
        reverse=True
    )
    
    # Try both possible field names for title
    title = sorted_pubs[0].get('article_title') or sorted_pubs[0].get('title', '')
    return title

def process_json_file(json_path: Path) -> Dict[str, Dict]:
    """
    Process JSON file and extract first author information.
    Returns dict: {author_id: {is_first_author, most_recent_title}}
    """
    print(f"Processing: {json_path.name}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        authors = json.load(f)
    
    author_info = {}
    
    for author in authors:
        if not isinstance(author, dict):
            continue
        
        author_id = author.get('author_id')
        if not author_id:
            continue
        
        # Check if author has first author publications
        first_author_count = author.get('first_author_count', 0)
        publications_as_first = author.get('publications_as_first_author', [])
        
        is_first_author = first_author_count > 0 or len(publications_as_first) > 0
        
        # Get most recent first author publication title
        most_recent_title = ""
        if is_first_author and publications_as_first:
            most_recent_title = get_most_recent_first_author_publication(publications_as_first) or ""
        
        author_info[author_id] = {
            'is_first_author': is_first_author,
            'most_recent_publication_title_as_first_author': most_recent_title
        }
    
    return author_info

def update_csv_file(csv_path: Path, author_info: Dict[str, Dict]):
    """
    Update CSV file with new first author fields.
    """
    print(f"\nUpdating CSV: {csv_path.name}")
    
    # Read existing CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)
    
    # Add new fields if they don't exist
    if 'is_first_author' not in fieldnames:
        fieldnames.append('is_first_author')
    if 'most_recent_publication_title_as_first_author' not in fieldnames:
        fieldnames.append('most_recent_publication_title_as_first_author')
    
    # Update rows
    updated_count = 0
    not_found_count = 0
    
    for row in rows:
        author_id = row.get('author_id')
        
        if author_id in author_info:
            row['is_first_author'] = str(author_info[author_id]['is_first_author']).lower()
            row['most_recent_publication_title_as_first_author'] = author_info[author_id]['most_recent_publication_title_as_first_author']
            updated_count += 1
        else:
            # Default values if author not found in JSON
            row['is_first_author'] = 'false'
            row['most_recent_publication_title_as_first_author'] = ''
            not_found_count += 1
    
    # Write updated CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"  Updated: {updated_count:,} authors")
    if not_found_count > 0:
        print(f"  Not found in JSON: {not_found_count:,} (set to defaults)")
    
    # Statistics
    true_count = sum(1 for r in rows if r['is_first_author'] == 'true')
    false_count = sum(1 for r in rows if r['is_first_author'] == 'false')
    with_title = sum(1 for r in rows if r['most_recent_publication_title_as_first_author'])
    
    print(f"  is_first_author = true: {true_count:,} ({true_count/len(rows)*100:.1f}%)")
    print(f"  is_first_author = false: {false_count:,} ({false_count/len(rows)*100:.1f}%)")
    print(f"  With recent title: {with_title:,}")

def main():
    print("=" * 80)
    print("ADDING FIRST AUTHOR FIELDS TO CSV FILES")
    print("=" * 80)
    
    # Process DACH
    print("\n" + "=" * 80)
    print("PROCESSING DACH")
    print("=" * 80)
    
    dach_json = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country/european_authors_dach_simple.json')
    dach_csv = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country/european_authors_dach_simple.csv')
    
    dach_info = process_json_file(dach_json)
    update_csv_file(dach_csv, dach_info)
    
    # Process Non-DACH
    print("\n" + "=" * 80)
    print("PROCESSING NON-DACH")
    print("=" * 80)
    
    # Need to process all individual country JSON files for non-DACH
    non_dach_csv = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_non_dach_no_france_merged.csv')
    results_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    # Excluded files
    exclude_files = {
        'european_authors_dach_simple.json',
        'european_authors_germany_simple.json',
        'european_authors_switzerland_simple.json',
        'european_authors_austria_simple.json',
        'european_authors_france_simple.json'
    }
    
    # Collect author info from all non-DACH JSON files
    print("\nCollecting data from all non-DACH JSON files...")
    all_non_dach_info = {}
    
    json_files = sorted(results_dir.glob('*_simple.json'))
    processed_files = 0
    
    for json_file in json_files:
        if json_file.name in exclude_files:
            print(f"  Skipping: {json_file.name}")
            continue
        
        file_info = process_json_file(json_file)
        all_non_dach_info.update(file_info)
        processed_files += 1
    
    print(f"\nProcessed {processed_files} JSON files")
    print(f"Total authors with info: {len(all_non_dach_info):,}")
    
    update_csv_file(non_dach_csv, all_non_dach_info)
    
    print("\n" + "=" * 80)
    print("✅ SUCCESSFULLY UPDATED ALL CSV FILES")
    print("=" * 80)
    print("\nUpdated files:")
    print(f"  - {dach_csv}")
    print(f"  - {non_dach_csv}")
    print("\nNew fields added:")
    print("  - is_first_author (true/false)")
    print("  - most_recent_publication_title_as_first_author")

if __name__ == "__main__":
    main()

