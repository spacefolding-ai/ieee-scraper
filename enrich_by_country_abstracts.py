#!/usr/bin/env python3
"""
Update all by_country files with full abstracts from european_authors_with_emails.json.
Matches publications by article_number and replaces truncated abstracts with full ones.
"""

import json
from pathlib import Path
from datetime import datetime

def build_abstract_lookup(source_file):
    """
    Build a lookup dictionary of article_number -> full abstract data
    from the source file with enriched abstracts.
    """
    print(f"Loading source file with full abstracts: {source_file.name}")
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    abstract_lookup = {}
    
    # Extract from all authors
    for author_id, author in data['authors'].items():
        # Check publications_as_non_first_author (where full abstracts are)
        for pub in author.get('publications_as_non_first_author', []):
            article_number = pub.get('article_number')
            if article_number and pub.get('is_full_abstract'):
                abstract_lookup[article_number] = {
                    'abstract': pub.get('abstract'),
                    'is_full_abstract': pub.get('is_full_abstract', True),
                    'abstract_enriched': pub.get('abstract_enriched'),
                    'abstract_enriched_at': pub.get('abstract_enriched_at'),
                    'is_full_abstract_field': pub.get('is_full_abstract')
                }
        
        # Also check all_publications (some might have full abstracts)
        for pub in author.get('all_publications', []):
            article_number = pub.get('article_number')
            if article_number and pub.get('is_full_abstract'):
                if article_number not in abstract_lookup:  # Don't override if already found
                    abstract_lookup[article_number] = {
                        'abstract': pub.get('abstract'),
                        'is_full_abstract': pub.get('is_full_abstract', True),
                        'abstract_enriched': pub.get('abstract_enriched'),
                        'abstract_enriched_at': pub.get('abstract_enriched_at'),
                        'is_full_abstract_field': pub.get('is_full_abstract')
                    }
    
    print(f"  ✓ Built lookup table with {len(abstract_lookup)} full abstracts")
    return abstract_lookup

def update_publication_abstract(pub, abstract_lookup):
    """
    Update a single publication with full abstract if available.
    Returns True if updated, False otherwise.
    """
    article_number = pub.get('article_number')
    if not article_number:
        return False
    
    full_abstract_data = abstract_lookup.get(article_number)
    if not full_abstract_data:
        return False
    
    # Update the publication with full abstract
    pub['abstract'] = full_abstract_data['abstract']
    pub['is_full_abstract'] = full_abstract_data['is_full_abstract']
    
    if full_abstract_data.get('abstract_enriched') is not None:
        pub['abstract_enriched'] = full_abstract_data['abstract_enriched']
    
    if full_abstract_data.get('abstract_enriched_at'):
        pub['abstract_enriched_at'] = full_abstract_data['abstract_enriched_at']
    
    return True

def update_country_file(file_path, abstract_lookup):
    """
    Update a single country file with full abstracts.
    """
    print(f"\n📄 Processing: {file_path.name}")
    
    # Load file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total_authors = len(data['authors'])
    total_pubs = 0
    updated_pubs = 0
    
    # Update each author's publications
    for author_id, author in data['authors'].items():
        # Update all_publications
        for pub in author.get('all_publications', []):
            total_pubs += 1
            if update_publication_abstract(pub, abstract_lookup):
                updated_pubs += 1
        
        # Update publications_as_first_author
        for pub in author.get('publications_as_first_author', []):
            if update_publication_abstract(pub, abstract_lookup):
                pass  # Already counted in all_publications
        
        # Update publications_as_non_first_author
        for pub in author.get('publications_as_non_first_author', []):
            if update_publication_abstract(pub, abstract_lookup):
                pass  # Already counted in all_publications
        
        # Update abstracts array (summary level)
        # This should also be updated to full abstracts
        if 'abstracts' in author and author['abstracts']:
            new_abstracts = []
            for i, old_abstract in enumerate(author['abstracts']):
                # Try to find corresponding publication
                found_full = False
                for pub in author.get('all_publications', []):
                    if pub.get('abstract') and len(pub['abstract']) > 500:
                        # This is a full abstract, use it
                        if len(new_abstracts) <= i:
                            new_abstracts.append(pub['abstract'])
                            found_full = True
                            break
                
                if not found_full:
                    new_abstracts.append(old_abstract)
            
            if new_abstracts:
                author['abstracts'] = new_abstracts
    
    # Update metadata
    if 'data_enhancements' not in data['metadata']:
        data['metadata']['data_enhancements'] = []
    
    data['metadata']['data_enhancements'].append({
        'date': datetime.now().isoformat(),
        'enhancement': 'Enriched with full abstracts from european_authors_with_emails.json',
        'publications_updated': updated_pubs,
        'total_publications': total_pubs,
        'source': 'european_authors_with_emails.json'
    })
    
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Save updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Print statistics
    update_rate = (updated_pubs / total_pubs * 100) if total_pubs > 0 else 0
    print(f"  ✓ Updated: {updated_pubs}/{total_pubs} publications ({update_rate:.1f}%)")
    
    return {
        'total_pubs': total_pubs,
        'updated_pubs': updated_pubs,
        'authors': total_authors
    }

def main():
    source_file = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails.json')
    by_country_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    print("="*80)
    print("Enriching By-Country Files with Full Abstracts")
    print("="*80)
    
    # Build abstract lookup table
    abstract_lookup = build_abstract_lookup(source_file)
    
    if not abstract_lookup:
        print("\n⚠ No full abstracts found in source file!")
        return
    
    # Get all country files
    json_files = sorted(by_country_dir.glob('european_authors_*.json'))
    
    if not json_files:
        print("\n⚠ No country files found!")
        return
    
    # Exclude summary file
    json_files = [f for f in json_files if f.name != 'countries_summary.json']
    
    print(f"\nFound {len(json_files)} country files to process")
    
    # Track overall statistics
    overall_stats = {
        'files_processed': 0,
        'total_pubs': 0,
        'updated_pubs': 0,
        'total_authors': 0
    }
    
    # Process each file
    for file_path in json_files:
        try:
            stats = update_country_file(file_path, abstract_lookup)
            
            overall_stats['files_processed'] += 1
            overall_stats['total_pubs'] += stats['total_pubs']
            overall_stats['updated_pubs'] += stats['updated_pubs']
            overall_stats['total_authors'] += stats['authors']
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
    
    # Final summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:          {overall_stats['files_processed']}/{len(json_files)}")
    print(f"Total authors:            {overall_stats['total_authors']}")
    print(f"Total publications:       {overall_stats['total_pubs']}")
    print(f"Publications enriched:    {overall_stats['updated_pubs']}")
    
    if overall_stats['total_pubs'] > 0:
        enrichment_rate = (overall_stats['updated_pubs'] / overall_stats['total_pubs']) * 100
        print(f"Enrichment rate:          {enrichment_rate:.1f}%")
    
    print(f"\n{'='*80}")
    print("✓ All files updated successfully!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

