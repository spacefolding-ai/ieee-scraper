#!/usr/bin/env python3
"""
Count authors by primary affiliation and show top institutions.
"""

import csv
import sys
from collections import defaultdict
import re

csv.field_size_limit(sys.maxsize)

def clean_affiliation(affiliation):
    """Clean and normalize affiliation names."""
    if not affiliation:
        return "Unknown"
    
    # Remove common prefixes
    affiliation = re.sub(r'^(Department of|Dept\.|Faculty of|Institute of|School of|Division of|Laboratory of|Lab\.|Research Group|Center for|Centre for)\s+', '', affiliation, flags=re.IGNORECASE)
    
    # Get the main institution (usually after the last comma)
    parts = [p.strip() for p in affiliation.split(',')]
    
    # Try to identify the main institution
    for part in reversed(parts):
        # Skip country names
        if len(part) > 3 and not part.lower() in ['usa', 'u.k.', 'germany', 'belgium', 'france', 'spain', 'italy']:
            return part
    
    return parts[0] if parts else "Unknown"

def count_affiliations(filepath, has_country_column=True):
    """Count authors per affiliation."""
    
    affiliation_counts = defaultdict(list)
    total_authors = 0
    no_affiliation = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_authors += 1
            author_id = row.get('author_id', '')
            name = row.get('name', '')
            country = row.get('country', 'N/A') if has_country_column else 'N/A'
            affiliation = row.get('primary_affiliation', '')
            
            if not affiliation or affiliation.strip() == '':
                no_affiliation += 1
                affiliation = "No Affiliation Listed"
            
            # Store full affiliation for reference
            affiliation_counts[affiliation].append({
                'id': author_id,
                'name': name,
                'country': country,
                'full_affiliation': affiliation
            })
    
    return affiliation_counts, total_authors, no_affiliation

def print_top_affiliations(affiliation_counts, total_authors, top_n=30):
    """Print top N affiliations by author count."""
    
    # Sort by count
    sorted_affiliations = sorted(affiliation_counts.items(), key=lambda x: len(x[1]), reverse=True)
    
    print(f"\n{'='*100}")
    print(f"TOP {top_n} AFFILIATIONS BY AUTHOR COUNT")
    print(f"{'='*100}")
    print(f"\nTotal authors analyzed: {total_authors}")
    print(f"Unique affiliations: {len(affiliation_counts)}")
    
    print(f"\n{'Rank':<6} {'Authors':<10} {'%':<8} {'Affiliation'}")
    print("-" * 100)
    
    for i, (affiliation, authors) in enumerate(sorted_affiliations[:top_n], 1):
        count = len(authors)
        percentage = count / total_authors * 100
        
        # Truncate long affiliations
        display_affiliation = affiliation if len(affiliation) <= 70 else affiliation[:67] + "..."
        
        print(f"{i:<6} {count:<10} {percentage:>6.2f}%  {display_affiliation}")
    
    # Show sample authors from top 10 institutions
    print(f"\n{'='*100}")
    print("SAMPLE AUTHORS FROM TOP 10 INSTITUTIONS")
    print(f"{'='*100}")
    
    for i, (affiliation, authors) in enumerate(sorted_affiliations[:10], 1):
        print(f"\n{'-'*100}")
        print(f"{i}. {affiliation} ({len(authors)} authors)")
        print(f"{'-'*100}")
        
        # Show first 5 authors
        for j, author in enumerate(authors[:5], 1):
            print(f"  {j}. {author['name']} (ID: {author['id']}, Country: {author['country']})")
        
        if len(authors) > 5:
            print(f"  ... and {len(authors) - 5} more authors")

def main():
    print("="*100)
    print("AUTHORS BY AFFILIATION ANALYSIS")
    print("="*100)
    print("\nAnalyzing power electronics authors (with power terms)...\n")
    
    results_dir = '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results'
    
    # Analyze Non-DACH file
    print("-"*100)
    print("Processing: Non-DACH with power terms")
    print("-"*100)
    
    non_dach_file = f'{results_dir}/non_dach_with_power_terms.csv'
    non_dach_affiliations, non_dach_total, non_dach_no_aff = count_affiliations(non_dach_file, has_country_column=True)
    
    print(f"Total authors: {non_dach_total}")
    print(f"Authors without affiliation: {non_dach_no_aff}")
    print(f"Unique affiliations: {len(non_dach_affiliations)}")
    
    print_top_affiliations(non_dach_affiliations, non_dach_total, top_n=30)
    
    # Analyze DACH file
    print("\n\n" + "="*100)
    print("-"*100)
    print("Processing: DACH with power terms")
    print("-"*100)
    
    dach_file = f'{results_dir}/dach_with_power_terms.csv'
    dach_affiliations, dach_total, dach_no_aff = count_affiliations(dach_file, has_country_column=False)
    
    print(f"\nTotal authors: {dach_total}")
    print(f"Authors without affiliation: {dach_no_aff}")
    print(f"Unique affiliations: {len(dach_affiliations)}")
    
    print_top_affiliations(dach_affiliations, dach_total, top_n=30)
    
    # Combined analysis
    print("\n\n" + "="*100)
    print("COMBINED ANALYSIS (ALL POWER ELECTRONICS AUTHORS)")
    print("="*100)
    
    # Merge affiliation counts
    combined_affiliations = defaultdict(list)
    for aff, authors in non_dach_affiliations.items():
        combined_affiliations[aff].extend(authors)
    for aff, authors in dach_affiliations.items():
        combined_affiliations[aff].extend(authors)
    
    combined_total = non_dach_total + dach_total
    
    print(f"\nTotal authors (both datasets): {combined_total}")
    print(f"Unique affiliations: {len(combined_affiliations)}")
    
    print_top_affiliations(combined_affiliations, combined_total, top_n=30)
    
    print("\n" + "="*100)
    print("✅ ANALYSIS COMPLETE")
    print("="*100)

if __name__ == "__main__":
    main()

