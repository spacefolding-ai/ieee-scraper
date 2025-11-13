#!/usr/bin/env python3
"""
Count unique authors across all country files.
"""

import json
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    # Track all author_ids and which countries they appear in
    author_to_countries = defaultdict(set)
    all_records = 0
    
    for json_path in simple_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                authors = json.load(f)
            
            if not isinstance(authors, list):
                continue
            
            for author in authors:
                if not isinstance(author, dict):
                    continue
                
                author_id = author.get('author_id')
                if author_id:
                    author_to_countries[author_id].add(country)
                    all_records += 1
                    
        except Exception as e:
            print(f"Error processing {json_path.name}: {e}")
    
    # Find duplicates (authors in multiple countries)
    duplicates = {aid: countries for aid, countries in author_to_countries.items() 
                  if len(countries) > 1}
    
    print("=" * 80)
    print("UNIQUE AUTHOR ANALYSIS")
    print("=" * 80)
    print()
    print(f"Total author records across all files: {all_records:,}")
    print(f"Unique authors (by author_id): {len(author_to_countries):,}")
    print(f"Duplicate records: {all_records - len(author_to_countries):,}")
    print()
    
    if duplicates:
        print(f"Authors appearing in multiple countries: {len(duplicates):,}")
        print()
        print("-" * 80)
        print("TOP 20 AUTHORS WITH MOST COUNTRY APPEARANCES")
        print("-" * 80)
        
        # Sort by number of countries
        sorted_duplicates = sorted(duplicates.items(), 
                                  key=lambda x: len(x[1]), 
                                  reverse=True)[:20]
        
        for author_id, countries in sorted_duplicates:
            print(f"  Author ID {author_id}: {len(countries)} countries - {', '.join(sorted(countries))}")
        
        print()
        
        # Count how many authors appear in exactly 2, 3, 4+ countries
        country_count_dist = defaultdict(int)
        for author_id, countries in duplicates.items():
            country_count_dist[len(countries)] += 1
        
        print("-" * 80)
        print("DISTRIBUTION OF MULTI-COUNTRY AUTHORS")
        print("-" * 80)
        for num_countries in sorted(country_count_dist.keys()):
            print(f"  {num_countries} countries: {country_count_dist[num_countries]:,} authors")
    else:
        print("No duplicate authors found across countries.")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

