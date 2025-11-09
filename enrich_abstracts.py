#!/usr/bin/env python3
"""
Enrich publications with complete abstracts from IEEE API
Fetches full abstracts for all publications in first_authors_enriched_cleaned.json
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
import requests
import html
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/abstract_enrichment.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AbstractEnricher:
    """Fetch complete abstracts from IEEE API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://ieeexplore.ieee.org/'
        })
        self.api_successes = 0
        self.api_failures = 0
        self.cache = {}  # Cache to avoid re-fetching same articles
    
    def fetch_full_abstract(self, article_number):
        """Fetch full abstract from IEEE document metadata API"""
        
        # Check cache first
        if article_number in self.cache:
            return self.cache[article_number]
        
        endpoint = f"https://ieeexplore.ieee.org/rest/document/{article_number}/metadata"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract abstract
                abstract = data.get('abstract')
                
                if abstract:
                    # Clean HTML entities and tags
                    abstract = html.unescape(abstract)
                    # Remove HTML tags
                    abstract = re.sub('<[^<]+?>', '', abstract)
                    # Clean up whitespace
                    abstract = re.sub(r'\s+', ' ', abstract).strip()
                    
                    self.cache[article_number] = abstract
                    self.api_successes += 1
                    return abstract
            
            self.api_failures += 1
            return None
            
        except Exception as e:
            logger.debug(f"Error fetching article {article_number}: {e}")
            self.api_failures += 1
            return None
    
    def close(self):
        self.session.close()


def load_cleaned_data(input_file='results/first_authors_enriched_cleaned.json'):
    """Load the cleaned first authors file"""
    logger.info(f"Loading data from {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    logger.info(f"Loaded {len(data['authors'])} authors")
    return data


def save_enriched_data(data, output_file):
    """Save enriched data"""
    logger.info(f"Saving enriched data to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Saved to {output_file}")


def collect_all_publications(data):
    """Collect all unique publications with their article numbers"""
    publications_map = {}  # article_number -> list of (author_id, pub_index)
    
    for author_id, author_info in data['authors'].items():
        pubs = author_info.get('publications_as_first_author', [])
        
        for pub_idx, pub in enumerate(pubs):
            article_number = pub.get('article_number')
            if article_number:
                if article_number not in publications_map:
                    publications_map[article_number] = []
                publications_map[article_number].append((author_id, pub_idx))
    
    return publications_map


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich publications with complete abstracts')
    parser.add_argument('--test', action='store_true', 
                       help='Test mode - only enrich first 10 publications')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of publications to enrich')
    parser.add_argument('--resume', action='store_true',
                       help='Resume - skip publications that already have full abstracts')
    parser.add_argument('--output', default='results/first_authors_enriched_cleaned_with_abstracts.json',
                       help='Output file path')
    parser.add_argument('--input', default='results/first_authors_enriched_cleaned.json',
                       help='Input file path')
    
    args = parser.parse_args()
    
    # Load data
    data = load_cleaned_data(args.input)
    
    # If resuming from existing enriched file, load it
    output_path = Path(args.output)
    if args.resume and output_path.exists():
        logger.info(f"Resume mode: loading existing enriched data from {args.output}...")
        data = load_cleaned_data(args.output)
    
    # Collect all publications
    publications_map = collect_all_publications(data)
    
    logger.info(f"Found {len(publications_map)} unique article numbers across all authors")
    
    # Determine which publications need enrichment
    pubs_to_enrich = {}
    already_enriched = 0
    
    for article_number, locations in publications_map.items():
        # Check if first occurrence already has full abstract
        author_id, pub_idx = locations[0]
        pub = data['authors'][author_id]['publications_as_first_author'][pub_idx]
        abstract = pub.get('abstract', '')
        
        # Skip if already has full abstract (doesn't end with ...)
        if args.resume and abstract and not abstract.strip().endswith('...'):
            already_enriched += 1
            continue
        
        pubs_to_enrich[article_number] = locations
    
    if args.test:
        pubs_to_enrich = dict(list(pubs_to_enrich.items())[:10])
        logger.info(f"TEST MODE: Enriching only {len(pubs_to_enrich)} publications")
    elif args.limit:
        pubs_to_enrich = dict(list(pubs_to_enrich.items())[:args.limit])
        logger.info(f"LIMITED MODE: Enriching {len(pubs_to_enrich)} publications")
    
    total = len(pubs_to_enrich)
    
    if total == 0:
        logger.info("No publications to enrich. All done!")
        if already_enriched > 0:
            logger.info(f"{already_enriched} publications already have full abstracts")
        return
    
    logger.info(f"Will enrich {total} publications")
    if already_enriched > 0:
        logger.info(f"Skipping {already_enriched} publications that already have full abstracts")
    logger.info(f"Estimated time: ~{(total * 1.5) / 60:.1f} minutes (~{(total * 1.5) / 3600:.1f} hours)")
    
    enricher = AbstractEnricher()
    enriched_count = 0
    failed_count = 0
    
    try:
        start_time = time.time()
        
        for idx, (article_number, locations) in enumerate(pubs_to_enrich.items(), 1):
            # Get title from first occurrence for logging
            author_id, pub_idx = locations[0]
            pub = data['authors'][author_id]['publications_as_first_author'][pub_idx]
            title = pub.get('title', 'N/A')[:80]
            
            logger.info(f"[{idx}/{total}] Fetching abstract for article {article_number}...")
            logger.info(f"  Title: {title}")
            logger.info(f"  Appears in {len(locations)} author record(s)")
            
            try:
                full_abstract = enricher.fetch_full_abstract(str(article_number))
                
                if full_abstract:
                    # Update all occurrences of this publication
                    for author_id, pub_idx in locations:
                        data['authors'][author_id]['publications_as_first_author'][pub_idx]['abstract'] = full_abstract
                        data['authors'][author_id]['publications_as_first_author'][pub_idx]['abstract_enriched'] = True
                        data['authors'][author_id]['publications_as_first_author'][pub_idx]['abstract_enriched_at'] = datetime.now().isoformat()
                    
                    enriched_count += 1
                    logger.info(f"  ✓ Success - {len(full_abstract)} chars")
                else:
                    # Mark as attempted but failed
                    for author_id, pub_idx in locations:
                        data['authors'][author_id]['publications_as_first_author'][pub_idx]['abstract_fetch_error'] = 'No data available'
                    
                    failed_count += 1
                    logger.warning(f"  ✗ Failed to fetch abstract")
                
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                for author_id, pub_idx in locations:
                    data['authors'][author_id]['publications_as_first_author'][pub_idx]['abstract_fetch_error'] = str(e)
                failed_count += 1
            
            # Save progress periodically
            if idx % 50 == 0:
                save_enriched_data(data, output_path)
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
                time.sleep(1.5)
        
        # Update summary
        data['summary']['abstracts_enriched'] = True
        data['summary']['abstract_enrichment_date'] = datetime.now().isoformat()
        data['summary']['publications_with_full_abstracts'] = enriched_count
        data['summary']['abstract_fetch_failures'] = failed_count
        
        # Final save
        save_enriched_data(data, output_path)
        
        elapsed = time.time() - start_time
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"ABSTRACT ENRICHMENT COMPLETED")
        logger.info(f"{'='*70}")
        logger.info(f"Total publications processed: {total}")
        logger.info(f"Successfully enriched: {enriched_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info(f"Success rate: {enriched_count/(enriched_count+failed_count)*100:.1f}%")
        logger.info(f"Total time: {elapsed/60:.1f} minutes ({elapsed/3600:.1f} hours)")
        logger.info(f"Average time per publication: {elapsed/total:.2f} seconds")
        logger.info(f"Output file: {output_path}")
        logger.info(f"Output file size: {file_size_mb:.1f} MB")
        logger.info(f"{'='*70}")
        
    finally:
        enricher.close()


if __name__ == '__main__':
    main()

