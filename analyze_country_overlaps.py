#!/usr/bin/env python3
"""
Analyze which country pairs have overlapping authors.
"""

import json
from pathlib import Path
from collections import defaultdict, Counter

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    # Track all author_ids and which countries they appear in
    author_to_countries = defaultdict(set)
    
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
                    
        except Exception as e:
            print(f"Error processing {json_path.name}: {e}")
    
    # Find all country pair combinations
    country_pair_counts = Counter()
    
    for author_id, countries in author_to_countries.items():
        if len(countries) > 1:
            # Convert to sorted tuple for consistent pairing
            country_list = sorted(countries)
            for i in range(len(country_list)):
                for j in range(i + 1, len(country_list)):
                    pair = (country_list[i], country_list[j])
                    country_pair_counts[pair] += 1
    
    print("=" * 80)
    print("COUNTRY OVERLAP ANALYSIS")
    print("=" * 80)
    print()
    print("Country pairs with shared authors:")
    print()
    
    for (country1, country2), count in country_pair_counts.most_common():
        print(f"  {country1:<25s} <-> {country2:<25s}: {count:>4d} shared authors")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()

