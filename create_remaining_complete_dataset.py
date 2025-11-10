#!/usr/bin/env python3
"""
Create a complete dataset for remaining European authors matching the schema of authors_complete_dataset.json
"""

import json
from datetime import datetime
from pathlib import Path

def main():
    print("🔄 Creating complete dataset for remaining European authors...")
    print("=" * 70)
    
    # Load email results
    with open('results/remaining_european_authors_emails.json', 'r') as f:
        email_data = json.load(f)
    
    # Load original enriched data (has affiliations and biography)
    with open('results/remaining_authors_enriched.json', 'r') as f:
        enriched_data = json.load(f)
    
    enriched_authors = enriched_data.get('authors', {})
    email_authors = email_data.get('authors', {})
    
    # Create complete dataset
    complete_authors = {}
    
    for author_id, email_result in email_authors.items():
        # Get enriched info
        enriched_info = enriched_authors.get(author_id, {})
        
        # Get email info
        email_search = email_result.get('email_search', {})
        email_found = email_search.get('found', False)
        email = email_search.get('email') if email_found else None
        
        # Build author record matching the schema
        author_record = {
            'author_id': author_id,
            'name': enriched_info.get('preferred_name', email_result.get('name', 'Unknown')),
            'all_names': [enriched_info.get('preferred_name', email_result.get('name', 'Unknown'))],
            'normalized_names': [],  # Not available for remaining authors
            'ieee_profile_url': f"https://ieeexplore.ieee.org/author/{author_id}",
            
            # Email info
            'email': email,
            'email_found': email_found,
            'email_source': email_search.get('source_url'),
            'email_citations': email_search.get('citations', []),
            
            # Affiliation info
            'primary_affiliation': enriched_info.get('current_affiliations', [None])[0],
            'all_affiliations': enriched_info.get('current_affiliations', []),
            
            # Biography (if available)
            'biography': enriched_info.get('biography'),
            'aliases': enriched_info.get('aliases', []),
            
            # Note: These authors don't have publications/abstracts in our dataset
            'publications_as_first_author': [],
            'total_first_author_pubs': 0,
            'first_author_count': 0,
            'publication_titles': [],
            'publication_years': [],
            'publication_dois': [],
            'abstracts': [],
            'total_citations': 0,
            'total_downloads': 0,
            
            # Add retry info if available
            'email_retry_info': email_search.get('retry_info')
        }
        
        complete_authors[author_id] = author_record
    
    # Calculate statistics
    emails_found = sum(1 for a in complete_authors.values() if a['email_found'])
    with_affiliations = sum(1 for a in complete_authors.values() if a['all_affiliations'])
    with_biography = sum(1 for a in complete_authors.values() if a.get('biography'))
    
    # Create metadata
    metadata = {
        'creation_date': datetime.now().isoformat(),
        'source_files': {
            'email_data': 'remaining_european_authors_emails.json',
            'author_data': 'remaining_authors_enriched.json'
        },
        'description': 'Complete dataset for remaining European authors with email addresses, affiliations, and biographies',
        'total_authors': len(complete_authors),
        'emails_found': emails_found,
        'email_success_rate': f"{emails_found/len(complete_authors)*100:.1f}%",
        'statistics': {
            'total': len(complete_authors),
            'with_email': emails_found,
            'without_email': len(complete_authors) - emails_found,
            'with_affiliations': with_affiliations,
            'with_biography': with_biography,
            'with_publications': 0,  # No publications for remaining authors
            'with_abstracts': 0
        },
        'coverage': {
            'authors_with_email': f"{emails_found}/{len(complete_authors)} ({emails_found/len(complete_authors)*100:.1f}%)",
            'authors_with_affiliations': f"{with_affiliations}/{len(complete_authors)} ({with_affiliations/len(complete_authors)*100:.1f}%)",
            'authors_with_biography': f"{with_biography}/{len(complete_authors)} ({with_biography/len(complete_authors)*100:.1f}%)",
        },
        'note': 'These are remaining European authors (non-first-authors or non-European first authors). They do not have publications/abstracts in this dataset.'
    }
    
    # Create final output
    output = {
        'metadata': metadata,
        'authors': complete_authors
    }
    
    # Save
    output_file = 'results/remaining_european_authors_complete_dataset.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ COMPLETE DATASET CREATED")
    print("=" * 70)
    print(f"Output file: {output_file}")
    print(f"Total authors: {len(complete_authors):,}")
    print(f"With emails: {emails_found:,} ({emails_found/len(complete_authors)*100:.1f}%)")
    print(f"With affiliations: {with_affiliations:,} ({with_affiliations/len(complete_authors)*100:.1f}%)")
    print(f"With biography: {with_biography:,} ({with_biography/len(complete_authors)*100:.1f}%)")
    print(f"File size: {Path(output_file).stat().st_size / 1024 / 1024:.1f} MB")
    print("=" * 70)
    
    # Also create a CSV export
    print("\n📊 Creating CSV export...")
    create_csv_export(complete_authors, metadata)
    print("✅ CSV created: results/remaining_european_authors_complete_dataset.csv")


def create_csv_export(authors, metadata):
    """Create a simplified CSV version"""
    import csv
    
    output_file = 'results/remaining_european_authors_complete_dataset.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'author_id',
            'name',
            'email',
            'email_found',
            'primary_affiliation',
            'affiliation_count',
            'has_biography',
            'ieee_profile_url',
            'email_source'
        ])
        
        # Data
        for author_id, author in authors.items():
            writer.writerow([
                author_id,
                author.get('name', ''),
                author.get('email', ''),
                'Yes' if author.get('email_found') else 'No',
                author.get('primary_affiliation', ''),
                len(author.get('all_affiliations', [])),
                'Yes' if author.get('biography') else 'No',
                author.get('ieee_profile_url', ''),
                author.get('email_source', '')
            ])


if __name__ == '__main__':
    main()

