#!/usr/bin/env python3
"""
Remove non-European authors from the dataset based on primary affiliation.
These authors were included due to secondary European affiliations.
"""

import json
from pathlib import Path
from datetime import datetime

# Non-European regions to exclude
NON_EUROPEAN_PATTERNS = [
    # Asia
    'hong kong', 'china', 'japan', 'korea', 'singapore', 'taiwan', 'thailand',
    'vietnam', 'malaysia', 'indonesia', 'philippines', 'india', 'pakistan',
    'bangladesh', 'sri lanka', 'nepal', 'iran', 'iraq', 'saudi', 'arabia',
    'emirates', 'uae', 'qatar', 'kuwait', 'oman', 'bahrain', 'jordan',
    'lebanon', 'israel', 'kazakhstan', 'uzbekistan', 'mongolia',
    # Americas
    'canada', 'usa', 'united states', 'america', 'mexico', 'brazil',
    'argentina', 'chile', 'colombia', 'peru', 'venezuela', 'ecuador',
    'uruguay', 'paraguay', 'bolivia', 'costa rica', 'panama', 'guatemala',
    'honduras', 'nicaragua', 'salvador', 'cuba', 'jamaica', 'haiti',
    'dominican', 'puerto rico', 'harvard', 'mit', 'stanford', 'berkeley',
    'princeton', 'yale', 'columbia', 'cornell', 'pennsylvania', 'michigan',
    'caltech', 'chicago', 'northwestern', 'duke', 'johns hopkins',
    # Oceania
    'australia', 'new zealand', 'sydney', 'melbourne', 'brisbane',
    'perth', 'adelaide', 'canberra', 'auckland', 'wellington',
    # Africa
    'south africa', 'nigeria', 'kenya', 'egypt', 'morocco', 'algeria',
    'tunisia', 'ghana', 'ethiopia', 'tanzania', 'uganda', 'zimbabwe',
    # Other
    '.hk', '.cn', '.jp', '.kr', '.sg', '.tw', '.in', '.pk', '.bd',
    '.au', '.nz', '.za', '.br', '.mx', '.ar', '.cl'
]

def is_non_european(affiliation, email=''):
    """Check if affiliation or email indicates non-European location"""
    if not affiliation:
        return False
    
    aff_lower = affiliation.lower()
    email_lower = email.lower()
    
    for pattern in NON_EUROPEAN_PATTERNS:
        if pattern in aff_lower or pattern in email_lower:
            return True
    
    return False

def main():
    input_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_academic_only.json')
    output_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_academic_only_cleaned.json')
    excluded_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/excluded_non_european_authors.json')
    
    print("="*80)
    print("Cleaning Non-European Authors from Dataset")
    print("="*80)
    
    # Load data
    print(f"\nLoading: {input_path}")
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    original_count = len(data['authors'])
    print(f"Original author count: {original_count}")
    
    # Identify non-European authors
    non_european_authors = []
    cleaned_authors = {}
    
    for author_id, author_data in data['authors'].items():
        primary_aff = author_data.get('primary_affiliation', '')
        email = author_data.get('email', '')
        
        if is_non_european(primary_aff, email):
            non_european_authors.append({
                'author_id': author_id,
                'name': author_data.get('name'),
                'email': email,
                'primary_affiliation': primary_aff,
                'all_affiliations': author_data.get('all_affiliations', [])
            })
        else:
            cleaned_authors[author_id] = author_data
    
    # Update metadata
    data['authors'] = cleaned_authors
    data['metadata']['total_authors'] = len(cleaned_authors)
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Add exclusion info
    if 'exclusions' not in data['metadata']:
        data['metadata']['exclusions'] = []
    
    data['metadata']['exclusions'].append({
        'date': datetime.now().isoformat(),
        'reason': 'Removed authors with non-European primary affiliations',
        'excluded_count': len(non_european_authors),
        'remaining_count': len(cleaned_authors),
        'note': 'These authors had secondary European affiliations but primary location outside Europe'
    })
    
    # Update statistics
    if 'statistics' in data['metadata']:
        stats = data['metadata']['statistics']
        stats['total'] = len(cleaned_authors)
        stats['with_email'] = len(cleaned_authors)
    
    # Save cleaned data
    print(f"\nSaving cleaned dataset...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to: {output_path}")
    
    # Save excluded authors
    excluded_data = {
        'metadata': {
            'description': 'Authors excluded due to non-European primary affiliations',
            'exclusion_date': datetime.now().isoformat(),
            'total_excluded': len(non_european_authors),
            'note': 'These authors had secondary European affiliations but are primarily based outside Europe'
        },
        'excluded_authors': non_european_authors
    }
    
    with open(excluded_path, 'w', encoding='utf-8') as f:
        json.dump(excluded_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved excluded authors to: {excluded_path}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Original authors:           {original_count}")
    print(f"Non-European (excluded):    {len(non_european_authors)}")
    print(f"Truly European (remaining): {len(cleaned_authors)}")
    print(f"\nReduction: {len(non_european_authors)} authors ({(len(non_european_authors)/original_count)*100:.1f}%)")
    
    # Show some examples
    if non_european_authors:
        print(f"\n{'='*80}")
        print("EXAMPLES OF EXCLUDED NON-EUROPEAN AUTHORS (first 15):")
        print(f"{'='*80}")
        for i, author in enumerate(non_european_authors[:15], 1):
            print(f"\n{i:2d}. {author['name']}")
            print(f"    Email: {author['email']}")
            print(f"    Primary: {author['primary_affiliation'][:100]}")
            if len(author.get('all_affiliations', [])) > 1:
                print(f"    Secondary: {author['all_affiliations'][1][:100] if len(author['all_affiliations']) > 1 else 'N/A'}")
    
    print(f"\n{'='*80}")
    print("✓ Cleanup completed successfully!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

