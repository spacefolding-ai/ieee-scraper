#!/usr/bin/env python3
"""
Generate comprehensive final report of author type enrichment.
"""

import json
from pathlib import Path
from collections import Counter

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    # Load all authors (unique only)
    unique_authors = {}
    
    simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    for json_path in simple_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            authors = json.load(f)
        
        for author in authors:
            author_id = author.get('author_id')
            if author_id and author_id not in unique_authors:
                unique_authors[author_id] = {
                    'author_id': author_id,
                    'name': author.get('name'),
                    'author_type': author.get('author_type'),
                    'country': country,
                    'primary_affiliation': author.get('primary_affiliation')
                }
    
    # Calculate statistics
    total_unique = len(unique_authors)
    
    # Count by author type
    type_counts = Counter()
    authors_with_type = 0
    authors_without_type = 0
    
    for author_id, data in unique_authors.items():
        author_type = data['author_type']
        if author_type:
            type_counts[author_type] += 1
            authors_with_type += 1
        else:
            authors_without_type += 1
    
    # Generate report
    print("\n" + "="*80)
    print("FINAL AUTHOR TYPE ENRICHMENT REPORT")
    print("Unique Authors Only (No Duplicates)")
    print("="*80)
    print()
    
    # Overall coverage
    print("OVERALL COVERAGE")
    print("-"*80)
    print(f"Total Unique Authors:           {total_unique:>10,}")
    print(f"Authors WITH Author Type:       {authors_with_type:>10,}  ({authors_with_type/total_unique*100:>5.1f}%)")
    print(f"Authors WITHOUT Author Type:    {authors_without_type:>10,}  ({authors_without_type/total_unique*100:>5.1f}%)")
    print()
    
    # Author type breakdown
    print("="*80)
    print("AUTHOR TYPE BREAKDOWN")
    print("="*80)
    print(f"{'Author Type':<35s} {'Count':>8s} {'% of Total':>12s} {'% of Typed':>12s}")
    print("-"*80)
    
    for author_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        pct_total = count / total_unique * 100
        pct_typed = count / authors_with_type * 100 if authors_with_type > 0 else 0
        print(f"{author_type:<35s} {count:>8,} {pct_total:>11.1f}% {pct_typed:>11.1f}%")
    
    print("-"*80)
    print(f"{'TOTAL WITH TYPE':<35s} {authors_with_type:>8,} {authors_with_type/total_unique*100:>11.1f}% {'100.0%':>12s}")
    print(f"{'WITHOUT TYPE':<35s} {authors_without_type:>8,} {authors_without_type/total_unique*100:>11.1f}% {'-':>12s}")
    print("-"*80)
    print(f"{'TOTAL UNIQUE AUTHORS':<35s} {total_unique:>8,} {'100.0%':>12s} {'-':>12s}")
    print()
    
    # Category breakdown
    print("="*80)
    print("BREAKDOWN BY CATEGORY")
    print("="*80)
    
    categories = {
        'Academic Faculty': ['Professor', 'Associate Professor', 'Assistant Professor'],
        'Teaching Staff': ['Lecturer (teaching)', 'Senior Lecturer', 'Assistant Lecturer', 
                          'Teaching Assistant', 'Demonstrator'],
        'Research Staff': ['Researcher', 'Senior Researcher', 'Research fellow', 
                          'Principal investigator', 'Research group manager'],
        'Management': ['Project Manager']
    }
    
    print(f"{'Category':<30s} {'Count':>8s} {'% of Total':>12s} {'% of Typed':>12s}")
    print("-"*80)
    
    for category, types in categories.items():
        category_count = sum(type_counts[t] for t in types if t in type_counts)
        pct_total = category_count / total_unique * 100
        pct_typed = category_count / authors_with_type * 100 if authors_with_type > 0 else 0
        print(f"{category:<30s} {category_count:>8,} {pct_total:>11.1f}% {pct_typed:>11.1f}%")
    
    print()
    
    # Top countries by coverage
    print("="*80)
    print("TOP 10 COUNTRIES BY AUTHOR COUNT (with type coverage)")
    print("="*80)
    
    country_stats = {}
    for author_id, data in unique_authors.items():
        country = data['country']
        if country not in country_stats:
            country_stats[country] = {'total': 0, 'with_type': 0}
        country_stats[country]['total'] += 1
        if data['author_type']:
            country_stats[country]['with_type'] += 1
    
    sorted_countries = sorted(country_stats.items(), 
                             key=lambda x: x[1]['total'], 
                             reverse=True)[:10]
    
    print(f"{'Country':<25s} {'Total':>8s} {'With Type':>10s} {'Coverage':>10s}")
    print("-"*80)
    
    for country, stats in sorted_countries:
        coverage = stats['with_type'] / stats['total'] * 100 if stats['total'] > 0 else 0
        print(f"{country:<25s} {stats['total']:>8,} {stats['with_type']:>10,} {coverage:>9.1f}%")
    
    print()
    print("="*80)
    
    # Save detailed data to JSON
    output_file = RESULTS_DIR / "author_type_final_report.json"
    report_data = {
        'summary': {
            'total_unique_authors': total_unique,
            'authors_with_type': authors_with_type,
            'authors_without_type': authors_without_type,
            'coverage_percentage': round(authors_with_type / total_unique * 100, 2)
        },
        'type_distribution': dict(type_counts),
        'category_breakdown': {
            category: sum(type_counts[t] for t in types if t in type_counts)
            for category, types in categories.items()
        },
        'country_stats': {
            country: {
                'total': stats['total'],
                'with_type': stats['with_type'],
                'coverage': round(stats['with_type'] / stats['total'] * 100, 2) if stats['total'] > 0 else 0
            }
            for country, stats in country_stats.items()
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nDetailed report saved to: {output_file}")
    print()

if __name__ == "__main__":
    main()

