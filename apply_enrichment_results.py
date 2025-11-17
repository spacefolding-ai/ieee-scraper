#!/usr/bin/env python3
"""
Apply enrichment results back to the original _simple.json and _simple.csv files.
"""

import json
import csv
import sys
from pathlib import Path
from collections import Counter

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")
ENRICHMENT_RESULTS = Path("/Users/miroslavjugovic/Projects/ieee-scraper/enrichment_results.json")

def main():
    print("="*60)
    print("APPLYING ENRICHMENT RESULTS")
    print("="*60)
    
    # Load enrichment results
    print("\nLoading enrichment results...")
    with open(ENRICHMENT_RESULTS, 'r') as f:
        enrichment_data = json.load(f)
    
    # Create mapping from author_id to author_type
    author_type_map = {}
    for result in enrichment_data:
        if result.get('author_type'):
            author_type_map[result['author_id']] = result['author_type']
    
    print(f"Loaded {len(author_type_map):,} enriched author types")
    
    # Process all _simple.json files
    json_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    total_updated = 0
    files_updated = 0
    
    for json_path in json_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        print(f"\nProcessing {country}...")
        
        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            authors = json.load(f)
        
        json_updated = 0
        for author in authors:
            author_id = author.get('author_id')
            if author_id in author_type_map:
                # Update if not already set or if we have a better value
                if not author.get('author_type'):
                    author['author_type'] = author_type_map[author_id]
                    json_updated += 1
        
        # Save updated JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(authors, f, indent=2, ensure_ascii=False)
        
        # Update corresponding CSV
        csv_path = json_path.with_suffix('.csv')
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                rows = list(reader)
            
            csv_updated = 0
            for row in rows:
                author_id = row.get('author_id')
                if author_id in author_type_map and not row.get('author_type'):
                    row['author_type'] = author_type_map[author_id]
                    csv_updated += 1
            
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"  Updated {json_updated} authors in JSON and CSV")
        total_updated += json_updated
        if json_updated > 0:
            files_updated += 1
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Files processed:     {len(json_files)}")
    print(f"Files updated:       {files_updated}")
    print(f"Total authors updated: {total_updated:,}")
    print("="*60)
    print("\n✅ Enrichment results successfully applied!")

if __name__ == "__main__":
    main()

