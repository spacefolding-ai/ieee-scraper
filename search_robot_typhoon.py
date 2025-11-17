#!/usr/bin/env python3
"""
Search for mentions of "robot" or "typhoon hil" in author biographies and affiliations.
"""

import csv
import sys
import re

csv.field_size_limit(sys.maxsize)

def search_terms_in_file(filepath, has_country_column=True):
    """Search for robot and typhoon hil mentions in a CSV file."""
    
    results = {
        'total_authors': 0,
        'robot_mentions': [],
        'typhoon_mentions': [],
        'both_mentions': []
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            results['total_authors'] += 1
            
            author_id = row.get('author_id', 'unknown')
            name = row.get('name', 'unknown')
            country = row.get('country', 'N/A') if has_country_column else 'N/A'
            
            primary_affiliation = row.get('primary_affiliation', '').lower()
            all_affiliations = row.get('all_affiliations', '').lower()
            biography = row.get('biography', '').lower()
            
            # Combine all text to search
            all_text = f"{primary_affiliation} {all_affiliations} {biography}"
            
            # Check for "robot" (as whole word or part of robotics, robotic, etc.)
            has_robot = bool(re.search(r'robot', all_text, re.IGNORECASE))
            
            # Check for "typhoon hil" or "typhoon-hil" or "typhoonhil"
            has_typhoon = bool(re.search(r'typhoon[\s\-]?hil', all_text, re.IGNORECASE))
            
            if has_robot or has_typhoon:
                author_info = {
                    'author_id': author_id,
                    'name': name,
                    'country': country,
                    'primary_affiliation': row.get('primary_affiliation', ''),
                    'all_affiliations': row.get('all_affiliations', '')[:300],
                    'biography': row.get('biography', '')[:500]
                }
                
                if has_robot:
                    results['robot_mentions'].append(author_info)
                if has_typhoon:
                    results['typhoon_mentions'].append(author_info)
                if has_robot and has_typhoon:
                    results['both_mentions'].append(author_info)
    
    return results

def print_results(filename, results):
    """Print search results."""
    print(f"\n{'='*80}")
    print(f"FILE: {filename}")
    print(f"{'='*80}")
    
    print(f"\nTotal authors: {results['total_authors']}")
    print(f"Authors with 'robot' mentions: {len(results['robot_mentions'])}")
    print(f"Authors with 'typhoon hil' mentions: {len(results['typhoon_mentions'])}")
    print(f"Authors with BOTH mentions: {len(results['both_mentions'])}")
    
    # Show some examples of robot mentions
    if results['robot_mentions']:
        print(f"\n{'-'*80}")
        print(f"EXAMPLES OF 'ROBOT' MENTIONS (showing first 10):")
        print(f"{'-'*80}")
        for i, author in enumerate(results['robot_mentions'][:10], 1):
            print(f"\n{i}. {author['name']} (ID: {author['author_id']}, Country: {author['country']})")
            print(f"   Affiliation: {author['primary_affiliation'][:150]}")
            if author['biography']:
                bio_snippet = author['biography'][:200].replace('\n', ' ')
                print(f"   Biography: {bio_snippet}...")
        
        if len(results['robot_mentions']) > 10:
            print(f"\n   ... and {len(results['robot_mentions']) - 10} more")
    
    # Show typhoon hil mentions
    if results['typhoon_mentions']:
        print(f"\n{'-'*80}")
        print(f"'TYPHOON HIL' MENTIONS:")
        print(f"{'-'*80}")
        for i, author in enumerate(results['typhoon_mentions'], 1):
            print(f"\n{i}. {author['name']} (ID: {author['author_id']}, Country: {author['country']})")
            print(f"   Affiliation: {author['primary_affiliation']}")
            if author['biography']:
                bio_snippet = author['biography'][:300].replace('\n', ' ')
                print(f"   Biography: {bio_snippet}...")

def main():
    print("="*80)
    print("SEARCHING FOR 'ROBOT' AND 'TYPHOON HIL' MENTIONS")
    print("="*80)
    print("\nSearching in affiliation and biography fields...")
    
    # Search in both files
    non_dach_results = search_terms_in_file(
        '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_non_dach_no_france_merged_cleaned.csv',
        has_country_column=True
    )
    
    dach_results = search_terms_in_file(
        '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_dach_simple_cleaned.csv',
        has_country_column=False
    )
    
    # Print results
    print_results("european_authors_non_dach_no_france_merged_cleaned.csv", non_dach_results)
    print_results("european_authors_dach_simple_cleaned.csv", dach_results)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY ACROSS ALL FILES")
    print(f"{'='*80}")
    
    total_authors = non_dach_results['total_authors'] + dach_results['total_authors']
    total_robot = len(non_dach_results['robot_mentions']) + len(dach_results['robot_mentions'])
    total_typhoon = len(non_dach_results['typhoon_mentions']) + len(dach_results['typhoon_mentions'])
    total_both = len(non_dach_results['both_mentions']) + len(dach_results['both_mentions'])
    
    print(f"\nTotal authors across all files: {total_authors}")
    print(f"Total with 'robot' mentions: {total_robot} ({total_robot/total_authors*100:.2f}%)")
    print(f"Total with 'typhoon hil' mentions: {total_typhoon} ({total_typhoon/total_authors*100:.2f}%)")
    print(f"Total with BOTH mentions: {total_both} ({total_both/total_authors*100:.2f}%)")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

