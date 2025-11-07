#!/usr/bin/env python3
"""
IEEE Xplore Scraper - POST API Method
Uses Selenium to capture POST /rest/search responses instead of HTML scraping
Much cleaner, faster, and more reliable than parsing HTML
"""

import json
import time
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IEEEScraperPostAPI:
    """
    IEEE Xplore Scraper using POST API responses
    """
    
    def __init__(self, config):
        """
        Initialize scraper with config
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.delay = config.get('delay_between_requests', 3)
        self.max_results = config.get('max_results_per_query', None)
        self.driver = None
        
    def _init_driver(self, headless=False):
        """
        Initialize Selenium WebDriver with network logging
        
        Args:
            headless (bool): Run in headless mode
        """
        mode = "headless" if headless else "visible"
        logger.info(f"Initializing Chrome WebDriver ({mode} mode)...")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless=new')  # Use new headless mode
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')  # Set window size in headless
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # Avoid detection
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Initialize driver
        driver_path = ChromeDriverManager().install()
        if 'THIRD_PARTY_NOTICES' in driver_path:
            driver_dir = os.path.dirname(driver_path)
            driver_path = os.path.join(driver_dir, 'chromedriver')
        
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info(f"Chrome WebDriver initialized ({mode} mode)")
    
    def _extract_post_response(self):
        """
        Extract POST /rest/search response from browser network logs
        
        Returns:
            dict: Response data or None
        """
        logs = self.driver.get_log('performance')
        logger.debug(f"Retrieved {len(logs)} performance log entries")
        
        rest_search_found = False
        
        for entry in logs:
            try:
                log = json.loads(entry['message'])
                message = log['message']
                method = message.get('method')
                
                if method == 'Network.responseReceived':
                    response = message['params']['response']
                    url = response.get('url', '')
                    
                    if '/rest/search' in url:
                        rest_search_found = True
                        status = response.get('status')
                        request_id = message['params']['requestId']
                        logger.debug(f"Found /rest/search response (status: {status}, request_id: {request_id})")
                        
                        if status == 200:
                            try:
                                response_body = self.driver.execute_cdp_cmd(
                                    'Network.getResponseBody',
                                    {'requestId': request_id}
                                )
                                
                                if response_body and 'body' in response_body:
                                    data = json.loads(response_body['body'])
                                    logger.debug(f"✓ Successfully extracted POST response")
                                    return data
                            except Exception as e:
                                logger.warning(f"Could not get response body: {e}")
                                continue
                        else:
                            logger.warning(f"/rest/search returned status {status}")
                            
            except:
                continue
        
        if not rest_search_found:
            logger.error("❌ No /rest/search POST request found in network logs")
            logger.error("   Possible causes:")
            logger.error("   • Page didn't load completely (try increasing wait time)")
            logger.error("   • IEEE detected automation and blocked the request")
            logger.error("   • Network logging isn't capturing requests properly")
        
        return None
    
    def _capture_page(self, url, page_number, save_individual=True):
        """
        Navigate to URL and capture POST response
        
        Args:
            url (str): URL to navigate to
            page_number (int): Page number for logging
            save_individual (bool): Save individual page response to file
            
        Returns:
            dict: Page data or None
        """
        try:
            # Add page number to URL if not page 1
            if page_number > 1:
                if '&pageNumber=' in url:
                    url = url.split('&pageNumber=')[0]
                url = f"{url}&pageNumber={page_number}"
            
            # Navigate
            self.driver.get(url)
            
            # Wait for page to load and POST request to complete
            logger.debug(f"Waiting for page {page_number} to load...")
            time.sleep(self.delay)
            
            # Wait for results to render
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "xpl-results-item"))
                )
                logger.debug(f"Page {page_number} loaded successfully")
            except:
                logger.debug(f"Timeout waiting for page {page_number} to render (continuing anyway)")
                pass  # Continue even if timeout
            
            # Give a bit more time for POST request to complete
            time.sleep(1)
            
            # Extract POST response
            response_data = self._extract_post_response()
            
            # Save individual page response immediately
            if response_data and save_individual:
                self._save_page_response(page_number, response_data)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error capturing page {page_number}: {e}")
            return None
    
    def _save_page_response(self, page_number, response_data):
        """
        Save individual page response to JSON file
        
        Args:
            page_number (int): Page number
            response_data (dict): Raw POST response data
        """
        try:
            # Create responses directory
            responses_dir = os.path.join('results', 'raw_responses')
            os.makedirs(responses_dir, exist_ok=True)
            
            # Save with timestamp and page number
            filename = f"page_{page_number:04d}.json"
            filepath = os.path.join(responses_dir, filename)
            
            output = {
                'page': page_number,
                'timestamp': datetime.now().isoformat(),
                'totalRecords': response_data.get('totalRecords'),
                'totalPages': response_data.get('totalPages'),
                'recordsOnPage': len(response_data.get('records', [])),
                'response': response_data
            }
            
            with open(filepath, 'w') as f:
                json.dump(output, f, indent=2)
            
            logger.debug(f"💾 Saved page {page_number} response to {filename}")
            
        except Exception as e:
            logger.warning(f"Failed to save page {page_number} response: {e}")
    
    def search_and_collect(self, search_url, headless=True):
        """
        Main method to search and collect all publications
        
        Args:
            search_url (str): IEEE search URL
            headless (bool): Run in headless mode (with fallback to visible if it fails)
            
        Returns:
            tuple: (list of publication records, list of raw POST responses)
        """
        logger.info("=" * 80)
        logger.info("Starting IEEE Xplore data collection (POST API method)")
        logger.info("=" * 80)
        
        # Initialize driver
        self._init_driver(headless=headless)
        
        try:
            # Fetch first page
            logger.info("Fetching first page to determine totals...")
            first_page = self._capture_page(search_url, 1)
            
            # If headless mode failed, try visible mode
            if not first_page and headless:
                logger.warning("⚠️  Headless mode failed to capture response")
                logger.info("🔄 Retrying with visible browser window...")
                
                # Close headless driver
                if self.driver:
                    self.driver.quit()
                
                # Reinitialize with visible mode
                self._init_driver(headless=False)
                first_page = self._capture_page(search_url, 1)
            
            if not first_page:
                logger.error("❌ Failed to capture first page (tried headless and visible mode)")
                return [], []
            
            total_records = first_page.get('totalRecords', 0)
            total_pages = first_page.get('totalPages', 0)
            
            logger.info(f"Search results: {total_records} total records across {total_pages} pages")
            
            # Collect records AND raw responses
            all_records = []
            all_raw_responses = []
            
            all_records.extend(first_page.get('records', []))
            all_raw_responses.append({
                'page': 1,
                'response': first_page
            })
            logger.info(f"✓ Page 1/{total_pages}: {len(first_page.get('records', []))} records")
            
            # Calculate pages to fetch
            if self.max_results:
                records_per_page = len(first_page.get('records', []))
                max_pages = (self.max_results + records_per_page - 1) // records_per_page
                pages_to_fetch = min(max_pages, total_pages)
                logger.info(f"Will fetch {pages_to_fetch} pages (max_results: {self.max_results})")
            else:
                pages_to_fetch = total_pages
            
            # Fetch remaining pages
            if pages_to_fetch > 1:
                logger.info(f"Fetching remaining {pages_to_fetch - 1} pages...")
                
                for page_num in range(2, pages_to_fetch + 1):
                    if page_num % 10 == 0:
                        logger.info(f"Progress: {page_num}/{pages_to_fetch} ({len(all_records)} records)")
                    
                    page_data = self._capture_page(search_url, page_num)
                    
                    if page_data and 'records' in page_data:
                        records = page_data['records']
                        all_records.extend(records)
                        
                        # Save raw response
                        all_raw_responses.append({
                            'page': page_num,
                            'response': page_data
                        })
                        
                        if page_num % 10 != 0:
                            logger.info(f"✓ Page {page_num}/{pages_to_fetch}: {len(records)} records")
                        
                        # Check if we've reached max_results
                        if self.max_results and len(all_records) >= self.max_results:
                            logger.info(f"Reached max_results limit ({self.max_results})")
                            break
                    else:
                        logger.warning(f"Failed to capture page {page_num}")
            
            logger.info("=" * 80)
            logger.info(f"✅ Collection complete: {len(all_records)} publications")
            logger.info(f"✅ Captured {len(all_raw_responses)} raw POST responses")
            logger.info(f"💾 Individual responses saved to results/raw_responses/")
            logger.info("=" * 80)
            
            return all_records, all_raw_responses
            
        finally:
            if self.driver:
                logger.info("Closing browser...")
                self.driver.quit()
    
    def filter_by_country(self, publications, countries):
        """
        Filter publications by author affiliations containing country names
        
        Args:
            publications (list): List of publication records
            countries (list): List of country names to filter by
            
        Returns:
            list: Filtered publications
        """
        logger.info(f"Filtering {len(publications)} publications by {len(countries)} countries...")
        
        filtered = []
        
        for pub in publications:
            # Check if any author has affiliation from target countries
            authors = pub.get('authors', [])
            
            for author in authors:
                affiliation = author.get('affiliation', '').lower()
                
                # Check if affiliation contains any target country
                for country in countries:
                    if country.lower() in affiliation:
                        filtered.append(pub)
                        break
                else:
                    continue
                break
        
        logger.info(f"✓ Filtered to {len(filtered)} publications with target country affiliations")
        
        return filtered
    
    def save_results(self, publications, output_file='publications_post_api.json'):
        """
        Save publications to JSON file
        
        Args:
            publications (list): List of publication records
            output_file (str): Output file path
        """
        os.makedirs('results', exist_ok=True)
        output_path = os.path.join('results', output_file)
        
        result = {
            'metadata': {
                'totalPublications': len(publications),
                'collectionDate': datetime.now().isoformat(),
                'method': 'POST API capture'
            },
            'publications': publications
        }
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"✅ Saved {len(publications)} publications to {output_path}")
    
    def save_raw_responses(self, raw_responses, output_file='raw_post_responses.json'):
        """
        Save raw POST responses to JSON file
        
        Args:
            raw_responses (list): List of raw response data
            output_file (str): Output file path
        """
        os.makedirs('results', exist_ok=True)
        output_path = os.path.join('results', output_file)
        
        result = {
            'metadata': {
                'totalPages': len(raw_responses),
                'collectionDate': datetime.now().isoformat(),
                'source': 'IEEE Xplore POST /rest/search responses'
            },
            'responses': raw_responses
        }
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"✅ Saved {len(raw_responses)} raw POST responses to {output_path}")


def main():
    """
    Main entry point
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='IEEE Xplore Scraper (POST API method)')
    parser.add_argument('--config', default='config.json', help='Config file path')
    parser.add_argument('--url-file', default='filtered_mode_url.txt', help='File containing search URL')
    parser.add_argument('--filter-countries', action='store_true', help='Filter by country affiliations')
    parser.add_argument('--output', default='publications_post_api.json', help='Output file name')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--visible', action='store_true', help='Use visible browser (skip headless mode)')
    
    args = parser.parse_args()
    
    # Enable debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Load config
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {args.config}")
    except FileNotFoundError:
        logger.error(f"Config file not found: {args.config}")
        return
    
    # Load search URL
    try:
        with open(args.url_file, 'r') as f:
            lines = f.readlines()
            url = None
            for line in lines:
                if line.strip().startswith('https://'):
                    url = line.strip()
                    break
        
        if not url:
            logger.error(f"Could not find URL in {args.url_file}")
            return
        
        logger.info(f"Loaded search URL from {args.url_file}")
        
    except FileNotFoundError:
        logger.error(f"URL file not found: {args.url_file}")
        return
    
    # Initialize scraper
    scraper = IEEEScraperPostAPI(config)
    
    # Collect publications and raw responses
    start_time = time.time()
    headless = not args.visible  # Use visible mode if --visible flag is set
    publications, raw_responses = scraper.search_and_collect(url, headless=headless)
    elapsed = time.time() - start_time
    
    logger.info(f"Collection took {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    
    if not publications:
        logger.warning("No publications collected")
        return
    
    # Save raw POST responses
    scraper.save_raw_responses(raw_responses)
    
    # Optionally filter by countries
    if args.filter_countries:
        countries = config.get('european_countries_exclude_france', [])
        if countries:
            publications = scraper.filter_by_country(publications, countries)
        else:
            logger.warning("No countries defined in config, skipping filtering")
    
    # Save processed results
    scraper.save_results(publications, args.output)
    
    # Show sample
    if publications:
        logger.info("\n" + "=" * 80)
        logger.info("Sample Publications:")
        logger.info("=" * 80)
        for i, pub in enumerate(publications[:3], 1):
            logger.info(f"\n{i}. {pub.get('articleTitle', 'N/A')[:70]}...")
            logger.info(f"   Year: {pub.get('publicationYear', 'N/A')}")
            logger.info(f"   DOI: {pub.get('doi', 'N/A')}")
            logger.info(f"   Authors: {len(pub.get('authors', []))} author(s)")
            if pub.get('authors'):
                authors = [a.get('normalizedName', 'N/A') for a in pub['authors'][:3]]
                logger.info(f"   {', '.join(authors)}...")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ Scraping complete!")
    logger.info("=" * 80)
    logger.info(f"\n📄 Results saved to:")
    logger.info(f"   • results/{args.output} (processed publications)")
    logger.info(f"   • results/raw_post_responses.json (all responses combined)")
    logger.info(f"   • results/raw_responses/page_XXXX.json (individual page responses)")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()

