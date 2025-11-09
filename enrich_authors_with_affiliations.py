#!/usr/bin/env python3
"""
Enrich unique_authors.json with latest affiliations and biography
Adds affiliation and bio data directly to each author entry
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/enrichment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AuthorEnricher:
    """Enrich author data with affiliations from IEEE API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://ieeexplore.ieee.org/'
        })
        self.api_successes = 0
        self.api_failures = 0
    
    def fetch_affiliation_data(self, author_id):
        """Fetch affiliation and bio from IEEE API"""
        endpoint = f"https://ieeexplore.ieee.org/rest/author/{author_id}"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    author_data = data[0]
                    
                    # Extract relevant fields
                    result = {
                        'current_affiliations': author_data.get('currentAffiliations', []),
                        'biography': self._clean_bio(author_data.get('bioParagraphs', [])),
                        'ieee_preferred_name': author_data.get('preferredName'),
                        'fetched_at': datetime.now().isoformat()
                    }
                    
                    self.api_successes += 1
                    return result
            
            self.api_failures += 1
            return None
            
        except Exception as e:
            logger.debug(f"Error fetching author {author_id}: {e}")
            self.api_failures += 1
            return None
    
    def _clean_bio(self, bio_paragraphs):
        """Clean biography text"""
        if not bio_paragraphs:
            return None
        
        # Join all paragraphs
        full_bio = '\n\n'.join(bio_paragraphs)
        
        # Remove HTML tags
        import re
        full_bio = re.sub('<br><br>', '\n\n', full_bio)
        full_bio = re.sub('<[^<]+?>', '', full_bio)
        
        return full_bio
    
    def close(self):
        self.session.close()


def load_unique_authors(input_file='results/unique_authors.json'):
    """Load the unique authors JSON file"""
    logger.info(f"Loading authors from {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data['authors'])} unique authors")
    return data


def save_enriched_authors(data, output_file):
    """Save enriched data"""
    logger.info(f"Saving enriched data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Saved to {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich unique_authors.json with affiliations')
    parser.add_argument('--test', action='store_true', 
                       help='Test mode - only enrich first 10 authors')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of authors to enrich')
    parser.add_argument('--resume', action='store_true',
                       help='Resume - skip authors that already have affiliation data')
    parser.add_argument('--output', default='results/unique_authors_enriched.json',
                       help='Output file path (default: results/unique_authors_enriched.json)')
    parser.add_argument('--input', default='results/unique_authors.json',
                       help='Input file path (default: results/unique_authors.json)')
    
    args = parser.parse_args()
    
    # Load existing data
    data = load_unique_authors(args.input)
    authors = data['authors']
    
    # If resuming from an existing enriched file, load it
    output_path = Path(args.output)
    if args.resume and output_path.exists():
        logger.info(f"Resume mode: loading existing enriched data from {args.output}...")
        data = load_unique_authors(args.output)
        authors = data['authors']
    
    # Determine which authors need enrichment
    authors_to_enrich = {}
    for author_id, author_info in authors.items():
        if args.resume and 'current_affiliations' in author_info:
            continue  # Skip already enriched
        authors_to_enrich[author_id] = author_info
    
    if args.test:
        authors_to_enrich = dict(list(authors_to_enrich.items())[:10])
        logger.info(f"TEST MODE: Enriching only {len(authors_to_enrich)} authors")
    elif args.limit:
        authors_to_enrich = dict(list(authors_to_enrich.items())[:args.limit])
        logger.info(f"LIMITED MODE: Enriching {len(authors_to_enrich)} authors")
    
    total = len(authors_to_enrich)
    
    if total == 0:
        logger.info("No authors to enrich. All done!")
        return
    
    logger.info(f"Will enrich {total} authors")
    
    enricher = AuthorEnricher()
    enriched_count = 0
    failed_count = 0
    
    try:
        start_time = time.time()
        
        for idx, (author_id, author_info) in enumerate(authors_to_enrich.items(), 1):
            author_name = author_info.get('primary_preferred_name', 'Unknown')
            logger.info(f"[{idx}/{total}] Enriching author {author_id} ({author_name})...")
            
            try:
                affiliation_data = enricher.fetch_affiliation_data(int(author_id))
                
                if affiliation_data:
                    # Add affiliation data to author
                    authors[author_id]['current_affiliations'] = affiliation_data['current_affiliations']
                    authors[author_id]['biography'] = affiliation_data['biography']
                    authors[author_id]['ieee_preferred_name'] = affiliation_data['ieee_preferred_name']
                    authors[author_id]['affiliation_fetched_at'] = affiliation_data['fetched_at']
                    
                    affiliations = affiliation_data['current_affiliations']
                    affiliation_str = ', '.join(affiliations) if affiliations else 'N/A'
                    
                    enriched_count += 1
                    logger.info(f"  ✓ Success - {affiliation_str[:100]}")
                else:
                    # Mark as attempted but failed
                    authors[author_id]['current_affiliations'] = None
                    authors[author_id]['biography'] = None
                    authors[author_id]['affiliation_fetch_error'] = 'No data available'
                    authors[author_id]['affiliation_fetched_at'] = datetime.now().isoformat()
                    
                    failed_count += 1
                    logger.warning(f"  ✗ Failed to fetch data")
                
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                authors[author_id]['affiliation_fetch_error'] = str(e)
                failed_count += 1
            
            # Save progress periodically
            if idx % 50 == 0:
                save_enriched_authors(data, output_path)
                elapsed = time.time() - start_time
                avg_time = elapsed / idx
                remaining = (total - idx) * avg_time
                
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"Progress: {idx}/{total} ({idx/total*100:.1f}%) - "
                          f"ETA: {remaining/60:.1f} min - "
                          f"File size: {file_size_mb:.1f} MB")
            
            # Rate limiting
            if idx % 10 == 0:
                time.sleep(3)
            else:
                time.sleep(0.5)
        
        # Update metadata
        data['summary']['enriched_with_affiliations'] = True
        data['summary']['affiliation_enrichment_date'] = datetime.now().isoformat()
        data['summary']['authors_with_affiliations'] = enriched_count
        data['summary']['affiliation_fetch_failures'] = failed_count
        
        # Final save
        save_enriched_authors(data, output_path)
        
        elapsed = time.time() - start_time
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"ENRICHMENT COMPLETED")
        logger.info(f"{'='*70}")
        logger.info(f"Total authors processed: {total}")
        logger.info(f"Successfully enriched: {enriched_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Success rate: {enriched_count/(enriched_count+failed_count)*100:.1f}%")
        logger.info(f"Total time: {elapsed/60:.1f} minutes")
        logger.info(f"Average time per author: {elapsed/total:.2f} seconds")
        logger.info(f"Output file: {output_path}")
        logger.info(f"Output file size: {file_size_mb:.1f} MB")
        logger.info(f"{'='*70}")
        
    finally:
        enricher.close()


if __name__ == '__main__':
    main()

