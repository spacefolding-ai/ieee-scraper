#!/usr/bin/env python3
"""
Analyze potential competitor company exclusions from the final results datasets.
This script identifies authors who have mentions of competitor companies in their
biography or affiliation fields.
"""

import csv
import re
from collections import defaultdict
import sys

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

# List of competitor companies to search for
COMPETITOR_COMPANIES = [
    "Keysight Technologies, Inc.",
    "Keysight Technologies France",
    "Keysight labs",
    "Keysight",
    "OPAL-RT Technologies",
    "OPAL-RT Germany",
    "OPAL-RT",
    "Pulse Power and Measurement Ltd",
    "Plexim GmbH",
    "Plexim",
    "IPG Automotive France",
    "IPG Automotive USA Inc",
    "IPG Automotive",
    "RTDS Technologies",
    "Speedgoat",
    "speedgoat.de",
    "National Instruments Corporation",
    "National Instruments",
    "ModelingTech Energy Technology Company",
    "ModelingTech",
    "Vector France",
    "The MathWorks, Inc.",
    "MathWorks",
    "dSPACE Company",
    "dSPACE",
    "ALIARO",
    "Vector Informatik"
]

def check_for_competitor(text, company_patterns):
    """Check if text contains any competitor company mentions."""
    if not text or text == "":
        return []
    
    found = []
    text_lower = text.lower()
    
    for company in company_patterns:
        # Create a regex pattern that matches the company name
        # but not as part of URLs or file paths
        company_lower = company.lower()
        
        # Look for the company name in the text
        if company_lower in text_lower:
            found.append(company)
    
    return found

def is_direct_affiliation(text, companies):
    """Check if any competitor company appears in affiliation fields."""
    if not text or text == "":
        return False, []
    
    found_companies = check_for_competitor(text, companies)
    return len(found_companies) > 0, found_companies

def analyze_file(filepath, has_country_column=True):
    """Analyze a CSV file for competitor mentions."""
    
    results = {
        'total_authors': 0,
        'authors_with_competitor_affiliation': [],
        'authors_with_competitor_biography': [],
        'authors_with_competitor_mention': [],
        'company_counts': defaultdict(int)
    }
    
    try:
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
                
                # Check primary affiliation
                is_primary_match, primary_companies = is_direct_affiliation(primary_affiliation, COMPETITOR_COMPANIES)
                
                # Check all affiliations
                is_all_match, all_companies = is_direct_affiliation(all_affiliations, COMPETITOR_COMPANIES)
                
                # Check biography
                is_bio_match, bio_companies = is_direct_affiliation(biography, COMPETITOR_COMPANIES)
                
                # Collect all unique companies found
                all_found_companies = set(primary_companies + all_companies + bio_companies)
                
                if all_found_companies:
                    author_info = {
                        'author_id': author_id,
                        'name': name,
                        'country': country,
                        'companies_found': list(all_found_companies),
                        'in_primary_affiliation': is_primary_match,
                        'in_all_affiliations': is_all_match,
                        'in_biography': is_bio_match,
                        'primary_affiliation': primary_affiliation[:200] if primary_affiliation else '',
                        'all_affiliations': all_affiliations[:200] if all_affiliations else '',
                        'biography_snippet': biography[:300] if biography else ''
                    }
                    
                    # Count each company
                    for company in all_found_companies:
                        results['company_counts'][company] += 1
                    
                    # Categorize based on where the mention appears
                    if is_primary_match or is_all_match:
                        results['authors_with_competitor_affiliation'].append(author_info)
                    elif is_bio_match:
                        results['authors_with_competitor_biography'].append(author_info)
                    
                    results['authors_with_competitor_mention'].append(author_info)
    
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
    
    return results

def print_analysis(filename, results):
    """Print analysis results."""
    print(f"\n{'='*80}")
    print(f"ANALYSIS FOR: {filename}")
    print(f"{'='*80}")
    
    print(f"\nTotal authors in file: {results['total_authors']}")
    print(f"Authors with competitor mentions: {len(results['authors_with_competitor_mention'])}")
    print(f"  - In affiliation fields: {len(results['authors_with_competitor_affiliation'])}")
    print(f"  - Only in biography: {len(results['authors_with_competitor_biography'])}")
    
    print(f"\n{'-'*80}")
    print("COMPANY MENTION COUNTS:")
    print(f"{'-'*80}")
    for company, count in sorted(results['company_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {company}: {count} mentions")
    
    # Print details for authors with competitor affiliations
    if results['authors_with_competitor_affiliation']:
        print(f"\n{'-'*80}")
        print("AUTHORS WITH COMPETITOR IN AFFILIATION FIELDS (HIGH PRIORITY FOR EXCLUSION):")
        print(f"{'-'*80}")
        for author in results['authors_with_competitor_affiliation']:
            print(f"\n  Author ID: {author['author_id']}")
            print(f"  Name: {author['name']}")
            print(f"  Country: {author['country']}")
            print(f"  Companies found: {', '.join(author['companies_found'])}")
            if author['in_primary_affiliation']:
                print(f"  Primary affiliation: {author['primary_affiliation']}")
            if author['in_all_affiliations']:
                print(f"  All affiliations: {author['all_affiliations'][:300]}...")
    
    # Print details for authors with mentions only in biography
    if results['authors_with_competitor_biography']:
        print(f"\n{'-'*80}")
        print("AUTHORS WITH COMPETITOR ONLY IN BIOGRAPHY (REVIEW NEEDED):")
        print(f"{'-'*80}")
        print("Note: These may be false positives (e.g., tool mentions, URLs)")
        for author in results['authors_with_competitor_biography'][:20]:  # Show first 20
            print(f"\n  Author ID: {author['author_id']}")
            print(f"  Name: {author['name']}")
            print(f"  Country: {author['country']}")
            print(f"  Companies found: {', '.join(author['companies_found'])}")
            print(f"  Biography snippet: {author['biography_snippet'][:200]}...")
        
        if len(results['authors_with_competitor_biography']) > 20:
            print(f"\n  ... and {len(results['authors_with_competitor_biography']) - 20} more")

def main():
    print("COMPETITOR COMPANY EXCLUSION ANALYSIS")
    print("="*80)
    print("\nSearching for mentions of the following companies:")
    for i, company in enumerate(COMPETITOR_COMPANIES, 1):
        print(f"  {i}. {company}")
    
    # Analyze both files
    non_dach_results = analyze_file(
        '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_non_dach_no_france_merged.csv',
        has_country_column=True
    )
    
    dach_results = analyze_file(
        '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/european_authors_dach_simple.csv',
        has_country_column=False
    )
    
    # Print results
    print_analysis("european_authors_non_dach_no_france_merged.csv", non_dach_results)
    print_analysis("european_authors_dach_simple.csv", dach_results)
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY ACROSS ALL FILES")
    print(f"{'='*80}")
    
    total_authors = non_dach_results['total_authors'] + dach_results['total_authors']
    total_with_mentions = len(non_dach_results['authors_with_competitor_mention']) + len(dach_results['authors_with_competitor_mention'])
    total_with_affiliation = len(non_dach_results['authors_with_competitor_affiliation']) + len(dach_results['authors_with_competitor_affiliation'])
    total_bio_only = len(non_dach_results['authors_with_competitor_biography']) + len(dach_results['authors_with_competitor_biography'])
    
    print(f"\nTotal authors across all files: {total_authors}")
    print(f"Total with competitor mentions: {total_with_mentions} ({total_with_mentions/total_authors*100:.2f}%)")
    print(f"  - With competitor in affiliation: {total_with_affiliation} ({total_with_affiliation/total_authors*100:.2f}%)")
    print(f"  - With competitor only in bio: {total_bio_only} ({total_bio_only/total_authors*100:.2f}%)")
    
    print("\n" + "="*80)
    print("RECOMMENDATION:")
    print("="*80)
    print(f"Authors to DEFINITELY exclude: {total_with_affiliation}")
    print("  (Those with competitor companies in their affiliation fields)")
    print(f"\nAuthors to REVIEW manually: {total_bio_only}")
    print("  (Those with mentions only in biography - may include tool/software mentions)")
    print("\n" + "="*80)

if __name__ == "__main__":
    main()

