#!/usr/bin/env python3
"""
IEEE Author Affiliation Fetcher
Tries direct API calls first, falls back to Selenium if needed
"""

import json
import time
import logging
import os
from pathlib import Path
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/author_affiliation_fetch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AuthorAffiliationFetcher:
    """Fetch author affiliation data from IEEE with fallback strategies"""
    
    def __init__(self, headless=True, method='auto'):
        """
        Initialize fetcher
        
        Args:
            headless (bool): Run Selenium in headless mode
            method (str): 'api', 'selenium', or 'auto' (try api first, fallback to selenium)
        """
        self.headless = headless
        self.method = method
        self.driver = None
        self.api_failures = 0
        self.api_successes = 0
        self.selenium_mode = False
        
        # HTTP session for API calls
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://ieeexplore.ieee.org/',
            'Origin': 'https://ieeexplore.ieee.org'
        })
    
    def fetch_via_api(self, author_id):
        """
        Try to fetch author data via direct API call
        
        Args:
            author_id (int): IEEE author ID
            
        Returns:
            dict: Author data or None if failed
        """
        # IEEE author API endpoint
        endpoint = f"https://ieeexplore.ieee.org/rest/author/{author_id}"
        
        try:
            response = self.session.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # API returns a list, take the first element
                if isinstance(data, list) and len(data) > 0:
                    author_data = data[0]
                    self.api_successes += 1
                    return author_data
                elif isinstance(data, dict):
                    self.api_successes += 1
                    return data
                else:
                    logger.warning(f"Unexpected data format from API for author {author_id}")
                    self.api_failures += 1
                    return None
            else:
                logger.debug(f"API returned status {response.status_code} for author {author_id}")
                self.api_failures += 1
                return None
                
        except requests.exceptions.RequestException as e:
            logger.debug(f"API request failed for {endpoint}: {e}")
            self.api_failures += 1
            return None
        except json.JSONDecodeError:
            logger.debug(f"Invalid JSON from {endpoint}")
            self.api_failures += 1
            return None
    
    def _init_selenium(self):
        """Initialize Selenium driver"""
        if self.driver is not None:
            return
        
        logger.info("Initializing Selenium WebDriver...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Initialize driver
        driver_path = ChromeDriverManager().install()
        if 'THIRD_PARTY_NOTICES' in driver_path:
            driver_dir = os.path.dirname(driver_path)
            driver_path = os.path.join(driver_dir, 'chromedriver')
        
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.selenium_mode = True
        logger.info("Selenium WebDriver initialized")
    
    def fetch_via_selenium(self, author_id):
        """
        Fetch author data via Selenium by capturing network requests
        
        Args:
            author_id (int): IEEE author ID
            
        Returns:
            dict: Author data or None if failed
        """
        if self.driver is None:
            self._init_selenium()
        
        try:
            url = f"https://ieeexplore.ieee.org/author/{author_id}"
            logger.debug(f"Loading author page: {url}")
            
            self.driver.get(url)
            time.sleep(3)  # Wait for page and API calls to load
            
            # Try to extract affiliation from the page directly
            affiliation_data = self._extract_affiliation_from_page()
            
            if affiliation_data:
                return affiliation_data
            
            # Fallback: try to get from network logs
            logs = self.driver.get_log('performance')
            
            for entry in logs:
                try:
                    log = json.loads(entry['message'])
                    message = log['message']
                    
                    if message.get('method') == 'Network.responseReceived':
                        response = message['params']['response']
                        response_url = response.get('url', '')
                        
                        # Look for author-related API responses
                        if '/author/' in response_url or '/rest/' in response_url:
                            request_id = message['params']['requestId']
                            
                            try:
                                body = self.driver.execute_cdp_cmd(
                                    'Network.getResponseBody',
                                    {'requestId': request_id}
                                )
                                
                                if body.get('body'):
                                    try:
                                        data = json.loads(body['body'])
                                        # Check if this looks like author data
                                        if isinstance(data, dict) and ('affiliation' in data or 'author' in data):
                                            return data
                                    except json.JSONDecodeError:
                                        continue
                            except Exception as e:
                                logger.debug(f"Could not get response body: {e}")
                                continue
                                
                except Exception as e:
                    logger.debug(f"Error processing log entry: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Selenium fetch failed for author {author_id}: {e}")
            return None
    
    def _extract_affiliation_from_page(self):
        """
        Extract affiliation by parsing the current page HTML
        
        Returns:
            dict: Author data with affiliation or None
        """
        try:
            from selenium.webdriver.common.by import By
            
            # Try to find affiliation elements
            author_data = {}
            
            # Look for author name
            try:
                name_elem = self.driver.find_element(By.CSS_SELECTOR, 'h1.author-name, .author-profile-name')
                author_data['name'] = name_elem.text.strip()
            except:
                pass
            
            # Look for affiliation
            affiliation_selectors = [
                '.author-affiliation',
                '.current-affiliation',
                '[class*="affiliation"]',
                '.author-info .affiliation'
            ]
            
            for selector in affiliation_selectors:
                try:
                    affiliation_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    author_data['affiliation'] = affiliation_elem.text.strip()
                    break
                except:
                    continue
            
            # Look for other metadata
            try:
                bio_elem = self.driver.find_element(By.CSS_SELECTOR, '.author-bio, .biography')
                author_data['biography'] = bio_elem.text.strip()
            except:
                pass
            
            if author_data.get('affiliation'):
                return author_data
            
            return None
            
        except Exception as e:
            logger.debug(f"Could not extract from page HTML: {e}")
            return None
    
    def fetch_author_data(self, author_id, force_method=None):
        """
        Fetch author data with fallback logic
        
        Args:
            author_id (int): IEEE author ID
            force_method (str): 'api' or 'selenium' to force a specific method
            
        Returns:
            dict: Author data or None if both methods fail
        """
        method = force_method or self.method
        
        if method == 'api':
            return self.fetch_via_api(author_id)
        elif method == 'selenium':
            return self.fetch_via_selenium(author_id)
        else:  # auto mode
            # Try API first
            data = self.fetch_via_api(author_id)
            
            if data:
                return data
            
            # If API consistently fails, switch to selenium mode permanently
            if self.api_failures > 10 and self.api_successes == 0:
                logger.warning("API method failing consistently, switching to Selenium mode")
                self.method = 'selenium'
                self._init_selenium()
            
            # Try Selenium as fallback
            if self.api_failures % 5 == 0:  # Only use selenium for every 5th failure to save time
                logger.debug(f"API failed for author {author_id}, trying Selenium fallback")
                return self.fetch_via_selenium(author_id)
            
            return None
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
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
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch IEEE author affiliations')
    parser.add_argument('--test', action='store_true', help='Test mode - only fetch first 10 authors')
    parser.add_argument('--method', choices=['auto', 'api', 'selenium'], default='auto',
                       help='Fetching method (default: auto)')
    parser.add_argument('--headless', action='store_true', default=True,
                       help='Run browser in headless mode')
    parser.add_argument('--resume', action='store_true',
                       help='Resume from existing output file')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of authors to fetch')
    
    args = parser.parse_args()
    
    # Load unique authors
    authors = load_unique_authors()
    
    # Load existing results if resuming
    output_file = Path('results/author_affiliations.json')
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
    logger.info(f"Will fetch data for {total} authors (method: {args.method})")
    
    # Initialize fetcher
    fetcher = AuthorAffiliationFetcher(headless=args.headless, method=args.method)
    
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
                    # Extract affiliation(s)
                    affiliations = author_data.get('currentAffiliations', [])
                    if not affiliations:
                        affiliations = [author_data.get('affiliation', 'N/A')]
                    
                    affiliation_str = ', '.join(affiliations) if isinstance(affiliations, list) else str(affiliations)
                    
                    results[author_id] = {
                        'id': author_id,
                        'name': author_name,
                        'publications_count': author_info.get('appearances_count', 0),
                        'fetched_data': author_data,
                        'fetched_at': datetime.now().isoformat(),
                        'method': 'selenium' if fetcher.selenium_mode else 'api'
                    }
                    successes += 1
                    logger.info(f"  ✓ Success - Affiliation: {affiliation_str[:100]}")
                else:
                    results[author_id] = {
                        'id': author_id,
                        'name': author_name,
                        'publications_count': author_info.get('appearances_count', 0),
                        'fetched_data': None,
                        'fetched_at': datetime.now().isoformat(),
                        'error': 'No data available'
                    }
                    failures += 1
                    logger.warning(f"  ✗ Failed to fetch data")
                
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                results[author_id] = {
                    'id': author_id,
                    'name': author_name,
                    'publications_count': author_info.get('appearances_count', 0),
                    'fetched_data': None,
                    'fetched_at': datetime.now().isoformat(),
                    'error': str(e)
                }
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
                time.sleep(3)  # Longer pause every 10 requests
            else:
                time.sleep(1 if fetcher.selenium_mode else 0.5)
        
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
        logger.info(f"{'='*60}")
        
    finally:
        fetcher.close()


def save_results(results, output_file, fetcher):
    """Save results to file"""
    output_data = {
        'metadata': {
            'total_authors': len(results),
            'successful_fetches': sum(1 for r in results.values() if r.get('fetched_data')),
            'failed_fetches': sum(1 for r in results.values() if not r.get('fetched_data')),
            'last_updated': datetime.now().isoformat(),
            'api_successes': fetcher.api_successes,
            'api_failures': fetcher.api_failures,
            'method_used': 'selenium' if fetcher.selenium_mode else 'api'
        },
        'authors': results
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.debug(f"Saved {len(results)} author records to {output_file}")


if __name__ == '__main__':
    main()

