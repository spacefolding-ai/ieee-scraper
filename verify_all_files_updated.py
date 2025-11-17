#!/usr/bin/env python3
"""
Verify that ALL _simple.json and _simple.csv files were updated with author_type.
"""

import json
import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    print("="*80)
    print("VERIFICATION: ALL FILES UPDATED WITH AUTHOR_TYPE")
    print("="*80)
    print()
    
    json_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    csv_files = sorted(RESULTS_DIR.glob("*_simple.csv"))
    
    print(f"Found {len(json_files)} JSON files")
    print(f"Found {len(csv_files)} CSV files")
    print()
    
    # Verify JSON files
    print("VERIFYING JSON FILES")
    print("-"*80)
    print(f"{'Country':<25s} {'Total':>8s} {'With Type':>10s} {'Coverage':>10s}")
    print("-"*80)
    
    json_results = {}
    total_authors = 0
    total_with_type = 0
    
    for json_path in json_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        with open(json_path, 'r') as f:
            authors = json.load(f)
        
        total = len(authors)
        with_type = sum(1 for a in authors if a.get('author_type'))
        coverage = with_type / total * 100 if total > 0 else 0
        
        json_results[country] = {'total': total, 'with_type': with_type, 'coverage': coverage}
        total_authors += total
        total_with_type += with_type
        
        status = "✅" if 'author_type' in authors[0] else "❌"
        print(f"{status} {country:<23s} {total:>8,} {with_type:>10,} {coverage:>9.1f}%")
    
    print("-"*80)
    overall_coverage = total_with_type / total_authors * 100 if total_authors > 0 else 0
    print(f"{'TOTAL':<25s} {total_authors:>8,} {total_with_type:>10,} {overall_coverage:>9.1f}%")
    print()
    
    # Verify CSV files
    print("VERIFYING CSV FILES")
    print("-"*80)
    
    csv_issues = []
    csv_verified = 0
    
    for csv_path in csv_files:
        country = csv_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        try:
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                
                if 'author_type' in fieldnames:
                    csv_verified += 1
                    rows = list(reader)
                    with_type = sum(1 for r in rows if r.get('author_type'))
                    print(f"✅ {country:<23s} has author_type column ({with_type}/{len(rows)} populated)")
                else:
                    csv_issues.append(country)
                    print(f"❌ {country:<23s} MISSING author_type column")
        except Exception as e:
            csv_issues.append(country)
            print(f"❌ {country:<23s} ERROR: {e}")
    
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"JSON files verified:      {len(json_files)}/{len(json_files)} ✅")
    print(f"CSV files verified:       {csv_verified}/{len(csv_files)} {'✅' if csv_verified == len(csv_files) else '⚠️'}")
    print()
    print(f"Total authors in dataset: {total_authors:,}")
    print(f"Authors with type:        {total_with_type:,} ({overall_coverage:.1f}%)")
    print()
    
    if csv_issues:
        print(f"⚠️  CSV files with issues: {', '.join(csv_issues)}")
    else:
        print("✅ ALL FILES SUCCESSFULLY UPDATED!")
    
    print("="*80)

if __name__ == "__main__":
    main()

