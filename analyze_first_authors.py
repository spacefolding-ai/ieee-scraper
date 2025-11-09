#!/usr/bin/env python3
"""
Analyze unique first/main authors across all publications
"""

import json
from pathlib import Path
from collections import Counter

def analyze_first_authors():
    raw_responses_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/raw_responses')
    
    # Track first authors
    first_authors = {}  # {author_id: {name, count}}
    total_publications = 0
    
    # Process all page files
    page_files = sorted(raw_responses_dir.glob('page_*.json'))
    
    print(f"Processing {len(page_files)} files...")
    
    for page_file in page_files:
        with open(page_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get('response', {}).get('records', [])
        
        for record in records:
            authors = record.get('authors', [])
            
            if authors:  # If there are authors
                # First author is the main author
                first_author = authors[0]
                author_id = first_author.get('id')
                author_name = first_author.get('preferredName', 'Unknown')
                
                if author_id:
                    if author_id not in first_authors:
                        first_authors[author_id] = {
                            'id': author_id,
                            'name': author_name,
                            'count': 0
                        }
                    first_authors[author_id]['count'] += 1
                    total_publications += 1
    
    # Sort by count (most prolific first authors)
    sorted_first_authors = sorted(
        first_authors.values(),
        key=lambda x: x['count'],
        reverse=True
    )
    
    # Print results
    print("\n" + "="*70)
    print("FIRST/MAIN AUTHOR ANALYSIS")
    print("="*70)
    print(f"\nTotal publications analyzed: {total_publications:,}")
    print(f"Unique first authors: {len(first_authors):,}")
    print(f"\nTop 20 Most Prolific First Authors:")
    print("-"*70)
    
    for idx, author in enumerate(sorted_first_authors[:20], 1):
        print(f"{idx:2d}. {author['name']:40s} - {author['count']:3d} publications (ID: {author['id']})")
    
    print("\n" + "="*70)
    print("STATISTICS")
    print("="*70)
    
    # Calculate statistics
    counts = [a['count'] for a in first_authors.values()]
    avg_pubs = sum(counts) / len(counts)
    
    # Count distribution
    single_pub = sum(1 for c in counts if c == 1)
    two_to_five = sum(1 for c in counts if 2 <= c <= 5)
    six_to_ten = sum(1 for c in counts if 6 <= c <= 10)
    over_ten = sum(1 for c in counts if c > 10)
    
    print(f"Average publications per first author: {avg_pubs:.2f}")
    print(f"\nDistribution:")
    print(f"  1 publication:     {single_pub:5,} authors ({single_pub/len(first_authors)*100:.1f}%)")
    print(f"  2-5 publications:  {two_to_five:5,} authors ({two_to_five/len(first_authors)*100:.1f}%)")
    print(f"  6-10 publications: {six_to_ten:5,} authors ({six_to_ten/len(first_authors)*100:.1f}%)")
    print(f"  10+ publications:  {over_ten:5,} authors ({over_ten/len(first_authors)*100:.1f}%)")
    
    print("="*70)
    
    # Save detailed results
    output_file = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/first_authors_analysis.json')
    output_data = {
        'summary': {
            'total_publications': total_publications,
            'unique_first_authors': len(first_authors),
            'average_publications_per_first_author': avg_pubs,
            'distribution': {
                'single_publication': single_pub,
                'two_to_five': two_to_five,
                'six_to_ten': six_to_ten,
                'over_ten': over_ten
            }
        },
        'first_authors': sorted_first_authors
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Detailed results saved to: {output_file}")

if __name__ == '__main__':
    analyze_first_authors()

