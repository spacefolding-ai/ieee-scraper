#!/usr/bin/env python3
"""
Extract and add additional properties to simplified files:
- domain: research domain from publications/abstracts
- department: from biography or affiliation
- name_of_project: project names mentioned
- last_publication_title: most recent publication title
- team: team name if mentioned
- adequate_title: academic/professional title
"""

import json
import csv
import re
from pathlib import Path
from collections import Counter

# Common academic titles
TITLE_PATTERNS = [
    r'\b(Professor|Prof\.?)\b',
    r'\b(Associate Professor|Assoc\.? Prof\.?)\b',
    r'\b(Assistant Professor|Asst\.? Prof\.?)\b',
    r'\b(Dr\.?|Doctor)\b',
    r'\b(Ph\.?D\.?|PhD)\b',
    r'\b(Research Scientist|Researcher)\b',
    r'\b(Senior Researcher|Senior Research)\b',
    r'\b(Post[- ]?doctoral|Postdoc)\b',
    r'\b(Lecturer|Senior Lecturer)\b',
    r'\b(Engineer|Senior Engineer|Principal Engineer)\b',
    r'\b(Director|Head)\b',
]

# Department keywords
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

# Project patterns
PROJECT_PATTERNS = [
    r'project[:\s]+([^,\.;]+)',
    r'Project[:\s]+([^,\.;]+)',
    r'([A-Z][A-Z0-9]+)\s+project',  # Acronym projects
]

# Team patterns
TEAM_PATTERNS = [
    r'team[:\s]+([^,\.;]+)',
    r'Team[:\s]+([^,\.;]+)',
    r'([A-Z][A-Za-z\s]+)\s+[Tt]eam',
    r'[Tt]eam\s+([A-Z][A-Za-z\s]+)',
]

# Common research domains/keywords
DOMAIN_KEYWORDS = {
    'power_systems': ['power system', 'power grid', 'electrical grid', 'smart grid', 'power network'],
    'renewable_energy': ['renewable energy', 'solar', 'photovoltaic', 'wind energy', 'wind power', 'PV system'],
    'microgrids': ['microgrid', 'micro-grid', 'distributed generation'],
    'electric_vehicles': ['electric vehicle', 'EV', 'charging station', 'EV charger', 'battery management'],
    'power_electronics': ['power electronic', 'converter', 'inverter', 'rectifier', 'DC-DC', 'AC-DC'],
    'energy_storage': ['energy storage', 'battery', 'ESS', 'storage system'],
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


def extract_title(author_data):
    """Extract academic/professional title"""
    title = None
    
    # Check biography
    bio = author_data.get('biography', '') or ''
    name = author_data.get('name', '') or ''
    
    text = bio + ' ' + name
    
    for pattern in TITLE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(0).strip()
            break
    
    return title


def extract_department(author_data):
    """Extract department from affiliation or biography"""
    departments = []
    
    # Check primary affiliation
    primary_aff = author_data.get('primary_affiliation', '') or ''
    bio = author_data.get('biography', '') or ''
    
    text = primary_aff + ' ' + bio
    
    for pattern in DEPARTMENT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        departments.extend(matches)
    
    # Clean and return first match
    if departments:
        dept = departments[0].strip()
        # Remove trailing punctuation and clean up
        dept = re.sub(r'[,\.;]$', '', dept).strip()
        return dept
    
    return None


def extract_project_name(author_data):
    """Extract project names from biography"""
    projects = []
    
    bio = author_data.get('biography', '') or ''
    
    for pattern in PROJECT_PATTERNS:
        matches = re.findall(pattern, bio, re.IGNORECASE)
        projects.extend(matches)
    
    if projects:
        return projects[0].strip()
    
    return None


def extract_team(author_data):
    """Extract team name from biography"""
    teams = []
    
    bio = author_data.get('biography', '') or ''
    
    for pattern in TEAM_PATTERNS:
        matches = re.findall(pattern, bio)
        teams.extend(matches)
    
    if teams:
        return teams[0].strip()
    
    return None


def extract_last_publication_title(author_data):
    """Get the most recent publication title"""
    all_pubs = author_data.get('all_publications', [])
    
    if not all_pubs:
        return None
    
    # Find publication with highest year
    latest_pub = None
    latest_year = 0
    
    for pub in all_pubs:
        try:
            year = int(pub.get('year', 0))
            if year > latest_year:
                latest_year = year
                latest_pub = pub
        except (ValueError, TypeError):
            continue
    
    if latest_pub:
        return latest_pub.get('title')
    
    return None


def extract_domain(author_data):
    """Extract research domain from publications and abstracts"""
    all_pubs = author_data.get('all_publications', [])
    
    if not all_pubs:
        return None
    
    # Collect all text from titles and abstracts
    text_corpus = []
    for pub in all_pubs:
        title = pub.get('title', '') or ''
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
    
    # Get top domains
    if domain_scores:
        # Sort by score and get top domain
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        # Return top 3 domains as comma-separated string
        top_domains = [domain.replace('_', ' ').title() for domain, score in sorted_domains[:3] if score > 0]
        if top_domains:
            return ', '.join(top_domains)
    
    return None


def enrich_author(author_data):
    """Add all new properties to author data"""
    author_data['domain'] = extract_domain(author_data)
    author_data['department'] = extract_department(author_data)
    author_data['name_of_project'] = extract_project_name(author_data)
    author_data['last_publication_title'] = extract_last_publication_title(author_data)
    author_data['team'] = extract_team(author_data)
    author_data['adequate_title'] = extract_title(author_data)
    
    return author_data


def process_json_file(file_path):
    """Process a single JSON file"""
    print(f"📄 Processing: {file_path.name}")
    
    # Load JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        authors = json.load(f)
    
    # Enrich each author
    enriched_count = 0
    for author in authors:
        enrich_author(author)
        enriched_count += 1
    
    # Save updated JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(authors, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Enriched {enriched_count} authors")
    
    return enriched_count


def process_csv_file(json_file_path, csv_file_path):
    """Update CSV file from enriched JSON"""
    print(f"📄 Updating CSV: {csv_file_path.name}")
    
    # Load JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        authors = json.load(f)
    
    if not authors:
        print(f"  ⚠ Empty file, skipping")
        return 0
    
    # Define all fieldnames (original + new ones)
    fieldnames = [
        'author_id', 'first_name', 'last_name', 'name', 'ieee_profile_url',
        'email', 'email_source', 'email_citations', 'primary_affiliation',
        'all_affiliations', 'biography', 'first_author_count',
        'all_publications', 'publications_as_first_author', 'publications_as_non_first_author',
        # New fields
        'domain', 'department', 'name_of_project', 'last_publication_title', 'team', 'adequate_title'
    ]
    
    # Write CSV
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for author in authors:
            # Stringify arrays and objects
            row = {}
            for key in fieldnames:
                value = author.get(key)
                if isinstance(value, (list, dict)):
                    row[key] = json.dumps(value, ensure_ascii=False) if value else ''
                elif value is None:
                    row[key] = ''
                else:
                    row[key] = value
            
            writer.writerow(row)
    
    print(f"  ✓ CSV updated with 6 new columns")
    
    return len(authors)


def main():
    by_country_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    print("="*80)
    print("Extracting Additional Properties")
    print("="*80)
    print("\nNew properties to extract:")
    print("  1. domain - research domain from publications")
    print("  2. department - from affiliation/biography")
    print("  3. name_of_project - project names mentioned")
    print("  4. last_publication_title - most recent publication")
    print("  5. team - team name if mentioned")
    print("  6. adequate_title - academic/professional title")
    print("="*80 + "\n")
    
    # Get all simplified JSON files
    json_files = sorted(by_country_dir.glob('european_authors_*_simple.json'))
    
    print(f"Found {len(json_files)} simplified JSON files\n")
    
    total_authors = 0
    
    # Process each file
    for json_file in json_files:
        try:
            # Update JSON
            count = process_json_file(json_file)
            total_authors += count
            
            # Update corresponding CSV
            csv_file = json_file.with_suffix('.csv')
            if csv_file.exists():
                process_csv_file(json_file, csv_file)
            
            print()
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print(f"{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Files processed:  {len(json_files)}")
    print(f"Total authors:    {total_authors}")
    print(f"\nNew properties added to all *_simple.json and *_simple.csv files:")
    print(f"  ✓ domain")
    print(f"  ✓ department")
    print(f"  ✓ name_of_project")
    print(f"  ✓ last_publication_title")
    print(f"  ✓ team")
    print(f"  ✓ adequate_title")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

