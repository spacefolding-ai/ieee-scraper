#!/usr/bin/env python3
"""
Script to exclude contacts from european_authors_with_emails.json
that are present in the HubSpot exclude list CSV.
"""

import json
import csv
from datetime import datetime
from pathlib import Path

def load_csv_emails(csv_path):
    """Load emails from CSV file"""
    emails = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row.get('Email', '').strip().lower()
            if email:
                emails.add(email)
    return emails

def filter_authors(json_path, exclude_emails):
    """Filter out authors whose emails are in the exclude list"""
    print(f"Loading JSON file: {json_path}")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data['authors'])
    print(f"Original author count: {original_count}")
    print(f"Emails to exclude: {len(exclude_emails)}")
    
    # Track excluded authors
    excluded_authors = []
    filtered_authors = {}
    
    for author_id, author_data in data['authors'].items():
        author_email = author_data.get('email', '').strip().lower()
        
        if author_email in exclude_emails:
            excluded_authors.append({
                'author_id': author_id,
                'name': author_data.get('name'),
                'email': author_email,
                'affiliation': author_data.get('primary_affiliation')
            })
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
        'reason': 'Excluded authors present in HubSpot database',
        'source_file': 'hubspot-crm-exports-academia-exclude-for-sf-2025-11-12_edit.csv',
        'excluded_count': len(excluded_authors),
        'remaining_count': len(filtered_authors)
    })
    
    # Update statistics
    if 'statistics' in data['metadata']:
        stats = data['metadata']['statistics']
        stats['total'] = len(filtered_authors)
        stats['with_email'] = len(filtered_authors)
    
    return data, excluded_authors

def main():
    # File paths
    csv_path = Path('/Users/miroslavjugovic/Downloads/hubspot-crm-exports-academia-exclude-for-sf-2025-11-12_edit.csv')
    json_input_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails.json')
    json_output_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_filtered.json')
    excluded_list_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/excluded_hubspot_authors.json')
    
    print("="*70)
    print("Excluding HubSpot contacts from European authors dataset")
    print("="*70)
    
    # Load exclude list from CSV
    print("\nStep 1: Loading HubSpot exclude list...")
    exclude_emails = load_csv_emails(csv_path)
    print(f"✓ Loaded {len(exclude_emails)} emails to exclude")
    
    # Filter authors
    print("\nStep 2: Filtering authors...")
    filtered_data, excluded_authors = filter_authors(json_input_path, exclude_emails)
    
    print(f"\n✓ Excluded {len(excluded_authors)} authors")
    print(f"✓ Remaining authors: {len(filtered_data['authors'])}")
    
    # Save filtered data
    print("\nStep 3: Saving filtered dataset...")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved filtered dataset to: {json_output_path}")
    
    # Save excluded authors list
    print("\nStep 4: Saving excluded authors list...")
    excluded_data = {
        'metadata': {
            'description': 'Authors excluded from european_authors_with_emails.json because they exist in HubSpot',
            'source_csv': 'hubspot-crm-exports-academia-exclude-for-sf-2025-11-12_edit.csv',
            'exclusion_date': datetime.now().isoformat(),
            'total_excluded': len(excluded_authors)
        },
        'excluded_authors': excluded_authors
    }
    
    with open(excluded_list_path, 'w', encoding='utf-8') as f:
        json.dump(excluded_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved excluded authors list to: {excluded_list_path}")
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Original authors:     {len(filtered_data['authors']) + len(excluded_authors)}")
    print(f"Excluded (in HubSpot): {len(excluded_authors)}")
    print(f"Remaining authors:    {len(filtered_data['authors'])}")
    print(f"\nFiltered dataset saved to:")
    print(f"  {json_output_path}")
    print(f"\nExcluded authors list saved to:")
    print(f"  {excluded_list_path}")
    
    # Show some examples of excluded authors
    if excluded_authors:
        print(f"\n{'='*70}")
        print(f"SAMPLE OF EXCLUDED AUTHORS (first 10)")
        print(f"{'='*70}")
        for i, author in enumerate(excluded_authors[:10], 1):
            print(f"\n{i}. {author['name']}")
            print(f"   Email: {author['email']}")
            print(f"   Affiliation: {author['affiliation']}")
    
    print("\n" + "="*70)
    print("✓ Process completed successfully!")
    print("="*70)

if __name__ == '__main__':
    main()

