#!/usr/bin/env python3
"""
Exclude authors with competitor company associations from the final results.
"""

import csv
import sys
import os
from datetime import datetime

csv.field_size_limit(sys.maxsize)

# Authors to exclude (based on competitor company associations)
AUTHORS_TO_EXCLUDE = {
    '37086108437',  # Wael Abdullah - Currently at Keysight Labs
    '37085658129',  # Sebastian Hubschneider - Currently at OPAL-RT Germany
    '37085761350',  # Min Luo - Past Plexim employment (2012-2022)
    '37089698180',  # Hermann Henrichfreise - Past dSPACE co-founder (1987-1994)
}

def exclude_authors_from_file(input_filepath, output_filepath, has_country_column=True):
    """
    Exclude specified authors from a CSV file.
    
    Args:
        input_filepath: Path to input CSV file
        output_filepath: Path to output CSV file
        has_country_column: Whether the CSV has a country column
    
    Returns:
        dict with statistics
    """
    excluded_count = 0
    kept_count = 0
    excluded_authors = []
    
    with open(input_filepath, 'r', encoding='utf-8') as infile, \
         open(output_filepath, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
        writer.writeheader()
        
        for row in reader:
            author_id = row.get('author_id', '')
            
            if author_id in AUTHORS_TO_EXCLUDE:
                excluded_count += 1
                excluded_authors.append({
                    'author_id': author_id,
                    'name': row.get('name', ''),
                    'country': row.get('country', 'N/A') if has_country_column else 'N/A',
                    'primary_affiliation': row.get('primary_affiliation', '')[:100]
                })
            else:
                writer.writerow(row)
                kept_count += 1
    
    return {
        'excluded_count': excluded_count,
        'kept_count': kept_count,
        'excluded_authors': excluded_authors
    }

def main():
    print("="*80)
    print("COMPETITOR AUTHOR EXCLUSION")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nExcluding {len(AUTHORS_TO_EXCLUDE)} authors with competitor company associations:")
    print("  1. Wael Abdullah (37086108437) - Keysight Labs")
    print("  2. Sebastian Hubschneider (37085658129) - OPAL-RT Germany")
    print("  3. Min Luo (37085761350) - Past Plexim employment")
    print("  4. Hermann Henrichfreise (37089698180) - Past dSPACE co-founder")
    
    results_dir = '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results'
    
    # Process non-DACH file
    print("\n" + "-"*80)
    print("Processing: european_authors_non_dach_no_france_merged.csv")
    print("-"*80)
    
    non_dach_input = os.path.join(results_dir, 'european_authors_non_dach_no_france_merged.csv')
    non_dach_output = os.path.join(results_dir, 'european_authors_non_dach_no_france_merged_cleaned.csv')
    
    non_dach_stats = exclude_authors_from_file(non_dach_input, non_dach_output, has_country_column=True)
    
    print(f"Original count: {non_dach_stats['kept_count'] + non_dach_stats['excluded_count']}")
    print(f"Excluded: {non_dach_stats['excluded_count']}")
    print(f"Kept: {non_dach_stats['kept_count']}")
    
    if non_dach_stats['excluded_authors']:
        print("\nExcluded authors from this file:")
        for author in non_dach_stats['excluded_authors']:
            print(f"  - {author['name']} (ID: {author['author_id']}, Country: {author['country']})")
    
    # Process DACH file
    print("\n" + "-"*80)
    print("Processing: european_authors_dach_simple.csv")
    print("-"*80)
    
    dach_input = os.path.join(results_dir, 'european_authors_dach_simple.csv')
    dach_output = os.path.join(results_dir, 'european_authors_dach_simple_cleaned.csv')
    
    dach_stats = exclude_authors_from_file(dach_input, dach_output, has_country_column=False)
    
    print(f"Original count: {dach_stats['kept_count'] + dach_stats['excluded_count']}")
    print(f"Excluded: {dach_stats['excluded_count']}")
    print(f"Kept: {dach_stats['kept_count']}")
    
    if dach_stats['excluded_authors']:
        print("\nExcluded authors from this file:")
        for author in dach_stats['excluded_authors']:
            print(f"  - {author['name']} (ID: {author['author_id']})")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_excluded = non_dach_stats['excluded_count'] + dach_stats['excluded_count']
    total_kept = non_dach_stats['kept_count'] + dach_stats['kept_count']
    total_original = total_excluded + total_kept
    
    print(f"\nTotal authors (original): {total_original}")
    print(f"Total excluded: {total_excluded} ({total_excluded/total_original*100:.2f}%)")
    print(f"Total kept: {total_kept} ({total_kept/total_original*100:.2f}%)")
    
    print("\n" + "="*80)
    print("OUTPUT FILES CREATED")
    print("="*80)
    print(f"\n1. {non_dach_output}")
    print(f"   ({non_dach_stats['kept_count']} authors)")
    print(f"\n2. {dach_output}")
    print(f"   ({dach_stats['kept_count']} authors)")
    
    print("\n" + "="*80)
    print("✅ EXCLUSION COMPLETE")
    print("="*80)
    print("\nThe cleaned files have been created with the '_cleaned' suffix.")
    print("Review the files and if satisfied, you can rename them to replace the originals.")

if __name__ == "__main__":
    main()

