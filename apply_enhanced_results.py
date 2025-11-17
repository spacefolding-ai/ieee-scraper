#!/usr/bin/env python3
"""
Apply the 19 enhanced pattern results to the database.
"""

import json
import csv
import sys
from pathlib import Path

csv.field_size_limit(sys.maxsize)

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")
ENHANCED_RESULTS = RESULTS_DIR / "enhanced_pattern_results.json"

def main():
    print("="*80)
    print("APPLYING 19 ENHANCED PATTERN RESULTS")
    print("="*80)
    print()
    
    # Load enhanced results
    with open(ENHANCED_RESULTS, 'r') as f:
        enhanced_data = json.load(f)
    
    print(f"Loaded {len(enhanced_data)} enhanced results")
    print()
    
    # Create mapping
    author_type_map = {
        author_id: data['author_type']
        for author_id, data in enhanced_data.items()
    }
    
    # Process all _simple.json files
    json_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    total_updated = 0
    files_updated = 0
    
    for json_path in json_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        # Load JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            authors = json.load(f)
        
        json_updated = 0
        for author in authors:
            author_id = author.get('author_id')
            if author_id in author_type_map:
                # Update if not already set
                if not author.get('author_type'):
                    author['author_type'] = author_type_map[author_id]
                    json_updated += 1
        
        if json_updated > 0:
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
                
                for row in rows:
                    author_id = row.get('author_id')
                    if author_id in author_type_map and not row.get('author_type'):
                        row['author_type'] = author_type_map[author_id]
                
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
            
            print(f"✅ {country:<25s} Updated {json_updated:>2} authors")
            total_updated += json_updated
            files_updated += 1
    
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Files processed:          {len(json_files)}")
    print(f"Files updated:            {files_updated}")
    print(f"Total authors updated:    {total_updated}")
    print("="*80)
    print()
    
    if total_updated == len(enhanced_data):
        print("✅ All 19 enhanced results successfully applied!")
    else:
        print(f"⚠️  Applied {total_updated} out of {len(enhanced_data)} results")
    
    print()

if __name__ == "__main__":
    main()

