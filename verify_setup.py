#!/usr/bin/env python3
"""
Setup Verification Script
Verifies that all dependencies are installed and the environment is ready.
"""

import sys
import importlib


def check_package(package_name, import_name=None):
    """
    Check if a package is installed.
    
    Args:
        package_name (str): Name of the package
        import_name (str): Import name if different from package name
    """
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False


def main():
    """Main verification function."""
    print("=" * 60)
    print("IEEE Xplore Scraper - Setup Verification")
    print("=" * 60)
    print()
    
    required_packages = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('selenium', 'selenium'),
        ('lxml', 'lxml'),
        ('pycountry', 'pycountry'),
        ('webdriver-manager', 'webdriver_manager'),
    ]
    
    all_installed = True
    
    print("Checking Python version...")
    python_version = sys.version_info
    print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("✗ Python 3.8 or higher is required")
        all_installed = False
    else:
        print("✓ Python version is compatible")
    
    print()
    print("Checking required packages...")
    
    for package_name, import_name in required_packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    print()
    print("Checking Chrome/Chromium for Selenium...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("Attempting to initialize Chrome driver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        
        print("✓ Chrome/Chromium is available and working")
    except Exception as e:
        print(f"✗ Chrome/Chromium setup issue: {e}")
        all_installed = False
    
    print()
    print("Checking project files...")
    
    import os
    project_files = [
        'config.json',
        'ieee_author_scraper.py',
        'scraper/ieee_scraper.py',
        'scraper/affiliation_parser.py',
        'scraper/author_extractor.py',
        'utils/data_aggregator.py',
    ]
    
    for file_path in project_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path} exists")
        else:
            print(f"✗ {file_path} is missing")
            all_installed = False
    
    print()
    print("=" * 60)
    
    if all_installed:
        print("✓ All checks passed! You're ready to run the scraper.")
        print()
        print("To start scraping, run:")
        print("  python ieee_author_scraper.py")
    else:
        print("✗ Some checks failed. Please install missing dependencies:")
        print("  pip install -r requirements.txt")
    
    print("=" * 60)
    
    return 0 if all_installed else 1


if __name__ == '__main__':
    sys.exit(main())

