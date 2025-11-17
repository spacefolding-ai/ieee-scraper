#!/usr/bin/env python3
"""
Fix country labels in the merged CSV and remove French authors.
1. Reclassify "Unknown" authors to their actual countries
2. Remove all French authors
"""

import csv
import sys
from pathlib import Path
from collections import Counter

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

INPUT_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_non_dach_merged.csv")
OUTPUT_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_non_dach_no_france_merged.csv")

def detect_actual_country(affiliation):
    """Detect the actual country from affiliation string."""
    if not affiliation:
        return None
    
    aff_lower = affiliation.lower()
    
    # Country detection patterns
    patterns = {
        'France': [
            'france', 'french', 'français', 'française',
            'paris', 'marseille', 'lyon', 'toulouse', 'nice', 'nantes',
            'strasbourg', 'montpellier', 'bordeaux', 'lille', 'rennes',
            'reims', 'grenoble', 'dijon', 'angers', 'tours', 'clermont',
            'cnrs', 'cnes', 'cea', 'inria', 'inserm',
            'gif-sur-yvette', 'saclay', 'palaiseau', 'orsay',
            'centralesupélec', 'supélec'
        ],
        'United Kingdom': [
            'u.k.', ' uk ', 'u.k', 'united kingdom', 'england', 'scotland',
            'wales', 'london', 'manchester', 'birmingham', 'essex',
            'hertfordshire', 'cambridge', 'oxford', 'imperial',
            'edinburgh', 'glasgow', 'leeds', 'liverpool', 'newcastle',
            'bristol', 'southampton', 'warwick', 'durham'
        ],
        'Italy': [
            'italy', 'italia', 'italian', 'rome', 'roma', 'milan', 'milano',
            'naples', 'napoli', 'turin', 'torino', 'bologna', 'florence',
            'firenze', 'genoa', 'genova', 'venice', 'venezia'
        ],
        'Spain': [
            'spain', 'españa', 'spanish', 'madrid', 'barcelona', 'valencia',
            'seville', 'sevilla', 'málaga', 'malaga'
        ],
        'Germany': [
            'germany', 'german', 'deutschland', 'berlin', 'munich', 'münchen',
            'hamburg', 'frankfurt', 'cologne', 'köln'
        ]
    }
    
    # Check each country pattern
    for country, keywords in patterns.items():
        for keyword in keywords:
            if keyword in aff_lower:
                return country
    
    return None

def main():
    print("=" * 80)
    print("FIXING MERGED CSV COUNTRIES AND REMOVING FRENCH AUTHORS")
    print("=" * 80)
    
    # Read the merged file
    print(f"\nReading: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames
    
    print(f"Total rows before processing: {len(rows)}")
    
    # Statistics
    unknown_before = sum(1 for r in rows if r['country'] == 'Unknown')
    france_before = sum(1 for r in rows if r['country'] == 'France')
    
    print(f"  Unknown authors: {unknown_before}")
    print(f"  France authors: {france_before}")
    
    # Reclassify unknown authors
    print("\n" + "=" * 80)
    print("RECLASSIFYING 'UNKNOWN' AUTHORS")
    print("=" * 80)
    
    reclassified = Counter()
    still_unknown = 0
    
    for row in rows:
        if row['country'] == 'Unknown':
            affiliation = row.get('primary_affiliation', '')
            actual_country = detect_actual_country(affiliation)
            
            if actual_country:
                row['country'] = actual_country
                reclassified[actual_country] += 1
            else:
                still_unknown += 1
    
    print("\nReclassification results:")
    for country, count in reclassified.most_common():
        print(f"  Unknown → {country}: {count}")
    print(f"  Still Unknown: {still_unknown}")
    
    # Remove French authors
    print("\n" + "=" * 80)
    print("REMOVING FRENCH AUTHORS")
    print("=" * 80)
    
    rows_before = len(rows)
    rows = [r for r in rows if r['country'] != 'France']
    rows_after = len(rows)
    removed = rows_before - rows_after
    
    print(f"French authors removed: {removed}")
    print(f"Remaining authors: {rows_after}")
    
    # Count by country after changes
    country_counts = Counter(r['country'] for r in rows)
    
    print("\n" + "=" * 80)
    print("FINAL COUNTRY DISTRIBUTION")
    print("=" * 80)
    
    for country in sorted(country_counts.keys()):
        count = country_counts[country]
        pct = count / len(rows) * 100
        print(f"  {country}: {count} ({pct:.1f}%)")
    
    # Save updated file
    print("\n" + "=" * 80)
    print("SAVING UPDATED FILE")
    print("=" * 80)
    print(f"\nWriting: {OUTPUT_FILE}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Original file: {INPUT_FILE}")
    print(f"Updated file: {OUTPUT_FILE}")
    print(f"\nChanges:")
    print(f"  - Reclassified {sum(reclassified.values())} 'Unknown' authors")
    print(f"  - Removed {removed} French authors")
    print(f"  - Final count: {len(rows)} authors in {len(country_counts)} countries")
    print("\n✅ Successfully updated merged CSV!")

if __name__ == "__main__":
    main()

