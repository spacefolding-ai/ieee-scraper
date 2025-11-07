#!/usr/bin/env python3
"""
Extract all unique authors from raw_responses JSON files.
Groups authors by ID and collects all their information.
"""

import json
import os
import html
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set


def clean_html_entities(text):
    """Decode HTML entities in text if present."""
    if text and isinstance(text, str):
        return html.unescape(text)
    return text


def extract_authors_from_file(filepath: str) -> List[Dict]:
    """Extract all authors from a single JSON file."""
    authors = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Navigate to records
        records = data.get('response', {}).get('records', [])
        
        for record in records:
            record_authors = record.get('authors', [])
            
            # Extract comprehensive publication information
            # Clean abstract by removing IEEE highlight markers [:: ::]
            abstract_raw = record.get('abstract', '')
            abstract_clean = abstract_raw.replace('[::', '').replace('::]', '') if abstract_raw else None
            abstract_clean = clean_html_entities(abstract_clean)
            
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
                'abstract': abstract_clean,
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
                    for a in record.get('authors', [])
                ],
                'source_file': os.path.basename(filepath)
            }
            
            for author in record_authors:
                # Add source information for traceability
                author_with_source = author.copy()
                author_with_source['_publication_info'] = publication_info
                authors.append(author_with_source)
        
        return authors
    
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return []


def merge_author_data(author_entries: List[Dict]) -> Dict:
    """
    Merge multiple entries for the same author.
    Keeps all unique values and tracks appearances.
    """
    merged = {
        'id': author_entries[0]['id'],
        'appearances_count': len(author_entries),
        'preferred_names': set(),
        'normalized_names': set(),
        'first_names': set(),
        'last_names': set(),
        'searchable_preferred_names': set(),
        'publications': []
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
        
        # Track publications with extended information
        publication_info = entry.get('_publication_info', {})
        merged['publications'].append(publication_info)
    
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
    # Define paths
    raw_responses_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/raw_responses')
    output_file = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/unique_authors.json')
    
    print("Starting author extraction from raw responses...")
    print(f"Source directory: {raw_responses_dir}")
    
    # Get all JSON files
    json_files = sorted(raw_responses_dir.glob('page_*.json'))
    print(f"Found {len(json_files)} JSON files to process")
    
    # Dictionary to group authors by ID
    authors_by_id = defaultdict(list)
    total_author_entries = 0
    
    # Process each file
    for idx, json_file in enumerate(json_files, 1):
        print(f"Processing {json_file.name} ({idx}/{len(json_files)})...")
        authors = extract_authors_from_file(json_file)
        
        # Group by author ID
        for author in authors:
            author_id = author.get('id')
            if author_id:
                authors_by_id[author_id].append(author)
                total_author_entries += 1
    
    print(f"\nTotal author entries found: {total_author_entries}")
    print(f"Unique authors (by ID): {len(authors_by_id)}")
    
    # Merge data for each unique author
    print("\nMerging author data...")
    unique_authors = {}
    for author_id, entries in authors_by_id.items():
        unique_authors[str(author_id)] = merge_author_data(entries)
    
    # Sort by number of appearances (most prolific first)
    sorted_authors = dict(
        sorted(
            unique_authors.items(),
            key=lambda x: x[1]['appearances_count'],
            reverse=True
        )
    )
    
    # Create summary statistics
    summary = {
        'total_unique_authors': len(sorted_authors),
        'total_author_entries': total_author_entries,
        'files_processed': len(json_files),
        'most_prolific_authors': []
    }
    
    # Add top 10 most prolific authors to summary
    for author_id, data in list(sorted_authors.items())[:10]:
        summary['most_prolific_authors'].append({
            'id': author_id,
            'name': data.get('primary_preferred_name', 'Unknown'),
            'publications_count': data['appearances_count']
        })
    
    # Prepare final output
    output_data = {
        'summary': summary,
        'authors': sorted_authors
    }
    
    # Write to output file
    print(f"\nWriting results to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Successfully extracted {len(sorted_authors)} unique authors")
    print(f"✓ Output saved to: {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total unique authors: {summary['total_unique_authors']}")
    print(f"Total author entries: {summary['total_author_entries']}")
    print(f"Files processed: {summary['files_processed']}")
    print("\nTop 10 Most Prolific Authors:")
    for i, author in enumerate(summary['most_prolific_authors'], 1):
        print(f"  {i}. {author['name']} (ID: {author['id']}) - {author['publications_count']} publications")
    print("="*60)


if __name__ == '__main__':
    main()

