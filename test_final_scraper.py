#!/usr/bin/env python3
"""Test the complete scraper with author profile extraction."""

import json
from scraper.ieee_scraper import IEEEXploreScraper
from scraper.affiliation_parser import AffiliationParser
from scraper.author_extractor import AuthorExtractor

# Load config
with open('config_test.json', 'r') as f:
    config = json.load(f)

print("="*60)
print("Testing Complete Scraper with Author Profile Extraction")
print("="*60)

# Initialize
scraper = IEEEXploreScraper(config)
parser = AffiliationParser()
extractor = AuthorExtractor(config)

# Test with one publication
test_url = "https://ieeexplore.ieee.org/document/9320121/"

print(f"\n1. Fetching publication: {test_url}")
pub_details = scraper.get_publication_details(test_url)

if pub_details and pub_details.get('authors'):
    author = pub_details['authors'][0]
    print(f"\n2. Found author: {author.get('name')}")
    print(f"   Affiliation from pub: {author.get('affiliation')}")
    
    # Get profile data
    if author.get('profile_url'):
        print(f"\n3. Fetching author profile...")
        ieee_profile = scraper.get_author_profile(author['profile_url'])
        
        print(f"\n4. Profile data extracted:")
        print(f"   - Affiliation: {ieee_profile.get('affiliation')}")
        print(f"   - Email: {ieee_profile.get('email')}")
        print(f"   - Topics: {ieee_profile.get('publication_topics')}")
        print(f"   - Biography length: {len(ieee_profile.get('biography', ''))} chars")
        
        # Extract detailed author info
        print(f"\n5. Processing author details...")
        author_details = extractor.extract_author_details(author, ieee_profile)
        
        print(f"\n6. Final author details:")
        print(f"   - Name: {author_details.get('full_name')}")
        print(f"   - Email: {author_details.get('email')}")
        print(f"   - City: {author_details.get('city')}")
        print(f"   - Country: {author_details.get('country')}")
        print(f"   - University: {author_details.get('university')}")
        print(f"   - Topics: {author_details.get('publication_topics')}")
        
        # Check if European
        aff_data = parser.parse_affiliation(author_details.get('affiliation_raw', ''))
        print(f"\n7. Affiliation check:")
        print(f"   - Is European: {aff_data.get('is_european')}")
        print(f"   - Country parsed: {aff_data.get('country')}")
        
        print("\n" + "="*60)
        if aff_data.get('is_european'):
            print("✅ SUCCESS: Would extract this European author!")
        else:
            print("ℹ️  This author is not European (as expected for this test)")
        print("="*60)

scraper.close()
print("\n✅ Test complete!")

