#!/usr/bin/env python3
"""
Enrich remaining authors (non-first-authors and non-European first authors) with affiliation data
"""

import json
import time
import logging
import requests
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Set

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/remaining_authors_enrichment.log'),
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
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://ieeexplore.ieee.org/',
            'Origin': 'https://ieeexplore.ieee.org'
        })
        
        self.api_successes = 0
        self.api_failures = 0
        self.no_affiliation_count = 0
    
    def _clean_bio(self, bio_paragraphs):
        """Clean biography text"""
        if not bio_paragraphs:
            return None
        
        # Join all paragraphs
        full_bio = '\n\n'.join(bio_paragraphs)
        
        # Remove HTML tags
        full_bio = re.sub('<br><br>', '\n\n', full_bio)
        full_bio = re.sub('<[^<]+?>', '', full_bio)
        
        return full_bio
    
    def fetch_author_affiliations(self, author_id: str) -> Dict:
        """
        Fetch author affiliation data from IEEE API
        
        Args:
            author_id: IEEE author ID
            
        Returns:
            dict with affiliation data
        """
        endpoint = f"https://ieeexplore.ieee.org/rest/author/{author_id}"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # API returns a list, take the first element
                if isinstance(data, list) and len(data) > 0:
                    author_data = data[0]
                elif isinstance(data, dict):
                    author_data = data
                else:
                    logger.warning(f"Unexpected data format for author {author_id}")
                    self.api_failures += 1
                    return None
                
                self.api_successes += 1
                
                # Extract affiliation info (use currentAffiliations to match original script)
                affiliations = author_data.get('currentAffiliations', [])
                
                if not affiliations:
                    self.no_affiliation_count += 1
                
                return {
                    'author_id': author_id,
                    'preferred_name': author_data.get('preferredName'),
                    'full_name': author_data.get('fullName'),
                    'current_affiliations': affiliations,
                    'biography': self._clean_bio(author_data.get('bioParagraphs', [])),
                    'aliases': author_data.get('aliases', []),
                    'affiliation_count': len(affiliations),
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                logger.debug(f"API returned status {response.status_code} for author {author_id}")
                self.api_failures += 1
                return None
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"API request failed for author {author_id}: {e}")
            self.api_failures += 1
            return None
        except Exception as e:
            logger.error(f"Error processing author {author_id}: {e}")
            self.api_failures += 1
            return None


def load_json(filepath: Path) -> Dict:
    """Load JSON file"""
    logger.info(f"Loading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict, filepath: Path):
    """Save JSON file"""
    logger.info(f"Saving to {filepath}...")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_already_processed_ids(processed_file: Path) -> Set[str]:
    """Get set of author IDs that have already been processed"""
    data = load_json(processed_file)
    author_ids = set(data.get('authors', {}).keys())
    logger.info(f"Found {len(author_ids)} already processed authors")
    return author_ids


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich remaining authors with affiliation data')
    parser.add_argument('--input', default='results/unique_authors.json',
                       help='Input file with all unique authors')
    parser.add_argument('--processed', default='results/first_authors_enriched_cleaned_with_abstracts.json',
                       help='File with already processed authors')
    parser.add_argument('--output', default='results/remaining_authors_enriched.json',
                       help='Output file for enriched remaining authors')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of authors to process (for testing)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - only process 10 authors')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from existing output file - skip already processed authors')
    
    args = parser.parse_args()
    
    logger.info("="*70)
    logger.info("ENRICHING REMAINING AUTHORS WITH AFFILIATIONS")
    logger.info("="*70)
    
    # Load data
    all_authors = load_json(args.input)
    already_processed_ids = get_already_processed_ids(args.processed)
    
    # Get authors dict
    all_authors_dict = all_authors.get('authors', {})
    total_authors = len(all_authors_dict)
    
    logger.info(f"Total unique authors: {total_authors}")
    logger.info(f"Already processed: {len(already_processed_ids)}")
    
    # Find remaining authors
    remaining_author_ids = set(all_authors_dict.keys()) - already_processed_ids
    
    # Handle resume - skip already processed in current run
    if args.resume and Path(args.output).exists():
        logger.info("Resume mode: loading existing output...")
        existing_output = load_json(args.output)
        already_in_output = set(existing_output.get('authors', {}).keys())
        remaining_author_ids = remaining_author_ids - already_in_output
        logger.info(f"Already processed in this run: {len(already_in_output)}")
    
    remaining_count = len(remaining_author_ids)
    
    logger.info(f"Remaining to process: {remaining_count}")
    
    if remaining_count == 0:
        logger.info("✅ All authors already processed!")
        return
    
    # Apply limits
    if args.test:
        remaining_author_ids = set(list(remaining_author_ids)[:10])
        logger.info(f"TEST MODE: Processing {len(remaining_author_ids)} authors")
    elif args.limit:
        remaining_author_ids = set(list(remaining_author_ids)[:args.limit])
        logger.info(f"LIMITED: Processing {len(remaining_author_ids)} authors")
    
    # Initialize enricher
    enricher = AuthorEnricher()
    
    # Process remaining authors
    # Load existing data if resuming
    enriched_authors = {}
    if args.resume and Path(args.output).exists():
        existing_output = load_json(args.output)
        enriched_authors = existing_output.get('authors', {})
        logger.info(f"Loaded {len(enriched_authors)} existing author records")
    
    total_to_process = len(remaining_author_ids)
    
    logger.info(f"\n⏱️  Estimated time: {total_to_process * 0.5 / 60:.1f} minutes")
    logger.info(f"Starting enrichment...\n")
    
    start_time = time.time()
    
    for idx, author_id in enumerate(remaining_author_ids, 1):
        logger.info(f"[{idx}/{total_to_process}] Processing author {author_id}")
        
        # Get basic info from unique_authors
        basic_info = all_authors_dict.get(author_id, {})
        
        # Fetch affiliation data
        affiliation_data = enricher.fetch_author_affiliations(author_id)
        
        if affiliation_data:
            # Combine basic info with affiliation data
            enriched_authors[author_id] = {
                **basic_info,
                **affiliation_data
            }
            
            affiliations = affiliation_data.get('current_affiliations', [])
            if affiliations:
                logger.info(f"  ✓ Found {len(affiliations)} affiliation(s)")
                logger.info(f"    Primary: {affiliations[0][:70]}...")
            else:
                logger.warning(f"  ⚠️  No affiliations found")
        else:
            # Still include basic info even if API failed
            enriched_authors[author_id] = {
                **basic_info,
                'current_affiliations': [],
                'affiliation_count': 0,
                'api_fetch_failed': True
            }
            logger.warning(f"  ✗ API fetch failed")
        
        # Save progress every 100 authors
        if idx % 100 == 0:
            save_progress(enriched_authors, args.output, enricher, total_to_process, idx)
            logger.info(f"💾 Progress saved: {idx}/{total_to_process}")
        
        # Rate limiting
        time.sleep(0.5)
    
    # Final save
    elapsed = time.time() - start_time
    save_progress(enriched_authors, args.output, enricher, total_to_process, total_to_process)
    
    # Print summary
    logger.info("\n" + "="*70)
    logger.info("ENRICHMENT COMPLETED")
    logger.info("="*70)
    logger.info(f"Total processed: {total_to_process}")
    logger.info(f"API successes: {enricher.api_successes}")
    logger.info(f"API failures: {enricher.api_failures}")
    logger.info(f"Authors without affiliations: {enricher.no_affiliation_count}")
    logger.info(f"Success rate: {enricher.api_successes/total_to_process*100:.1f}%")
    logger.info(f"Total time: {elapsed/60:.1f} minutes ({elapsed/3600:.2f} hours)")
    logger.info(f"Avg per author: {elapsed/total_to_process:.2f} seconds")
    
    file_size = Path(args.output).stat().st_size / (1024 * 1024)
    logger.info(f"Output file size: {file_size:.1f} MB")
    logger.info(f"Output: {args.output}")
    logger.info("="*70)


def save_progress(enriched_authors: Dict, output_file: Path, enricher, total: int, processed: int):
    """Save progress to output file"""
    output_data = {
        'metadata': {
            'creation_date': datetime.now().isoformat(),
            'source': 'unique_authors.json',
            'description': 'Enriched data for remaining authors (non-first-authors and non-European first authors)',
            'total_processed': processed,
            'total_remaining': total,
            'api_successes': enricher.api_successes,
            'api_failures': enricher.api_failures,
            'authors_without_affiliations': enricher.no_affiliation_count,
            'last_updated': datetime.now().isoformat()
        },
        'authors': enriched_authors
    }
    
    save_json(output_data, output_file)


if __name__ == '__main__':
    main()

