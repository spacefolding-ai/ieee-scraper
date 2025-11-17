#!/usr/bin/env python3
"""
Merge all non-DACH _simple.csv files into one file.
Excludes: dach, germany, switzerland, austria
Adds a 'country' column and sorts by country.
"""

import csv
import sys
from pathlib import Path
from collections import defaultdict

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")
OUTPUT_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_non_dach_merged.csv")

# Files to exclude
EXCLUDE_FILES = [
    "european_authors_dach_simple.csv",
    "european_authors_germany_simple.csv",
    "european_authors_switzerland_simple.csv",
    "european_authors_austria_simple.csv"
]

def extract_country_from_filename(filename):
    """Extract country name from filename."""
    # Remove 'european_authors_' prefix and '_simple.csv' suffix
    country = filename.replace('european_authors_', '').replace('_simple.csv', '')
    # Replace underscores with spaces and title case
    country = country.replace('_', ' ').title()
    return country

def main():
    print("=" * 80)
    print("MERGING NON-DACH CSV FILES")
    print("=" * 80)
    
    # Find all _simple.csv files
    all_csv_files = sorted(RESULTS_DIR.glob("*_simple.csv"))
    
    # Filter out excluded files
    csv_files = [f for f in all_csv_files if f.name not in EXCLUDE_FILES]
    
    print(f"\nTotal _simple.csv files: {len(all_csv_files)}")
    print(f"Excluded files: {len(EXCLUDE_FILES)}")
    print(f"Files to merge: {len(csv_files)}")
    
    print("\nExcluded files:")
    for excluded in EXCLUDE_FILES:
        print(f"  ❌ {excluded}")
    
    print("\nFiles to include:")
    for csv_file in csv_files:
        country = extract_country_from_filename(csv_file.name)
        print(f"  ✅ {csv_file.name} → {country}")
    
    # Collect all rows with country information
    all_rows = []
    headers = None
    stats = defaultdict(int)
    
    print("\nProcessing files...")
    for csv_file in csv_files:
        country = extract_country_from_filename(csv_file.name)
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Get headers from first file
                if headers is None:
                    headers = reader.fieldnames
                
                # Read all rows and add country
                for row in reader:
                    row['country'] = country
                    all_rows.append(row)
                    stats[country] += 1
            
            print(f"  ✅ {csv_file.name}: {stats[country]} authors")
        
        except Exception as e:
            print(f"  ❌ Error processing {csv_file.name}: {e}")
            continue
    
    # Sort by country
    print("\nSorting by country...")
    all_rows.sort(key=lambda x: x['country'])
    
    # Write merged file
    print(f"\nWriting merged file: {OUTPUT_FILE}")
    
    # Add 'country' to headers at the beginning
    output_headers = ['country'] + list(headers)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_headers)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print("\n" + "=" * 80)
    print("MERGE COMPLETE")
    print("=" * 80)
    print(f"\nOutput file: {OUTPUT_FILE}")
    print(f"Total authors: {len(all_rows):,}")
    print(f"Countries included: {len(stats)}")
    
    print("\nAuthors by country:")
    for country in sorted(stats.keys()):
        print(f"  {country}: {stats[country]:,}")
    
    print("\n✅ Successfully merged all non-DACH CSV files!")

if __name__ == "__main__":
    main()

