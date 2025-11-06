"""
Debug script to check IEEE Xplore's HTML structure for pagination.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import glob

# Initialize Chrome with same settings as scraper
chrome_options = Options()
chrome_options.add_argument('--headless=new')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Get Chrome driver
try:
    driver_path = ChromeDriverManager().install()
except:
    driver_path = None

# Fix for macOS ARM64
if not driver_path or 'THIRD_PARTY_NOTICES' in driver_path or not os.path.isfile(driver_path):
    cache_dir = os.path.expanduser('~/.wdm/drivers/chromedriver')
    if os.path.exists(cache_dir):
        driver_files = glob.glob(os.path.join(cache_dir, '**/chromedriver'), recursive=True)
        for driver_file in driver_files:
            if os.path.isfile(driver_file) and 'THIRD_PARTY' not in driver_file:
                os.chmod(driver_file, 0o755)
                driver_path = driver_file
                break

service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    print("Testing IEEE Xplore pagination HTML structure...")
    print("=" * 70)
    
    # Test search URL
    query = "multilevel inverter"
    search_params = {
        'queryText': query,
        'highlight': 'true',
        'returnFacets': 'ALL',
        'returnType': 'SEARCH',
        'matchPubs': 'true',
        'ranges': '2022_2025_Year'
    }
    
    param_string = '&'.join([f"{k}={v}" for k, v in search_params.items()])
    url = f"https://ieeexplore.ieee.org/search/searchresult.jsp?{param_string}"
    
    print(f"\nSearching for: {query}")
    print(f"URL: {url}\n")
    
    driver.get(url)
    time.sleep(5)  # Wait for page to load
    
    # Get page HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    print("\n1. Looking for result count elements:")
    print("-" * 70)
    
    # Try various selectors
    selectors = [
        ('span.result-count', soup.find('span', class_='result-count')),
        ('span.stats-number', soup.find('span', class_='stats-number')),
        ('xpl-search-results-header', soup.find('xpl-search-results-header')),
        ('div.Dashboard-header', soup.find('div', class_='Dashboard-header')),
        ('span with "results"', soup.find('span', string=lambda t: t and 'results' in t.lower() if t else False)),
    ]
    
    for selector_name, elem in selectors:
        if elem:
            print(f"\n✅ Found: {selector_name}")
            print(f"   Text: {elem.get_text()[:200]}")
            print(f"   HTML: {str(elem)[:300]}")
        else:
            print(f"❌ Not found: {selector_name}")
    
    print("\n\n2. All elements with 'result' in class or text:")
    print("-" * 70)
    
    # Find all elements with 'result' in class
    result_elems = soup.find_all(class_=lambda c: c and 'result' in c.lower())
    for i, elem in enumerate(result_elems[:5]):
        print(f"\nElement {i+1}: {elem.name} class='{elem.get('class')}'")
        print(f"  Text: {elem.get_text()[:100]}")
    
    print("\n\n3. Looking for pagination elements:")
    print("-" * 70)
    
    pagination_selectors = [
        ('xpl-paginator', soup.find('xpl-paginator')),
        ('div.pagination', soup.find('div', class_='pagination')),
        ('ul.pagination', soup.find('ul', class_='pagination')),
    ]
    
    for selector_name, elem in pagination_selectors:
        if elem:
            print(f"\n✅ Found: {selector_name}")
            print(f"   Text: {elem.get_text()[:200]}")
        else:
            print(f"❌ Not found: {selector_name}")
    
    print("\n\n4. Searching for text containing 'of' and numbers:")
    print("-" * 70)
    
    import re
    all_text = soup.get_text()
    matches = re.findall(r'[\d,]+-[\d,]+\s+of\s+[\d,]+', all_text)
    for match in matches[:5]:
        print(f"  Found pattern: {match}")
    
    # Also look for standalone "X results"
    result_matches = re.findall(r'([\d,]+)\s+results?', all_text, re.IGNORECASE)
    print(f"\n  Found 'X results' patterns: {result_matches[:5]}")
    
    print("\n\n5. Saving HTML for manual inspection:")
    print("-" * 70)
    
    with open('debug_ieee_page.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)
    
    print("✅ Saved to: debug_ieee_page.html")
    print("\nYou can open this file in a browser to inspect the HTML structure.")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
    print("\n" + "=" * 70)
    print("Debug complete!")

