#!/usr/bin/env python3
"""
Search for power electronics and energy-related terms in author data.
"""

import csv
import sys
import re

csv.field_size_limit(sys.maxsize)

# Search terms (case-insensitive)
SEARCH_TERMS = [
    'verter',  # catches converter, inverter
    'switch',
    'power',
    'motor',
    'grid',
    'charging',
    'charger',
    'bms',
    'battery management',
    'active filter',
    'bess',
    'energy storage system',
    'electric drive'
]

def search_terms_in_text(text, terms):
    """Check if any of the search terms appear in the text."""
    if not text:
        return False, []
    
    text_lower = text.lower()
    found_terms = []
    
    for term in terms:
        if term.lower() in text_lower:
            found_terms.append(term)
    
    return len(found_terms) > 0, found_terms

def search_in_file(filepath, has_country_column=True):
    """Search for terms in a CSV file."""
    
    results = {
        'total_authors': 0,
        'matching_authors': 0,
        'matches_by_field': {
            'affiliation_only': 0,
            'biography_only': 0,
            'publications_only': 0,
            'multiple_fields': 0
        },
        'term_counts': {term: 0 for term in SEARCH_TERMS},
        'sample_matches': []
    }
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            results['total_authors'] += 1
            
            author_id = row.get('author_id', 'unknown')
            name = row.get('name', 'unknown')
            country = row.get('country', 'N/A') if has_country_column else 'N/A'
            
            primary_affiliation = row.get('primary_affiliation', '')
            all_affiliations = row.get('all_affiliations', '')
            biography = row.get('biography', '')
            all_publications = row.get('all_publications', '')
            
            # Check each field
            has_affiliation_match, affiliation_terms = search_terms_in_text(
                f"{primary_affiliation} {all_affiliations}", SEARCH_TERMS
            )
            has_bio_match, bio_terms = search_terms_in_text(biography, SEARCH_TERMS)
            has_pub_match, pub_terms = search_terms_in_text(all_publications, SEARCH_TERMS)
            
            # Combine all found terms
            all_found_terms = set(affiliation_terms + bio_terms + pub_terms)
            
            if all_found_terms:
                results['matching_authors'] += 1
                
                # Count by field
                fields_matched = sum([has_affiliation_match, has_bio_match, has_pub_match])
                if fields_matched == 1:
                    if has_affiliation_match:
                        results['matches_by_field']['affiliation_only'] += 1
                    elif has_bio_match:
                        results['matches_by_field']['biography_only'] += 1
                    else:
                        results['matches_by_field']['publications_only'] += 1
                else:
                    results['matches_by_field']['multiple_fields'] += 1
                
                # Count each term
                for term in all_found_terms:
                    results['term_counts'][term] += 1
                
                # Store sample (first 10)
                if len(results['sample_matches']) < 10:
                    results['sample_matches'].append({
                        'author_id': author_id,
                        'name': name,
                        'country': country,
                        'terms_found': list(all_found_terms),
                        'in_affiliation': has_affiliation_match,
                        'in_biography': has_bio_match,
                        'in_publications': has_pub_match,
                        'affiliation': primary_affiliation[:100]
                    })
    
    return results

def print_results(filename, results):
    """Print search results."""
    print(f"\n{'='*80}")
    print(f"FILE: {filename}")
    print(f"{'='*80}")
    
    print(f"\nTotal authors: {results['total_authors']}")
    print(f"Authors with matching terms: {results['matching_authors']}")
    print(f"Match rate: {results['matching_authors']/results['total_authors']*100:.2f}%")
    
    print(f"\n{'-'*80}")
    print("MATCHES BY FIELD:")
    print(f"{'-'*80}")
    print(f"  Affiliation only: {results['matches_by_field']['affiliation_only']}")
    print(f"  Biography only: {results['matches_by_field']['biography_only']}")
    print(f"  Publications only: {results['matches_by_field']['publications_only']}")
    print(f"  Multiple fields: {results['matches_by_field']['multiple_fields']}")
    
    print(f"\n{'-'*80}")
    print("TOP TERMS FOUND:")
    print(f"{'-'*80}")
    sorted_terms = sorted(results['term_counts'].items(), key=lambda x: x[1], reverse=True)
    for term, count in sorted_terms[:15]:
        if count > 0:
            print(f"  {term}: {count} authors ({count/results['matching_authors']*100:.1f}% of matches)")
    
    # Show sample matches
    if results['sample_matches']:
        print(f"\n{'-'*80}")
        print(f"SAMPLE MATCHES (first 10):")
        print(f"{'-'*80}")
        for i, author in enumerate(results['sample_matches'], 1):
            print(f"\n{i}. {author['name']} (ID: {author['author_id']}, Country: {author['country']})")
            print(f"   Terms found: {', '.join(author['terms_found'][:5])}{'...' if len(author['terms_found']) > 5 else ''}")
            print(f"   Found in: ", end='')
            locations = []
            if author['in_affiliation']:
                locations.append('affiliation')
            if author['in_biography']:
                locations.append('biography')
            if author['in_publications']:
                locations.append('publications')
            print(', '.join(locations))
            print(f"   Affiliation: {author['affiliation']}...")

def main():
    print("="*80)
    print("SEARCHING FOR POWER ELECTRONICS & ENERGY TERMS")
    print("="*80)
    print("\nSearch terms:")
    for i, term in enumerate(SEARCH_TERMS, 1):
        print(f"  {i}. {term}")
    
    print("\nSearching in: affiliation, biography, and publications...")
    
    # Search in both files
    non_dach_results = search_in_file(
        '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_non_dach_no_france_merged_no_robots.csv',
        has_country_column=True
    )
    
    dach_results = search_in_file(
        '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_dach_simple_no_robots.csv',
        has_country_column=False
    )
    
    # Print results
    print_results("european_authors_non_dach_no_france_merged_no_robots.csv", non_dach_results)
    print_results("european_authors_dach_simple_no_robots.csv", dach_results)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY ACROSS ALL FILES")
    print(f"{'='*80}")
    
    total_authors = non_dach_results['total_authors'] + dach_results['total_authors']
    total_matching = non_dach_results['matching_authors'] + dach_results['matching_authors']
    total_non_matching = total_authors - total_matching
    
    print(f"\nTotal authors across all files: {total_authors}")
    print(f"Authors WITH power electronics/energy terms: {total_matching} ({total_matching/total_authors*100:.2f}%)")
    print(f"Authors WITHOUT these terms: {total_non_matching} ({total_non_matching/total_authors*100:.2f}%)")
    
    # Combined term counts
    print(f"\n{'-'*80}")
    print("COMBINED TERM STATISTICS:")
    print(f"{'-'*80}")
    combined_counts = {}
    for term in SEARCH_TERMS:
        combined_counts[term] = non_dach_results['term_counts'][term] + dach_results['term_counts'][term]
    
    sorted_combined = sorted(combined_counts.items(), key=lambda x: x[1], reverse=True)
    for term, count in sorted_combined:
        if count > 0:
            print(f"  {term}: {count} authors ({count/total_matching*100:.1f}% of matches)")
    
    print("\n" + "="*80)
    print(f"\n✓ Found {total_matching} authors working in power electronics/energy domains")
    print(f"  ({total_matching/total_authors*100:.1f}% of dataset)")

if __name__ == "__main__":
    main()

