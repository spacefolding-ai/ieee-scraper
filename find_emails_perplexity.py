#!/usr/bin/env python3
"""
Find author emails using Perplexity API
Optimized for speed with parallel processing support
"""

import json
import requests
import asyncio
import aiohttp
import re
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/perplexity_email_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PerplexityEmailFinder:
    """Find author emails using Perplexity API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.emails_found = 0
        self.emails_not_found = 0
        self.api_errors = 0
        
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        if not text:
            return None
        
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        
        # Filter out common non-personal emails
        skip_patterns = ['example.com', 'test.', 'noreply', 'no-reply', 
                        'info@', 'contact@', 'admin@', 'support@']
        
        for email in emails:
            email_lower = email.lower()
            if not any(skip in email_lower for skip in skip_patterns):
                return email
        
        return None
    
    def search_email_sync(self, author_name: str, affiliation: str) -> Dict:
        """
        Search for author email using Perplexity API (synchronous)
        
        Args:
            author_name: Full name of author
            affiliation: Author's institution
            
        Returns:
            dict with 'found', 'email', 'source', 'response' keys
        """
        prompt = f"""Find the institutional email address for this researcher:

Name: {author_name}
Affiliation: {affiliation}

Search university staff directories, academic profiles (Google Scholar, ResearchGate), 
and department pages. Return the email address if found (format: email@domain.edu), 
or respond with "NOT_FOUND" if no email is discovered.

Include the source URL where the email was found."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant finding academic email addresses. Be precise and cite sources."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "return_citations": True,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                citations = data.get('citations', [])
                
                # Extract email
                email = self.extract_email(content)
                
                if email and "NOT_FOUND" not in content.upper():
                    self.emails_found += 1
                    return {
                        'found': True,
                        'email': email,
                        'source_url': citations[0] if citations else None,
                        'response': content[:200],
                        'citations': citations
                    }
                else:
                    self.emails_not_found += 1
                    return {
                        'found': False,
                        'email': None,
                        'source_url': None,
                        'reason': 'Not found in search results'
                    }
            else:
                self.api_errors += 1
                error_body = response.text
                logger.warning(f"API returned status {response.status_code}")
                logger.warning(f"Response body: {error_body}")
                return {
                    'found': False,
                    'email': None,
                    'error': f"API error: {response.status_code}",
                    'error_details': error_body
                }
                
        except Exception as e:
            self.api_errors += 1
            logger.error(f"Error searching for {author_name}: {e}")
            return {
                'found': False,
                'email': None,
                'error': str(e)
            }
    
    async def search_email_async(self, session: aiohttp.ClientSession, 
                                 author_name: str, affiliation: str) -> Dict:
        """
        Search for author email using Perplexity API (asynchronous)
        
        Args:
            session: aiohttp ClientSession
            author_name: Full name of author
            affiliation: Author's institution
            
        Returns:
            dict with 'found', 'email', 'source', 'response' keys
        """
        prompt = f"""Find the institutional email address for this researcher:

Name: {author_name}
Affiliation: {affiliation}

Search university staff directories, academic profiles, and department pages. 
Return the email if found, or "NOT_FOUND" if not found. Include the source URL."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a research assistant finding academic emails. Be precise."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "return_citations": True,
            "max_tokens": 500
        }
        
        try:
            async with session.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    citations = data.get('citations', [])
                    
                    email = self.extract_email(content)
                    
                    if email and "NOT_FOUND" not in content.upper():
                        self.emails_found += 1
                        return {
                            'found': True,
                            'email': email,
                            'source_url': citations[0] if citations else None,
                            'response': content[:200],
                            'citations': citations
                        }
                    else:
                        self.emails_not_found += 1
                        return {
                            'found': False,
                            'email': None,
                            'reason': 'Not found'
                        }
                else:
                    self.api_errors += 1
                    error_body = await response.text()
                    logger.warning(f"API returned status {response.status}")
                    logger.warning(f"Response body: {error_body}")
                    return {
                        'found': False,
                        'error': f"API error: {response.status}",
                        'error_details': error_body
                    }
                    
        except Exception as e:
            self.api_errors += 1
            logger.error(f"Error: {e}")
            return {
                'found': False,
                'error': str(e)
            }


async def process_authors_parallel(finder: PerplexityEmailFinder,
                                   authors_dict: Dict,
                                   output_file: Path,
                                   concurrent: int = 5) -> Dict:
    """
    Process authors in parallel using asyncio
    
    Args:
        finder: PerplexityEmailFinder instance
        authors_dict: Dictionary of authors to process
        output_file: Path to output file
        concurrent: Number of concurrent requests
        
    Returns:
        Dictionary with results
    """
    results = {}
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(concurrent)
        
        async def search_with_semaphore(author_id, author_info):
            async with semaphore:
                name = author_info.get('primary_preferred_name', 'Unknown')
                affiliations = author_info.get('current_affiliations', [])
                
                if not affiliations:
                    return author_id, {
                        'name': name,
                        'affiliation': None,
                        'email_search': {'found': False, 'reason': 'no affiliation'}
                    }
                
                affiliation = affiliations[0]
                
                logger.info(f"Searching: {name}")
                email_result = await finder.search_email_async(session, name, affiliation)
                
                return author_id, {
                    'name': name,
                    'affiliation': affiliation,
                    'all_affiliations': affiliations,
                    'email_search': email_result
                }
        
        # Create tasks for all authors
        tasks = [search_with_semaphore(aid, ainfo) 
                for aid, ainfo in authors_dict.items()]
        
        # Process in batches with progress tracking
        batch_size = 50
        total = len(tasks)
        
        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch_tasks)
            
            # Store results
            for author_id, result in batch_results:
                results[author_id] = result
            
            # Save progress
            progress = min(i + batch_size, total)
            logger.info(f"Progress: {progress}/{total} ({progress/total*100:.1f}%)")
            logger.info(f"Emails found so far: {finder.emails_found}")
            
            # Save intermediate results
            if progress % 100 == 0 or progress == total:
                save_results(results, output_file, finder, total, progress)
            
            # Small delay between batches
            if i + batch_size < len(tasks):
                await asyncio.sleep(2)
    
    return results


def process_authors_sync(finder: PerplexityEmailFinder,
                         authors_dict: Dict,
                         output_file: Path) -> Dict:
    """
    Process authors synchronously (slower but more stable)
    
    Args:
        finder: PerplexityEmailFinder instance
        authors_dict: Dictionary of authors to process
        output_file: Path to output file
        
    Returns:
        Dictionary with results
    """
    results = {}
    total = len(authors_dict)
    
    for idx, (author_id, author_info) in enumerate(authors_dict.items(), 1):
        name = author_info.get('primary_preferred_name', 'Unknown')
        affiliations = author_info.get('current_affiliations', [])
        
        logger.info(f"[{idx}/{total}] Processing: {name}")
        
        if not affiliations:
            logger.warning("  No affiliation available")
            results[author_id] = {
                'name': name,
                'affiliation': None,
                'email_search': {'found': False, 'reason': 'no affiliation'}
            }
            continue
        
        affiliation = affiliations[0]
        logger.info(f"  Affiliation: {affiliation[:80]}")
        
        # Search for email
        email_result = finder.search_email_sync(name, affiliation)
        
        if email_result.get('found'):
            logger.info(f"  ✓ Found: {email_result['email']}")
        else:
            logger.warning(f"  ✗ Not found")
        
        results[author_id] = {
            'name': name,
            'affiliation': affiliation,
            'all_affiliations': affiliations,
            'email_search': email_result
        }
        
        # Save progress every 25 authors
        if idx % 25 == 0:
            save_results(results, output_file, finder, total, idx)
            logger.info(f"Progress saved: {idx}/{total} ({idx/total*100:.1f}%)")
        
        # Rate limiting
        time.sleep(2)
    
    return results


def save_results(results: Dict, output_file: Path, 
                finder: PerplexityEmailFinder, total: int, processed: int):
    """Save results to JSON file"""
    output_data = {
        'summary': {
            'total_authors': total,
            'processed': processed,
            'emails_found': finder.emails_found,
            'emails_not_found': finder.emails_not_found,
            'api_errors': finder.api_errors,
            'success_rate': f"{finder.emails_found/(processed)*100:.1f}%" if processed > 0 else "0%",
            'last_updated': datetime.now().isoformat()
        },
        'authors': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def main():
    import argparse
    import os
    
    # Try to load from .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        # dotenv not installed, will try environment variables or command line
        pass
    
    parser = argparse.ArgumentParser(description='Find author emails using Perplexity API')
    parser.add_argument('--input', default='results/first_authors_enriched_cleaned_with_abstracts.json',
                       help='Input JSON file')
    parser.add_argument('--output', default='results/authors_with_emails_perplexity.json',
                       help='Output JSON file')
    parser.add_argument('--api-key', default=None,
                       help='Perplexity API key (or set PERPLEXITY_API_KEY env var)')
    parser.add_argument('--parallel', action='store_true',
                       help='Use parallel processing (faster)')
    parser.add_argument('--concurrent', type=int, default=5,
                       help='Number of concurrent requests (default: 5)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - only process 10 authors')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of authors')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from existing output')
    
    args = parser.parse_args()
    
    # Get API key from args, environment, or .env file
    api_key = args.api_key or os.getenv('PERPLEXITY_API_KEY')
    
    if not api_key:
        logger.error("Perplexity API key not found!")
        logger.error("Please provide it via:")
        logger.error("  1. Command line: --api-key 'pplx-xxx'")
        logger.error("  2. Environment variable: export PERPLEXITY_API_KEY='pplx-xxx'")
        logger.error("  3. .env file: PERPLEXITY_API_KEY=pplx-xxx")
        return
    
    # Load data
    logger.info(f"Loading authors from {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    authors = data['authors']
    logger.info(f"Loaded {len(authors)} authors")
    
    # Handle resume
    processed_ids = set()
    output_path = Path(args.output)
    
    if args.resume and output_path.exists():
        logger.info("Resume mode: loading existing results...")
        with open(args.output, 'r', encoding='utf-8') as f:
            existing = json.load(f)
            processed_ids = set(existing.get('authors', {}).keys())
            logger.info(f"Already processed {len(processed_ids)} authors")
    
    # Filter authors to process
    authors_to_process = {
        aid: ainfo for aid, ainfo in authors.items()
        if aid not in processed_ids
    }
    
    if args.test:
        authors_to_process = dict(list(authors_to_process.items())[:10])
        logger.info(f"TEST MODE: Processing {len(authors_to_process)} authors")
    elif args.limit:
        authors_to_process = dict(list(authors_to_process.items())[:args.limit])
        logger.info(f"LIMITED: Processing {len(authors_to_process)} authors")
    
    total = len(authors_to_process)
    
    if total == 0:
        logger.info("No authors to process!")
        return
    
    # Initialize finder
    finder = PerplexityEmailFinder(api_key)
    
    # Estimate
    if args.parallel:
        est_time = (total / args.concurrent * 6) / 60
        logger.info(f"PARALLEL MODE: {args.concurrent} concurrent requests")
    else:
        est_time = (total * 6) / 60
        logger.info(f"SEQUENTIAL MODE")
    
    logger.info(f"Processing {total} authors")
    logger.info(f"Estimated time: {est_time:.1f} minutes ({est_time/60:.1f} hours)")
    
    start_time = time.time()
    
    # Process
    if args.parallel:
        results = asyncio.run(process_authors_parallel(
            finder, authors_to_process, output_path, args.concurrent
        ))
    else:
        results = process_authors_sync(finder, authors_to_process, output_path)
    
    # Final save
    elapsed = time.time() - start_time
    save_results(results, output_path, finder, total, total)
    
    file_size = output_path.stat().st_size / (1024 * 1024)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"EMAIL SEARCH COMPLETED")
    logger.info(f"{'='*70}")
    logger.info(f"Total processed: {total}")
    logger.info(f"Emails found: {finder.emails_found}")
    logger.info(f"Not found: {finder.emails_not_found}")
    logger.info(f"API errors: {finder.api_errors}")
    logger.info(f"Success rate: {finder.emails_found/total*100:.1f}%")
    logger.info(f"Total time: {elapsed/60:.1f} minutes ({elapsed/3600:.1f} hours)")
    logger.info(f"Avg per author: {elapsed/total:.1f} seconds")
    logger.info(f"Output: {output_path} ({file_size:.1f} MB)")
    logger.info(f"{'='*70}")


if __name__ == '__main__':
    main()

