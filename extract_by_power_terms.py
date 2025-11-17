#!/usr/bin/env python3
"""
Extract authors into separate files based on power electronics terms.
Creates 4 files: with_terms and without_terms for both DACH and Non-DACH.
"""

import csv
import sys
import re
from datetime import datetime

csv.field_size_limit(sys.maxsize)

# Search terms (case-insensitive)
SEARCH_TERMS = [
    'verter',  # catches converter, inverter
    'switch',
    'power',
    'motor',
    'grid',
    'charging',
    'charger',
    'bms',
    'battery management',
    'active filter',
    'bess',
    'energy storage system',
    'electric drive'
]

def has_power_terms(row):
    """Check if an author has any power electronics terms."""
    primary_affiliation = row.get('primary_affiliation', '')
    all_affiliations = row.get('all_affiliations', '')
    biography = row.get('biography', '')
    all_publications = row.get('all_publications', '')
    
    # Combine all text to search
    all_text = f"{primary_affiliation} {all_affiliations} {biography} {all_publications}".lower()
    
    # Check if any term is present
    for term in SEARCH_TERMS:
        if term.lower() in all_text:
            return True
    
    return False

def split_file_by_terms(input_filepath, output_with_terms, output_without_terms, has_country_column=True):
    """Split a CSV file into two files based on power electronics terms."""
    
    with_terms_count = 0
    without_terms_count = 0
    
    with open(input_filepath, 'r', encoding='utf-8') as infile, \
         open(output_with_terms, 'w', encoding='utf-8', newline='') as with_file, \
         open(output_without_terms, 'w', encoding='utf-8', newline='') as without_file:
        
        reader = csv.DictReader(infile)
        
        # Create writers for both output files
        with_writer = csv.DictWriter(with_file, fieldnames=reader.fieldnames)
        without_writer = csv.DictWriter(without_file, fieldnames=reader.fieldnames)
        
        # Write headers
        with_writer.writeheader()
        without_writer.writeheader()
        
        for row in reader:
            if has_power_terms(row):
                with_writer.writerow(row)
                with_terms_count += 1
            else:
                without_writer.writerow(row)
                without_terms_count += 1
    
    return {
        'with_terms_count': with_terms_count,
        'without_terms_count': without_terms_count,
        'total': with_terms_count + without_terms_count
    }

def main():
    print("="*80)
    print("EXTRACTING AUTHORS BY POWER ELECTRONICS TERMS")
    print("="*80)
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nSearch terms:")
    for i, term in enumerate(SEARCH_TERMS, 1):
        print(f"  {i}. {term}")
    
    results_dir = '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results'
    
    # Process Non-DACH file
    print("\n" + "-"*80)
    print("Processing: Non-DACH file")
    print("-"*80)
    
    non_dach_input = f'{results_dir}/european_authors_non_dach_no_france_merged_no_robots.csv'
    non_dach_with = f'{results_dir}/non_dach_with_power_terms.csv'
    non_dach_without = f'{results_dir}/non_dach_without_power_terms.csv'
    
    non_dach_stats = split_file_by_terms(non_dach_input, non_dach_with, non_dach_without, has_country_column=True)
    
    print(f"Total authors: {non_dach_stats['total']}")
    print(f"  WITH power terms: {non_dach_stats['with_terms_count']} ({non_dach_stats['with_terms_count']/non_dach_stats['total']*100:.2f}%)")
    print(f"  WITHOUT power terms: {non_dach_stats['without_terms_count']} ({non_dach_stats['without_terms_count']/non_dach_stats['total']*100:.2f}%)")
    
    # Process DACH file
    print("\n" + "-"*80)
    print("Processing: DACH file")
    print("-"*80)
    
    dach_input = f'{results_dir}/european_authors_dach_simple_no_robots.csv'
    dach_with = f'{results_dir}/dach_with_power_terms.csv'
    dach_without = f'{results_dir}/dach_without_power_terms.csv'
    
    dach_stats = split_file_by_terms(dach_input, dach_with, dach_without, has_country_column=False)
    
    print(f"Total authors: {dach_stats['total']}")
    print(f"  WITH power terms: {dach_stats['with_terms_count']} ({dach_stats['with_terms_count']/dach_stats['total']*100:.2f}%)")
    print(f"  WITHOUT power terms: {dach_stats['without_terms_count']} ({dach_stats['without_terms_count']/dach_stats['total']*100:.2f}%)")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    total_authors = non_dach_stats['total'] + dach_stats['total']
    total_with = non_dach_stats['with_terms_count'] + dach_stats['with_terms_count']
    total_without = non_dach_stats['without_terms_count'] + dach_stats['without_terms_count']
    
    print(f"\nTotal authors across all files: {total_authors}")
    print(f"Total WITH power terms: {total_with} ({total_with/total_authors*100:.2f}%)")
    print(f"Total WITHOUT power terms: {total_without} ({total_without/total_authors*100:.2f}%)")
    
    print("\n" + "="*80)
    print("OUTPUT FILES CREATED")
    print("="*80)
    
    print(f"\n📁 Non-DACH Files:")
    print(f"  1. non_dach_with_power_terms.csv")
    print(f"     → {non_dach_stats['with_terms_count']} authors WITH power electronics terms")
    print(f"  2. non_dach_without_power_terms.csv")
    print(f"     → {non_dach_stats['without_terms_count']} authors WITHOUT power electronics terms")
    
    print(f"\n📁 DACH Files:")
    print(f"  3. dach_with_power_terms.csv")
    print(f"     → {dach_stats['with_terms_count']} authors WITH power electronics terms")
    print(f"  4. dach_without_power_terms.csv")
    print(f"     → {dach_stats['without_terms_count']} authors WITHOUT power electronics terms")
    
    print("\n" + "="*80)
    print("✅ EXTRACTION COMPLETE")
    print("="*80)
    
    print("\nFiles are saved in: results/final_results/")
    print("\nUse cases:")
    print("  • *_with_power_terms.csv - Target power electronics/energy researchers")
    print("  • *_without_power_terms.csv - Target other electrical engineering domains")

if __name__ == "__main__":
    main()

