"""Quick test to verify pagination fix."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scraper.ieee_scraper import IEEEXploreScraper
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

print("=" * 70)
print("Testing Pagination Fix")
print("=" * 70)

test_config = {
    "max_results_per_query": 50,  # Should collect 2 pages (25 per page)
    "delay_between_requests": 2,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

scraper = None
try:
    print("\n1. Initializing scraper...")
    scraper = IEEEXploreScraper(test_config)
    
    print("\n2. Testing search with pagination enabled...")
    query = "multilevel inverter"
    publications = scraper.search_publications(query, collect_all_pages=True)
    
    print(f"\n✅ Results:")
    print(f"   Query: {query}")
    print(f"   Publications collected: {len(publications)}")
    print(f"   Expected: ~50 (2 pages)")
    
    if len(publications) >= 40:
        print(f"\n🎉 SUCCESS! Pagination is working!")
        print(f"   Got {len(publications)} publications (more than 1 page worth)")
    elif len(publications) <= 25:
        print(f"\n⚠️  WARNING: Only got {len(publications)} publications")
        print(f"   This suggests pagination might not be working correctly")
    else:
        print(f"\n✓ Partial success: Got {len(publications)} publications")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if scraper:
        scraper.close()
    print("\nTest complete!")

