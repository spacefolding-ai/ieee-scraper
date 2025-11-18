#!/usr/bin/env python3
"""
Count authors with and without author_type classification.
"""

import csv
import sys
from collections import Counter

csv.field_size_limit(sys.maxsize)

def count_author_types(filepath, has_country_column=True):
    """Count authors by author_type status."""
    
    total = 0
    with_type = 0
    without_type = 0
    type_counts = Counter()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total += 1
            author_type = row.get('author_type', '').strip()
            
            if author_type and author_type != '':
                with_type += 1
                type_counts[author_type] += 1
            else:
                without_type += 1
    
    return {
        'total': total,
        'with_type': with_type,
        'without_type': without_type,
        'type_counts': type_counts
    }

def print_results(name, stats):
    """Print statistics."""
    total = stats['total']
    with_type = stats['with_type']
    without_type = stats['without_type']
    
    print(f"\n{'='*80}")
    print(f"{name}")
    print(f"{'='*80}")
    print(f"\nTotal authors: {total}")
    print(f"With author_type: {with_type} ({with_type/total*100:.2f}%)")
    print(f"Without author_type: {without_type} ({without_type/total*100:.2f}%)")
    
    if stats['type_counts']:
        print(f"\n{'-'*80}")
        print("Author Type Distribution:")
        print(f"{'-'*80}")
        for author_type, count in stats['type_counts'].most_common():
            pct = count / with_type * 100
            print(f"  {author_type:<30s}: {count:>5} ({pct:>5.1f}% of classified)")

def main():
    print("="*80)
    print("AUTHOR TYPE CLASSIFICATION STATISTICS")
    print("="*80)
    
    results_dir = '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results'
    
    # Analyze power electronics authors
    print("\n📊 Analyzing POWER ELECTRONICS authors (with power terms)...")
    
    # Non-DACH
    non_dach_file = f'{results_dir}/non_dach_with_power_terms.csv'
    non_dach_stats = count_author_types(non_dach_file, has_country_column=True)
    print_results("NON-DACH (with power terms)", non_dach_stats)
    
    # DACH
    dach_file = f'{results_dir}/dach_with_power_terms.csv'
    dach_stats = count_author_types(dach_file, has_country_column=False)
    print_results("DACH (with power terms)", dach_stats)
    
    # Combined
    print(f"\n{'='*80}")
    print("COMBINED STATISTICS (ALL POWER ELECTRONICS AUTHORS)")
    print(f"{'='*80}")
    
    total_all = non_dach_stats['total'] + dach_stats['total']
    with_type_all = non_dach_stats['with_type'] + dach_stats['with_type']
    without_type_all = non_dach_stats['without_type'] + dach_stats['without_type']
    
    print(f"\nTotal authors: {total_all}")
    print(f"With author_type: {with_type_all} ({with_type_all/total_all*100:.2f}%)")
    print(f"Without author_type: {without_type_all} ({without_type_all/total_all*100:.2f}%)")
    
    # Combine type counts
    combined_types = Counter()
    combined_types.update(non_dach_stats['type_counts'])
    combined_types.update(dach_stats['type_counts'])
    
    print(f"\n{'-'*80}")
    print("Combined Author Type Distribution:")
    print(f"{'-'*80}")
    for author_type, count in combined_types.most_common():
        pct_of_classified = count / with_type_all * 100
        pct_of_total = count / total_all * 100
        print(f"  {author_type:<30s}: {count:>5} ({pct_of_classified:>5.1f}% of classified, {pct_of_total:>5.1f}% of all)")
    
    # Also check non-power authors
    print("\n\n" + "="*80)
    print("📊 Analyzing NON-POWER ELECTRONICS authors (without power terms)...")
    print("="*80)
    
    # Non-DACH without power
    non_dach_no_power_file = f'{results_dir}/non_dach_without_power_terms.csv'
    non_dach_no_power_stats = count_author_types(non_dach_no_power_file, has_country_column=True)
    print_results("NON-DACH (without power terms)", non_dach_no_power_stats)
    
    # DACH without power
    dach_no_power_file = f'{results_dir}/dach_without_power_terms.csv'
    dach_no_power_stats = count_author_types(dach_no_power_file, has_country_column=False)
    print_results("DACH (without power terms)", dach_no_power_stats)
    
    # Grand total
    print(f"\n{'='*80}")
    print("📈 GRAND TOTAL (ALL AUTHORS)")
    print(f"{'='*80}")
    
    grand_total = total_all + non_dach_no_power_stats['total'] + dach_no_power_stats['total']
    grand_with_type = with_type_all + non_dach_no_power_stats['with_type'] + dach_no_power_stats['with_type']
    grand_without_type = without_type_all + non_dach_no_power_stats['without_type'] + dach_no_power_stats['without_type']
    
    print(f"\nTotal authors: {grand_total}")
    print(f"With author_type: {grand_with_type} ({grand_with_type/grand_total*100:.2f}%)")
    print(f"Without author_type: {grand_without_type} ({grand_without_type/grand_total*100:.2f}%)")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()


