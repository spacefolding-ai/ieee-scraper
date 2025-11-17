#!/usr/bin/env python3
import pandas as pd
import json

# Read the CSV
df = pd.read_csv('/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_dach_simple.csv')

# Find Wael Abdullah
author = df[df['author_id'] == 37086108437].iloc[0]

print("=" * 80)
print("WAEL ABDULLAH - DETAILED RECORD")
print("=" * 80)
print(f"\nAuthor ID: {author['author_id']}")
print(f"Name: {author['name']}")
print(f"Email: {author['email']}")
print(f"\nPrimary Affiliation:")
print(f"  {author['primary_affiliation']}")
print(f"\nAll Affiliations:")

try:
    all_affs = json.loads(author['all_affiliations'])
    for i, aff in enumerate(all_affs, 1):
        print(f"  {i}. {aff}")
        if 'keysight' in aff.lower():
            print(f"     ⚠️  MATCH: Contains 'Keysight'")
except:
    print(f"  {author['all_affiliations']}")

print("\n" + "=" * 80)

