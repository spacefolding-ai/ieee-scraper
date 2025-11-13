#!/usr/bin/env python3
"""
Find authors without author_type to enrich via web scraping.
"""

import json
from pathlib import Path

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    # Collect unique authors without author_type
    authors_without_type = {}
    
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
                author_type = author.get('author_type')
                
                # Only add if no author_type and not already added
                if author_id and not author_type and author_id not in authors_without_type:
                    authors_without_type[author_id] = {
                        'author_id': author_id,
                        'name': author.get('name'),
                        'ieee_profile_url': author.get('ieee_profile_url'),
                        'primary_affiliation': author.get('primary_affiliation'),
                        'email': author.get('email'),
                        'country': country
                    }
                    
        except Exception as e:
            print(f"Error processing {json_path.name}: {e}")
    
    print(f"Found {len(authors_without_type):,} unique authors without author_type")
    print()
    
    # Save to file for browser enrichment
    output_file = RESULTS_DIR / "authors_missing_type.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(list(authors_without_type.values()), f, indent=2, ensure_ascii=False)
    
    print(f"Saved to: {output_file}")
    print()
    
    # Show first 10 examples
    print("=" * 80)
    print("SAMPLE AUTHORS TO ENRICH (First 10):")
    print("=" * 80)
    
    for i, author in enumerate(list(authors_without_type.values())[:10], 1):
        print(f"\n{i}. {author['name']}")
        print(f"   Country: {author['country']}")
        print(f"   Affiliation: {author.get('primary_affiliation', 'N/A')}")
        print(f"   IEEE Profile: {author['ieee_profile_url']}")
        if author.get('email'):
            print(f"   Email: {author['email']}")

if __name__ == "__main__":
    main()

