#!/usr/bin/env python3
"""
Analyze null values in specified fields across all European authors JSON files.
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_null_fields():
    """Count null values for specific fields across all JSON files."""
    
    # Fields to check
    fields_to_check = [
        'domain',
        'department',
        'name_of_project',
        'last_publication_title',
        'team',
        'adequate_title',
        'author_type'
    ]
    
    # Initialize counters
    null_counts = {field: 0 for field in fields_to_check}
    total_entries = 0
    files_processed = 0
    
    # Per-file statistics
    file_stats = {}
    
    # Directory containing the JSON files
    results_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    # Process all JSON files (simple versions)
    json_files = sorted(results_dir.glob('european_authors_*_simple.json'))
    
    print(f"Found {len(json_files)} JSON files to process\n")
    
    for json_file in json_files:
        print(f"Processing: {json_file.name}...")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            file_null_counts = {field: 0 for field in fields_to_check}
            file_entries = len(data)
            
            for entry in data:
                for field in fields_to_check:
                    # Check if field is null, None, or doesn't exist
                    if entry.get(field) is None:
                        null_counts[field] += 1
                        file_null_counts[field] += 1
            
            file_stats[json_file.name] = {
                'entries': file_entries,
                'null_counts': file_null_counts
            }
            
            total_entries += file_entries
            files_processed += 1
            
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
    
    # Print summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)
    print(f"Total files processed: {files_processed}")
    print(f"Total entries analyzed: {total_entries:,}")
    print()
    
    print("NULL VALUE COUNTS:")
    print("-" * 80)
    for field in fields_to_check:
        count = null_counts[field]
        percentage = (count / total_entries * 100) if total_entries > 0 else 0
        print(f"{field:30s}: {count:8,} ({percentage:6.2f}%)")
    
    print("\n" + "="*80)
    print("NON-NULL VALUE COUNTS (for reference):")
    print("="*80)
    for field in fields_to_check:
        non_null_count = total_entries - null_counts[field]
        percentage = (non_null_count / total_entries * 100) if total_entries > 0 else 0
        print(f"{field:30s}: {non_null_count:8,} ({percentage:6.2f}%)")
    
    # Print top 5 files with most entries
    print("\n" + "="*80)
    print("TOP 5 FILES BY ENTRY COUNT:")
    print("="*80)
    sorted_files = sorted(file_stats.items(), key=lambda x: x[1]['entries'], reverse=True)[:5]
    for filename, stats in sorted_files:
        print(f"{filename:50s}: {stats['entries']:8,} entries")
    
    # Save detailed report to JSON
    report = {
        'summary': {
            'total_files': files_processed,
            'total_entries': total_entries,
            'null_counts': null_counts,
            'non_null_counts': {field: total_entries - null_counts[field] for field in fields_to_check}
        },
        'file_details': file_stats
    }
    
    report_file = results_dir / 'null_fields_analysis.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")

if __name__ == '__main__':
    analyze_null_fields()

