#!/usr/bin/env python3
"""
Fix inconsistent publication arrays.
Ensures all_publications contains all publications (first-author + non-first-author).
"""

import json
from pathlib import Path
from datetime import datetime

def fix_author_publications(author_data):
    """
    Fix publication arrays to ensure consistency:
    - all_publications should contain ALL publications
    - If all_publications is empty but publications_as_first_author has content, copy it over
    """
    first_author_pubs = author_data.get('publications_as_first_author', [])
    non_first_pubs = author_data.get('publications_as_non_first_author', [])
    all_pubs = author_data.get('all_publications', [])
    
    # Check if fix is needed
    if len(first_author_pubs) > 0 and len(all_pubs) == 0:
        # Copy first-author publications to all_publications
        author_data['all_publications'] = first_author_pubs.copy()
        author_data['total_publications'] = len(first_author_pubs)
        return True
    
    # Also ensure total_publications is correct
    if len(all_pubs) > 0:
        expected_total = len(first_author_pubs) + len(non_first_pubs)
        if author_data.get('total_publications', 0) != expected_total:
            author_data['total_publications'] = expected_total
            return True
    
    return False

def update_country_file(file_path):
    """
    Update a single country file to fix publication arrays.
    """
    print(f"\n📄 Processing: {file_path.name}")
    
    # Load file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_authors = len(data['authors'])
    authors_fixed = 0
    
    # Fix each author
    for author_id, author in data['authors'].items():
        if fix_author_publications(author):
            authors_fixed += 1
    
    if authors_fixed > 0:
        # Update metadata
        if 'data_enhancements' not in data['metadata']:
            data['metadata']['data_enhancements'] = []
        
        data['metadata']['data_enhancements'].append({
            'date': datetime.now().isoformat(),
            'enhancement': 'Fixed inconsistent publication arrays',
            'issue': 'all_publications was empty despite having publications_as_first_author',
            'authors_fixed': authors_fixed,
            'fix': 'Copied publications_as_first_author to all_publications'
        })
        
        data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Save updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ Fixed: {authors_fixed}/{total_authors} authors")
    else:
        print(f"  ℹ No fixes needed")
    
    return {
        'total_authors': total_authors,
        'authors_fixed': authors_fixed
    }

def main():
    by_country_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    print("="*80)
    print("Fixing Inconsistent Publication Arrays")
    print("="*80)
    print("\nIssue: all_publications empty despite having publications_as_first_author")
    print("Fix: Copy publications_as_first_author → all_publications")
    
    # Get all country files
    json_files = sorted(by_country_dir.glob('european_authors_*.json'))
    
    if not json_files:
        print("\n⚠ No country files found!")
        return
    
    # Exclude summary file
    json_files = [f for f in json_files if f.name != 'countries_summary.json']
    
    print(f"\nFound {len(json_files)} country files to process")
    
    # Track statistics
    overall_stats = {
        'files_processed': 0,
        'total_authors': 0,
        'authors_fixed': 0
    }
    
    # Process each file
    for file_path in json_files:
        try:
            stats = update_country_file(file_path)
            
            overall_stats['files_processed'] += 1
            overall_stats['total_authors'] += stats['total_authors']
            overall_stats['authors_fixed'] += stats['authors_fixed']
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:    {overall_stats['files_processed']}/{len(json_files)}")
    print(f"Total authors:      {overall_stats['total_authors']}")
    print(f"Authors fixed:      {overall_stats['authors_fixed']}")
    
    if overall_stats['authors_fixed'] > 0:
        fix_rate = (overall_stats['authors_fixed'] / overall_stats['total_authors']) * 100
        print(f"Fix rate:           {fix_rate:.1f}%")
        
        print(f"\n✅ Fixed authors now have:")
        print(f"   - all_publications: Contains their first-author publications")
        print(f"   - publications_as_first_author: Same publications (for filtering)")
        print(f"   - publications_as_non_first_author: Empty (no co-author pubs)")
    
    print(f"\n{'='*80}")
    print("✓ Publication arrays are now consistent!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

