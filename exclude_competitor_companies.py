#!/usr/bin/env python3
"""
Exclude authors affiliated with competitor companies from the final datasets.
"""

import pandas as pd
import json
import os
from datetime import datetime

# Define competitor companies from Apollo.io list
# Using core company names for partial matching
COMPETITOR_COMPANIES = [
    "Keysight",  # Matches Keysight Technologies, Keysight Technologies France, etc.
    "OPAL-RT",  # Matches OPAL-RT TECHNOLOGIES, OPAL-RT Germany GmbH, etc.
    "Pulse Power and Measurement",
    "Plexim",
    "IPG Automotive",  # Matches IPG Automotive France, IPG Automotive USA Inc, etc.
    "RTDS Technologies",
    "RTDS",  # Shorter version
    "Speedgoat",
    "National Instruments",
    "Vector France",
    "Vektor Informatik",
    "Vector Informatik",  # Alternative spelling
    "ModelingTech Energy Technology",
    "ModelingTech",
    "MathWorks",  # Matches The MathWorks, Inc. and variations
    "dSPACE",
    "ALIARO"
]

def contains_competitor(affiliation_text, competitors):
    """
    Check if affiliation text contains any competitor company name.
    Case-insensitive partial matching.
    """
    if not affiliation_text or pd.isna(affiliation_text):
        return False, None
    
    affiliation_lower = str(affiliation_text).lower()
    
    for competitor in competitors:
        competitor_lower = competitor.lower()
        if competitor_lower in affiliation_lower:
            return True, competitor
    
    return False, None

def check_all_affiliations(all_affiliations_str, competitors):
    """
    Check if any affiliation in the all_affiliations field matches a competitor.
    """
    if not all_affiliations_str or pd.isna(all_affiliations_str):
        return False, None
    
    try:
        # Parse the JSON array
        affiliations = json.loads(all_affiliations_str)
        for affiliation in affiliations:
            is_match, matched_company = contains_competitor(affiliation, competitors)
            if is_match:
                return True, matched_company
    except (json.JSONDecodeError, TypeError):
        # If parsing fails, check as string
        return contains_competitor(all_affiliations_str, competitors)
    
    return False, None

def filter_csv_file(input_file, output_file, competitors):
    """
    Filter out authors affiliated with competitor companies.
    """
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(input_file)}")
    print(f"{'='*80}")
    
    # Read CSV
    print("Reading CSV file...")
    df = pd.read_csv(input_file)
    initial_count = len(df)
    print(f"Initial author count: {initial_count:,}")
    
    # Track exclusions
    excluded_authors = []
    
    # Check each author
    print("\nChecking affiliations against competitor list...")
    for idx, row in df.iterrows():
        author_name = row.get('name', 'Unknown')
        author_id = row.get('author_id', 'N/A')
        
        # Check primary affiliation
        primary_aff = row.get('primary_affiliation', '')
        is_competitor_primary, matched_primary = contains_competitor(primary_aff, competitors)
        
        # Check all affiliations
        all_aff = row.get('all_affiliations', '')
        is_competitor_all, matched_all = check_all_affiliations(all_aff, competitors)
        
        # If any match found, exclude this author
        if is_competitor_primary or is_competitor_all:
            matched_company = matched_primary or matched_all
            excluded_authors.append({
                'author_id': author_id,
                'name': author_name,
                'country': row.get('country', 'Unknown'),
                'primary_affiliation': primary_aff,
                'matched_competitor': matched_company,
                'email': row.get('email', '')
            })
    
    # Create mask for rows to keep (not in excluded list)
    excluded_ids = [author['author_id'] for author in excluded_authors]
    df_filtered = df[~df['author_id'].isin(excluded_ids)]
    
    final_count = len(df_filtered)
    excluded_count = initial_count - final_count
    
    # Save filtered CSV
    print(f"\nSaving filtered CSV to: {output_file}")
    df_filtered.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\n{'─'*80}")
    print(f"SUMMARY:")
    print(f"{'─'*80}")
    print(f"Initial authors:   {initial_count:,}")
    print(f"Excluded authors:  {excluded_count:,}")
    print(f"Remaining authors: {final_count:,}")
    print(f"Exclusion rate:    {(excluded_count/initial_count*100):.2f}%")
    
    # Print excluded authors details
    if excluded_authors:
        print(f"\n{'─'*80}")
        print(f"EXCLUDED AUTHORS ({len(excluded_authors)}):")
        print(f"{'─'*80}")
        for author in excluded_authors:
            print(f"\n• {author['name']} (ID: {author['author_id']})")
            print(f"  Country: {author['country']}")
            print(f"  Email: {author['email']}")
            print(f"  Affiliation: {author['primary_affiliation']}")
            print(f"  Matched Competitor: {author['matched_competitor']}")
    
    return {
        'file': os.path.basename(input_file),
        'initial_count': initial_count,
        'excluded_count': excluded_count,
        'final_count': final_count,
        'excluded_authors': excluded_authors
    }

def generate_exclusion_report(results, output_file):
    """
    Generate a detailed exclusion report.
    """
    print(f"\n{'='*80}")
    print(f"GENERATING EXCLUSION REPORT")
    print(f"{'='*80}")
    
    with open(output_file, 'w') as f:
        f.write("# COMPETITOR COMPANIES EXCLUSION REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## COMPETITOR COMPANIES LIST\n\n")
        for i, company in enumerate(COMPETITOR_COMPANIES, 1):
            f.write(f"{i}. {company}\n")
        
        f.write("\n## PROCESSING RESULTS\n\n")
        
        total_initial = 0
        total_excluded = 0
        total_final = 0
        all_excluded_authors = []
        
        for result in results:
            total_initial += result['initial_count']
            total_excluded += result['excluded_count']
            total_final += result['final_count']
            all_excluded_authors.extend(result['excluded_authors'])
            
            f.write(f"### {result['file']}\n\n")
            f.write(f"- Initial authors: {result['initial_count']:,}\n")
            f.write(f"- Excluded authors: {result['excluded_count']:,}\n")
            f.write(f"- Remaining authors: {result['final_count']:,}\n")
            f.write(f"- Exclusion rate: {(result['excluded_count']/result['initial_count']*100):.2f}%\n\n")
        
        f.write(f"## OVERALL SUMMARY\n\n")
        f.write(f"- Total initial authors: {total_initial:,}\n")
        f.write(f"- Total excluded authors: {total_excluded:,}\n")
        f.write(f"- Total remaining authors: {total_final:,}\n")
        f.write(f"- Overall exclusion rate: {(total_excluded/total_initial*100):.2f}%\n\n")
        
        f.write(f"## DETAILED EXCLUSION LIST ({len(all_excluded_authors)} authors)\n\n")
        
        # Group by competitor
        by_competitor = {}
        for author in all_excluded_authors:
            competitor = author['matched_competitor']
            if competitor not in by_competitor:
                by_competitor[competitor] = []
            by_competitor[competitor].append(author)
        
        for competitor, authors in sorted(by_competitor.items()):
            f.write(f"### {competitor} ({len(authors)} authors)\n\n")
            for author in authors:
                f.write(f"- **{author['name']}** (ID: {author['author_id']})\n")
                f.write(f"  - Country: {author['country']}\n")
                f.write(f"  - Email: {author['email']}\n")
                f.write(f"  - Affiliation: {author['primary_affiliation']}\n\n")
    
    print(f"Report saved to: {output_file}")

def main():
    """Main execution function."""
    print("\n" + "="*80)
    print("COMPETITOR COMPANIES EXCLUSION SCRIPT")
    print("="*80)
    print(f"\nExcluding authors affiliated with {len(COMPETITOR_COMPANIES)} competitor companies")
    
    # Define file paths
    base_dir = "/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results"
    
    files_to_process = [
        {
            'input': os.path.join(base_dir, "european_authors_non_dach_no_france_merged.csv"),
            'output': os.path.join(base_dir, "european_authors_non_dach_no_france_merged_no_competitors.csv")
        },
        {
            'input': os.path.join(base_dir, "european_authors_dach_simple.csv"),
            'output': os.path.join(base_dir, "european_authors_dach_simple_no_competitors.csv")
        }
    ]
    
    results = []
    
    # Process each file
    for file_config in files_to_process:
        if os.path.exists(file_config['input']):
            result = filter_csv_file(
                file_config['input'],
                file_config['output'],
                COMPETITOR_COMPANIES
            )
            results.append(result)
        else:
            print(f"\n⚠️  WARNING: File not found: {file_config['input']}")
    
    # Generate comprehensive report
    report_file = "/Users/miroslavjugovic/Projects/ieee-scraper/COMPETITOR_EXCLUSION_REPORT.md"
    generate_exclusion_report(results, report_file)
    
    print("\n" + "="*80)
    print("PROCESSING COMPLETE!")
    print("="*80)
    print("\nFiltered CSV files have been created with '_no_competitors' suffix")
    print(f"Detailed report: {report_file}")
    print()

if __name__ == "__main__":
    main()

