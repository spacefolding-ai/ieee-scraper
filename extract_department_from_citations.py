#!/usr/bin/env python3
"""
Extract current department information from email citation URLs.
Priority: University profiles > Google Scholar > ORCID > Others
"""

import json
import csv
import sys
import re
from pathlib import Path

csv.field_size_limit(sys.maxsize)

# Department extraction patterns
DEPARTMENT_PATTERNS = [
    r'Department of ([^,\.;]+)',
    r'Dept\.? of ([^,\.;]+)',
    r'School of ([^,\.;]+)',
    r'Faculty of ([^,\.;]+)',
    r'Institute of ([^,\.;]+)',
    r'Division of ([^,\.;]+)',
    r'Center for ([^,\.;]+)',
    r'Centre for ([^,\.;]+)',
    r'Laboratory of ([^,\.;]+)',
    r'Lab of ([^,\.;]+)',
]

def categorize_urls(citation_list):
    """Categorize citation URLs by type"""
    university_profiles = []
    google_scholar = []
    orcid = []
    researchgate = []
    linkedin = []
    others = []
    
    for url in citation_list:
        if 'scholar.google' in url:
            google_scholar.append(url)
        elif 'orcid.org' in url:
            orcid.append(url)
        elif 'researchgate.net' in url:
            researchgate.append(url)
        elif 'linkedin.com' in url:
            linkedin.append(url)
        elif ('.edu' in url or '.ac.' in url or 
              any(x in url.lower() for x in ['university', 'universit', 'univ', '.be/en/who-is-who'])):
            university_profiles.append(url)
        else:
            others.append(url)
    
    return {
        'university': university_profiles,
        'scholar': google_scholar,
        'orcid': orcid,
        'researchgate': researchgate,
        'linkedin': linkedin,
        'others': others
    }

def get_priority_urls(categorized_urls, max_urls=3):
    """Get top priority URLs for department extraction"""
    priority_urls = []
    
    # Priority 1: University profiles (most reliable)
    priority_urls.extend(categorized_urls['university'][:2])
    
    # Priority 2: Google Scholar
    if len(priority_urls) < max_urls:
        priority_urls.extend(categorized_urls['scholar'][:1])
    
    # Priority 3: ORCID
    if len(priority_urls) < max_urls:
        priority_urls.extend(categorized_urls['orcid'][:1])
    
    # Priority 4: ResearchGate
    if len(priority_urls) < max_urls:
        priority_urls.extend(categorized_urls['researchgate'][:1])
    
    return priority_urls[:max_urls]

def prepare_authors_for_extraction():
    """Prepare list of authors who need department extraction from citations"""
    
    csv_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_non_dach_no_france_merged.csv')
    
    authors_to_enrich = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            author_id = row['author_id']
            name = row['name']
            current_dept = row.get('department', '').strip()
            citations = row.get('email_citations', '')
            
            # Skip if no citations
            if not citations or citations == '[]':
                continue
            
            try:
                citation_list = json.loads(citations)
                if not citation_list:
                    continue
                
                # Categorize URLs
                categorized = categorize_urls(citation_list)
                
                # Get priority URLs
                priority_urls = get_priority_urls(categorized)
                
                if priority_urls:
                    authors_to_enrich.append({
                        'author_id': author_id,
                        'name': name,
                        'current_department': current_dept,
                        'priority_urls': priority_urls,
                        'all_categorized_urls': categorized
                    })
            except:
                continue
    
    return authors_to_enrich

def generate_report():
    """Generate a report of authors needing department extraction"""
    
    print("="*80)
    print("DEPARTMENT EXTRACTION FROM CITATIONS - PREPARATION REPORT")
    print("="*80)
    
    authors = prepare_authors_for_extraction()
    
    # Statistics
    has_uni_profile = sum(1 for a in authors if a['all_categorized_urls']['university'])
    has_scholar = sum(1 for a in authors if a['all_categorized_urls']['scholar'])
    has_orcid = sum(1 for a in authors if a['all_categorized_urls']['orcid'])
    has_dept_already = sum(1 for a in authors if a['current_department'])
    needs_dept = sum(1 for a in authors if not a['current_department'])
    
    print(f"\nTotal authors with citations: {len(authors)}")
    print(f"Already have department: {has_dept_already} ({has_dept_already/len(authors)*100:.1f}%)")
    print(f"Need department: {needs_dept} ({needs_dept/len(authors)*100:.1f}%)")
    print(f"\nAvailable sources:")
    print(f"  University profiles: {has_uni_profile} ({has_uni_profile/len(authors)*100:.1f}%)")
    print(f"  Google Scholar: {has_scholar} ({has_scholar/len(authors)*100:.1f}%)")
    print(f"  ORCID: {has_orcid} ({has_orcid/len(authors)*100:.1f}%)")
    
    print("\n" + "="*80)
    print("SAMPLE AUTHORS WITH PRIORITY URLs FOR EXTRACTION")
    print("="*80)
    
    # Show first 10 authors needing department
    samples = [a for a in authors if not a['current_department']][:10]
    
    for i, author in enumerate(samples, 1):
        print(f"\n{i}. {author['name']} (ID: {author['author_id']})")
        print(f"   Current department: {author['current_department'] or 'MISSING'}")
        print(f"   Priority URLs to check:")
        for j, url in enumerate(author['priority_urls'], 1):
            url_type = 'University' if any(x in url.lower() for x in ['.edu', '.ac.', 'university']) else \
                       'Scholar' if 'scholar.google' in url else \
                       'ORCID' if 'orcid.org' in url else 'Other'
            print(f"      {j}. [{url_type}] {url}")
        print("-" * 80)
    
    # Save to JSON for browser-based extraction
    output_file = Path('/Users/miroslavjugovic/Projects/ieee-scraper/authors_for_citation_dept_extraction.json')
    
    # Focus on authors without department
    authors_needing_dept = [a for a in authors if not a['current_department']]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(authors_needing_dept, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*80}")
    print(f"SAVED: {len(authors_needing_dept)} authors needing department extraction")
    print(f"File: {output_file}")
    print(f"{'='*80}")
    
    # Also save all authors for verification
    all_authors_file = Path('/Users/miroslavjugovic/Projects/ieee-scraper/all_authors_for_dept_verification.json')
    with open(all_authors_file, 'w', encoding='utf-8') as f:
        json.dump(authors, f, indent=2, ensure_ascii=False)
    
    print(f"\nALSO SAVED: All {len(authors)} authors for verification")
    print(f"File: {all_authors_file}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    generate_report()


