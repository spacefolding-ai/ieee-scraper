"""
IEEE Xplore Scraper Module

Handles web scraping of IEEE Xplore using Selenium.
Searches for publications, extracts author details, and navigates author profiles.

OPTIMIZATION: Checks author countries FIRST before extracting publication details.
"""

import time
import re
import logging
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class IEEEXploreScraper:
    """Scraper for IEEE Xplore website."""
    
    BASE_URL = "https://ieeexplore.ieee.org"
    SEARCH_URL = "https://ieeexplore.ieee.org/search/searchresult.jsp"
    
    def __init__(self, config):
        """
        Initialize IEEE Xplore scraper.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.max_results = config.get('max_results_per_query', 20)
        self.delay = config.get('delay_between_requests', 2)
        self.user_agent = config.get('user_agent', 
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        self.driver = None
        self._init_selenium()
    
    def _init_selenium(self):
        """Initialize Selenium WebDriver with Chrome."""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless=new')  # Use new headless mode
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={self.user_agent}')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Get Chrome driver path and ensure it's the actual binary
            import os
            import glob
            
            # Try to get driver path from webdriver-manager
            try:
                driver_path = ChromeDriverManager().install()
            except Exception as e:
                logger.warning(f"WebDriver manager error: {e}")
                driver_path = None
            
            # Fix for webdriver-manager bug on macOS ARM64 - find actual chromedriver
            if not driver_path or 'THIRD_PARTY_NOTICES' in driver_path or not os.path.isfile(driver_path) or not os.access(driver_path, os.X_OK):
                # Search for chromedriver in webdriver-manager cache
                cache_dir = os.path.expanduser('~/.wdm/drivers/chromedriver')
                if os.path.exists(cache_dir):
                    # Find all chromedriver files
                    driver_files = glob.glob(os.path.join(cache_dir, '**/chromedriver'), recursive=True)
                    for driver_file in driver_files:
                        if os.path.isfile(driver_file) and 'THIRD_PARTY' not in driver_file:
                            # Make sure it's executable
                            os.chmod(driver_file, 0o755)
                            driver_path = driver_file
                            logger.info(f"Found chromedriver at: {driver_path}")
                            break
            
            if not driver_path or not os.path.isfile(driver_path):
                raise Exception("Could not find chromedriver executable. Please install Chrome/Chromium.")
            
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            raise
    
    def search_publications(self, query, collect_all_pages=False):
        """
        Search IEEE Xplore for publications matching the query with pagination support.
        
        Args:
            query (str): Search query string
            collect_all_pages (bool): If True, collect from all paginated pages
            
        Returns:
            list: List of publication dictionaries
        """
        publications = []
        
        try:
            search_params = {
                'queryText': query,
                'highlight': 'true',
                'returnFacets': 'ALL',
                'returnType': 'SEARCH',
                'matchPubs': 'true',
                'ranges': '2022_2025_Year'
            }
            
            # Construct search URL
            param_string = '&'.join([f"{k}={v}" for k, v in search_params.items()])
            base_url = f"{self.SEARCH_URL}?{param_string}"
            
            logger.info(f"Searching IEEE Xplore for: {query}")
            
            # Determine number of pages to fetch
            if collect_all_pages:
                # First, get the first page to determine total results
                self.driver.get(base_url)
                time.sleep(self.delay + 2)
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for search results for query: {query}")
                    return publications
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Try to extract total results count
                total_results = self._extract_total_results(soup)
                
                if total_results:
                    logger.info(f"  Total results available: {total_results}")
                    # IEEE typically shows 25 results per page
                    results_per_page = 25
                    # Limit to max_results if specified
                    target_count = min(total_results, self.max_results) if self.max_results else total_results
                    num_pages = (target_count + results_per_page - 1) // results_per_page
                    logger.info(f"  Will collect from {num_pages} page(s)")
                else:
                    num_pages = 1
                    logger.info(f"  Could not determine total results, collecting first page only")
                
                # Collect from all pages
                for page_num in range(1, num_pages + 1):
                    if page_num > 1:
                        page_url = f"{base_url}&pageNumber={page_num}"
                        logger.info(f"  Fetching page {page_num}/{num_pages}")
                        self.driver.get(page_url)
                        time.sleep(self.delay + 1)
                        
                        try:
                            WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.TAG_NAME, "body"))
                            )
                        except TimeoutException:
                            logger.warning(f"Timeout on page {page_num}")
                            continue
                        
                        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                    
                    # Extract publication entries from current page
                    result_items = soup.find_all('xpl-results-item')
                    page_count = 0
                    
                    for item in result_items:
                        try:
                            pub_data = self._extract_publication_data(item)
                            if pub_data:
                                publications.append(pub_data)
                                page_count += 1
                                
                                # Stop if we've reached max_results
                                if self.max_results and len(publications) >= self.max_results:
                                    break
                        except Exception as e:
                            logger.error(f"Error extracting publication data: {e}")
                            continue
                    
                    logger.info(f"  Collected {page_count} publications from page {page_num}")
                    
                    # Stop if we've reached max_results
                    if self.max_results and len(publications) >= self.max_results:
                        break
            
            else:
                # Original behavior: single page only
                self.driver.get(base_url)
                time.sleep(self.delay + 2)
                
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for search results for query: {query}")
                    return publications
                
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                result_items = soup.find_all('xpl-results-item', limit=self.max_results)
                
                for item in result_items:
                    try:
                        pub_data = self._extract_publication_data(item)
                        if pub_data:
                            publications.append(pub_data)
                    except Exception as e:
                        logger.error(f"Error extracting publication data: {e}")
                        continue
            
            logger.info(f"Found {len(publications)} publications for query: {query}")
            
        except Exception as e:
            logger.error(f"Error searching publications for '{query}': {e}")
        
        return publications
    
    def _extract_total_results(self, soup):
        """
        Extract total results count from search results page.
        
        Args:
            soup: BeautifulSoup object of search results page
            
        Returns:
            int or None: Total number of results
        """
        try:
            # Method 1: Search entire page text for "X-Y of Z" pattern
            # IEEE shows patterns like "1-25 of 3,698" in the page
            all_text = soup.get_text()
            
            # Look for "1-25 of 3,698" pattern
            match = re.search(r'[\d,]+-[\d,]+\s+of\s+([\d,]+)', all_text)
            if match:
                count_str = match.group(1).replace(',', '')
                logger.debug(f"Found total results using pattern match: {count_str}")
                return int(count_str)
            
            # Method 2: Look for specific elements
            result_text_elem = soup.find('span', class_='result-count') or \
                              soup.find('span', class_='stats-number') or \
                              soup.find('xpl-search-results-header')
            
            if result_text_elem:
                text = result_text_elem.get_text()
                # Extract number after "of" - e.g., "1-25 of 1,234 results"
                match = re.search(r'of\s+([\d,]+)', text)
                if match:
                    count_str = match.group(1).replace(',', '')
                    logger.debug(f"Found total results in element: {count_str}")
                    return int(count_str)
                
                # Alternative pattern: just a number
                match = re.search(r'([\d,]+)\s+results?', text, re.IGNORECASE)
                if match:
                    count_str = match.group(1).replace(',', '')
                    logger.debug(f"Found total results with 'results' keyword: {count_str}")
                    return int(count_str)
            
            # Method 3: Look for pagination info
            pagination = soup.find('xpl-paginator') or soup.find('div', class_='pagination')
            if pagination:
                text = pagination.get_text()
                match = re.search(r'of\s+([\d,]+)', text)
                if match:
                    count_str = match.group(1).replace(',', '')
                    logger.debug(f"Found total results in pagination: {count_str}")
                    return int(count_str)
        
        except Exception as e:
            logger.debug(f"Error extracting total results: {e}")
        
        logger.debug("Could not extract total results from page")
        return None
    
    def _extract_publication_data(self, item):
        """
        Extract publication data from search result item.
        
        Args:
            item: BeautifulSoup element representing a publication
            
        Returns:
            dict: Publication data with URL and title
        """
        try:
            # Find the title link
            title_link = item.find('a', href=re.compile(r'/document/\d+'))
            
            if not title_link:
                return None
            
            title = title_link.get_text(strip=True)
            href = title_link.get('href', '')
            
            # Construct full URL
            if href.startswith('http'):
                url = href
            else:
                url = f"{self.BASE_URL}{href}"
            
            return {
                'title': title,
                'url': url
            }
        
        except Exception as e:
            logger.debug(f"Error extracting publication data: {e}")
            return None
    
    def quick_check_authors_european(self, publication_url):
        """
        OPTIMIZATION: Quick check if publication has European authors.
        Only extracts author affiliations to check countries, nothing else.
        
        Args:
            publication_url (str): URL of the publication
            
        Returns:
            tuple: (has_european, authors_data) where authors_data includes affiliations
        """
        try:
            logger.info(f"Quick-checking authors: {publication_url}")
            self.driver.get(publication_url)
            time.sleep(self.delay + 1)
            
            # Wait for page to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.warning(f"Timeout waiting for publication page")
                return False, []
            
            # Try to click "Authors" button to expand author list
            try:
                # First try by ID (most reliable - id="authors")
                try:
                    authors_button = self.driver.find_element(By.ID, "authors")
                    authors_button.click()
                    time.sleep(2)  # Wait for section to expand
                    logger.info("  ✓ Expanded Authors section by clicking id='authors'")
                except NoSuchElementException:
                    # Fallback: try by text/aria-label
                    logger.debug("Button id='authors' not found, trying fallback...")
                    authors_buttons = self.driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Authors') or contains(@aria-label, 'Authors')]")
                    for btn in authors_buttons:
                        try:
                            if 'collapsed' in btn.get_attribute('class') or btn.get_attribute('aria-expanded') == 'false':
                                btn.click()
                                time.sleep(2)
                                logger.info("  ✓ Expanded Authors section (fallback method)")
                                break
                        except:
                            pass
            except Exception as e:
                logger.warning(f"Could not expand Authors section: {e}")
            
            # Re-parse the page after clicking to get updated content
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract ONLY authors with affiliations (minimal extraction)
            authors = self._extract_authors_with_affiliations(soup)
            
            # Quick check: any European affiliation?
            has_european = False
            for author in authors:
                affiliation = author.get('affiliation', '')
                if affiliation:
                    # Look for European country names in affiliation
                    # This is a very quick string check
                    affiliation_lower = affiliation.lower()
                    european_countries = self.config.get('european_countries_exclude_france', [])
                    for country in european_countries:
                        if country.lower() in affiliation_lower:
                            has_european = True
                            logger.info(f"  ✓ Found European country: {country}")
                            break
                if has_european:
                    break
            
            return has_european, authors
            
        except Exception as e:
            logger.error(f"Error in quick check for {publication_url}: {e}")
            return False, []
    
    def get_publication_details(self, publication_url, authors_data=None):
        """
        Get detailed information from a publication page.
        
        OPTIMIZATION: If authors_data is provided, skip author extraction
        (already done in quick check).
        
        Args:
            publication_url (str): URL of the publication
            authors_data (list, optional): Pre-extracted authors data
            
        Returns:
            dict: Publication details including authors
        """
        try:
            # If we don't have the page loaded, load it
            if authors_data is None:
                logger.info(f"Fetching publication: {publication_url}")
                self.driver.get(publication_url)
                time.sleep(self.delay + 2)
                
                # Wait for page to load
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    logger.warning(f"Timeout waiting for publication page")
                    return None
                
                # Scroll and expand authors
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(1)
                
                try:
                    # First try by ID (most reliable - id="authors")
                    try:
                        authors_button = self.driver.find_element(By.ID, "authors")
                        authors_button.click()
                        time.sleep(2)  # Wait for section to expand
                        logger.debug("Expanded Authors section by clicking id='authors'")
                    except NoSuchElementException:
                        # Fallback: try by text/aria-label
                        logger.debug("Button id='authors' not found, trying fallback...")
                        authors_buttons = self.driver.find_elements(By.XPATH, 
                            "//button[contains(text(), 'Authors') or contains(@aria-label, 'Authors')]")
                        for btn in authors_buttons:
                            try:
                                if 'collapsed' in btn.get_attribute('class') or btn.get_attribute('aria-expanded') == 'false':
                                    btn.click()
                                    time.sleep(2)
                                    logger.debug("Expanded Authors section (fallback)")
                                    break
                            except:
                                pass
                except Exception as e:
                    logger.debug(f"Could not click Authors button: {e}")
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            pub_details = {
                'url': publication_url,
                'title': None,
                'year': None,
                'type': None,
                'publisher': 'IEEE',
                'doi': None,
                'doi_url': None,
                'abstract': None,
                'conference': None,
                'journal': None,
                'authors': []
            }
            
            # Extract title
            title_elem = soup.find('h1', class_='document-title')
            if not title_elem:
                title_elem = soup.find('h1')
            pub_details['title'] = title_elem.get_text(strip=True) if title_elem else None
            
            # Extract DOI
            doi_elem = soup.find('div', class_='stats-document-abstract-doi')
            if doi_elem:
                doi_link = doi_elem.find('a')
                if doi_link:
                    pub_details['doi'] = doi_link.get_text(strip=True)
                    pub_details['doi_url'] = doi_link.get('href', '')
            
            # Extract publication year
            year_elem = soup.find('div', class_='doc-abstract-pubdate') or soup.find('div', class_='document-date')
            if year_elem:
                year_text = year_elem.get_text()
                year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                if year_match:
                    pub_details['year'] = int(year_match.group(0))
            
            # Extract publication type (Conference Paper, Journal Article, etc.)
            type_elem = soup.find('div', class_='doc-type') or soup.find('span', class_='document-type')
            if type_elem:
                pub_details['type'] = type_elem.get_text(strip=True)
            
            # Extract conference or journal name
            conf_elem = soup.find('div', class_='doc-abstract-confTitle') or soup.find('div', class_='stats-document-abstract-publishedIn')
            if conf_elem:
                conf_link = conf_elem.find('a')
                if conf_link:
                    conf_name = conf_link.get_text(strip=True)
                    # Determine if it's a conference or journal
                    if any(keyword in conf_name.lower() for keyword in ['conference', 'symposium', 'workshop', 'congress']):
                        pub_details['conference'] = conf_name
                    else:
                        pub_details['journal'] = conf_name
                else:
                    conf_name = conf_elem.get_text(strip=True)
                    if 'conference' in conf_name.lower():
                        pub_details['conference'] = conf_name
                    else:
                        pub_details['journal'] = conf_name
            
            # Extract abstract
            abstract_elem = soup.find('div', class_='abstract-text')
            if not abstract_elem:
                abstract_elem = soup.find('div', class_='document-abstract')
            if abstract_elem:
                # Remove any "Abstract:" label
                abstract_text = abstract_elem.get_text(strip=True)
                abstract_text = re.sub(r'^Abstract:\s*', '', abstract_text, flags=re.IGNORECASE)
                pub_details['abstract'] = abstract_text
                logger.info(f"  Extracted abstract ({len(abstract_text)} chars)")
            
            # Extract publisher (usually IEEE, but check)
            publisher_elem = soup.find('div', class_='publisher-name')
            if publisher_elem:
                pub_details['publisher'] = publisher_elem.get_text(strip=True)
            
            # Use pre-extracted authors if available, otherwise extract now
            if authors_data:
                pub_details['authors'] = authors_data
                logger.info(f"  Using pre-extracted authors: {len(authors_data)} authors")
            else:
                authors = self._extract_authors_with_affiliations(soup)
                pub_details['authors'] = authors
                logger.info(f"  Extracted {len(authors)} authors")
            
            logger.info(f"  Publication details: {pub_details.get('year')} {pub_details.get('type')} - {len(pub_details['authors'])} authors")
            
            return pub_details
            
        except Exception as e:
            logger.error(f"Error getting publication details from {publication_url}: {e}")
            return None
    
    def _extract_authors_with_affiliations(self, soup):
        """
        Extract authors and their affiliations from publication page.
        
        Args:
            soup: BeautifulSoup object of publication page
            
        Returns:
            list: List of author dictionaries with affiliations
        """
        authors = []
        
        try:
            # Look for xpl-author-item elements (new IEEE structure)
            author_items = soup.find_all('xpl-author-item')
            
            if author_items:
                logger.debug(f"Found {len(author_items)} xpl-author-item elements")
                
                for author_item in author_items:
                    try:
                        author_data = {}
                        
                        # Find the author-card div
                        author_card = author_item.find('div', class_='author-card')
                        if not author_card:
                            continue
                        
                        # Extract author name from the link
                        author_link = author_card.find('a', href=re.compile(r'/author/'))
                        if author_link:
                            author_data['name'] = author_link.get_text(strip=True)
                            author_data['profile_url'] = f"{self.BASE_URL}{author_link.get('href')}"
                            # Extract author ID
                            id_match = re.search(r'/author/(\d+)', author_link.get('href', ''))
                            if id_match:
                                author_data['author_id'] = id_match.group(1)
                        
                        # Extract affiliation - it's in a div after the author name div
                        # Structure: <div><div>[name]</div><div><div>[affiliation]</div></div></div>
                        parent_div = author_link.find_parent('div') if author_link else None
                        if parent_div:
                            # Get the next sibling div
                            next_div = parent_div.find_next_sibling('div')
                            if next_div:
                                # The affiliation is in a nested div
                                aff_div = next_div.find('div')
                                if aff_div:
                                    affiliation_text = aff_div.get_text(strip=True)
                                    if affiliation_text and len(affiliation_text) > 5:
                                        author_data['affiliation'] = affiliation_text
                        
                        if author_data.get('name'):
                            authors.append(author_data)
                            logger.debug(f"Extracted author: {author_data.get('name')} - {author_data.get('affiliation')[:50] if author_data.get('affiliation') else 'No affiliation'}")
                    
                    except Exception as e:
                        logger.error(f"Error extracting author from xpl-author-item: {e}")
                        continue
            
            # If no authors found with xpl-author-item, try fallback methods
            if not authors:
                logger.info("No xpl-author-item found, trying fallback methods")
                authors = self._extract_authors_simple(soup)
        
        except Exception as e:
            logger.error(f"Error extracting authors with affiliations: {e}")
        
        return authors
    
    def _extract_authors_simple(self, soup):
        """
        Fallback method to extract authors.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            list: List of author dictionaries
        """
        authors = []
        
        try:
            # Look for author links
            author_links = soup.find_all('a', href=re.compile(r'/author/\d+'))
            
            for link in author_links:
                author_data = {
                    'name': link.get_text(strip=True),
                    'profile_url': f"{self.BASE_URL}{link.get('href')}",
                    'affiliation': None
                }
                
                # Extract author ID
                id_match = re.search(r'/author/(\d+)', link.get('href', ''))
                if id_match:
                    author_data['author_id'] = id_match.group(1)
                
                if author_data['name']:
                    authors.append(author_data)
        
        except Exception as e:
            logger.error(f"Error in fallback author extraction: {e}")
        
        return authors
    
    def get_author_profile(self, author_profile_url):
        """
        Get detailed information from author's IEEE profile page.
        Extracts affiliation (with city/country), publication topics, and biography.
        
        Args:
            author_profile_url (str): URL of author's IEEE profile
            
        Returns:
            dict: Author profile information with affiliation, topics, bio
        """
        try:
            logger.info(f"Fetching author profile: {author_profile_url}")
            self.driver.get(author_profile_url)
            time.sleep(self.delay)
            
            # Wait for page to load
            time.sleep(2)
            
            # Try to click "Show More" buttons to expand content
            try:
                show_more_buttons = self.driver.find_elements(By.XPATH,
                    "//button[contains(text(), 'Show More') or contains(text(), 'show more')]")
                for btn in show_more_buttons:
                    try:
                        btn.click()
                        time.sleep(0.5)
                        logger.debug("Clicked 'Show More' button")
                    except:
                        pass
            except Exception as e:
                logger.debug(f"Could not click Show More buttons: {e}")
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            profile_data = {}
            
            # Extract affiliation (format: "University, City, Country")
            # Look for heading with "Affiliation"
            affiliation_section = soup.find(['h2', 'h3', 'div'], string=re.compile(r'Affiliation', re.IGNORECASE))
            if affiliation_section:
                # Get the next text element
                affiliation_text = None
                next_elem = affiliation_section.find_next()
                if next_elem:
                    affiliation_text = next_elem.get_text(separator=', ', strip=True)
                
                if not affiliation_text:
                    # Try finding by class
                    affiliation_div = affiliation_section.find_next(['div', 'p'])
                    if affiliation_div:
                        affiliation_text = affiliation_div.get_text(separator=', ', strip=True)
                
                if affiliation_text:
                    profile_data['affiliation'] = affiliation_text
                    logger.info(f"  Found affiliation: {affiliation_text}")
            
            # Alternative: search for text patterns that look like affiliations
            if not profile_data.get('affiliation'):
                # Look for common patterns: "University, City, Country"
                all_text = soup.get_text()
                lines = [line.strip() for line in all_text.split('\n') if line.strip()]
                for line in lines:
                    # Affiliations typically have commas and reasonable length
                    if 10 < len(line) < 200 and line.count(',') >= 2:
                        # Check if it contains university/institute keywords
                        if any(keyword in line.lower() for keyword in
                              ['university', 'institute', 'college', 'laboratory']):
                            profile_data['affiliation'] = line
                            logger.info(f"  Found affiliation (pattern match): {line}")
                            break
            
            # Extract publication topics
            topics_section = soup.find(['h2', 'h3', 'div'], string=re.compile(r'Publication Topics?', re.IGNORECASE))
            if topics_section:
                topics = []
                # Find links or text items after the heading
                next_container = topics_section.find_next(['div', 'ul'])
                if next_container:
                    # Look for links (topics are often linked)
                    topic_links = next_container.find_all('a')
                    for link in topic_links:
                        topic_text = link.get_text(strip=True)
                        if topic_text and len(topic_text) > 2:
                            topics.append(topic_text)
                    
                    # If no links, try getting comma-separated text
                    if not topics:
                        topic_text = next_container.get_text(strip=True)
                        # Split by commas
                        topics = [t.strip() for t in topic_text.split(',') if t.strip() and len(t.strip()) > 2]
                
                if topics:
                    profile_data['publication_topics'] = topics[:10]  # Limit to first 10
                    logger.info(f"  Found {len(topics)} publication topics")
            
            # Extract biography
            bio_section = soup.find(['h2', 'h3', 'div'], string=re.compile(r'Biography', re.IGNORECASE))
            if bio_section:
                # Get the biography text
                bio_div = bio_section.find_next(['div', 'p'])
                if bio_div:
                    bio_text = bio_div.get_text(strip=True)
                    if bio_text and len(bio_text) > 20:
                        profile_data['biography'] = bio_text
                        logger.info(f"  Found biography ({len(bio_text)} chars)")
            
            # Extract email if available
            email_elem = soup.find('a', href=re.compile(r'mailto:'))
            if email_elem:
                email_href = email_elem.get('href', '')
                email_match = re.search(r'mailto:([^\s,]+)', email_href)
                if email_match:
                    profile_data['email'] = email_match.group(1)
                    logger.info(f"  Found email: {profile_data['email']}")
            
            # Extract author's publication list from xpl-results-list with pagination
            author_publications = []
            publication_count = 0
            
            try:
                # First, try to get the total publication count from the results header
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                # Look for total count in various places
                count_elem = soup.find('span', class_=re.compile(r'total.*results|result.*count', re.IGNORECASE))
                if not count_elem:
                    # Try finding in text like "1-25 of 347 results"
                    results_text = soup.find(string=re.compile(r'\d+\s*-\s*\d+\s+of\s+\d+', re.IGNORECASE))
                    if results_text:
                        count_match = re.search(r'of\s+(\d+)', results_text, re.IGNORECASE)
                        if count_match:
                            publication_count = int(count_match.group(1).replace(',', ''))
                
                if count_elem and not publication_count:
                    count_match = re.search(r'(\d[\d,]*)', count_elem.get_text())
                    if count_match:
                        publication_count = int(count_match.group(1).replace(',', ''))
                
                # Find the xpl-results-list element
                results_list = soup.find('xpl-results-list')
                
                if results_list:
                    current_page = 1
                    max_pages = 10  # Limit to 10 pages to avoid excessive scraping
                    
                    while current_page <= max_pages:
                        logger.info(f"  Extracting publications from page {current_page}...")
                        
                        # Re-parse the page
                        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                        results_list = soup.find('xpl-results-list')
                        
                        if results_list:
                            # Find all publication links in the results list
                            pub_links = results_list.find_all('a', href=re.compile(r'/document/\d+'))
                            
                            for pub_link in pub_links:
                                pub_url = pub_link.get('href', '')
                                if pub_url:
                                    # Ensure full URL
                                    if not pub_url.startswith('http'):
                                        pub_url = f"{self.BASE_URL}{pub_url}"
                                    
                                    # Avoid duplicates
                                    if pub_url not in author_publications:
                                        author_publications.append(pub_url)
                            
                            logger.info(f"    Found {len(pub_links)} publications on page {current_page}")
                        
                        # Check if there's a next page
                        try:
                            # Look for xpl-paginator
                            paginator = self.driver.find_element(By.CSS_SELECTOR, 'xpl-paginator')
                            
                            # Try to find and click the next button
                            next_buttons = paginator.find_elements(By.CSS_SELECTOR, 'button[aria-label*="next" i], button.next-page, a.next-page')
                            
                            next_clicked = False
                            for next_btn in next_buttons:
                                try:
                                    if next_btn.is_enabled() and next_btn.is_displayed():
                                        next_btn.click()
                                        time.sleep(self.delay * 2)  # Wait for page to load
                                        next_clicked = True
                                        break
                                except:
                                    continue
                            
                            if not next_clicked:
                                logger.info("  No more pages to process")
                                break
                            
                            current_page += 1
                            
                        except Exception as e:
                            logger.debug(f"  No pagination found or end of pages: {e}")
                            break
                    
                    if author_publications:
                        profile_data['author_publications'] = author_publications
                        logger.info(f"  Found {len(author_publications)} total publication URLs")
                
                # Set publication count
                if not publication_count and author_publications:
                    # If we couldn't find the count, use the number we collected
                    publication_count = len(author_publications)
                
                if publication_count > 0:
                    profile_data['publication_count'] = publication_count
                    logger.info(f"  Total publication count: {publication_count}")
                
            except Exception as e:
                logger.debug(f"Error extracting author publications: {e}")
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error fetching author profile {author_profile_url}: {e}")
            return {}
    
    def close(self):
        """Close the Selenium WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")
