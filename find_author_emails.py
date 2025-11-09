#!/usr/bin/env python3
"""
Find author emails by searching Google
Checks top 5 results and stops when email is found
"""

import json
import requests
import re
import time
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/email_search.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailFinder:
    """Find author emails using Google search"""
    
    def __init__(self, google_api_key=None, google_cx=None, use_scraping=True):
        """
        Initialize email finder
        
        Args:
            google_api_key: Google Custom Search API key (optional)
            google_cx: Google Custom Search Engine ID (optional)
            use_scraping: If True, use web scraping as fallback (slower but free)
        """
        self.api_key = google_api_key
        self.cx = google_cx
        self.use_scraping = use_scraping
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
        self.emails_found = 0
        self.emails_not_found = 0
    
    def extract_emails(self, text):
        """Extract email addresses from text"""
        if not text:
            return []
        
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        
        # Filter out common non-personal emails
        filtered = []
        skip_patterns = ['example.com', 'test.', 'noreply', 'no-reply', 
                        'info@', 'contact@', 'admin@', 'support@']
        
        for email in emails:
            email_lower = email.lower()
            if not any(skip in email_lower for skip in skip_patterns):
                filtered.append(email)
        
        return list(set(filtered))  # Remove duplicates
    
    def search_google_api(self, query, num_results=5):
        """
        Search using Google Custom Search API
        
        Args:
            query: Search query
            num_results: Number of results to check (max 10)
            
        Returns:
            List of search result items
        """
        if not self.api_key or not self.cx:
            return None
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.cx,
            'q': query,
            'num': min(num_results, 10)
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
            else:
                logger.warning(f"Google API returned status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return None
    
    def search_google_scraping(self, query, num_results=5):
        """
        Search using web scraping (fallback method)
        Note: Use responsibly, add delays between requests
        
        Args:
            query: Search query
            num_results: Number of results to fetch
            
        Returns:
            List of URLs from search results
        """
        from bs4 import BeautifulSoup
        
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num={num_results}"
        
        try:
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract URLs from search results
                results = []
                for g in soup.find_all('div', class_='g'):
                    link = g.find('a')
                    if link and link.get('href'):
                        url = link['href']
                        if url.startswith('http'):
                            results.append({'link': url})
                            if len(results) >= num_results:
                                break
                
                return results
            else:
                logger.warning(f"Google search returned status {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Google scraping error: {e}")
            return []
    
    def fetch_page_content(self, url):
        """Fetch and return page content"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            return None
        except Exception as e:
            logger.debug(f"Error fetching {url}: {e}")
            return None
    
    def find_author_email(self, author_name, affiliation, max_results=5):
        """
        Find author email by searching Google
        Checks top results and stops when email is found
        
        Args:
            author_name: Full name of author
            affiliation: Author's institution/university
            max_results: Number of results to check (default 5)
            
        Returns:
            dict with 'email', 'source_url', 'found' keys
        """
        # Construct search query
        query = f'"{author_name}" "{affiliation}" email OR contact'
        logger.info(f"Searching: {query}")
        
        # Try API first
        search_results = None
        if self.api_key and self.cx:
            search_results = self.search_google_api(query, max_results)
            method = "API"
        
        # Fallback to scraping
        if not search_results and self.use_scraping:
            time.sleep(2)  # Rate limiting
            search_results = self.search_google_scraping(query, max_results)
            method = "Scraping"
        
        if not search_results:
            logger.warning(f"No search results for {author_name}")
            self.emails_not_found += 1
            return {'found': False, 'email': None, 'source_url': None}
        
        logger.info(f"Got {len(search_results)} results via {method}")
        
        # Check each result for emails
        for idx, result in enumerate(search_results[:max_results], 1):
            url = result.get('link', '')
            snippet = result.get('snippet', '')
            
            logger.debug(f"Checking result {idx}: {url}")
            
            # First check snippet for emails
            emails = self.extract_emails(snippet)
            if emails:
                logger.info(f"✓ Found email in snippet: {emails[0]}")
                self.emails_found += 1
                return {
                    'found': True,
                    'email': emails[0],
                    'source_url': url,
                    'source': f'snippet (result {idx})'
                }
            
            # Fetch page content
            content = self.fetch_page_content(url)
            if content:
                emails = self.extract_emails(content)
                if emails:
                    logger.info(f"✓ Found email on page: {emails[0]}")
                    self.emails_found += 1
                    return {
                        'found': True,
                        'email': emails[0],
                        'source_url': url,
                        'source': f'page content (result {idx})'
                    }
            
            # Add small delay between page fetches
            time.sleep(1)
        
        logger.warning(f"✗ No email found for {author_name}")
        self.emails_not_found += 1
        return {'found': False, 'email': None, 'source_url': None}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Find author emails via Google search')
    parser.add_argument('--input', default='results/first_authors_enriched_cleaned_with_abstracts.json',
                       help='Input JSON file with author data')
    parser.add_argument('--output', default='results/authors_with_emails.json',
                       help='Output JSON file')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of authors to process')
    parser.add_argument('--test', action='store_true',
                       help='Test mode - only process first 5 authors')
    parser.add_argument('--api-key', default=None,
                       help='Google Custom Search API key')
    parser.add_argument('--cx', default=None,
                       help='Google Custom Search Engine ID')
    parser.add_argument('--no-scraping', action='store_true',
                       help='Disable web scraping fallback')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from existing output file')
    
    args = parser.parse_args()
    
    # Load author data
    logger.info(f"Loading authors from {args.input}...")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    authors = data['authors']
    total_authors = len(authors)
    logger.info(f"Loaded {total_authors} authors")
    
    # Load existing results if resuming
    processed_ids = set()
    results = {}
    
    output_path = Path(args.output)
    if args.resume and output_path.exists():
        logger.info(f"Resume mode: loading existing results from {args.output}")
        with open(args.output, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            results = existing_data.get('authors', {})
            processed_ids = set(results.keys())
            logger.info(f"Already processed {len(processed_ids)} authors")
    
    # Filter authors to process
    authors_to_process = {
        aid: ainfo for aid, ainfo in authors.items() 
        if aid not in processed_ids
    }
    
    if args.test:
        authors_to_process = dict(list(authors_to_process.items())[:5])
        logger.info(f"TEST MODE: Processing only {len(authors_to_process)} authors")
    elif args.limit:
        authors_to_process = dict(list(authors_to_process.items())[:args.limit])
        logger.info(f"LIMITED MODE: Processing {len(authors_to_process)} authors")
    
    total_to_process = len(authors_to_process)
    
    if total_to_process == 0:
        logger.info("No authors to process. All done!")
        return
    
    logger.info(f"Will search for emails of {total_to_process} authors")
    
    # Initialize email finder
    use_scraping = not args.no_scraping
    finder = EmailFinder(
        google_api_key=args.api_key,
        google_cx=args.cx,
        use_scraping=use_scraping
    )
    
    if args.api_key and args.cx:
        logger.info("Using Google Custom Search API")
    elif use_scraping:
        logger.info("Using web scraping method (free but slower)")
    else:
        logger.error("No search method available! Provide API credentials or enable scraping")
        return
    
    start_time = time.time()
    
    # Process each author
    for idx, (author_id, author_info) in enumerate(authors_to_process.items(), 1):
        name = author_info.get('primary_preferred_name', 'Unknown')
        affiliations = author_info.get('current_affiliations', [])
        
        logger.info(f"\n[{idx}/{total_to_process}] Processing: {name}")
        
        if not affiliations:
            logger.warning("  No affiliation available, skipping")
            results[author_id] = {
                'name': name,
                'affiliation': None,
                'email_search': {'found': False, 'reason': 'no affiliation'}
            }
            continue
        
        main_affiliation = affiliations[0]
        logger.info(f"  Affiliation: {main_affiliation[:80]}")
        
        # Search for email
        email_result = finder.find_author_email(name, main_affiliation)
        
        # Store result
        results[author_id] = {
            'name': name,
            'affiliation': main_affiliation,
            'all_affiliations': affiliations,
            'email_search': email_result
        }
        
        # Save progress every 10 authors
        if idx % 10 == 0:
            output_data = {
                'summary': {
                    'total_authors': total_to_process,
                    'processed': idx,
                    'emails_found': finder.emails_found,
                    'emails_not_found': finder.emails_not_found,
                    'success_rate': f"{finder.emails_found/(finder.emails_found+finder.emails_not_found)*100:.1f}%",
                    'last_updated': datetime.now().isoformat()
                },
                'authors': results
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Progress saved: {idx}/{total_to_process} ({idx/total_to_process*100:.1f}%)")
        
        # Rate limiting - be nice to Google
        time.sleep(3)
    
    # Final save
    elapsed = time.time() - start_time
    
    output_data = {
        'summary': {
            'total_authors': total_to_process,
            'processed': total_to_process,
            'emails_found': finder.emails_found,
            'emails_not_found': finder.emails_not_found,
            'success_rate': f"{finder.emails_found/(finder.emails_found+finder.emails_not_found)*100:.1f}%",
            'completed_at': datetime.now().isoformat(),
            'processing_time_minutes': elapsed / 60
        },
        'authors': results
    }
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n{'='*70}")
    logger.info(f"EMAIL SEARCH COMPLETED")
    logger.info(f"{'='*70}")
    logger.info(f"Total authors processed: {total_to_process}")
    logger.info(f"Emails found: {finder.emails_found}")
    logger.info(f"Emails not found: {finder.emails_not_found}")
    logger.info(f"Success rate: {finder.emails_found/(finder.emails_found+finder.emails_not_found)*100:.1f}%")
    logger.info(f"Total time: {elapsed/60:.1f} minutes")
    logger.info(f"Output file: {args.output}")
    logger.info(f"{'='*70}")


if __name__ == '__main__':
    main()

