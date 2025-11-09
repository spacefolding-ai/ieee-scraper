#!/usr/bin/env python3
"""
Extract unique first authors from raw responses
Format matches unique_authors.json but only includes publications where they are first author
Includes complete abstract text
"""

import json
import html
from pathlib import Path
from collections import defaultdict
from datetime import datetime


def clean_html_entities(text):
    """Decode HTML entities in text if present."""
    if text and isinstance(text, str):
        return html.unescape(text)
    return text


def extract_first_authors_from_file(filepath):
    """Extract first authors and their publications from a single JSON file."""
    authors_data = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = data.get('response', {}).get('records', [])
        
        for record in records:
            record_authors = record.get('authors', [])
            
            # Only process if there are authors
            if not record_authors:
                continue
            
            # Get the first author
            first_author = record_authors[0]
            author_id = first_author.get('id')
            
            if not author_id:
                continue
            
            # Clean abstract by removing IEEE highlight markers [:: ::]
            abstract_raw = record.get('abstract', '')
            abstract_clean = abstract_raw.replace('[::', '').replace('::]', '') if abstract_raw else None
            abstract_clean = clean_html_entities(abstract_clean)
            
            # Extract comprehensive publication information
            publication_info = {
                'article_number': record.get('articleNumber'),
                'article_title': clean_html_entities(record.get('articleTitle')),
                'doi': record.get('doi'),
                'publication_year': record.get('publicationYear'),
                'publication_date': record.get('publicationDate'),
                'publication_title': record.get('publicationTitle'),
                'display_publication_title': record.get('displayPublicationTitle'),
                'volume': record.get('volume'),
                'issue': record.get('issue'),
                'start_page': record.get('startPage'),
                'end_page': record.get('endPage'),
                'citation_count': record.get('citationCount'),
                'download_count': record.get('downloadCount'),
                'patent_citation_count': record.get('patentCitationCount'),
                'document_link': record.get('documentLink'),
                'pdf_link': record.get('pdfLink'),
                'pdf_size': record.get('pdfSize'),
                'abstract': abstract_clean,  # COMPLETE abstract text
                'content_type': record.get('contentType'),
                'article_content_type': record.get('articleContentType'),
                'publisher': record.get('publisher'),
                'is_open_access': record.get('isOpenAccess'),
                'is_early_access': record.get('isEarlyAccess'),
                'access_type': record.get('accessType', {}).get('type'),
                'is_journal': record.get('isJournal'),
                'is_conference': record.get('isConference'),
                'is_magazine': record.get('isMagazine'),
                'is_standard': record.get('isStandard'),
                'all_coauthors': [
                    {
                        'id': a.get('id'),
                        'preferred_name': clean_html_entities(a.get('preferredName')),
                        'normalized_name': clean_html_entities(a.get('normalizedName')),
                        'first_name': clean_html_entities(a.get('firstName')),
                        'last_name': clean_html_entities(a.get('lastName'))
                    }
                    for a in record_authors
                ],
                'source_file': filepath.name
            }
            
            # Store first author with publication info
            author_entry = first_author.copy()
            author_entry['_publication_info'] = publication_info
            authors_data.append(author_entry)
        
        return authors_data
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def merge_first_author_data(author_entries):
    """
    Merge multiple entries for the same first author.
    Keeps all unique values and tracks publications where they are first author.
    """
    merged = {
        'id': author_entries[0]['id'],
        'first_author_count': len(author_entries),  # Count as first author
        'preferred_names': set(),
        'normalized_names': set(),
        'first_names': set(),
        'last_names': set(),
        'searchable_preferred_names': set(),
        'publications_as_first_author': []
    }
    
    for entry in author_entries:
        # Collect all unique name variants (clean HTML entities)
        if 'preferredName' in entry:
            merged['preferred_names'].add(clean_html_entities(entry['preferredName']))
        if 'normalizedName' in entry:
            merged['normalized_names'].add(clean_html_entities(entry['normalizedName']))
        if 'firstName' in entry:
            merged['first_names'].add(clean_html_entities(entry['firstName']))
        if 'lastName' in entry:
            merged['last_names'].add(clean_html_entities(entry['lastName']))
        if 'searchablePreferredName' in entry:
            merged['searchable_preferred_names'].add(clean_html_entities(entry['searchablePreferredName']))
        
        # Track publications where they are first author
        publication_info = entry.get('_publication_info', {})
        merged['publications_as_first_author'].append(publication_info)
    
    # Convert sets to sorted lists for JSON serialization
    merged['preferred_names'] = sorted(list(merged['preferred_names']))
    merged['normalized_names'] = sorted(list(merged['normalized_names']))
    merged['first_names'] = sorted(list(merged['first_names']))
    merged['last_names'] = sorted(list(merged['last_names']))
    merged['searchable_preferred_names'] = sorted(list(merged['searchable_preferred_names']))
    
    # Add most common name as primary
    if merged['preferred_names']:
        merged['primary_preferred_name'] = merged['preferred_names'][0]
    
    return merged


def main():
    print("="*70)
    print("EXTRACTING UNIQUE FIRST AUTHORS")
    print("="*70)
    
    # Define paths
    raw_responses_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/raw_responses')
    output_file = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/first_authors_unique.json')
    
    print(f"\nSource directory: {raw_responses_dir}")
    
    # Get all JSON files
    json_files = sorted(raw_responses_dir.glob('page_*.json'))
    print(f"Found {len(json_files)} JSON files to process")
    
    # Dictionary to group first authors by ID
    first_authors_by_id = defaultdict(list)
    total_first_author_entries = 0
    
    # Process each file
    for idx, json_file in enumerate(json_files, 1):
        print(f"Processing {json_file.name} ({idx}/{len(json_files)})...")
        authors = extract_first_authors_from_file(json_file)
        
        # Group by author ID
        for author in authors:
            author_id = author.get('id')
            if author_id:
                first_authors_by_id[author_id].append(author)
                total_first_author_entries += 1
    
    print(f"\nTotal first author entries found: {total_first_author_entries}")
    print(f"Unique first authors: {len(first_authors_by_id)}")
    
    # Merge data for each unique first author
    print("\nMerging first author data...")
    unique_first_authors = {}
    for author_id, entries in first_authors_by_id.items():
        unique_first_authors[str(author_id)] = merge_first_author_data(entries)
    
    # Sort by number of publications as first author (most prolific first)
    sorted_first_authors = dict(
        sorted(
            unique_first_authors.items(),
            key=lambda x: x[1]['first_author_count'],
            reverse=True
        )
    )
    
    # Create summary statistics
    summary = {
        'total_unique_first_authors': len(sorted_first_authors),
        'total_publications': total_first_author_entries,
        'extraction_date': datetime.now().isoformat(),
        'source': 'IEEE Xplore raw_responses (page_0001 to page_0050)',
        'note': 'Only includes publications where author is the first author',
        'most_prolific_first_authors': []
    }
    
    # Add top 10 most prolific first authors to summary
    for author_id, data in list(sorted_first_authors.items())[:10]:
        summary['most_prolific_first_authors'].append({
            'id': author_id,
            'name': data.get('primary_preferred_name', 'Unknown'),
            'first_author_publications': data['first_author_count']
        })
    
    # Prepare final output (matching unique_authors.json format)
    output_data = {
        'summary': summary,
        'authors': sorted_first_authors
    }
    
    # Write to output file
    print(f"\nWriting results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Calculate file size
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    
    print(f"\n{'='*70}")
    print("EXTRACTION COMPLETED")
    print(f"{'='*70}")
    print(f"✓ Successfully extracted {len(sorted_first_authors)} unique first authors")
    print(f"✓ Total publications as first author: {total_first_author_entries}")
    print(f"✓ Output saved to: {output_file}")
    print(f"✓ File size: {file_size_mb:.1f} MB")
    
    # Print summary
    print(f"\n{'='*70}")
    print("TOP 10 MOST PROLIFIC FIRST AUTHORS")
    print(f"{'='*70}")
    for i, author in enumerate(summary['most_prolific_first_authors'], 1):
        print(f"  {i:2d}. {author['name']:40s} - {author['first_author_publications']} publications")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()

