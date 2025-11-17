#!/usr/bin/env python3
"""
Update domain field in CSV files using fixed extraction logic.
Applies word boundary matching for short keywords (≤3 chars) to eliminate false positives.
"""

import json
import csv
import sys
import re
from pathlib import Path
from collections import Counter

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)

# Domain keywords (same as extract_additional_properties.py, with AI removed)
DOMAIN_KEYWORDS = {
    'power_systems': ['power system', 'power grid', 'electrical grid', 'smart grid', 'power network'],
    'renewable_energy': ['renewable energy', 'solar', 'photovoltaic', 'wind energy', 'wind power', 'PV system'],
    'microgrids': ['microgrid', 'micro-grid', 'distributed generation'],
    'electric_vehicles': ['electric vehicle', 'EV', 'charging station', 'EV charger', 'battery management'],
    'power_electronics': ['power electronic', 'converter', 'inverter', 'rectifier', 'DC-DC', 'AC-DC'],
    'energy_storage': ['energy storage', 'battery', 'ESS', 'storage system'],
    'machine_learning': ['machine learning', 'deep learning', 'neural network', 'artificial intelligence'],
    'control_systems': ['control system', 'controller', 'control strategy', 'model predictive control', 'MPC'],
    'optimization': ['optimization', 'optimal', 'scheduling', 'dispatch'],
    'smart_grid': ['smart grid', 'demand response', 'demand side management', 'DSM'],
    'power_quality': ['power quality', 'harmonics', 'voltage stability', 'frequency control'],
    'hvdc': ['HVDC', 'high voltage DC', 'DC transmission'],
    'protection': ['protection', 'relay', 'fault detection', 'fault diagnosis'],
    'forecasting': ['forecast', 'prediction', 'estimation'],
    'iot': ['IoT', 'Internet of Things', 'wireless sensor', 'WSN'],
    '5g_6g': ['5G', '6G', 'wireless communication', 'mobile network'],
    'cybersecurity': ['cybersecurity', 'cyber security', 'cyber-physical', 'security'],
}


def extract_domain_fixed(all_publications_json):
    """
    Extract research domain from publications using FIXED logic.
    - AI keyword removed
    - Word boundaries for short keywords (≤3 chars)
    """
    if not all_publications_json or all_publications_json == '[]':
        return None
    
    try:
        all_pubs = json.loads(all_publications_json)
    except:
        return None
    
    if not all_pubs:
        return None
    
    # Collect all text from titles and abstracts
    text_corpus = []
    for pub in all_pubs:
        title = pub.get('title', '') or pub.get('article_title', '') or ''
        abstract = pub.get('abstract', '') or ''
        text_corpus.append((title + ' ' + abstract).lower())
    
    combined_text = ' '.join(text_corpus)
    
    # Count domain keyword occurrences
    domain_scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Use word boundaries for short keywords (3 chars or less) to avoid false positives
            # e.g., "EV" should not match "develop", "whatever", "level"
            if len(keyword) <= 3:
                # Use regex with word boundaries for short keywords
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = re.findall(pattern, combined_text, re.IGNORECASE)
                count = len(matches)
            else:
                # Use substring matching for longer keywords (safer)
                count = combined_text.count(keyword.lower())
            score += count
        
        if score > 0:
            domain_scores[domain] = score
    
    # Get top 3 domains
    if domain_scores:
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        # Return top 3 domains as comma-separated string
        top_domains = [domain.replace('_', ' ').title() for domain, score in sorted_domains[:3] if score > 0]
        if top_domains:
            return ', '.join(top_domains)
    
    return None


def update_csv_file(csv_path):
    """Update domain field in a CSV file"""
    print(f"\n{'='*80}")
    print(f"Processing: {csv_path.name}")
    print(f"{'='*80}")
    
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        return
    
    # Read CSV
    print("Reading CSV...")
    with open(csv_path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    print(f"  Total authors: {len(rows)}")
    
    # Track changes
    updated_count = 0
    unchanged_count = 0
    domain_changes = []
    old_domain_dist = Counter()
    new_domain_dist = Counter()
    
    # Update domain for each author
    print("\nUpdating domains...")
    for i, row in enumerate(rows):
        if (i + 1) % 100 == 0:
            print(f"  Processed {i+1}/{len(rows)} authors...", end='\r')
        
        old_domain = row.get('domain', '')
        all_pubs = row.get('all_publications', '')
        
        # Extract new domain
        new_domain = extract_domain_fixed(all_pubs) or ''
        
        # Track old domain distribution
        if old_domain:
            for d in old_domain.split(', '):
                old_domain_dist[d.strip()] += 1
        
        # Track new domain distribution
        if new_domain:
            for d in new_domain.split(', '):
                new_domain_dist[d.strip()] += 1
        
        # Update if changed
        if new_domain != old_domain:
            if len(domain_changes) < 10:  # Keep first 10 examples
                domain_changes.append({
                    'name': row.get('name', 'N/A'),
                    'old': old_domain,
                    'new': new_domain
                })
            row['domain'] = new_domain
            updated_count += 1
        else:
            unchanged_count += 1
    
    print(f"  Processed {len(rows)}/{len(rows)} authors... Done!")
    
    # Write updated CSV
    print("\nWriting updated CSV...")
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Report
    print(f"\n{'='*80}")
    print("RESULTS")
    print(f"{'='*80}")
    print(f"Authors updated: {updated_count} ({updated_count/len(rows)*100:.1f}%)")
    print(f"Authors unchanged: {unchanged_count} ({unchanged_count/len(rows)*100:.1f}%)")
    
    if domain_changes:
        print(f"\n{'-'*80}")
        print("SAMPLE DOMAIN CHANGES (first 10):")
        print(f"{'-'*80}")
        for i, change in enumerate(domain_changes, 1):
            print(f"\n{i}. {change['name']}")
            print(f"   OLD: {change['old'] or '(empty)'}")
            print(f"   NEW: {change['new'] or '(empty)'}")
    
    print(f"\n{'-'*80}")
    print("DOMAIN DISTRIBUTION COMPARISON")
    print(f"{'-'*80}")
    print(f"{'Domain':<30s} {'Before':>10s} {'After':>10s} {'Change':>10s}")
    print(f"{'-'*80}")
    
    # Get all unique domains
    all_domains = sorted(set(list(old_domain_dist.keys()) + list(new_domain_dist.keys())))
    
    for domain in all_domains:
        old_count = old_domain_dist.get(domain, 0)
        new_count = new_domain_dist.get(domain, 0)
        change = new_count - old_count
        change_str = f"{change:+d}" if change != 0 else "0"
        print(f"{domain:<30s} {old_count:>10,} {new_count:>10,} {change_str:>10s}")
    
    print(f"\n✅ Successfully updated: {csv_path}")


def main():
    print("="*80)
    print("UPDATING DOMAIN FIELD IN CSV FILES")
    print("="*80)
    print("\nFixes applied:")
    print("  ✅ Removed 'AI' keyword (prevents 'main', 'gain', 'obtain' matches)")
    print("  ✅ Word boundaries for 'EV' (prevents 'develop', 'level' matches)")
    print("  ✅ Word boundaries for all keywords ≤3 chars")
    print("="*80)
    
    # Files to update
    files = [
        Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country/european_authors_dach_simple.csv'),
        Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_non_dach_no_france_merged.csv'),
    ]
    
    for csv_file in files:
        try:
            update_csv_file(csv_file)
        except Exception as e:
            print(f"\n❌ ERROR processing {csv_file.name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("✅ ALL FILES UPDATED")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()

