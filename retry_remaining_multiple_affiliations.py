#!/usr/bin/env python3
"""
Retry email search for authors with multiple affiliations who weren't found
"""

import json
import time
import logging
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import from the main script
import sys
sys.path.append(str(Path(__file__).parent))
from find_emails_perplexity import PerplexityEmailFinder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/retry_remaining_affiliations.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

def main():
    logger.info("=" * 70)
    logger.info("RETRY EMAIL SEARCH WITH ALTERNATIVE AFFILIATIONS")
    logger.info("=" * 70)
    
    # Load API key
    api_key = os.getenv('PERPLEXITY_API_KEY')
    if not api_key:
        logger.error("Perplexity API key not found!")
        return
    
    # Load results
    results_file = Path('results/remaining_european_authors_emails.json')
    with open(results_file, 'r') as f:
        results_data = json.load(f)
    
    # Load original data with all affiliations
    original_file = Path('results/remaining_european_authors_for_emails.json')
    with open(original_file, 'r') as f:
        original_data = json.load(f)
    
    original_authors = original_data.get('authors', {})
    results_authors = results_data.get('authors', {})
    
    # Find retry candidates
    retry_candidates = []
    for author_id, result in results_authors.items():
        if not result.get('email_search', {}).get('found', False):
            orig_author = original_authors.get(author_id, {})
            affiliations = orig_author.get('current_affiliations', [])
            
            if len(affiliations) > 1:
                retry_candidates.append({
                    'id': author_id,
                    'name': orig_author.get('primary_preferred_name', 'Unknown'),
                    'tried_affiliation': result.get('affiliation'),
                    'alternative_affiliations': affiliations[1:],  # Skip first (already tried)
                    'original_result': result
                })
    
    logger.info(f"Found {len(retry_candidates)} authors with multiple affiliations to retry")
    
    if not retry_candidates:
        logger.info("No authors to retry!")
        return
    
    # Initialize finder
    finder = PerplexityEmailFinder(api_key)
    
    # Retry each author with alternative affiliations
    emails_found = 0
    attempts = 0
    
    for i, candidate in enumerate(retry_candidates, 1):
        author_id = candidate['id']
        name = candidate['name']
        
        logger.info(f"[{i}/{len(retry_candidates)}] Retrying: {name}")
        logger.info(f"  Originally tried: {candidate['tried_affiliation'][:70]}...")
        
        # Try each alternative affiliation
        found = False
        for j, alt_affiliation in enumerate(candidate['alternative_affiliations'], 2):
            logger.info(f"  Trying affiliation #{j}: {alt_affiliation[:70]}...")
            
            # Search with this affiliation
            result = finder.search_email_sync(name, alt_affiliation)
            attempts += 1
            
            time.sleep(2.5)  # Rate limiting
            
            if result.get('found'):
                email = result.get('email')
                logger.info(f"    ✓ Found: {email}")
                
                # Update the results
                results_authors[author_id]['email_search'] = {
                    'found': True,
                    'email': email,
                    'source_url': result.get('source_url'),
                    'response': result.get('response'),
                    'citations': result.get('citations'),
                    'retry_info': {
                        'originally_tried': candidate['tried_affiliation'],
                        'successful_affiliation': alt_affiliation,
                        'retry_attempt': j,
                        'retried_at': datetime.now().isoformat()
                    }
                }
                
                emails_found += 1
                found = True
                break  # Stop trying other affiliations for this author
            else:
                logger.info(f"    ✗ Not found")
        
        if not found:
            logger.info(f"  ✗ No email found with any alternative affiliation")
        
        # Save progress every 10 authors
        if i % 10 == 0:
            logger.info(f"💾 Saving progress... ({emails_found} emails found so far)")
            save_results(results_data, results_file, emails_found, attempts, len(retry_candidates))
    
    # Final save
    logger.info("\n" + "=" * 70)
    logger.info("RETRY COMPLETED")
    logger.info("=" * 70)
    logger.info(f"Authors retried: {len(retry_candidates)}")
    logger.info(f"Alternative affiliations tried: {attempts}")
    logger.info(f"Additional emails found: {emails_found}")
    logger.info(f"Success rate: {emails_found/len(retry_candidates)*100:.1f}%")
    
    save_results(results_data, results_file, emails_found, attempts, len(retry_candidates))
    logger.info(f"Updated: {results_file}")
    logger.info("=" * 70)


def save_results(results_data, output_file, emails_found, attempts, total_retried):
    """Save updated results"""
    # Update summary
    summary = results_data.get('summary', {})
    
    # Recalculate totals
    authors = results_data.get('authors', {})
    total_emails = sum(1 for a in authors.values() if a.get('email_search', {}).get('found', False))
    total_not_found = sum(1 for a in authors.values() if not a.get('email_search', {}).get('found', False))
    
    summary['emails_found'] = total_emails
    summary['not_found'] = total_not_found
    summary['success_rate'] = f"{total_emails/summary['total_authors']*100:.1f}%"
    summary['last_updated'] = datetime.now().isoformat()
    summary['retry_info'] = {
        'authors_retried': total_retried,
        'additional_emails_from_retry': emails_found,
        'alternative_affiliations_tried': attempts,
        'retry_date': datetime.now().isoformat()
    }
    
    results_data['summary'] = summary
    
    with open(output_file, 'w') as f:
        json.dump(results_data, f, indent=2)


if __name__ == '__main__':
    main()

