#!/usr/bin/env python3
"""
Manual Browser Capture Helper

This script helps you manually capture IEEE search results from your browser.
You'll copy/paste JSON responses from browser DevTools.
"""

import json
import os

def generate_urls(base_url, total_pages):
    """
    Generate URLs for all pages
    
    Args:
        base_url: Base search URL
        total_pages: Total number of pages to generate
        
    Returns:
        list: List of URLs with page numbers
    """
    urls = []
    
    # Remove existing pageNumber if present
    if '&pageNumber=' in base_url:
        base_url = base_url.split('&pageNumber=')[0]
    
    for page_num in range(1, total_pages + 1):
        page_url = f"{base_url}&pageNumber={page_num}"
        urls.append({
            'page': page_num,
            'url': page_url
        })
    
    return urls


def save_response(page_number, response_json):
    """
    Save a captured response to file
    
    Args:
        page_number: Page number
        response_json: JSON response data
    """
    output_dir = 'manual_captures'
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{output_dir}/page_{page_number:03d}.json"
    
    with open(filename, 'w') as f:
        json.dump(response_json, f, indent=2)
    
    print(f"✅ Saved page {page_number} to {filename}")


def combine_all_captures():
    """
    Combine all manually captured pages into one file
    
    Returns:
        dict: Combined result
    """
    output_dir = 'manual_captures'
    
    if not os.path.exists(output_dir):
        print("❌ No captures found in manual_captures/")
        return None
    
    files = sorted([f for f in os.listdir(output_dir) if f.startswith('page_') and f.endswith('.json')])
    
    if not files:
        print("❌ No page files found")
        return None
    
    print(f"Found {len(files)} captured pages")
    
    all_records = []
    total_records = 0
    
    for filename in files:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'r') as f:
            data = json.load(f)
            
            if 'records' in data:
                records = data['records']
                all_records.extend(records)
                print(f"  ✓ {filename}: {len(records)} records")
                
                if 'totalRecords' in data and total_records == 0:
                    total_records = data['totalRecords']
    
    result = {
        'metadata': {
            'totalRecords': total_records,
            'recordsCollected': len(all_records),
            'pagesCaptured': len(files),
            'captureMethod': 'Manual browser capture'
        },
        'records': all_records
    }
    
    return result


def main():
    print("=" * 80)
    print("IEEE Xplore - Manual Browser Capture Helper")
    print("=" * 80)
    
    print("\nWhat would you like to do?")
    print("  1. Generate page URLs (to visit in browser)")
    print("  2. Save a captured response")
    print("  3. Combine all captured pages into one file")
    print()
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == '1':
        # Generate URLs
        print("\n" + "=" * 80)
        print("GENERATE PAGE URLs")
        print("=" * 80)
        
        # Load base URL
        try:
            with open('filtered_mode_url.txt', 'r') as f:
                lines = f.readlines()
                url = None
                for line in lines:
                    if line.strip().startswith('https://'):
                        url = line.strip()
                        break
            
            if not url:
                print("❌ Could not find URL in filtered_mode_url.txt")
                return
        except FileNotFoundError:
            print("❌ filtered_mode_url.txt not found")
            return
        
        total_pages_input = input("\nHow many pages do you want URLs for? (e.g., 53): ").strip()
        try:
            total_pages = int(total_pages_input)
        except ValueError:
            print("❌ Invalid number")
            return
        
        urls = generate_urls(url, total_pages)
        
        # Save to file
        output_file = 'page_urls.txt'
        with open(output_file, 'w') as f:
            f.write("IEEE Xplore Page URLs\n")
            f.write("=" * 80 + "\n\n")
            f.write("INSTRUCTIONS:\n")
            f.write("1. Open each URL in your browser\n")
            f.write("2. Open DevTools (Cmd+Option+I)\n")
            f.write("3. Go to Network tab\n")
            f.write("4. Look for POST to 'rest/search'\n")
            f.write("5. Click on it → Response tab\n")
            f.write("6. Copy the JSON response\n")
            f.write("7. Run this script again (option 2) to save it\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            for item in urls:
                f.write(f"Page {item['page']}:\n")
                f.write(f"{item['url']}\n\n")
        
        print(f"\n✅ Generated {len(urls)} URLs")
        print(f"✅ Saved to: {output_file}")
        print(f"\nOpen {output_file} and follow the instructions!")
        
    elif choice == '2':
        # Save a captured response
        print("\n" + "=" * 80)
        print("SAVE CAPTURED RESPONSE")
        print("=" * 80)
        
        page_num_input = input("\nWhich page number is this? ").strip()
        try:
            page_num = int(page_num_input)
        except ValueError:
            print("❌ Invalid page number")
            return
        
        print("\nPaste the JSON response (from browser DevTools)")
        print("Press Ctrl+D (Mac) or Ctrl+Z (Windows) when done:")
        print()
        
        import sys
        json_text = sys.stdin.read()
        
        try:
            response_data = json.loads(json_text)
            save_response(page_num, response_data)
            
            # Show what we got
            if 'records' in response_data:
                print(f"   Records in this page: {len(response_data['records'])}")
            if 'totalRecords' in response_data:
                print(f"   Total records: {response_data['totalRecords']}")
                
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return
        
    elif choice == '3':
        # Combine all captures
        print("\n" + "=" * 80)
        print("COMBINE ALL CAPTURES")
        print("=" * 80)
        
        result = combine_all_captures()
        
        if result:
            output_file = 'ieee_all_publications_manual.json'
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"\n✅ Combined {result['metadata']['pagesCaptured']} pages")
            print(f"✅ Total records: {result['metadata']['recordsCollected']}")
            print(f"✅ Saved to: {output_file}")
            
            # Show sample
            if result['records']:
                print(f"\n📄 Sample publication:")
                sample = result['records'][0]
                print(f"   Title: {sample.get('articleTitle', 'N/A')[:70]}...")
                print(f"   Year: {sample.get('publicationYear', 'N/A')}")
                print(f"   Authors: {len(sample.get('authors', []))}")
    
    else:
        print("❌ Invalid choice")


if __name__ == '__main__':
    main()

