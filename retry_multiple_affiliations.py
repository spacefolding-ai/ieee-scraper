#!/usr/bin/env python3
"""
Retry email search for authors with multiple affiliations who weren't found
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime

# Import from existing script
import sys
sys.path.insert(0, str(Path(__file__).parent))
from find_emails_perplexity import PerplexityEmailFinder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/perplexity_retry_multiple_aff.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_results(filepath):
    """Load existing results"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_results(data, filepath):
    """Save updated results"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_retry_candidates(data):
    """Find authors with multiple affiliations who weren't found"""
    retry_list = []
    
    for author_id, info in data['authors'].items():
        all_affs = info.get('all_affiliations', [])
        
        # If email NOT found and has multiple affiliations
        if not info['email_search'].get('found') and len(all_affs) > 1:
            retry_list.append({
                'author_id': author_id,
                'name': info['name'],
                'tried_affiliation': info.get('affiliation'),
                'remaining_affiliations': all_affs[1:]  # All except first (already tried)
            })
    
    return retry_list


def retry_with_alternative_affiliations(finder, retry_list, data):
    """
    Retry email search with alternative affiliations
    
    Args:
        finder: PerplexityEmailFinder instance
        retry_list: List of authors to retry
        data: The full results data structure
    
    Returns:
        Number of newly found emails
    """
    newly_found = 0
    total_to_retry = len(retry_list)
    
    logger.info(f"🔄 Starting retry for {total_to_retry} authors with multiple affiliations")
    logger.info(f"⏱️  Estimated time: {(total_to_retry * 6) / 60:.1f} minutes")
    
    for idx, candidate in enumerate(retry_list, 1):
        author_id = candidate['author_id']
        name = candidate['name']
        remaining_affs = candidate['remaining_affiliations']
        
        logger.info(f"\n[{idx}/{total_to_retry}] Retrying: {name}")
        logger.info(f"  Previous attempt: {candidate['tried_affiliation'][:80]}")
        
        # Try each remaining affiliation until we find an email
        for aff_idx, affiliation in enumerate(remaining_affs, 1):
            logger.info(f"  Try #{aff_idx + 1}: {affiliation[:80]}")
            
            # Search for email with this affiliation
            email_result = finder.search_email_sync(name, affiliation)
            
            if email_result.get('found'):
                logger.info(f"  ✅ FOUND: {email_result['email']}")
                
                # Update the author's data
                data['authors'][author_id]['affiliation'] = affiliation
                data['authors'][author_id]['email_search'] = email_result
                data['authors'][author_id]['email_search']['note'] = f"Found on retry attempt #{aff_idx + 1} with alternative affiliation"
                data['authors'][author_id]['email_search']['retry_info'] = {
                    'originally_tried': candidate['tried_affiliation'],
                    'successful_affiliation': affiliation,
                    'retry_attempt': aff_idx + 1,
                    'retry_date': datetime.now().isoformat()
                }
                
                newly_found += 1
                break  # Found email, no need to try other affiliations
            else:
                logger.info(f"  ❌ Not found with this affiliation")
            
            # Rate limiting between attempts
            time.sleep(2)
        
        if not data['authors'][author_id]['email_search'].get('found'):
            logger.warning(f"  ⚠️  Still not found after trying {len(remaining_affs)} additional affiliation(s)")
        
        # Save progress every 10 authors
        if idx % 10 == 0:
            logger.info(f"\n💾 Saving progress... ({newly_found} newly found so far)")
    
    return newly_found


def main():
    import argparse
    import os
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    parser = argparse.ArgumentParser(description='Retry email search with alternative affiliations')
    parser.add_argument('--input', default='results/authors_with_emails_perplexity.json',
                       help='Input/Output JSON file')
    parser.add_argument('--api-key', default=None,
                       help='Perplexity API key (or set PERPLEXITY_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key or os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        logger.error("Perplexity API key not found!")
        logger.error("Please provide it via:")
        logger.error("  1. Command line: --api-key 'pplx-xxx'")
        logger.error("  2. Environment variable: export PERPLEXITY_API_KEY='pplx-xxx'")
        logger.error("  3. .env file: PERPLEXITY_API_KEY=pplx-xxx")
        return
    
    # Load existing results
    logger.info(f"📂 Loading results from {args.input}...")
    data = load_results(args.input)
    
    original_found = data['summary']['emails_found']
    original_not_found = data['summary']['emails_not_found']
    
    logger.info(f"📊 Current stats: {original_found} found, {original_not_found} not found")
    
    # Find retry candidates
    logger.info("🔍 Finding authors to retry...")
    retry_list = find_retry_candidates(data)
    
    if not retry_list:
        logger.info("✅ No authors to retry - all done!")
        return
    
    logger.info(f"📋 Found {len(retry_list)} authors to retry")
    
    # Initialize finder
    finder = PerplexityEmailFinder(api_key)
    
    # Retry with alternative affiliations
    start_time = time.time()
    newly_found = retry_with_alternative_affiliations(finder, retry_list, data)
    elapsed = time.time() - start_time
    
    # Update summary
    data['summary']['emails_found'] = original_found + newly_found
    data['summary']['emails_not_found'] = original_not_found - newly_found
    data['summary']['success_rate'] = f"{data['summary']['emails_found']/data['summary']['total_authors']*100:.1f}%"
    data['summary']['last_updated'] = datetime.now().isoformat()
    data['summary']['retry_info'] = {
        'retry_date': datetime.now().isoformat(),
        'authors_retried': len(retry_list),
        'newly_found': newly_found,
        'retry_success_rate': f"{newly_found/len(retry_list)*100:.1f}%"
    }
    
    # Save final results
    logger.info("\n💾 Saving final results...")
    save_results(data, args.input)
    
    # Print final summary
    logger.info(f"\n{'='*70}")
    logger.info(f"🎉 RETRY COMPLETED")
    logger.info(f"{'='*70}")
    logger.info(f"Authors retried: {len(retry_list)}")
    logger.info(f"Newly found emails: {newly_found}")
    logger.info(f"Retry success rate: {newly_found/len(retry_list)*100:.1f}%")
    logger.info(f"Time taken: {elapsed/60:.1f} minutes")
    logger.info(f"")
    logger.info(f"📊 UPDATED OVERALL STATS:")
    logger.info(f"Total emails found: {data['summary']['emails_found']} (was {original_found})")
    logger.info(f"Overall success rate: {data['summary']['success_rate']} (was {original_found/2211*100:.1f}%)")
    logger.info(f"Improvement: +{newly_found} emails (+{newly_found/2211*100:.2f}%)")
    logger.info(f"{'='*70}")


if __name__ == '__main__':
    main()

