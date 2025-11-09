#!/usr/bin/env python3
"""
IEEE Author Affiliation Fetcher - COMPACT VERSION
Only stores essential data: name, affiliations, basic info
Reduces file size from ~3GB to ~50-100MB
"""

import json
import time
import logging
import os
from pathlib import Path
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/author_affiliation_compact_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CompactAuthorFetcher:
    """Fetch only essential author affiliation data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://ieeexplore.ieee.org/'
        })
        self.api_successes = 0
        self.api_failures = 0
    
    def fetch_author_data(self, author_id):
        """Fetch and extract only essential data"""
        endpoint = f"https://ieeexplore.ieee.org/rest/author/{author_id}"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    full_data = data[0]
                    
                    # Extract only essential fields
                    compact_data = {
                        'id': full_data.get('id'),
                        'preferred_name': full_data.get('preferredName'),
                        'first_name': full_data.get('firstName'),
                        'last_name': full_data.get('lastName'),
                        'affiliations': full_data.get('currentAffiliations', []),
                        'aliases': full_data.get('aliases', [])[:5],  # Limit to 5 aliases
                        'bio_summary': self._extract_bio_summary(full_data.get('bioParagraphs', [])),
                        'coauthor_count': len(full_data.get('coAuthors', []))  # Just the count, not the full list
                    }
                    
                    self.api_successes += 1
                    return compact_data
            
            self.api_failures += 1
            return None
            
        except Exception as e:
            logger.debug(f"Error fetching author {author_id}: {e}")
            self.api_failures += 1
            return None
    
    def _extract_bio_summary(self, bio_paragraphs):
        """Extract first 200 characters of bio as summary"""
        if not bio_paragraphs:
            return None
        
        full_bio = ' '.join(bio_paragraphs)
        # Remove HTML tags
        import re
        full_bio = re.sub('<[^<]+?>', '', full_bio)
        
        # Return first 200 characters
        return full_bio[:200] + '...' if len(full_bio) > 200 else full_bio
    
    def close(self):
        self.session.close()


def load_unique_authors(authors_file='results/unique_authors.json'):
    """Load the unique authors JSON file"""
    logger.info(f"Loading authors from {authors_file}...")
    
    with open(authors_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    authors = data.get('authors', {})
    logger.info(f"Loaded {len(authors)} unique authors")
    
    return authors


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch IEEE author affiliations (compact version)')
    parser.add_argument('--test', action='store_true', help='Test mode - only fetch first 10 authors')
    parser.add_argument('--resume', action='store_true', help='Resume from existing output file')
    parser.add_argument('--limit', type=int, default=None, help='Limit number of authors to fetch')
    
    args = parser.parse_args()
    
    # Load unique authors
    authors = load_unique_authors()
    
    # Load existing results if resuming
    output_file = Path('results/author_affiliations_compact.json')
    existing_results = {}
    
    if args.resume and output_file.exists():
        logger.info("Resume mode: loading existing results...")
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_results = existing_data.get('authors', {})
        logger.info(f"Loaded {len(existing_results)} existing author records")
    
    # Filter authors to fetch
    authors_to_fetch = {
        author_id: info 
        for author_id, info in authors.items() 
        if author_id not in existing_results
    }
    
    if args.test:
        authors_to_fetch = dict(list(authors_to_fetch.items())[:10])
        logger.info(f"TEST MODE: Fetching only {len(authors_to_fetch)} authors")
    elif args.limit:
        authors_to_fetch = dict(list(authors_to_fetch.items())[:args.limit])
        logger.info(f"LIMITED MODE: Fetching {len(authors_to_fetch)} authors")
    
    total = len(authors_to_fetch)
    logger.info(f"Will fetch data for {total} authors (COMPACT mode)")
    
    fetcher = CompactAuthorFetcher()
    results = existing_results.copy()
    successes = len(existing_results)
    failures = 0
    
    try:
        start_time = time.time()
        
        for idx, (author_id, author_info) in enumerate(authors_to_fetch.items(), 1):
            author_name = author_info.get('primary_preferred_name', 'Unknown')
            logger.info(f"[{idx}/{total}] Fetching author {author_id} ({author_name})...")
            
            try:
                author_data = fetcher.fetch_author_data(int(author_id))
                
                if author_data:
                    affiliations = author_data.get('affiliations', [])
                    affiliation_str = ', '.join(affiliations) if affiliations else 'N/A'
                    
                    results[author_id] = {
                        'id': author_id,
                        'name': author_name,
                        'publications_count': author_info.get('appearances_count', 0),
                        'data': author_data,
                        'fetched_at': datetime.now().isoformat()
                    }
                    successes += 1
                    logger.info(f"  ✓ Success - Affiliation: {affiliation_str[:100]}")
                else:
                    results[author_id] = {
                        'id': author_id,
                        'name': author_name,
                        'publications_count': author_info.get('appearances_count', 0),
                        'data': None,
                        'fetched_at': datetime.now().isoformat(),
                        'error': 'No data available'
                    }
                    failures += 1
                    logger.warning(f"  ✗ Failed to fetch data")
                
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                failures += 1
            
            # Save progress periodically
            if idx % 50 == 0:
                save_results(results, output_file, fetcher)
                elapsed = time.time() - start_time
                avg_time = elapsed / idx
                remaining = (total - idx) * avg_time
                logger.info(f"Progress: {idx}/{total} ({idx/total*100:.1f}%) - "
                          f"ETA: {remaining/60:.1f} minutes")
            
            # Rate limiting
            if idx % 10 == 0:
                time.sleep(3)
            else:
                time.sleep(0.5)
        
        # Final save
        save_results(results, output_file, fetcher)
        
        elapsed = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"COMPLETED")
        logger.info(f"{'='*60}")
        logger.info(f"Total authors processed: {total}")
        logger.info(f"Successes: {successes}")
        logger.info(f"Failures: {failures}")
        logger.info(f"Success rate: {successes/(successes+failures)*100:.1f}%")
        logger.info(f"Total time: {elapsed/60:.1f} minutes")
        logger.info(f"Average time per author: {elapsed/total:.2f} seconds")
        logger.info(f"Results saved to: {output_file}")
        
        # Show file size
        file_size_mb = output_file.stat().st_size / (1024 * 1024)
        logger.info(f"Output file size: {file_size_mb:.1f} MB")
        logger.info(f"{'='*60}")
        
    finally:
        fetcher.close()


def save_results(results, output_file, fetcher):
    """Save results to file"""
    output_data = {
        'metadata': {
            'total_authors': len(results),
            'successful_fetches': sum(1 for r in results.values() if r.get('data')),
            'failed_fetches': sum(1 for r in results.values() if not r.get('data')),
            'last_updated': datetime.now().isoformat(),
            'api_successes': fetcher.api_successes,
            'api_failures': fetcher.api_failures,
            'version': 'compact',
            'note': 'Compact version - excludes full biography and detailed co-author list'
        },
        'authors': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.debug(f"Saved {len(results)} author records to {output_file}")


if __name__ == '__main__':
    main()

