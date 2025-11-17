#!/usr/bin/env python3
"""
Extract detailed biography information for authors with competitor mentions.
"""

import csv
import sys

csv.field_size_limit(sys.maxsize)

# Author IDs to examine
authors_to_check = {
    '37279667100': 'Turkey',
    '37085584797': 'United Kingdom',
    '37085761350': 'Germany (DACH)',
    '37089698180': 'Germany (DACH)',
    '37086108437': 'Germany (DACH)',
    '37085658129': 'Germany (DACH)'
}

def find_author_in_file(filepath, author_ids, has_country=True):
    """Find specific authors and extract their details."""
    found = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            author_id = row.get('author_id', '')
            if author_id in author_ids:
                found.append({
                    'author_id': author_id,
                    'name': row.get('name', ''),
                    'country': row.get('country', 'N/A') if has_country else 'N/A',
                    'email': row.get('email', ''),
                    'primary_affiliation': row.get('primary_affiliation', ''),
                    'all_affiliations': row.get('all_affiliations', ''),
                    'biography': row.get('biography', ''),
                    'author_type': row.get('author_type', '')
                })
    
    return found

print("="*80)
print("DETAILED COMPETITOR ANALYSIS")
print("="*80)

# Search in both files
non_dach_authors = find_author_in_file(
    '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_non_dach_no_france_merged.csv',
    authors_to_check.keys(),
    has_country=True
)

dach_authors = find_author_in_file(
    '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_dach_simple.csv',
    authors_to_check.keys(),
    has_country=False
)

all_authors = non_dach_authors + dach_authors

print(f"\nFound {len(all_authors)} authors with competitor mentions\n")

for author in all_authors:
    print("="*80)
    print(f"AUTHOR ID: {author['author_id']}")
    print(f"NAME: {author['name']}")
    print(f"COUNTRY: {author['country']}")
    print(f"EMAIL: {author['email']}")
    print(f"AUTHOR TYPE: {author['author_type']}")
    print("-"*80)
    print("PRIMARY AFFILIATION:")
    print(f"  {author['primary_affiliation']}")
    print("-"*80)
    print("ALL AFFILIATIONS:")
    print(f"  {author['all_affiliations']}")
    print("-"*80)
    print("BIOGRAPHY:")
    bio = author['biography']
    if bio:
        # Split into paragraphs for better readability
        paragraphs = bio.split('\n\n')
        for para in paragraphs:
            print(f"  {para.strip()}")
            print()
    else:
        print("  (No biography)")
    print("="*80)
    print()

print("\n" + "="*80)
print("ANALYSIS & RECOMMENDATIONS:")
print("="*80)
print()
print("DEFINITELY EXCLUDE (Working at competitor companies):")
print("  1. Wael Abdullah (37086108437) - Currently at Keysight Labs")
print("  2. Sebastian Hubschneider (37085658129) - Currently at OPAL-RT Germany")
print()
print("REVIEW CAREFULLY (Past employment or tool mentions):")
print("  3. Min Luo (37085761350) - Past employment at Plexim (2012-2022)")
print("  4. Hermann Henrichfreise (37089698180) - Co-founder of dSPACE (1987-1994)")
print("  5. Hüseyin Arslan (37279667100) - Keysight in URL citation only?")
print("  6. Daniel J. Auger (37085584797) - MathWorks in URL citation only?")
print()
print("RECOMMENDATION:")
print("  - Exclude #1 and #2 (current employees)")
print("  - For #3: Past employment ended 2+ years ago - consider keeping")
print("  - For #4: Co-founder 30+ years ago, now professor - consider keeping")
print("  - For #5 and #6: Verify if mentions are just in URLs/citations")
print("="*80)

