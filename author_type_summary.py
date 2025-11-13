#!/usr/bin/env python3
"""
Generate a summary report of author_type distribution across all countries.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    json_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    total_authors = 0
    authors_with_type = 0
    authors_without_type = 0
    type_distribution = Counter()
    country_stats = {}
    
    for json_path in json_files:
        # Extract country name from filename
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                authors = json.load(f)
            
            if not isinstance(authors, list):
                continue
            
            country_total = len(authors)
            country_with_type = 0
            country_types = Counter()
            
            for author in authors:
                if not isinstance(author, dict):
                    continue
                
                total_authors += 1
                author_type = author.get('author_type')
                
                if author_type:
                    authors_with_type += 1
                    type_distribution[author_type] += 1
                    country_with_type += 1
                    country_types[author_type] += 1
                else:
                    authors_without_type += 1
            
            country_stats[country] = {
                'total': country_total,
                'with_type': country_with_type,
                'percentage': (country_with_type / country_total * 100) if country_total > 0 else 0,
                'types': dict(country_types)
            }
            
        except Exception as e:
            print(f"Error processing {json_path.name}: {e}")
    
    # Print summary report
    print("=" * 80)
    print("AUTHOR TYPE EXTRACTION SUMMARY")
    print("=" * 80)
    print()
    
    print(f"Total authors processed: {total_authors:,}")
    print(f"Authors with author_type: {authors_with_type:,} ({authors_with_type/total_authors*100:.1f}%)")
    print(f"Authors without author_type: {authors_without_type:,} ({authors_without_type/total_authors*100:.1f}%)")
    print()
    
    print("-" * 80)
    print("AUTHOR TYPE DISTRIBUTION (Overall)")
    print("-" * 80)
    for author_type, count in type_distribution.most_common():
        percentage = count / authors_with_type * 100 if authors_with_type > 0 else 0
        print(f"  {author_type:30s}: {count:5d} ({percentage:5.1f}%)")
    print()
    
    print("-" * 80)
    print("AUTHOR TYPE COVERAGE BY COUNTRY")
    print("-" * 80)
    print(f"{'Country':<30s} {'Total':>8s} {'With Type':>10s} {'Coverage':>10s}")
    print("-" * 80)
    
    # Sort by percentage descending
    sorted_countries = sorted(country_stats.items(), 
                            key=lambda x: x[1]['percentage'], 
                            reverse=True)
    
    for country, stats in sorted_countries:
        if stats['total'] > 0:
            print(f"{country:<30s} {stats['total']:>8d} {stats['with_type']:>10d} {stats['percentage']:>9.1f}%")
    
    print("=" * 80)
    
    # Save detailed report to file
    report_path = RESULTS_DIR / "author_type_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'total_authors': total_authors,
                'authors_with_type': authors_with_type,
                'authors_without_type': authors_without_type
            },
            'type_distribution': dict(type_distribution),
            'country_stats': country_stats
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {report_path}")

if __name__ == "__main__":
    main()

