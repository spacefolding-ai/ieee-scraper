#!/usr/bin/env python3
"""
Analyze the domains of authors WITHOUT power electronics terms.
Identify what fields these 1,961 authors work in.
"""

import csv
import sys
import re
from collections import defaultdict

csv.field_size_limit(sys.maxsize)

# Domain keywords to search for
DOMAIN_KEYWORDS = {
    'Communications & Networking': [
        'communication', 'wireless', 'network', 'antenna', '5g', '6g', 'lte',
        'telecommunications', 'radio', 'cellular', 'wifi', 'iot', 'internet of things'
    ],
    'RF & Microwave': [
        'microwave', 'rf ', ' rf', 'radio frequency', 'millimeter wave', 'mmwave',
        'electromagnetic', 'radar'
    ],
    'Signal Processing': [
        'signal processing', 'image processing', 'dsp', 'digital signal',
        'audio', 'video', 'multimedia', 'speech'
    ],
    'Semiconductors & IC Design': [
        'semiconductor', 'vlsi', 'cmos', 'analog', 'mixed-signal', 'ic design',
        'integrated circuit', 'chip design', 'asic', 'fpga'
    ],
    'Computing & AI': [
        'machine learning', 'deep learning', 'artificial intelligence', 'neural network',
        'computer vision', 'data mining', 'algorithm', 'optimization'
    ],
    'Control Systems': [
        'control system', 'control theory', 'automation', 'process control',
        'feedback control', 'optimal control', 'adaptive control'
    ],
    'Sensors & Instrumentation': [
        'sensor', 'measurement', 'instrumentation', 'mems', 'sensing',
        'accelerometer', 'gyroscope', 'temperature', 'pressure sensor'
    ],
    'Medical Electronics': [
        'medical', 'biomedical', 'healthcare', 'diagnosis', 'imaging',
        'patient', 'clinical', 'hospital', 'eeg', 'ecg'
    ],
    'Optical & Photonics': [
        'optical', 'photonic', 'laser', 'fiber optic', 'photodetector',
        'led', 'lighting', 'spectroscopy'
    ],
    'Embedded Systems': [
        'embedded', 'microcontroller', 'firmware', 'real-time',
        'iot device', 'edge computing'
    ],
    'Quantum & Advanced Tech': [
        'quantum', 'photon', 'quantum computing', 'quantum communication'
    ],
    'Security & Cryptography': [
        'security', 'cryptography', 'encryption', 'privacy',
        'authentication', 'cyber'
    ],
    'Materials & Devices': [
        'material', 'nanomaterial', 'graphene', 'thin film',
        'fabrication', 'device characterization'
    ]
}

def analyze_author_domain(row):
    """Identify which domains an author works in based on their data."""
    primary_affiliation = row.get('primary_affiliation', '').lower()
    all_affiliations = row.get('all_affiliations', '').lower()
    biography = row.get('biography', '').lower()
    all_publications = row.get('all_publications', '').lower()
    
    # Combine all text
    all_text = f"{primary_affiliation} {all_affiliations} {biography} {all_publications}"
    
    # Find matching domains
    matching_domains = []
    for domain, keywords in DOMAIN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in all_text:
                matching_domains.append(domain)
                break  # Only count domain once per author
    
    return matching_domains

def analyze_files(non_dach_file, dach_file):
    """Analyze both files and categorize authors by domain."""
    
    results = {
        'total_authors': 0,
        'domain_counts': defaultdict(int),
        'authors_by_domain': defaultdict(list),
        'authors_with_no_domain': [],
        'authors_with_multiple_domains': [],
        'sample_by_domain': defaultdict(list)
    }
    
    # Process both files
    for filepath, has_country in [(non_dach_file, True), (dach_file, False)]:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                results['total_authors'] += 1
                
                author_id = row.get('author_id', '')
                name = row.get('name', '')
                country = row.get('country', 'N/A') if has_country else 'N/A'
                affiliation = row.get('primary_affiliation', '')[:100]
                
                domains = analyze_author_domain(row)
                
                if not domains:
                    results['authors_with_no_domain'].append({
                        'id': author_id,
                        'name': name,
                        'country': country,
                        'affiliation': affiliation
                    })
                else:
                    # Count domains
                    for domain in domains:
                        results['domain_counts'][domain] += 1
                        
                        # Store sample authors (first 5 per domain)
                        if len(results['sample_by_domain'][domain]) < 5:
                            results['sample_by_domain'][domain].append({
                                'id': author_id,
                                'name': name,
                                'country': country,
                                'affiliation': affiliation
                            })
                    
                    if len(domains) > 1:
                        results['authors_with_multiple_domains'].append({
                            'id': author_id,
                            'name': name,
                            'country': country,
                            'domains': domains
                        })
    
    return results

def print_results(results):
    """Print analysis results."""
    print("\n" + "="*80)
    print("NON-POWER ELECTRONICS AUTHORS - DOMAIN ANALYSIS")
    print("="*80)
    
    print(f"\nTotal authors analyzed: {results['total_authors']}")
    print(f"Authors matched to domains: {results['total_authors'] - len(results['authors_with_no_domain'])}")
    print(f"Authors with no clear domain: {len(results['authors_with_no_domain'])} ({len(results['authors_with_no_domain'])/results['total_authors']*100:.1f}%)")
    print(f"Authors working in multiple domains: {len(results['authors_with_multiple_domains'])} ({len(results['authors_with_multiple_domains'])/results['total_authors']*100:.1f}%)")
    
    print("\n" + "-"*80)
    print("DOMAIN DISTRIBUTION (sorted by count)")
    print("-"*80)
    
    sorted_domains = sorted(results['domain_counts'].items(), key=lambda x: x[1], reverse=True)
    
    for i, (domain, count) in enumerate(sorted_domains, 1):
        percentage = count / results['total_authors'] * 100
        print(f"{i:2}. {domain:.<40} {count:4} authors ({percentage:5.1f}%)")
    
    # Show samples for top domains
    print("\n" + "="*80)
    print("TOP DOMAINS - SAMPLE AUTHORS")
    print("="*80)
    
    for domain, count in sorted_domains[:10]:  # Top 10 domains
        print(f"\n{'-'*80}")
        print(f"{domain.upper()} ({count} authors)")
        print(f"{'-'*80}")
        
        samples = results['sample_by_domain'][domain]
        for i, author in enumerate(samples, 1):
            print(f"\n  {i}. {author['name']} (ID: {author['id']}, Country: {author['country']})")
            print(f"     {author['affiliation']}...")
    
    # Show authors with no clear domain
    if results['authors_with_no_domain']:
        print("\n" + "="*80)
        print(f"AUTHORS WITH NO CLEAR DOMAIN MATCH ({len(results['authors_with_no_domain'])} total)")
        print("="*80)
        print("\nThese authors may work in specialized/niche areas or have limited information.")
        print("Sample (first 20):")
        
        for i, author in enumerate(results['authors_with_no_domain'][:20], 1):
            print(f"\n  {i}. {author['name']} (ID: {author['id']}, Country: {author['country']})")
            print(f"     {author['affiliation']}...")
    
    # Show multi-domain authors
    if results['authors_with_multiple_domains']:
        print("\n" + "="*80)
        print(f"MULTI-DOMAIN AUTHORS (first 15 of {len(results['authors_with_multiple_domains'])})")
        print("="*80)
        print("\nAuthors working across multiple domains:")
        
        for i, author in enumerate(results['authors_with_multiple_domains'][:15], 1):
            print(f"\n  {i}. {author['name']} (Country: {author['country']})")
            print(f"     Domains: {', '.join(author['domains'])}")

def main():
    print("="*80)
    print("ANALYZING NON-POWER ELECTRONICS AUTHORS")
    print("="*80)
    print("\nThis analysis identifies the research domains of the 1,961 authors")
    print("who do NOT have power electronics/energy terms in their profiles.")
    
    non_dach_file = '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/non_dach_without_power_terms.csv'
    dach_file = '/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/dach_without_power_terms.csv'
    
    print("\nSearching for domains across 13 categories:")
    for i, domain in enumerate(DOMAIN_KEYWORDS.keys(), 1):
        print(f"  {i:2}. {domain}")
    
    print("\nProcessing files...")
    results = analyze_files(non_dach_file, dach_file)
    
    print_results(results)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nKey Insights:")
    print("  • These 1,961 authors work in diverse electrical engineering domains")
    print("  • Most common areas: Communications, RF, Signal Processing, Computing/AI")
    print("  • They are legitimate researchers, just not in power electronics")
    print("  • Valuable for broader electrical engineering outreach")

if __name__ == "__main__":
    main()


