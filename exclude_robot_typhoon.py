#!/usr/bin/env python3
"""
Exclude authors with "robot" or "typhoon hil" mentions in their biography or affiliations.
"""

import csv
import sys
import re
from datetime import datetime

csv.field_size_limit(sys.maxsize)

def should_exclude_author(row):
    """
    Check if an author should be excluded based on robot or typhoon hil mentions.
    
    Returns: (should_exclude, reasons)
    """
    primary_affiliation = row.get('primary_affiliation', '').lower()
    all_affiliations = row.get('all_affiliations', '').lower()
    biography = row.get('biography', '').lower()
    
    # Combine all text to search
    all_text = f"{primary_affiliation} {all_affiliations} {biography}"
    
    reasons = []
    
    # Check for "robot" (as whole word or part of robotics, robotic, etc.)
    if re.search(r'robot', all_text, re.IGNORECASE):
        reasons.append('robot')
    
    # Check for "typhoon hil" or "typhoon-hil" or "typhoonhil"
    if re.search(r'typhoon[\s\-]?hil', all_text, re.IGNORECASE):
        reasons.append('typhoon hil')
    
    return len(reasons) > 0, reasons

def exclude_authors_from_file(input_filepath, output_filepath, has_country_column=True):
    """
    Exclude authors with robot or typhoon hil mentions from a CSV file.
    
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
            should_exclude, reasons = should_exclude_author(row)
            
            if should_exclude:
                excluded_count += 1
                excluded_authors.append({
                    'author_id': author_id,
                    'name': row.get('name', ''),
                    'country': row.get('country', 'N/A') if has_country_column else 'N/A',
                    'reasons': reasons,
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
    print("EXCLUDING AUTHORS WITH 'ROBOT' OR 'TYPHOON HIL' MENTIONS")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nExcluding authors with mentions of:")
    print("  - 'robot' (in any form: robot, robotic, robotics, etc.)")
    print("  - 'typhoon hil' (hardware-in-the-loop testing platform)")
    
    results_dir = '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results'
    
    # Process non-DACH file
    print("\n" + "-"*80)
    print("Processing: european_authors_non_dach_no_france_merged_cleaned.csv")
    print("-"*80)
    
    non_dach_input = f'{results_dir}/european_authors_non_dach_no_france_merged_cleaned.csv'
    non_dach_output = f'{results_dir}/european_authors_non_dach_no_france_merged_no_robots.csv'
    
    non_dach_stats = exclude_authors_from_file(non_dach_input, non_dach_output, has_country_column=True)
    
    print(f"Original count: {non_dach_stats['kept_count'] + non_dach_stats['excluded_count']}")
    print(f"Excluded: {non_dach_stats['excluded_count']}")
    print(f"Kept: {non_dach_stats['kept_count']}")
    print(f"Exclusion rate: {non_dach_stats['excluded_count']/(non_dach_stats['kept_count'] + non_dach_stats['excluded_count'])*100:.2f}%")
    
    # Show sample of excluded authors
    if non_dach_stats['excluded_authors']:
        print("\nSample of excluded authors (first 10):")
        for i, author in enumerate(non_dach_stats['excluded_authors'][:10], 1):
            print(f"  {i}. {author['name']} (ID: {author['author_id']}, Country: {author['country']})")
            print(f"     Reason: {', '.join(author['reasons'])}")
            print(f"     Affiliation: {author['primary_affiliation'][:80]}...")
    
    # Process DACH file
    print("\n" + "-"*80)
    print("Processing: european_authors_dach_simple_cleaned.csv")
    print("-"*80)
    
    dach_input = f'{results_dir}/european_authors_dach_simple_cleaned.csv'
    dach_output = f'{results_dir}/european_authors_dach_simple_no_robots.csv'
    
    dach_stats = exclude_authors_from_file(dach_input, dach_output, has_country_column=False)
    
    print(f"Original count: {dach_stats['kept_count'] + dach_stats['excluded_count']}")
    print(f"Excluded: {dach_stats['excluded_count']}")
    print(f"Kept: {dach_stats['kept_count']}")
    print(f"Exclusion rate: {dach_stats['excluded_count']/(dach_stats['kept_count'] + dach_stats['excluded_count'])*100:.2f}%")
    
    # Show sample of excluded authors
    if dach_stats['excluded_authors']:
        print("\nSample of excluded authors (first 10):")
        for i, author in enumerate(dach_stats['excluded_authors'][:10], 1):
            print(f"  {i}. {author['name']} (ID: {author['author_id']})")
            print(f"     Reason: {', '.join(author['reasons'])}")
            print(f"     Affiliation: {author['primary_affiliation'][:80]}...")
    
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
    
    # Break down by reason
    robot_only = sum(1 for a in non_dach_stats['excluded_authors'] + dach_stats['excluded_authors'] 
                     if 'robot' in a['reasons'] and 'typhoon hil' not in a['reasons'])
    typhoon_only = sum(1 for a in non_dach_stats['excluded_authors'] + dach_stats['excluded_authors'] 
                       if 'typhoon hil' in a['reasons'] and 'robot' not in a['reasons'])
    both = sum(1 for a in non_dach_stats['excluded_authors'] + dach_stats['excluded_authors'] 
               if 'robot' in a['reasons'] and 'typhoon hil' in a['reasons'])
    
    print(f"\nExclusion breakdown:")
    print(f"  - 'robot' only: {robot_only}")
    print(f"  - 'typhoon hil' only: {typhoon_only}")
    print(f"  - Both: {both}")
    
    print("\n" + "="*80)
    print("OUTPUT FILES CREATED")
    print("="*80)
    print(f"\n1. {non_dach_output}")
    print(f"   ({non_dach_stats['kept_count']} authors - {non_dach_stats['excluded_count']} excluded)")
    print(f"\n2. {dach_output}")
    print(f"   ({dach_stats['kept_count']} authors - {dach_stats['excluded_count']} excluded)")
    
    print("\n" + "="*80)
    print("✅ EXCLUSION COMPLETE")
    print("="*80)
    print("\nThe cleaned files (without robot/typhoon mentions) have been created.")
    print("Review the files and if satisfied, you can use them going forward.")
    print(f"\nNote: This exclusion removed {total_excluded/total_original*100:.1f}% of your authors.")
    print("Most are likely legitimate robotics researchers, not competitors.")

if __name__ == "__main__":
    main()

