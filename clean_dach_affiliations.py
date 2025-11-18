#!/usr/bin/env python3
"""
Clean DACH affiliations to official German names using Perplexity API
Validates against email domains for accuracy
"""

import json
import csv
import sys
import time
import logging
import argparse
import requests
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('affiliation_cleaning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Increase CSV field size limit
csv.field_size_limit(sys.maxsize)


class AffiliationCleaner:
    """Clean affiliations using Perplexity API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.cache = {}
        self.cache_file = Path("affiliation_cache.json")
        self.load_cache()
    
    def load_cache(self):
        """Load cached results to avoid re-processing"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Loaded {len(self.cache)} cached affiliations")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def save_cache(self):
        """Save cache to disk"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved {len(self.cache)} affiliations to cache")
        except Exception as e:
            logger.error(f"Could not save cache: {e}")
    
    def clean_affiliation(self, raw_affiliation: str, email: str) -> dict:
        """
        Clean a single affiliation using Perplexity API
        
        Returns:
            dict with keys: official_german_name, validation_status, confidence
        """
        # Check cache first
        cache_key = f"{raw_affiliation}||{email}"
        if cache_key in self.cache:
            logger.debug(f"Cache hit for: {raw_affiliation[:50]}...")
            return self.cache[cache_key]
        
        # Extract email domain
        email_domain = email.split('@')[-1] if email and '@' in email else "unknown"
        
        # Build prompt
        prompt = self._build_prompt(raw_affiliation, email, email_domain)
        
        try:
            # Call Perplexity API
            response = self._call_api(prompt)
            result = self._parse_response(response, raw_affiliation, email_domain)
            
            # Cache result
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error cleaning affiliation '{raw_affiliation[:50]}...': {e}")
            return {
                "official_german_name": raw_affiliation,
                "validation_status": "❌ Error",
                "confidence": "low",
                "error": str(e)
            }
    
    def _build_prompt(self, affiliation: str, email: str, email_domain: str) -> str:
        """Build the Perplexity prompt"""
        return f"""You are a specialist in German academic and corporate organization names.

TASK: Convert this affiliation to its official German name.

INPUT:
- Raw affiliation: "{affiliation}"
- Email domain: {email_domain}

REQUIREMENTS:
1. Provide the OFFICIAL GERMAN NAME as written on the organization's German website
2. Use proper German characters (ä, ö, ü, ß)
3. Remove department/institute names - only keep the main organization
4. Remove city and country names
5. Keep legal suffixes for companies (GmbH, AG, etc.)
6. Validate the name matches the email domain

COMMON CONVERSIONS:
- Technical University of Munich → Technische Universität München (TUM)
- ETH Zurich → ETH Zürich
- Vienna University of Technology → Technische Universität Wien
- Robert Bosch GmbH, Corporate Research → Robert Bosch GmbH
- Fraunhofer Institute for Solar Energy Systems → Fraunhofer ISE

EMAIL DOMAIN HINTS:
- @tum.de, @mytum.de → Technische Universität München
- @tu-berlin.de → Technische Universität Berlin
- @ethz.ch → ETH Zürich
- @kit.edu → Karlsruher Institut für Technologie
- @rwth-aachen.de → RWTH Aachen
- @bosch.com → Robert Bosch GmbH
- @siemens.com → Siemens AG
- @fz-juelich.de → Forschungszentrum Jülich

RESPOND IN JSON FORMAT:
{{
  "official_german_name": "[cleaned name]",
  "validation": "✅ Match" or "⚠️ Email suggests different org" or "❓ Unknown domain",
  "confidence": "high" or "medium" or "low",
  "reasoning": "[brief explanation]"
}}

Provide ONLY the JSON, no other text."""
    
    def _call_api(self, prompt: str) -> dict:
        """Call Perplexity API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a precise German organization name specialist. Always respond in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def _parse_response(self, response: dict, original: str, email_domain: str) -> dict:
        """Parse Perplexity API response"""
        try:
            content = response['choices'][0]['message']['content']
            
            # Try to extract JSON from response
            # Sometimes the model wraps it in markdown code blocks
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            result = json.loads(content)
            
            return {
                "official_german_name": result.get("official_german_name", original),
                "validation_status": result.get("validation", "❓ Unknown"),
                "confidence": result.get("confidence", "medium"),
                "reasoning": result.get("reasoning", "")
            }
            
        except Exception as e:
            logger.warning(f"Could not parse response, using original: {e}")
            return {
                "official_german_name": original,
                "validation_status": "❌ Parse error",
                "confidence": "low",
                "error": str(e)
            }


def extract_unique_affiliations(input_file: str) -> list:
    """Extract unique (affiliation, email) pairs from CSV"""
    logger.info(f"Extracting unique affiliations from {input_file}")
    
    affiliation_map = {}
    author_affiliations = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            author_id = row['author_id']
            affiliation = row.get('primary_affiliation', '').strip()
            email = row.get('email', '').strip()
            
            # Parse all_affiliations to check secondary affiliations for email validation
            all_affiliations_str = row.get('all_affiliations', '[]').strip()
            try:
                all_affiliations = json.loads(all_affiliations_str) if all_affiliations_str else []
            except:
                all_affiliations = [affiliation] if affiliation else []
            
            # Store for each author
            author_affiliations.append({
                'author_id': author_id,
                'affiliation': affiliation,
                'email': email,
                'all_affiliations': all_affiliations
            })
            
            # Track unique combinations (keyed by primary affiliation and email)
            # but store all_affiliations for validation
            key = (affiliation, email)
            if key not in affiliation_map:
                affiliation_map[key] = {
                    'author_ids': [],
                    'all_affiliations': []
                }
            affiliation_map[key]['author_ids'].append(author_id)
            # Collect all secondary affiliations for this combination
            affiliation_map[key]['all_affiliations'].extend(all_affiliations)
    
    logger.info(f"Found {len(author_affiliations)} authors")
    logger.info(f"Found {len(affiliation_map)} unique affiliation+email combinations")
    
    return author_affiliations, affiliation_map


def revalidate_against_all_affiliations(result: dict, primary_affiliation: str, 
                                       all_affiliations: list, email: str) -> dict:
    """
    Re-validate email against all affiliations (not just primary).
    This reduces false positives for authors with multiple affiliations.
    """
    # If already validated as a match, keep it
    if '✅' in result.get('validation_status', ''):
        return result
    
    # Extract email domain
    if not email or '@' not in email:
        return result
    
    email_domain = email.split('@')[-1].lower()
    
    # Check if email matches any of the all_affiliations
    for affiliation in all_affiliations:
        affiliation_lower = affiliation.lower()
        
        # Simple heuristic matching
        # Check for university/institution matches
        email_parts = email_domain.replace('.', ' ').replace('-', ' ').split()
        
        for part in email_parts:
            if len(part) > 3 and part in affiliation_lower:
                # Found a match in secondary affiliation!
                result['validation_status'] = f"✅ Match (via secondary affiliation)"
                result['confidence'] = 'high'
                if 'reasoning' in result:
                    result['reasoning'] += f" Note: Email matches secondary affiliation: {affiliation[:80]}"
                return result
    
    # No match found in any affiliation
    return result


def process_affiliations(cleaner: AffiliationCleaner, affiliation_map: dict, delay: float = 2.0) -> dict:
    """Process all unique affiliations"""
    logger.info(f"Processing {len(affiliation_map)} unique affiliations...")
    
    results = {}
    total = len(affiliation_map)
    
    for idx, ((affiliation, email), data) in enumerate(affiliation_map.items(), 1):
        author_ids = data['author_ids']
        all_affiliations = data['all_affiliations']
        
        logger.info(f"[{idx}/{total}] Processing: {affiliation[:60]}... (Email: {email})")
        
        result = cleaner.clean_affiliation(affiliation, email)
        
        # Re-validate against all affiliations (not just primary)
        result = revalidate_against_all_affiliations(
            result, affiliation, all_affiliations, email
        )
        
        # Store result for this affiliation+email combo
        key = (affiliation, email)
        results[key] = result
        
        logger.info(f"  ➜ {result['official_german_name']} {result['validation_status']}")
        
        # Save cache periodically
        if idx % 10 == 0:
            cleaner.save_cache()
        
        # Rate limiting
        if idx < total:
            time.sleep(delay)
    
    # Final cache save
    cleaner.save_cache()
    
    return results


def update_csv(input_file: str, output_file: str, author_affiliations: list, cleaned_results: dict):
    """Update CSV with cleaned affiliations"""
    logger.info(f"Updating CSV: {input_file} → {output_file}")
    
    # Create a mapping from (affiliation, email) to cleaned name
    lookup = {
        (aff, email): result['official_german_name']
        for (aff, email), result in cleaned_results.items()
    }
    
    # Read and update
    updated_count = 0
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['official_german_name']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            affiliation = row.get('primary_affiliation', '').strip()
            email = row.get('email', '').strip()
            
            # Look up cleaned name
            key = (affiliation, email)
            cleaned_name = lookup.get(key, affiliation)
            
            # Add new column
            row['official_german_name'] = cleaned_name
            writer.writerow(row)
            updated_count += 1
    
    logger.info(f"✅ Updated {updated_count} rows")
    logger.info(f"✅ Output saved to: {output_file}")


def generate_review_report(cleaned_results: dict, affiliation_map: dict, output_file: str = "affiliation_review.txt"):
    """Generate a review report for manual checking"""
    logger.info(f"Generating review report: {output_file}")
    
    flagged = []
    high_confidence = []
    
    for (affiliation, email), result in cleaned_results.items():
        data = affiliation_map.get((affiliation, email), {})
        author_ids = data.get('author_ids', [])
        author_count = len(author_ids)
        
        item = {
            'original': affiliation,
            'cleaned': result['official_german_name'],
            'email': email,
            'status': result['validation_status'],
            'confidence': result['confidence'],
            'author_count': author_count
        }
        
        if '⚠️' in result['validation_status'] or '❌' in result['validation_status'] or result['confidence'] == 'low':
            flagged.append(item)
        else:
            high_confidence.append(item)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DACH AFFILIATION CLEANING REVIEW REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total unique affiliations: {len(cleaned_results)}\n")
        f.write(f"High confidence: {len(high_confidence)}\n")
        f.write(f"Needs review: {len(flagged)}\n\n")
        
        if flagged:
            f.write("=" * 80 + "\n")
            f.write("⚠️  FLAGGED FOR REVIEW (sorted by author count)\n")
            f.write("=" * 80 + "\n\n")
            
            flagged.sort(key=lambda x: x['author_count'], reverse=True)
            
            for item in flagged:
                f.write(f"Authors affected: {item['author_count']}\n")
                f.write(f"Original: {item['original']}\n")
                f.write(f"Cleaned:  {item['cleaned']}\n")
                f.write(f"Email:    {item['email']}\n")
                f.write(f"Status:   {item['status']} (Confidence: {item['confidence']})\n")
                f.write("-" * 80 + "\n\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("✅ HIGH CONFIDENCE CLEANINGS (Top 20 by author count)\n")
        f.write("=" * 80 + "\n\n")
        
        high_confidence.sort(key=lambda x: x['author_count'], reverse=True)
        
        for item in high_confidence[:20]:
            f.write(f"Authors: {item['author_count']:3d} | {item['original'][:60]:<60} → {item['cleaned']}\n")
    
    logger.info(f"✅ Review report saved to: {output_file}")
    logger.info(f"   Flagged for review: {len(flagged)} affiliations")


def main():
    parser = argparse.ArgumentParser(description='Clean DACH affiliations to official German names')
    parser.add_argument('--api-key', required=True, help='Perplexity API key')
    parser.add_argument('--input', default='results/final_results/ultimate_results/dach/final_dach.csv',
                       help='Input CSV file')
    parser.add_argument('--output', default='results/final_results/ultimate_results/dach/final_dach_cleaned.csv',
                       help='Output CSV file')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between API calls (seconds)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: process only first 5 unique affiliations')
    
    args = parser.parse_args()
    
    logger.info("=" * 80)
    logger.info("DACH AFFILIATION CLEANER - Official German Names")
    logger.info("=" * 80)
    
    # Initialize cleaner
    cleaner = AffiliationCleaner(args.api_key)
    
    # Extract affiliations
    author_affiliations, affiliation_map = extract_unique_affiliations(args.input)
    
    # Test mode
    if args.test:
        logger.info("🧪 TEST MODE: Processing first 5 unique affiliations")
        affiliation_map = dict(list(affiliation_map.items())[:5])
    
    # Process affiliations
    cleaned_results = process_affiliations(cleaner, affiliation_map, args.delay)
    
    # Update CSV
    update_csv(args.input, args.output, author_affiliations, cleaned_results)
    
    # Generate review report
    generate_review_report(cleaned_results, affiliation_map)
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"Input:  {args.input}")
    logger.info(f"Output: {args.output}")
    logger.info(f"Review: affiliation_review.txt")
    logger.info(f"Log:    affiliation_cleaning.log")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()

