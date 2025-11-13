#!/usr/bin/env python3
"""
Calculate author type statistics for unique authors only (no duplicates).
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    # Track unique authors with their data
    unique_authors = {}
    
    for json_path in simple_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                authors = json.load(f)
            
            if not isinstance(authors, list):
                continue
            
            for author in authors:
                if not isinstance(author, dict):
                    continue
                
                author_id = author.get('author_id')
                if author_id and author_id not in unique_authors:
                    # Store first occurrence of each unique author
                    unique_authors[author_id] = {
                        'author_type': author.get('author_type'),
                        'name': author.get('name'),
                        'country': country
                    }
                    
        except Exception as e:
            print(f"Error processing {json_path.name}: {e}")
    
    # Count author types among unique authors
    type_distribution = Counter()
    authors_with_type = 0
    authors_without_type = 0
    
    for author_id, data in unique_authors.items():
        author_type = data['author_type']
        if author_type:
            type_distribution[author_type] += 1
            authors_with_type += 1
        else:
            authors_without_type += 1
    
    total_unique = len(unique_authors)
    
    print("=" * 80)
    print("AUTHOR TYPE STATISTICS - UNIQUE AUTHORS ONLY")
    print("=" * 80)
    print()
    print(f"Total unique authors: {total_unique:,}")
    print(f"Authors with author_type: {authors_with_type:,} ({authors_with_type/total_unique*100:.1f}%)")
    print(f"Authors without author_type: {authors_without_type:,} ({authors_without_type/total_unique*100:.1f}%)")
    print()
    
    print("-" * 80)
    print("AUTHOR TYPE DISTRIBUTION (Unique Authors)")
    print("-" * 80)
    print(f"{'Author Type':<35s} {'Count':>8s} {'% of Total':>12s} {'% of Typed':>12s}")
    print("-" * 80)
    
    for author_type, count in type_distribution.most_common():
        pct_total = count / total_unique * 100
        pct_typed = count / authors_with_type * 100 if authors_with_type > 0 else 0
        print(f"{author_type:<35s} {count:>8,} {pct_total:>11.1f}% {pct_typed:>11.1f}%")
    
    print("-" * 80)
    print(f"{'TOTAL WITH TYPE':<35s} {authors_with_type:>8,} {authors_with_type/total_unique*100:>11.1f}% {'100.0%':>12s}")
    print(f"{'NO TYPE':<35s} {authors_without_type:>8,} {authors_without_type/total_unique*100:>11.1f}% {'-':>12s}")
    print("-" * 80)
    print(f"{'TOTAL UNIQUE AUTHORS':<35s} {total_unique:>8,} {'100.0%':>12s} {'-':>12s}")
    print()
    
    # Compare with original stats
    print("=" * 80)
    print("COMPARISON: Unique vs All Records")
    print("=" * 80)
    print()
    print(f"{'Metric':<40s} {'All Records':>15s} {'Unique Only':>15s}")
    print("-" * 80)
    print(f"{'Total authors':<40s} {7666:>15,} {total_unique:>15,}")
    print(f"{'Authors with type':<40s} {3853:>15,} {authors_with_type:>15,}")
    print(f"{'Coverage rate':<40s} {'50.3%':>15s} {f'{authors_with_type/total_unique*100:.1f}%':>15s}")
    print()
    
    # Show breakdown by type
    print("-" * 80)
    print(f"{'Author Type':<40s} {'All Records':>15s} {'Unique Only':>15s}")
    print("-" * 80)
    
    # Original counts from all records
    original_counts = {
        "Professor": 2755,
        "Researcher": 525,
        "Research fellow": 383,
        "Lecturer (teaching)": 68,
        "Senior Lecturer": 41,
        "Project Manager": 26,
        "Research group manager": 21,
        "Principal investigator": 15,
        "Teaching Assistant": 15,
        "Demonstrator": 4
    }
    
    for author_type, original_count in original_counts.items():
        unique_count = type_distribution.get(author_type, 0)
        print(f"{author_type:<40s} {original_count:>15,} {unique_count:>15,}")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

