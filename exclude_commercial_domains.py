#!/usr/bin/env python3
"""
Script to exclude authors with commercial email domains from the filtered dataset.
"""

import json
from datetime import datetime
from pathlib import Path

# Commercial domain patterns to exclude
COMMERCIAL_DOMAINS = [
    'abb',
    'siemens',
    'ge.com',
    'samsung',
    'mitsubishi',
    'hitachi',
    'huawei',
    'intel',
    'mee.',
    'lge.com',
    'ericsson',
    'infineon',
    'ti.com'
]

def extract_domain(email):
    """Extract domain from email address"""
    if '@' in email:
        return email.split('@')[1].lower()
    return ''

def is_commercial_domain(email, patterns):
    """Check if email domain contains any commercial patterns"""
    domain = extract_domain(email)
    for pattern in patterns:
        if pattern.lower() in domain:
            return True, pattern
    return False, None

def filter_commercial_authors(json_path, commercial_patterns):
    """Filter out authors with commercial email domains"""
    print(f"Loading JSON file: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data['authors'])
    print(f"Original author count: {original_count}")
    print(f"Commercial patterns to exclude: {len(commercial_patterns)}")
    
    # Track excluded authors
    excluded_authors = []
    filtered_authors = {}
    commercial_domain_stats = {pattern: 0 for pattern in commercial_patterns}
    
    for author_id, author_data in data['authors'].items():
        author_email = author_data.get('email', '').strip()
        
        is_commercial, matched_pattern = is_commercial_domain(author_email, commercial_patterns)
        
        if is_commercial:
            excluded_authors.append({
                'author_id': author_id,
                'name': author_data.get('name'),
                'email': author_email,
                'domain': extract_domain(author_email),
                'matched_pattern': matched_pattern,
                'affiliation': author_data.get('primary_affiliation')
            })
            commercial_domain_stats[matched_pattern] += 1
        else:
            filtered_authors[author_id] = author_data
    
    # Update metadata
    data['authors'] = filtered_authors
    data['metadata']['total_authors'] = len(filtered_authors)
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Add exclusion info to metadata
    if 'exclusions' not in data['metadata']:
        data['metadata']['exclusions'] = []
    
    data['metadata']['exclusions'].append({
        'date': datetime.now().isoformat(),
        'reason': 'Excluded authors with commercial email domains',
        'commercial_patterns': commercial_patterns,
        'excluded_count': len(excluded_authors),
        'remaining_count': len(filtered_authors),
        'breakdown_by_pattern': commercial_domain_stats
    })
    
    # Update statistics
    if 'statistics' in data['metadata']:
        stats = data['metadata']['statistics']
        stats['total'] = len(filtered_authors)
        stats['with_email'] = len(filtered_authors)
    
    return data, excluded_authors, commercial_domain_stats

def main():
    # File paths
    json_input_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_filtered.json')
    json_output_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_academic_only.json')
    excluded_list_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/excluded_commercial_authors.json')
    
    print("="*70)
    print("Excluding Commercial Email Domains from European Authors Dataset")
    print("="*70)
    
    # Show patterns
    print("\nCommercial domain patterns to exclude:")
    for i, pattern in enumerate(COMMERCIAL_DOMAINS, 1):
        print(f"  {i:2d}. {pattern}")
    
    # Filter authors
    print("\nStep 1: Filtering authors with commercial domains...")
    filtered_data, excluded_authors, domain_stats = filter_commercial_authors(
        json_input_path, COMMERCIAL_DOMAINS
    )
    
    print(f"\n✓ Excluded {len(excluded_authors)} authors with commercial domains")
    print(f"✓ Remaining authors: {len(filtered_data['authors'])}")
    
    # Show breakdown by pattern
    print("\nBreakdown by commercial pattern:")
    for pattern, count in sorted(domain_stats.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {pattern:15s}: {count:3d} authors")
    
    # Save filtered data
    print("\nStep 2: Saving academic-only dataset...")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved academic-only dataset to: {json_output_path}")
    
    # Save excluded authors list
    print("\nStep 3: Saving excluded commercial authors list...")
    excluded_data = {
        'metadata': {
            'description': 'Authors excluded due to commercial email domains',
            'exclusion_date': datetime.now().isoformat(),
            'commercial_patterns': COMMERCIAL_DOMAINS,
            'total_excluded': len(excluded_authors),
            'breakdown_by_pattern': domain_stats
        },
        'excluded_authors': excluded_authors
    }
    
    with open(excluded_list_path, 'w', encoding='utf-8') as f:
        json.dump(excluded_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved excluded commercial authors to: {excluded_list_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Original authors:              {len(filtered_data['authors']) + len(excluded_authors)}")
    print(f"Excluded (commercial domains): {len(excluded_authors)}")
    print(f"Remaining (academic only):     {len(filtered_data['authors'])}")
    print(f"\nAcademic-only dataset saved to:")
    print(f"  {json_output_path}")
    print(f"\nExcluded commercial authors list saved to:")
    print(f"  {excluded_list_path}")
    
    # Show some examples of excluded authors
    if excluded_authors:
        print(f"\n{'='*70}")
        print(f"SAMPLE OF EXCLUDED COMMERCIAL AUTHORS (first 15)")
        print(f"{'='*70}")
        for i, author in enumerate(excluded_authors[:15], 1):
            print(f"\n{i}. {author['name']}")
            print(f"   Email: {author['email']}")
            print(f"   Domain: {author['domain']}")
            print(f"   Matched: {author['matched_pattern']}")
            if author['affiliation']:
                aff = author['affiliation'][:80] + '...' if len(author['affiliation']) > 80 else author['affiliation']
                print(f"   Affiliation: {aff}")
    
    print("\n" + "="*70)
    print("✓ Process completed successfully!")
    print("="*70)

if __name__ == '__main__':
    main()

