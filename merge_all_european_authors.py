#!/usr/bin/env python3
"""
Merge authors_complete_dataset.json and remaining_european_authors_complete_dataset.json
into one complete European authors dataset
"""

import json
from datetime import datetime
from pathlib import Path

def main():
    print("🔄 Merging all European author datasets...")
    print("=" * 70)
    
    # Load first authors dataset
    print("Loading authors_complete_dataset.json...")
    with open('results/authors_complete_dataset.json', 'r') as f:
        first_authors_data = json.load(f)
    
    # Load remaining European authors dataset
    print("Loading remaining_european_authors_complete_dataset.json...")
    with open('results/remaining_european_authors_complete_dataset.json', 'r') as f:
        remaining_data = json.load(f)
    
    first_authors = first_authors_data.get('authors', {})
    remaining_authors = remaining_data.get('authors', {})
    
    print(f"\nDataset 1 (First authors): {len(first_authors):,} authors")
    print(f"Dataset 2 (Remaining European): {len(remaining_authors):,} authors")
    
    # Check for overlap
    overlap = set(first_authors.keys()) & set(remaining_authors.keys())
    if overlap:
        print(f"\n⚠️  Warning: {len(overlap)} authors appear in both datasets")
        print(f"   Using data from first authors dataset for these authors")
    
    # Merge authors (first authors take precedence)
    all_authors = {}
    all_authors.update(remaining_authors)  # Add remaining first
    all_authors.update(first_authors)  # Then add first authors (overwrites duplicates)
    
    print(f"\n✅ Total unique authors after merge: {len(all_authors):,}")
    
    # Calculate combined statistics
    total_emails = sum(1 for a in all_authors.values() if a.get('email_found', False))
    total_with_pubs = sum(1 for a in all_authors.values() if a.get('total_publications', 0) > 0)
    total_with_abstracts = sum(1 for a in all_authors.values() if a.get('abstracts') and len(a.get('abstracts', [])) > 0)
    total_with_bio = sum(1 for a in all_authors.values() if a.get('biography'))
    total_with_affiliations = sum(1 for a in all_authors.values() if a.get('all_affiliations'))
    
    # Count publications
    total_publications = 0
    total_first_author_pubs = 0
    total_citations = 0
    total_downloads = 0
    
    for author in all_authors.values():
        total_publications += author.get('total_publications', 0)
        total_first_author_pubs += author.get('total_first_author_pubs', 0)
        total_citations += author.get('total_citations', 0)
        total_downloads += author.get('total_downloads', 0)
    
    # Create combined metadata
    metadata = {
        'creation_date': datetime.now().isoformat(),
        'source_files': {
            'first_authors': 'authors_complete_dataset.json',
            'remaining_european': 'remaining_european_authors_complete_dataset.json'
        },
        'description': 'Complete merged dataset of ALL European authors with emails, affiliations, biographies, and publications',
        'total_authors': len(all_authors),
        'emails_found': total_emails,
        'email_success_rate': f"{total_emails/len(all_authors)*100:.1f}%",
        'statistics': {
            'total': len(all_authors),
            'with_email': total_emails,
            'without_email': len(all_authors) - total_emails,
            'with_publications': total_with_pubs,
            'with_abstracts': total_with_abstracts,
            'with_biography': total_with_bio,
            'with_affiliations': total_with_affiliations,
            'total_publications': total_publications,
            'total_first_author_publications': total_first_author_pubs,
            'total_citations': total_citations,
            'total_downloads': total_downloads
        },
        'coverage': {
            'authors_with_email': f"{total_emails}/{len(all_authors)} ({total_emails/len(all_authors)*100:.1f}%)",
            'authors_with_publications': f"{total_with_pubs}/{len(all_authors)} ({total_with_pubs/len(all_authors)*100:.1f}%)",
            'authors_with_abstracts': f"{total_with_abstracts}/{len(all_authors)} ({total_with_abstracts/len(all_authors)*100:.1f}%)",
            'authors_with_biography': f"{total_with_bio}/{len(all_authors)} ({total_with_bio/len(all_authors)*100:.1f}%)",
            'authors_with_affiliations': f"{total_with_affiliations}/{len(all_authors)} ({total_with_affiliations/len(all_authors)*100:.1f}%)"
        },
        'breakdown': {
            'first_authors_with_full_abstracts': len(first_authors),
            'remaining_european_authors': len(remaining_authors),
            'overlap_resolved': len(overlap)
        }
    }
    
    # Create final output
    output = {
        'metadata': metadata,
        'authors': all_authors
    }
    
    # Save
    output_file = 'results/all_european_authors_complete.json'
    print("\n💾 Saving merged dataset...")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    file_size = Path(output_file).stat().st_size / 1024 / 1024
    
    print("\n✅ MERGE COMPLETED")
    print("=" * 70)
    print(f"Output file: {output_file}")
    print(f"File size: {file_size:.1f} MB")
    print(f"\n📊 COMBINED STATISTICS:")
    print(f"  Total authors: {len(all_authors):,}")
    print(f"  With emails: {total_emails:,} ({total_emails/len(all_authors)*100:.1f}%)")
    print(f"  With publications: {total_with_pubs:,} ({total_with_pubs/len(all_authors)*100:.1f}%)")
    print(f"  With abstracts: {total_with_abstracts:,} ({total_with_abstracts/len(all_authors)*100:.1f}%)")
    print(f"  With biography: {total_with_bio:,} ({total_with_bio/len(all_authors)*100:.1f}%)")
    print(f"  With affiliations: {total_with_affiliations:,} ({total_with_affiliations/len(all_authors)*100:.1f}%)")
    print(f"\n📚 PUBLICATIONS:")
    print(f"  Total publications: {total_publications:,}")
    print(f"  First author publications: {total_first_author_pubs:,}")
    print(f"  Total citations: {total_citations:,}")
    print(f"  Total downloads: {total_downloads:,}")
    print("=" * 70)
    
    # Create CSV export
    print("\n📊 Creating CSV export...")
    create_csv_export(all_authors)
    print("✅ CSV created: results/all_european_authors_complete.csv")
    
    print("\n" + "=" * 70)
    print("✅ ALL EUROPEAN AUTHORS MERGED SUCCESSFULLY!")
    print("=" * 70)


def create_csv_export(authors):
    """Create a simplified CSV version"""
    import csv
    
    output_file = 'results/all_european_authors_complete.csv'
    
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
            'total_publications',
            'first_author_publications',
            'non_first_author_publications',
            'total_citations',
            'total_downloads',
            'ieee_profile_url'
        ])
        
        # Data
        for author_id, author in sorted(authors.items()):
            writer.writerow([
                author_id,
                author.get('name', ''),
                author.get('email', ''),
                'Yes' if author.get('email_found') else 'No',
                author.get('primary_affiliation', ''),
                len(author.get('all_affiliations', [])),
                'Yes' if author.get('biography') else 'No',
                author.get('total_publications', 0),
                author.get('total_first_author_pubs', 0),
                author.get('total_non_first_author_pubs', 0),
                author.get('total_citations', 0),
                author.get('total_downloads', 0),
                author.get('ieee_profile_url', '')
            ])


if __name__ == '__main__':
    main()

