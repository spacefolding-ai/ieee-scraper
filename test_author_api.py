#!/usr/bin/env python3
"""
Quick test to see what IEEE author API returns
"""

import requests
import json

def test_author_api(author_id):
    """Test different API endpoints for author data"""
    
    print(f"\n{'='*60}")
    print(f"Testing Author ID: {author_id}")
    print(f"{'='*60}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://ieeexplore.ieee.org/'
    }
    
    # Try different endpoint patterns
    endpoints = [
        f"https://ieeexplore.ieee.org/rest/author/{author_id}",
        f"https://ieeexplore.ieee.org/rest/authors/{author_id}",
        f"https://ieeexplore.ieee.org/author/{author_id}/data",
        f"https://ieeexplore.ieee.org/gateway/author/{author_id}",
    ]
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  ✓ Success! Response type: {type(data)}")
                    print(f"  Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                    
                    if isinstance(data, dict):
                        # Show relevant fields
                        for key in ['name', 'affiliation', 'biography', 'authorId', 'preferredName']:
                            if key in data:
                                value = str(data[key])[:100]  # Truncate long values
                                print(f"    {key}: {value}")
                    
                    print(f"\n  Full response preview:")
                    print(f"  {json.dumps(data, indent=2)[:500]}...\n")
                    return data
                    
                except json.JSONDecodeError:
                    print(f"  ✗ Response is not JSON")
                    print(f"  Content preview: {response.text[:200]}")
            
            elif response.status_code == 404:
                print(f"  ✗ Not found")
            else:
                print(f"  ✗ Error status")
                
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Request failed: {e}")
        
        print()
    
    print("No working endpoint found for direct API access")
    print("Will need to use Selenium to scrape author pages")
    return None


if __name__ == '__main__':
    # Test with F. Blaabjerg (most prolific author in our dataset)
    print("\nTest 1: F. Blaabjerg (37278889300) - Most prolific author")
    test_author_api(37278889300)
    
    print("\n" + "="*60)
    
    # Test with another author
    print("\nTest 2: Josep Guerrero (37274692200) - Second most prolific")
    test_author_api(37274692200)
    
    print("\n" + "="*60)
    print("\nIf no APIs worked, the script will automatically fall back to Selenium.")
    print("You can now run: python fetch_author_affiliations.py --test")

