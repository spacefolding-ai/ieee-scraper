#!/usr/bin/env python3
"""
Analyze the 378 authors without author_type to understand why and propose solutions.
"""

import json
from pathlib import Path
from collections import Counter

RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")

def main():
    # Load all unique authors without author_type
    authors_without_type = []
    
    simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    seen_ids = set()
    
    for json_path in simple_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            authors = json.load(f)
        
        for author in authors:
            author_id = author.get('author_id')
            if author_id and author_id not in seen_ids and not author.get('author_type'):
                authors_without_type.append({
                    'author_id': author_id,
                    'name': author.get('name'),
                    'email': author.get('email'),
                    'email_source': author.get('email_source'),
                    'email_citations': author.get('email_citations', []),
                    'biography': author.get('biography'),
                    'primary_affiliation': author.get('primary_affiliation'),
                    'country': country
                })
                seen_ids.add(author_id)
    
    print("="*80)
    print(f"ANALYSIS OF {len(authors_without_type)} AUTHORS WITHOUT AUTHOR_TYPE")
    print("="*80)
    print()
    
    # Analyze why they don't have types
    has_biography = sum(1 for a in authors_without_type if a['biography'])
    has_email_citations = sum(1 for a in authors_without_type if a['email_citations'])
    has_no_citations = sum(1 for a in authors_without_type if not a['email_citations'])
    
    print("AVAILABILITY OF DATA")
    print("-"*80)
    print(f"Authors with biography:           {has_biography:>4} ({has_biography/len(authors_without_type)*100:>5.1f}%)")
    print(f"Authors with email citations:     {has_email_citations:>4} ({has_email_citations/len(authors_without_type)*100:>5.1f}%)")
    print(f"Authors WITHOUT email citations:  {has_no_citations:>4} ({has_no_citations/len(authors_without_type)*100:>5.1f}%)")
    print()
    
    # Count by country
    country_counts = Counter(a['country'] for a in authors_without_type)
    
    print("DISTRIBUTION BY COUNTRY (Top 15)")
    print("-"*80)
    print(f"{'Country':<25s} {'Missing Types':>15s}")
    print("-"*80)
    for country, count in country_counts.most_common(15):
        print(f"{country:<25s} {count:>15,}")
    print()
    
    # Analyze affiliation patterns
    affiliation_types = {
        'university': 0,
        'institute': 0,
        'company': 0,
        'unknown': 0
    }
    
    for author in authors_without_type:
        affiliation = (author['primary_affiliation'] or '').lower()
        if any(term in affiliation for term in ['university', 'universit', 'college']):
            affiliation_types['university'] += 1
        elif any(term in affiliation for term in ['institute', 'institut', 'research', 'center', 'centre']):
            affiliation_types['institute'] += 1
        elif affiliation:
            affiliation_types['company'] += 1
        else:
            affiliation_types['unknown'] += 1
    
    print("AFFILIATION TYPE PATTERNS")
    print("-"*80)
    for aff_type, count in sorted(affiliation_types.items(), key=lambda x: x[1], reverse=True):
        pct = count / len(authors_without_type) * 100
        print(f"{aff_type.capitalize():<15s} {count:>4} ({pct:>5.1f}%)")
    print()
    
    # Show sample authors with different data availability
    print("="*80)
    print("SAMPLE AUTHORS BY DATA AVAILABILITY")
    print("="*80)
    
    # Sample with biography
    print("\n1. Authors WITH Biography (can re-check patterns):")
    print("-"*80)
    with_bio = [a for a in authors_without_type if a['biography']][:5]
    for i, author in enumerate(with_bio, 1):
        print(f"\n{i}. {author['name']} ({author['country']})")
        print(f"   Affiliation: {author['primary_affiliation']}")
        print(f"   Biography: {author['biography'][:150]}...")
    
    # Sample with email citations but no type found
    print("\n\n2. Authors WITH Email Citations (URLs may need manual check):")
    print("-"*80)
    with_citations = [a for a in authors_without_type if a['email_citations'] and not a['biography']][:5]
    for i, author in enumerate(with_citations, 1):
        print(f"\n{i}. {author['name']} ({author['country']})")
        print(f"   Email: {author['email']}")
        print(f"   Email source: {author['email_source']}")
        print(f"   Citations ({len(author['email_citations'])}): {author['email_citations'][0] if author['email_citations'] else 'None'}")
    
    # Sample with NO data
    print("\n\n3. Authors WITHOUT Email Citations (need alternative sources):")
    print("-"*80)
    no_data = [a for a in authors_without_type if not a['email_citations'] and not a['biography']][:5]
    for i, author in enumerate(no_data, 1):
        print(f"\n{i}. {author['name']} ({author['country']})")
        print(f"   Affiliation: {author['primary_affiliation']}")
        print(f"   Email: {author['email']}")
        print(f"   Has biography: {bool(author['biography'])}")
        print(f"   Has citations: {bool(author['email_citations'])}")
    
    print()
    print("="*80)
    print("RECOMMENDED STRATEGIES")
    print("="*80)
    print()
    print(f"Strategy 1: RE-CHECK BIOGRAPHIES ({has_biography} authors)")
    print("  - Use enhanced pattern matching")
    print("  - Look for alternative titles (e.g., 'scientist', 'engineer')")
    print("  - Check for job titles in different languages")
    print()
    print(f"Strategy 2: MANUAL URL REVIEW ({has_email_citations - has_biography} authors)")
    print("  - Manually visit email citation URLs")
    print("  - Check LinkedIn profiles")
    print("  - Search on Google Scholar with different queries")
    print()
    print(f"Strategy 3: ALTERNATIVE SOURCES ({has_no_citations} authors)")
    print("  - Search by name + affiliation on Google")
    print("  - Check university staff directories directly")
    print("  - Look up on ResearchGate, ORCID, LinkedIn")
    print("  - Check co-author papers for affiliation info")
    print()
    print(f"Strategy 4: ACCEPT LIMITATIONS")
    print("  - Some authors may be:")
    print("    * Industry researchers (no academic title)")
    print("    * Retired or moved positions")
    print("    * Using outdated affiliations")
    print("    * Privacy-conscious (minimal online presence)")
    print()
    
    # Save detailed list
    output_file = RESULTS_DIR / "authors_without_type.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(authors_without_type, f, indent=2, ensure_ascii=False)
    
    print(f"Full list saved to: {output_file}")
    print("="*80)

if __name__ == "__main__":
    main()

