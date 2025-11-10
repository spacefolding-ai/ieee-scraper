#!/usr/bin/env python3
"""
Combine email search results with enriched author data
Creates a comprehensive dataset with all valuable information
"""

import json
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json(filepath):
    """Load JSON file"""
    logger.info(f"Loading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data, filepath):
    """Save JSON file"""
    logger.info(f"Saving to {filepath}...")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def combine_data(email_data, author_data):
    """
    Combine email search results with enriched author data
    
    Args:
        email_data: Data from authors_with_emails_perplexity.json
        author_data: Data from first_authors_enriched_cleaned_with_abstracts.json
        
    Returns:
        Combined dataset with all valuable information
    """
    logger.info("Combining email and author data...")
    
    # Create combined dataset
    combined = {
        'metadata': {
            'creation_date': datetime.now().isoformat(),
            'source_files': {
                'email_data': 'authors_with_emails_perplexity.json',
                'author_data': 'first_authors_enriched_cleaned_with_abstracts.json'
            },
            'description': 'Combined dataset with author details, publications, abstracts, and email addresses',
            'total_authors': email_data['summary']['total_authors'],
            'emails_found': email_data['summary']['emails_found'],
            'email_success_rate': email_data['summary']['success_rate']
        },
        'authors': {}
    }
    
    # Track statistics
    stats = {
        'total': 0,
        'with_email': 0,
        'without_email': 0,
        'with_publications': 0,
        'with_abstracts': 0,
        'missing_in_author_data': 0
    }
    
    # Combine data for each author
    email_authors = email_data.get('authors', {})
    enriched_authors = author_data.get('authors', {})
    
    for author_id, email_info in email_authors.items():
        stats['total'] += 1
        
        # Get enriched author data
        enriched_info = enriched_authors.get(author_id)
        
        if not enriched_info:
            logger.warning(f"Author {author_id} not found in enriched data")
            stats['missing_in_author_data'] += 1
            # Still include with email data only
            combined['authors'][author_id] = email_info
            continue
        
        # Get publications
        publications = enriched_info.get('publications_as_first_author', [])
        
        # Build comprehensive author profile
        author_profile = {
            # Core identification
            'author_id': author_id,
            'name': enriched_info.get('preferred_names', [None])[0],
            'all_names': enriched_info.get('preferred_names', []),
            'normalized_names': enriched_info.get('normalized_names', []),
            'ieee_profile_url': f"https://ieeexplore.ieee.org/author/{author_id}",
            
            # Email information
            'email': email_info['email_search'].get('email'),
            'email_found': email_info['email_search'].get('found', False),
            'email_source': email_info['email_search'].get('source_url'),
            'email_citations': email_info['email_search'].get('citations', []),
            
            # Affiliations
            'primary_affiliation': email_info.get('affiliation') or enriched_info.get('current_affiliations', [None])[0],
            'all_affiliations': enriched_info.get('current_affiliations', []),
            
            # Publications as first author
            'publications_as_first_author': publications,
            'total_first_author_pubs': len(publications),
            'first_author_count': enriched_info.get('first_author_count', 0),
            
            # Research areas (from publications)
            'publication_titles': [pub.get('article_title') for pub in publications],
            'publication_years': [pub.get('publication_year') for pub in publications],
            'publication_dois': [pub.get('doi') for pub in publications],
            'abstracts': [pub.get('abstract') for pub in publications if pub.get('abstract')],
            
            # Publication metrics
            'total_citations': sum(pub.get('citation_count', 0) for pub in publications),
            'total_downloads': sum(pub.get('download_count', 0) for pub in publications),
        }
        
        # Add email retry info if available
        if 'retry_info' in email_info['email_search']:
            author_profile['email_retry_info'] = email_info['email_search']['retry_info']
        
        # Statistics tracking
        if author_profile['email_found']:
            stats['with_email'] += 1
        else:
            stats['without_email'] += 1
        
        if author_profile['total_first_author_pubs'] > 0:
            stats['with_publications'] += 1
        
        if author_profile['abstracts']:
            stats['with_abstracts'] += 1
        
        combined['authors'][author_id] = author_profile
    
    # Add statistics to metadata
    combined['metadata']['statistics'] = stats
    combined['metadata']['coverage'] = {
        'authors_with_email': f"{stats['with_email']}/{stats['total']} ({stats['with_email']/stats['total']*100:.1f}%)",
        'authors_with_publications': f"{stats['with_publications']}/{stats['total']} ({stats['with_publications']/stats['total']*100:.1f}%)",
        'authors_with_abstracts': f"{stats['with_abstracts']}/{stats['total']} ({stats['with_abstracts']/stats['total']*100:.1f}%)"
    }
    
    return combined


def create_csv_export(combined_data, output_path):
    """
    Create a CSV export with key fields for easy analysis
    """
    import csv
    
    logger.info(f"Creating CSV export: {output_path}")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'author_id', 
            'name', 
            'email', 
            'email_found',
            'primary_affiliation',
            'total_publications',
            'latest_publication_year',
            'publication_titles',
            'ieee_profile_url'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for author_id, author in combined_data['authors'].items():
            # Get latest publication year
            years = [y for y in author.get('publication_years', []) if y]
            latest_year = max(years) if years else None
            
            # Combine publication titles
            titles = author.get('publication_titles', [])
            titles_str = ' | '.join(titles[:3]) if titles else ''  # First 3 titles
            
            writer.writerow({
                'author_id': author_id,
                'name': author.get('name', ''),
                'email': author.get('email', ''),
                'email_found': 'Yes' if author.get('email_found') else 'No',
                'primary_affiliation': author.get('primary_affiliation', ''),
                'total_publications': author.get('total_first_author_pubs', 0),
                'latest_publication_year': latest_year or '',
                'publication_titles': titles_str,
                'ieee_profile_url': author.get('ieee_profile_url', '')
            })
    
    logger.info(f"✅ CSV export created")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Combine email and author data')
    parser.add_argument('--email-file', 
                       default='results/authors_with_emails_perplexity.json',
                       help='Email search results file')
    parser.add_argument('--author-file',
                       default='results/first_authors_enriched_cleaned_with_abstracts.json',
                       help='Enriched author data file')
    parser.add_argument('--output-json',
                       default='results/authors_complete_dataset.json',
                       help='Output JSON file')
    parser.add_argument('--output-csv',
                       default='results/authors_complete_dataset.csv',
                       help='Output CSV file')
    parser.add_argument('--skip-csv', action='store_true',
                       help='Skip CSV export')
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("COMBINING EMAIL AND AUTHOR DATA")
    logger.info("="*70)
    
    # Load data
    email_data = load_json(args.email_file)
    author_data = load_json(args.author_file)
    
    # Combine
    combined = combine_data(email_data, author_data)
    
    # Save JSON
    save_json(combined, args.output_json)
    
    # Create CSV export
    if not args.skip_csv:
        create_csv_export(combined, args.output_csv)
    
    # Print summary
    metadata = combined['metadata']
    stats = metadata['statistics']
    
    logger.info("\n" + "="*70)
    logger.info("COMBINATION COMPLETED")
    logger.info("="*70)
    logger.info(f"Total authors: {stats['total']}")
    logger.info(f"Authors with email: {stats['with_email']} ({stats['with_email']/stats['total']*100:.1f}%)")
    logger.info(f"Authors without email: {stats['without_email']} ({stats['without_email']/stats['total']*100:.1f}%)")
    logger.info(f"Authors with publications: {stats['with_publications']} ({stats['with_publications']/stats['total']*100:.1f}%)")
    logger.info(f"Authors with abstracts: {stats['with_abstracts']} ({stats['with_abstracts']/stats['total']*100:.1f}%)")
    logger.info("")
    logger.info(f"📁 JSON output: {args.output_json}")
    if not args.skip_csv:
        logger.info(f"📊 CSV output: {args.output_csv}")
    
    file_size_json = Path(args.output_json).stat().st_size / (1024 * 1024)
    logger.info(f"📦 JSON file size: {file_size_json:.1f} MB")
    
    if not args.skip_csv:
        file_size_csv = Path(args.output_csv).stat().st_size / (1024 * 1024)
        logger.info(f"📊 CSV file size: {file_size_csv:.1f} MB")
    
    logger.info("="*70)
    logger.info("\n✅ All data combined successfully!")


if __name__ == '__main__':
    main()

