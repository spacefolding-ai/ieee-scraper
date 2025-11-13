#!/usr/bin/env python3
"""
Enrich publications with complete abstracts using Selenium
Scrapes individual IEEE document pages to extract full abstracts
"""

import json
import time
import logging
from pathlib import Path
from datetime import datetime
import html
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('results/abstract_enrichment_selenium.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SeleniumAbstractEnricher:
    """Scrape complete abstracts from IEEE document pages using Selenium"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.driver = None
        self.successes = 0
        self.failures = 0
        self.cache = {}  # Cache to avoid re-fetching same articles
        self._init_driver()
    
    def _init_driver(self):
        """Initialize Selenium WebDriver"""
        mode = "headless" if self.headless else "visible"
        logger.info(f"Initializing Chrome WebDriver ({mode} mode)...")
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Initialize driver
        # Try to use older approved ChromeDriver version first
        old_driver_path = os.path.expanduser('~/.wdm/drivers/chromedriver/mac64/142.0.7444.59/chromedriver-mac-arm64/chromedriver')
        
        if os.path.exists(old_driver_path) and os.access(old_driver_path, os.X_OK):
            driver_path = old_driver_path
            logger.info(f"Using previously approved ChromeDriver: {driver_path}")
        else:
            driver_path = ChromeDriverManager().install()
            if 'THIRD_PARTY_NOTICES' in driver_path:
                driver_dir = os.path.dirname(driver_path)
                driver_path = os.path.join(driver_dir, 'chromedriver')
            
            # Ensure the driver path is correct and executable
            if not os.path.exists(driver_path):
                raise FileNotFoundError(f"ChromeDriver not found at: {driver_path}")
            if not os.access(driver_path, os.X_OK):
                os.chmod(driver_path, 0o755)
                logger.info(f"Made ChromeDriver executable: {driver_path}")
        
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info(f"Chrome WebDriver initialized ({mode} mode)")
    
    def fetch_full_abstract(self, article_number):
        """Fetch full abstract by scraping the document page"""
        
        # Check cache first
        if article_number in self.cache:
            return self.cache[article_number]
        
        url = f"https://ieeexplore.ieee.org/document/{article_number}"
        
        try:
            logger.debug(f"Navigating to {url}")
            self.driver.get(url)
            
            # Wait for abstract to load
            wait = WebDriverWait(self.driver, 15)
            
            # Try multiple possible selectors for the abstract
            abstract_selectors = [
                "div[xplreadinglenshighlight]",  # Primary selector based on user's hint
                "div.abstract-text",
                "div.abstract",
                "div[class*='abstract']",
            ]
            
            abstract_text = None
            
            for selector in abstract_selectors:
                try:
                    abstract_element = wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    abstract_text = abstract_element.text
                    if abstract_text and len(abstract_text) > 100:
                        logger.debug(f"Found abstract using selector: {selector}")
                        break
                except:
                    continue
            
            if not abstract_text:
                # Try by XPath for the directive
                try:
                    abstract_element = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//div[@xplreadinglenshighlight]"))
                    )
                    abstract_text = abstract_element.text
                except:
                    pass
            
            if abstract_text:
                # Clean the abstract
                abstract_text = html.unescape(abstract_text)
                # Remove "Abstract:" prefix if present
                abstract_text = re.sub(r'^Abstract:\s*', '', abstract_text, flags=re.IGNORECASE)
                # Clean up whitespace
                abstract_text = re.sub(r'\s+', ' ', abstract_text).strip()
                
                if len(abstract_text) > 100:  # Ensure it's substantial
                    self.cache[article_number] = abstract_text
                    self.successes += 1
                    return abstract_text
            
            self.failures += 1
            logger.warning(f"Could not find abstract for article {article_number}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching abstract for article {article_number}: {e}")
            self.failures += 1
            return None
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


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
    publications_map = {}  # article_number -> list of (author_id, pub_index, pub_type)
    
    for author_id, author_info in data['authors'].items():
        # Collect first-author publications
        pubs = author_info.get('publications_as_first_author', [])
        for pub_idx, pub in enumerate(pubs):
            article_number = pub.get('article_number')
            if article_number:
                if article_number not in publications_map:
                    publications_map[article_number] = []
                publications_map[article_number].append((author_id, pub_idx, 'first'))
        
        # Collect non-first-author publications
        pubs = author_info.get('publications_as_non_first_author', [])
        for pub_idx, pub in enumerate(pubs):
            article_number = pub.get('article_number')
            if article_number:
                if article_number not in publications_map:
                    publications_map[article_number] = []
                publications_map[article_number].append((author_id, pub_idx, 'non_first'))
    
    return publications_map


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enrich publications with complete abstracts using Selenium')
    parser.add_argument('--test', action='store_true', 
                       help='Test mode - only enrich first 10 publications')
    parser.add_argument('--limit', type=int, default=None,
                       help='Limit number of publications to enrich')
    parser.add_argument('--resume', action='store_true',
                       help='Resume - skip publications that already have full abstracts')
    parser.add_argument('--visible', action='store_true',
                       help='Run browser in visible mode (not headless)')
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
        author_id, pub_idx, pub_type = locations[0]
        pub_list = 'publications_as_first_author' if pub_type == 'first' else 'publications_as_non_first_author'
        pub = data['authors'][author_id][pub_list][pub_idx]
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
    logger.info(f"Estimated time: ~{(total * 3.0) / 60:.1f} minutes (~{(total * 3.0) / 3600:.1f} hours)")
    
    enricher = SeleniumAbstractEnricher(headless=not args.visible)
    enriched_count = 0
    failed_count = 0
    
    try:
        start_time = time.time()
        
        for idx, (article_number, locations) in enumerate(pubs_to_enrich.items(), 1):
            # Get title from first occurrence for logging
            author_id, pub_idx, pub_type = locations[0]
            pub_list = 'publications_as_first_author' if pub_type == 'first' else 'publications_as_non_first_author'
            pub = data['authors'][author_id][pub_list][pub_idx]
            title = pub.get('title', pub.get('article_title', 'N/A'))[:80]
            
            logger.info(f"[{idx}/{total}] Fetching abstract for article {article_number}...")
            logger.info(f"  Title: {title}")
            logger.info(f"  Appears in {len(locations)} author record(s)")
            
            try:
                full_abstract = enricher.fetch_full_abstract(str(article_number))
                
                if full_abstract:
                    # Update all occurrences of this publication
                    for author_id, pub_idx, pub_type in locations:
                        pub_list = 'publications_as_first_author' if pub_type == 'first' else 'publications_as_non_first_author'
                        data['authors'][author_id][pub_list][pub_idx]['abstract'] = full_abstract
                        data['authors'][author_id][pub_list][pub_idx]['abstract_enriched'] = True
                        data['authors'][author_id][pub_list][pub_idx]['abstract_enriched_at'] = datetime.now().isoformat()
                        data['authors'][author_id][pub_list][pub_idx]['is_full_abstract'] = True
                    
                    enriched_count += 1
                    logger.info(f"  ✓ Success - {len(full_abstract)} chars")
                else:
                    # Mark as attempted but failed
                    for author_id, pub_idx, pub_type in locations:
                        pub_list = 'publications_as_first_author' if pub_type == 'first' else 'publications_as_non_first_author'
                        data['authors'][author_id][pub_list][pub_idx]['abstract_fetch_error'] = 'Could not extract from page'
                    
                    failed_count += 1
                    logger.warning(f"  ✗ Failed to fetch abstract")
                
            except Exception as e:
                logger.error(f"  ✗ Error: {e}")
                for author_id, pub_idx, pub_type in locations:
                    pub_list = 'publications_as_first_author' if pub_type == 'first' else 'publications_as_non_first_author'
                    data['authors'][author_id][pub_list][pub_idx]['abstract_fetch_error'] = str(e)
                failed_count += 1
            
            # Save progress periodically
            if idx % 25 == 0:
                save_enriched_data(data, output_path)
                elapsed = time.time() - start_time
                avg_time = elapsed / idx
                remaining = (total - idx) * avg_time
                
                file_size_mb = output_path.stat().st_size / (1024 * 1024)
                logger.info(f"Progress: {idx}/{total} ({idx/total*100:.1f}%) - "
                          f"ETA: {remaining/60:.1f} min - "
                          f"File size: {file_size_mb:.1f} MB")
            
            # Rate limiting - slightly longer for Selenium
            time.sleep(2.0)
        
        # Update summary
        if 'summary' not in data:
            data['summary'] = {}
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

