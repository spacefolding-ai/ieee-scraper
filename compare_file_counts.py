#!/usr/bin/env python3
"""
Compare author counts between regular and _simple JSON files.
"""

import json
from pathlib import Path

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def count_authors_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return len(data) if isinstance(data, list) else 0
    except Exception as e:
        return 0

# Count authors in _simple.json files
simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
regular_files = sorted(RESULTS_DIR.glob("european_authors_*.json"))
regular_files = [f for f in regular_files if not f.name.endswith("_simple.json")]

print("Comparing author counts:\n")
print(f"{'Country':<30s} {'Regular':>10s} {'Simple':>10s} {'Difference':>12s}")
print("-" * 65)

total_regular = 0
total_simple = 0

# Create a mapping
country_data = {}

for simple_file in simple_files:
    country = simple_file.stem.replace("european_authors_", "").replace("_simple", "")
    simple_count = count_authors_in_file(simple_file)
    
    # Find corresponding regular file
    regular_file = RESULTS_DIR / f"european_authors_{country}.json"
    regular_count = count_authors_in_file(regular_file) if regular_file.exists() else 0
    
    if regular_count > 0 or simple_count > 0:
        diff = regular_count - simple_count
        print(f"{country:<30s} {regular_count:>10d} {simple_count:>10d} {diff:>12d}")
        total_regular += regular_count
        total_simple += simple_count

print("-" * 65)
print(f"{'TOTAL':<30s} {total_regular:>10d} {total_simple:>10d} {total_regular - total_simple:>12d}")
print()
print(f"Number of _simple.json files: {len(simple_files)}")
print(f"Number of regular .json files: {len(regular_files)}")

