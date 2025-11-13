#!/usr/bin/env python3
"""
Automated author type extraction with batch processing and resume capability.

Features:
- Batch processing with configurable batch size
- Progress monitoring and logging
- Resume from last checkpoint
- Incremental saves
- Error handling and retry logic
"""

import json
import re
import time
from pathlib import Path
from datetime import datetime
from collections import Counter
import requests
from typing import Optional, Dict, List

# Configuration
RESULTS_DIR = Path("/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country")
PROGRESS_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/enrichment_progress.json")
LOG_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/enrichment.log")
OUTPUT_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/enrichment_results.json")

BATCH_SIZE = 50  # Process 50 authors at a time
DELAY_BETWEEN_REQUESTS = 3  # seconds
MAX_RETRIES = 2

# Author type patterns (from our original script)
AUTHOR_TYPE_PATTERNS = {
    "Professor": [
        r'\bprofessor\b(?!\s+(?:associate|assistant))',
        r'\bprof\.\b(?!\s+(?:assoc|asst))',
        r'\bfull\s+professor\b',
        r'\bordinary\s+professor\b'
    ],
    "Associate Professor": [
        r'\bassociate\s+professor\b',
        r'\bassoc\.\s+prof\.\b',
        r'\bassoc\s+prof\b'
    ],
    "Assistant Professor": [
        r'\bassistant\s+professor\b',
        r'\basst\.\s+prof\.\b',
        r'\basst\s+prof\b'
    ],
    "Senior Lecturer": [
        r'\bsenior\s+lecturer\b',
        r'\bsr\.\s+lecturer\b'
    ],
    "Lecturer (teaching)": [
        r'\blecturer\b(?!\s+(?:senior|assistant))',
        r'\bteaching\s+fellow\b'
    ],
    "Assistant Lecturer": [
        r'\bassistant\s+lecturer\b',
        r'\basst\.\s+lecturer\b'
    ],
    "Principal investigator": [
        r'\bprincipal\s+investigator\b',
        r'\bPI\b',
        r'\bprincipal\s+researcher\b',
        r'\bprinciple\s+investigator\b'  # Common misspelling
    ],
    "Research group manager": [
        r'\bresearch\s+group\s+(?:manager|leader|head)\b',
        r'\bgroup\s+leader\b',
        r'\bhead\s+of\s+(?:research\s+)?group\b'
    ],
    "Senior Researcher": [
        r'\bsenior\s+researcher\b',
        r'\bsenior\s+research\s+(?:scientist|fellow|associate)\b',
        r'\bsr\.\s+researcher\b',
        r'\bsenior\s+scientist\b'
    ],
    "Research fellow": [
        r'\bresearch\s+fellow\b',
        r'\bpostdoctoral\s+(?:research\s+)?fellow\b',
        r'\bpostdoc(?:toral)?\b'
    ],
    "Researcher": [
        r'\bresearcher\b(?!\s+(?:senior))',
        r'\bresearch\s+(?:scientist|associate)\b(?!\s+(?:senior))',
        r'\bjunior\s+(?:researcher|scientist)\b',
        r'\bproject\s+assistant\b',
        r'\bprojektass\b'  # German
    ],
    "Project Manager": [
        r'\bproject\s+manager\b',
        r'\bprogram\s+manager\b'
    ],
    "Teaching Assistant": [
        r'\bteaching\s+assistant\b',
        r'\bTA\b'
    ],
    "Demonstrator": [
        r'\bdemonstrator\b'
    ]
}


def log_message(message: str, level: str = "INFO"):
    """Log message to file and print to console."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    print(log_entry)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")


def extract_author_type_from_text(text: str) -> Optional[Dict]:
    """
    Extract author type from text content.
    Returns dict with author_type and confidence.
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Try each author type in priority order
    for author_type, patterns in AUTHOR_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                # Determine confidence based on pattern strength
                confidence = "HIGH" if any(strong in text_lower for strong in 
                    ['professor', 'lecturer', 'senior', 'principal']) else "MEDIUM"
                
                return {
                    "author_type": author_type,
                    "confidence": confidence,
                    "matched_pattern": pattern
                }
    
    return None


def fetch_url_content(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch content from URL with error handling.
    Returns text content or None if failed.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except Exception as e:
        log_message(f"Failed to fetch {url}: {str(e)}", "WARNING")
        return None


def prioritize_urls(urls: List[str]) -> List[str]:
    """
    Prioritize URLs based on likelihood of success.
    University staff pages > institute pages > news > scholar > others
    """
    priority_score = []
    
    for url in urls:
        score = 0
        url_lower = url.lower()
        
        # Highest priority: staff/profile pages
        if any(term in url_lower for term in ['/staff', '/person', '/employee', '/team', '/profile']):
            score = 100
        # High priority: institute/university pages
        elif any(domain in url_lower for domain in ['.edu', '.ac.', 'university', 'institut']):
            score = 80
        # Medium priority: publications/research pages
        elif any(term in url_lower for term in ['publication', 'research', 'project']):
            score = 60
        # Lower priority: scholar pages
        elif 'scholar.google' in url_lower:
            score = 40
        # Low priority: others
        else:
            score = 20
        
        priority_score.append((score, url))
    
    # Sort by score (descending) and return URLs
    priority_score.sort(reverse=True, key=lambda x: x[0])
    return [url for score, url in priority_score]


def enrich_author(author_data: Dict) -> Dict:
    """
    Enrich a single author with author_type from their email citations.
    Returns updated author data with enrichment metadata.
    """
    author_id = author_data.get('author_id')
    name = author_data.get('name', 'Unknown')
    email_citations = author_data.get('email_citations', [])
    
    result = {
        'author_id': author_id,
        'name': name,
        'author_type': None,
        'confidence': None,
        'source_url': None,
        'matched_pattern': None,
        'status': 'NOT_FOUND',
        'urls_checked': 0,
        'error': None
    }
    
    if not email_citations:
        result['status'] = 'NO_URLS'
        return result
    
    # Prioritize URLs
    prioritized_urls = prioritize_urls(email_citations[:5])  # Check top 5
    
    for url in prioritized_urls:
        result['urls_checked'] += 1
        
        # Skip PDFs and some problematic domains
        if any(ext in url.lower() for ext in ['.pdf', '.doc', '.ppt']):
            continue
        
        try:
            content = fetch_url_content(url)
            if content:
                extraction = extract_author_type_from_text(content)
                if extraction:
                    result.update({
                        'author_type': extraction['author_type'],
                        'confidence': extraction['confidence'],
                        'source_url': url,
                        'matched_pattern': extraction['matched_pattern'],
                        'status': 'SUCCESS'
                    })
                    return result
            
            # Delay between requests
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
        except Exception as e:
            log_message(f"Error processing {url} for {name}: {str(e)}", "ERROR")
            result['error'] = str(e)
            continue
    
    result['status'] = 'NOT_FOUND' if result['urls_checked'] > 0 else 'NO_URLS'
    return result


def load_progress() -> Dict:
    """Load progress from checkpoint file."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {
        'last_processed_index': -1,
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'started_at': datetime.now().isoformat(),
        'last_updated': None,
        'results': []
    }


def save_progress(progress: Dict):
    """Save progress to checkpoint file."""
    progress['last_updated'] = datetime.now().isoformat()
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
    
    # Also save results separately
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress['results'], f, indent=2, ensure_ascii=False)


def load_authors_to_enrich() -> List[Dict]:
    """Load all authors without author_type from simple.json files."""
    log_message("Loading authors without author_type...")
    
    authors = []
    simple_files = sorted(RESULTS_DIR.glob("*_simple.json"))
    
    # Track unique authors
    seen_ids = set()
    
    for json_path in simple_files:
        country = json_path.stem.replace("european_authors_", "").replace("_simple", "")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                country_authors = json.load(f)
            
            for author in country_authors:
                author_id = author.get('author_id')
                
                # Skip if already seen or has author_type
                if author_id in seen_ids or author.get('author_type'):
                    continue
                
                # Only process if has email citations
                if author.get('email_citations'):
                    authors.append({
                        'author_id': author_id,
                        'name': author.get('name'),
                        'email_citations': author.get('email_citations'),
                        'email_source': author.get('email_source'),
                        'primary_affiliation': author.get('primary_affiliation'),
                        'country': country
                    })
                    seen_ids.add(author_id)
                    
        except Exception as e:
            log_message(f"Error loading {json_path.name}: {e}", "ERROR")
    
    log_message(f"Loaded {len(authors)} unique authors to process")
    return authors


def process_batch(authors: List[Dict], start_idx: int, batch_size: int, progress: Dict) -> Dict:
    """Process a batch of authors."""
    end_idx = min(start_idx + batch_size, len(authors))
    batch = authors[start_idx:end_idx]
    
    log_message(f"\n{'='*60}")
    log_message(f"Processing batch: authors {start_idx+1} to {end_idx} of {len(authors)}")
    log_message(f"{'='*60}")
    
    batch_results = []
    
    for i, author_data in enumerate(batch, start=start_idx+1):
        log_message(f"\n[{i}/{len(authors)}] Processing: {author_data['name']}")
        
        result = enrich_author(author_data)
        batch_results.append(result)
        
        if result['status'] == 'SUCCESS':
            log_message(f"  ✅ Found: {result['author_type']} ({result['confidence']})", "SUCCESS")
            progress['successful'] += 1
        else:
            log_message(f"  ❌ Status: {result['status']}", "WARNING")
            progress['failed'] += 1
        
        progress['total_processed'] += 1
        progress['last_processed_index'] = i - 1
    
    progress['results'].extend(batch_results)
    
    # Save progress after each batch
    save_progress(progress)
    
    # Print batch statistics
    batch_success = sum(1 for r in batch_results if r['status'] == 'SUCCESS')
    log_message(f"\nBatch complete: {batch_success}/{len(batch)} successful ({batch_success/len(batch)*100:.1f}%)")
    
    return progress


def print_statistics(progress: Dict):
    """Print enrichment statistics."""
    total = progress['total_processed']
    successful = progress['successful']
    failed = progress['failed']
    
    if total == 0:
        return
    
    print("\n" + "="*60)
    print("ENRICHMENT STATISTICS")
    print("="*60)
    print(f"Total processed:    {total:>6}")
    print(f"Successful:         {successful:>6} ({successful/total*100:>5.1f}%)")
    print(f"Not found:          {failed:>6} ({failed/total*100:>5.1f}%)")
    print("="*60)
    
    # Count by author type
    if progress['results']:
        type_counts = Counter(r['author_type'] for r in progress['results'] if r['author_type'])
        if type_counts:
            print("\nAuthor Types Found:")
            print("-"*60)
            for author_type, count in type_counts.most_common():
                print(f"  {author_type:<30s}: {count:>4}")
    
    print("="*60)


def main():
    """Main processing function."""
    log_message("\n" + "="*60)
    log_message("AUTOMATED AUTHOR TYPE ENRICHMENT")
    log_message("="*60)
    
    # Load authors to process
    authors = load_authors_to_enrich()
    
    if not authors:
        log_message("No authors to process!", "WARNING")
        return
    
    # Load or initialize progress
    progress = load_progress()
    start_idx = progress['last_processed_index'] + 1
    
    if start_idx > 0:
        log_message(f"\nResuming from author {start_idx + 1} of {len(authors)}")
    else:
        log_message(f"\nStarting fresh enrichment of {len(authors)} authors")
    
    log_message(f"Batch size: {BATCH_SIZE}")
    log_message(f"Delay between requests: {DELAY_BETWEEN_REQUESTS}s")
    
    # Process in batches
    try:
        while start_idx < len(authors):
            progress = process_batch(authors, start_idx, BATCH_SIZE, progress)
            start_idx = progress['last_processed_index'] + 1
            
            # Print current statistics
            print_statistics(progress)
            
            # Optional: Add a longer pause between batches
            if start_idx < len(authors):
                log_message(f"\nPausing 5 seconds before next batch...")
                time.sleep(5)
    
    except KeyboardInterrupt:
        log_message("\n\nProcess interrupted by user. Progress saved.", "WARNING")
        save_progress(progress)
        print_statistics(progress)
        return
    
    except Exception as e:
        log_message(f"\n\nFatal error: {e}", "ERROR")
        save_progress(progress)
        raise
    
    log_message("\n" + "="*60)
    log_message("ENRICHMENT COMPLETE!")
    log_message("="*60)
    print_statistics(progress)
    
    log_message(f"\nResults saved to: {OUTPUT_FILE}")
    log_message(f"Progress saved to: {PROGRESS_FILE}")
    log_message(f"Log saved to: {LOG_FILE}")


if __name__ == "__main__":
    main()

