#!/usr/bin/env python3
"""
IEEE Xplore Author Scraper
Main script to extract author details from IEEE Xplore publications.

This script searches IEEE Xplore for publications in specific research areas,
filters authors affiliated with European universities (excluding France),
and extracts their contact and profile information.
"""

import json
import logging
import sys
import time
import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

from scraper.ieee_scraper import IEEEXploreScraper
from scraper.affiliation_parser import AffiliationParser
from scraper.author_extractor import AuthorExtractor
from utils.data_aggregator import DataAggregator


# Create results directory
os.makedirs('results', exist_ok=True)

# Configure logging (will be reconfigured per query later)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class IEEEAuthorScraperApp:
    """Main application class for IEEE author scraping."""
    
    def __init__(self, config_path='config.json'):
        """
        Initialize the scraper application.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.ieee_scraper = None
        self.affiliation_parser = AffiliationParser(self.config)  # Pass config for country list
        self.author_extractor = AuthorExtractor(self.config)
        self.data_aggregator = DataAggregator()
        
        # Create results directory if it doesn't exist
        import os
        self.results_dir = 'results'
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.output_file = os.path.join(self.results_dir, 'authors_output.json')  # Default, can be overridden
        
        # Store publications with their authors, grouped by query
        self.publications_by_query = defaultdict(list)  # {query: [{publication: {...}, authors: [...]}, ...]}
        self.publications_data = []  # List of {publication: {...}, authors: [...]} (all combined)
        
        # Statistics
        self.stats = {
            'total_publications_found': 0,
            'publications_processed': 0,
            'publications_with_european_authors': 0,
            'publications_skipped_no_european': 0,
            'total_authors_found': 0,
            'european_authors_found': 0,
            'authors_with_details': 0,
            'queries_executed': 0,
            'country_distribution': {},  # Track authors by country
            'start_time': None,
            'end_time': None
        }
    
    def _sanitize_query_name(self, query):
        """
        Sanitize query string to create a valid directory name.
        
        Args:
            query (str): Query string
            
        Returns:
            str: Sanitized directory name
        """
        # Remove or replace invalid filesystem characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '', query)
        # Replace spaces and special chars with hyphens
        sanitized = re.sub(r'[\s\-]+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        # Ensure it's not empty
        if not sanitized:
            sanitized = 'query'
        return sanitized.lower()
    
    def _load_config(self, config_path):
        """
        Load configuration from JSON file.
        
        Args:
            config_path (str): Path to config file
        
        Returns:
            dict: Configuration dictionary
        """
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def run(self, skip_confirmation=False, collect_all_pages=True):
        """
        Run the complete scraping workflow.
        
        Args:
            skip_confirmation (bool): If True, skip user confirmation before scraping
            collect_all_pages (bool): If True, collect from all paginated pages
        """
        # Set up main log file
        main_log_file = os.path.join(self.results_dir, 'ieee_scraper.log')
        file_handler = logging.FileHandler(main_log_file, mode='w')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)
        
        try:
            self.stats['start_time'] = datetime.now()
            logger.info("=" * 70)
            logger.info("IEEE Xplore Author Scraper - Starting")
            logger.info("=" * 70)
            
            # Initialize IEEE scraper
            logger.info("Initializing IEEE Xplore scraper...")
            self.ieee_scraper = IEEEXploreScraper(self.config)
            
            # Step 1: Search for publications
            logger.info("\nSTEP 1: Collecting publications from IEEE Xplore...")
            publications = self._search_all_publications(collect_all_pages=collect_all_pages)
            self.stats['total_publications_found'] = len(publications)
            
            if not publications:
                logger.warning("No publications found. Exiting.")
                return
            
            # Show summary and ask for confirmation
            print(f"\n{'='*70}")
            print(f"📊 COLLECTION COMPLETE")
            print(f"{'='*70}")
            print(f"✅ Total publications found: {len(publications)}")
            print(f"✅ Search queries executed: {self.stats['queries_executed']}")
            print(f"\nNext steps:")
            print(f"  • Visit {len(publications)} publication pages")
            print(f"  • Extract author details from European affiliations")
            print(f"  • Visit author profile pages for additional information")
            print(f"\n⏱️  Estimated time: ~{self._estimate_time(len(publications))} minutes")
            print(f"{'='*70}\n")
            
            if not skip_confirmation:
                response = input("Do you want to proceed with the scrape? (yes/no): ").strip().lower()
                
                if response not in ['yes', 'y']:
                    logger.info("Scrape cancelled by user.")
                    print("\n❌ Scrape cancelled. Publication URLs have been collected but not processed.")
                    return
                
                print("\n✅ Starting scrape...\n")
            else:
                logger.info("Auto-confirmation mode enabled, proceeding with scrape...")
            
            # Step 2: Process each publication
            logger.info("STEP 2: Processing publications and extracting authors...")
            self._process_publications(publications)
            
            # Step 3: Get aggregated results
            logger.info("\nSTEP 3: Aggregating author data...")
            authors_list = self.data_aggregator.get_aggregated_authors()
            
            # Step 4: Save results
            logger.info("\nSTEP 4: Saving results...")
            self._save_results(authors_list)
            
            # Copy log files to query directories
            self._copy_logs_to_query_dirs()
            
            # Print statistics
            self.stats['end_time'] = datetime.now()
            self._print_statistics()
            
            logger.info("=" * 70)
            logger.info("✅ IEEE Xplore Author Scraper - Completed Successfully")
            logger.info("=" * 70)
            
        except KeyboardInterrupt:
            logger.warning("\nScraping interrupted by user")
            self._save_partial_results()
        except Exception as e:
            logger.error(f"Error during scraping: {e}", exc_info=True)
            self._save_partial_results()
        finally:
            # Clean up
            if self.ieee_scraper:
                self.ieee_scraper.close()
    
    def _estimate_time(self, num_publications):
        """
        Estimate scraping time based on number of publications.
        
        Args:
            num_publications (int): Number of publications to scrape
        
        Returns:
            int: Estimated time in minutes
        """
        # Rough estimate: ~10 seconds per publication
        seconds_per_pub = 10
        total_seconds = num_publications * seconds_per_pub
        return max(1, round(total_seconds / 60))
    
    def _search_all_publications(self, collect_all_pages=False):
        """
        Search for publications across all configured topics.
        
        Args:
            collect_all_pages (bool): If True, collect from all paginated pages
        
        Returns:
            list: List of publication dictionaries
        """
        all_publications = []
        search_queries = self.config.get('search_queries', [])
        
        total_queries = len(search_queries)
        
        logger.info(f"Starting search with {total_queries} queries...")
        
        for idx, query in enumerate(search_queries, 1):
            try:
                self.stats['queries_executed'] += 1
                logger.info(f"\n[{idx}/{total_queries}] Query: {query}")
                
                publications = self.ieee_scraper.search_publications(
                    query, 
                    collect_all_pages=collect_all_pages
                )
                
                # Add query metadata
                for pub in publications:
                    pub['query'] = query
                
                all_publications.extend(publications)
                
                logger.info(f"  Collected {len(publications)} publications")
                
                # Delay between queries to be respectful
                time.sleep(self.config.get('delay_between_requests', 2))
                
            except Exception as e:
                logger.error(f"Error searching for '{query}': {e}")
                continue
        
        # Remove duplicates based on URL
        unique_pubs = {}
        for pub in all_publications:
            url = pub.get('url')
            if url and url not in unique_pubs:
                unique_pubs[url] = pub
        
        logger.info(f"\nDeduplication: {len(all_publications)} total → {len(unique_pubs)} unique")
        return list(unique_pubs.values())
    
    def _process_publications(self, publications):
        """
        Process publications to extract and filter authors.
        
        OPTIMIZATION: Checks author countries FIRST before extracting full publication details.
        
        Args:
            publications (list): List of publication dictionaries
        """
        total = len(publications)
        
        for idx, pub in enumerate(publications, 1):
            try:
                logger.info(f"Processing publication {idx}/{total}: {pub.get('title', 'Unknown')}")
                
                # OPTIMIZATION: Quick check for European authors FIRST
                # This saves ~10 seconds per publication if no European authors found
                has_european, authors_data = self.ieee_scraper.quick_check_authors_european(pub['url'])
                
                if not authors_data:
                    logger.warning(f"  ⏭️  Skipping: No author data found")
                    continue
                
                # EARLY EXIT: Skip if no European authors found
                if not has_european:
                    logger.info(f"  ⏭️  Skipping: No European research authors found")
                    self.stats['publications_skipped_no_european'] += 1
                    continue
                
                # Now check which European authors have research affiliations
                has_european_research_author = False
                european_countries_found = []
                
                for author in authors_data:
                    affiliation = author.get('affiliation', '')
                    if affiliation:
                        affiliation_data = self.affiliation_parser.parse_affiliation(affiliation)
                        if affiliation_data['is_european'] and affiliation_data['is_research_institution']:
                            has_european_research_author = True
                            country = affiliation_data.get('country')
                            if country and country not in european_countries_found:
                                european_countries_found.append(country)
                
                # Skip if no research institution affiliations
                if not has_european_research_author:
                    logger.info(f"  ⏭️  Skipping: No European research institution authors found")
                    self.stats['publications_skipped_no_european'] += 1
                    continue
                
                # Log which European countries were found
                countries_str = ", ".join(european_countries_found[:3])  # Show first 3
                if len(european_countries_found) > 3:
                    countries_str += f" +{len(european_countries_found)-3} more"
                logger.info(f"  ✓ Found European author(s) from: {countries_str}")
                
                # NOW extract full publication details (we already have authors)
                pub_details = self.ieee_scraper.get_publication_details(pub['url'], authors_data=authors_data)
                
                if not pub_details:
                    logger.warning(f"  ⏭️  Skipping: Could not extract publication details")
                    continue
                
                self.stats['publications_processed'] += 1
                
                # Get DOI or URL for publication reference
                publication_ref = pub_details.get('doi_url') or pub_details.get('doi') or pub['url']
                
                # Process each author
                authors = pub_details['authors']
                self.stats['total_authors_found'] += len(authors)
                
                # Store publication with authors for this publication
                pub_with_authors = {
                    'publication': {
                        'title': pub_details.get('title'),
                        'url': pub_details.get('url'),
                        'year': pub_details.get('year'),
                        'type': pub_details.get('type'),
                        'publisher': pub_details.get('publisher'),
                        'doi': pub_details.get('doi'),
                        'doi_url': pub_details.get('doi_url'),
                        'abstract': pub_details.get('abstract'),
                        'conference': pub_details.get('conference'),
                        'journal': pub_details.get('journal')
                    },
                    'authors': []
                }
                
                for author in authors:
                    try:
                        author_details = self._process_author(author, publication_ref)
                        if author_details:
                            pub_with_authors['authors'].append(author_details)
                    except Exception as e:
                        logger.error(f"  Error processing author {author.get('name')}: {e}")
                        continue
                
                # Add to publications data if it has European authors
                if pub_with_authors['authors']:
                    self.publications_data.append(pub_with_authors)
                    # Also group by query for per-query results
                    query = pub.get('query', 'unknown')
                    self.publications_by_query[query].append(pub_with_authors)
                    self.stats['publications_with_european_authors'] += 1
                
                # Save progress periodically
                if idx % 10 == 0:
                    self._save_partial_results()
                
            except Exception as e:
                logger.error(f"Error processing publication {pub.get('url')}: {e}")
                continue
    
    def _process_author(self, author, publication_ref):
        """
        Process a single author: check affiliation, extract details, add to aggregator.
        
        Args:
            author (dict): Author data from publication
            publication_ref (str): DOI or URL of the publication
            
        Returns:
            dict: Author details if European, None otherwise
        """
        author_name = author.get('name', 'Unknown')
        
        # Step 1: Parse and validate affiliation
        affiliation_data = self.affiliation_parser.parse_affiliation(
            author.get('affiliation', '')
        )
        
        # Filter: Only European authors (excluding France)
        if not affiliation_data['is_european']:
            logger.debug(f"  Skipping {author_name}: Not European affiliation")
            return None
        
        # Filter: Only university/research institution affiliations
        if not affiliation_data['is_research_institution']:
            logger.debug(f"  Skipping {author_name}: Not a research institution")
            return None
        
        logger.info(f"  ✓ European author found: {author_name} ({affiliation_data['country']})")
        self.stats['european_authors_found'] += 1
        
        # Track country distribution
        country = affiliation_data['country']
        if country:
            self.stats['country_distribution'][country] = self.stats['country_distribution'].get(country, 0) + 1
        
        # Step 2: Extract detailed author information
        ieee_profile_data = None
        
        # Try to get IEEE profile data
        if author.get('profile_url'):
            try:
                ieee_profile_data = self.ieee_scraper.get_author_profile(
                    author['profile_url']
                )
            except Exception as e:
                logger.warning(f"  Could not fetch IEEE profile for {author_name}: {e}")
        
        # Extract comprehensive author details
        author_details = self.author_extractor.extract_author_details(
            author, 
            ieee_profile_data
        )
        
        # Add affiliation data
        author_details['country'] = affiliation_data['country']
        author_details['affiliation_raw'] = author.get('affiliation', '')
        
        # Ensure university/research institution are set
        if not author_details.get('university') and not author_details.get('research_institution'):
            if affiliation_data.get('institution'):
                author_details['university'] = affiliation_data['institution']
        
        self.stats['authors_with_details'] += 1
        
        # Step 3: Add to aggregator
        self.data_aggregator.add_author(author_details, publication_ref)
        
        logger.info(f"    Email: {author_details.get('email') or 'Not found'}")
        logger.info(f"    Institution: {author_details.get('university') or author_details.get('research_institution') or 'Unknown'}")
        
        return author_details
    
    def _save_results(self, authors_list):
        """
        Save results to JSON files organized by query in subdirectories.
        Each query gets its own directory within results/.
        
        Args:
            authors_list (list): List of author dictionaries
        """
        try:
            logger.info("\n" + "=" * 70)
            logger.info("SAVING RESULTS")
            logger.info("=" * 70)
            
            # Save results for each query in its own subdirectory
            for query, publications in self.publications_by_query.items():
                if not publications:
                    continue
                    
                # Create sanitized directory name
                query_dir_name = self._sanitize_query_name(query)
                query_dir = os.path.join(self.results_dir, query_dir_name)
                os.makedirs(query_dir, exist_ok=True)
                
                # Save publications with authors for this query
                pub_output_file = os.path.join(query_dir, 'publications_with_authors.json')
                with open(pub_output_file, 'w', encoding='utf-8') as f:
                    json.dump(publications, f, indent=2, ensure_ascii=False)
                
                # Extract unique authors for this query
                query_authors = defaultdict(lambda: None)
                for pub_data in publications:
                    for author in pub_data['authors']:
                        author_key = author.get('email') or author.get('name')
                        if author_key:
                            if query_authors[author_key] is None:
                                query_authors[author_key] = author
                            else:
                                # Merge publication DOIs
                                existing = query_authors[author_key]
                                existing_dois = set(existing.get('publication_dois', []))
                                new_dois = set(author.get('publication_dois', []))
                                existing['publication_dois'] = list(existing_dois | new_dois)
                
                query_authors_list = [a for a in query_authors.values() if a is not None]
                
                # Save unique authors for this query
                authors_output_file = os.path.join(query_dir, 'authors_output.json')
                with open(authors_output_file, 'w', encoding='utf-8') as f:
                    json.dump(query_authors_list, f, indent=2, ensure_ascii=False)
                
                # Set up logging for this query
                log_file = os.path.join(query_dir, 'ieee_scraper.log')
                
                logger.info(f"\n📁 Query: '{query}'")
                logger.info(f"   Directory: {query_dir}/")
                logger.info(f"   Publications: {len(publications)}")
                logger.info(f"   Unique authors: {len(query_authors_list)}")
                logger.info(f"   Files saved:")
                logger.info(f"     • publications_with_authors.json")
                logger.info(f"     • authors_output.json")
            
            # Also save combined results in the main results directory for convenience
            pub_output_file = os.path.join(self.results_dir, 'publications_with_authors.json')
            with open(pub_output_file, 'w', encoding='utf-8') as f:
                json.dump(self.publications_data, f, indent=2, ensure_ascii=False)
            
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(authors_list, f, indent=2, ensure_ascii=False)
            
            logger.info(f"\n📁 Combined results:")
            logger.info(f"   Directory: {self.results_dir}/")
            logger.info(f"   Publications: {len(self.publications_data)}")
            logger.info(f"   Unique authors: {len(authors_list)}")
            logger.info(f"   Files saved:")
            logger.info(f"     • publications_with_authors.json")
            logger.info(f"     • authors_output.json")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def _copy_logs_to_query_dirs(self):
        """Copy the main log file to each query-specific directory."""
        try:
            import shutil
            main_log_file = os.path.join(self.results_dir, 'ieee_scraper.log')
            
            if not os.path.exists(main_log_file):
                logger.warning("Main log file not found, skipping log copy")
                return
            
            # Copy to each query directory
            for query in self.publications_by_query.keys():
                query_dir_name = self._sanitize_query_name(query)
                query_dir = os.path.join(self.results_dir, query_dir_name)
                
                if os.path.exists(query_dir):
                    dest_log = os.path.join(query_dir, 'ieee_scraper.log')
                    shutil.copy2(main_log_file, dest_log)
                    logger.debug(f"Copied log to {dest_log}")
            
            logger.info("✅ Log files copied to query directories")
            
        except Exception as e:
            logger.error(f"Error copying log files: {e}")
    
    def _save_partial_results(self):
        """Save partial results in case of interruption."""
        try:
            authors_list = self.data_aggregator.get_aggregated_authors()
            output_file = os.path.join(self.results_dir, f'authors_output_partial_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(authors_list, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Partial results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving partial results: {e}")
    
    def _print_statistics(self):
        """Print scraping statistics."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("SCRAPING STATISTICS")
        logger.info("=" * 70)
        
        duration = self.stats['end_time'] - self.stats['start_time']
        
        logger.info(f"Duration: {duration}")
        logger.info(f"Queries executed: {self.stats['queries_executed']}")
        logger.info(f"Total publications found: {self.stats['total_publications_found']}")
        logger.info(f"Publications processed: {self.stats['publications_processed']}")
        logger.info(f"Publications with European authors: {self.stats['publications_with_european_authors']}")
        logger.info(f"Publications skipped (no European authors): {self.stats['publications_skipped_no_european']}")
        logger.info(f"Total authors encountered: {self.stats['total_authors_found']}")
        logger.info(f"European authors found: {self.stats['european_authors_found']}")
        logger.info(f"Authors with details extracted: {self.stats['authors_with_details']}")
        
        # Data aggregator statistics
        agg_stats = self.data_aggregator.get_statistics()
        logger.info(f"Unique authors aggregated: {agg_stats['total_authors']}")
        logger.info(f"Authors with email: {agg_stats['authors_with_email']} ({agg_stats['email_coverage']})")
        logger.info(f"Total publication references: {agg_stats['total_publications']}")
        
        # Country distribution
        if self.stats['country_distribution']:
            logger.info("")
            logger.info("COUNTRY DISTRIBUTION (Authors)")
            logger.info("-" * 70)
            
            # Get priority countries from config
            priority_countries = self.config.get('priority_countries', [])
            
            # Sort by count (descending)
            sorted_countries = sorted(
                self.stats['country_distribution'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Display priority countries first (highlighted)
            priority_shown = []
            for country, count in sorted_countries:
                if country in priority_countries:
                    logger.info(f"  ⭐ {country}: {count} authors")
                    priority_shown.append(country)
            
            # Display other countries
            if len(sorted_countries) > len(priority_shown):
                logger.info("")
                for country, count in sorted_countries:
                    if country not in priority_countries:
                        logger.info(f"  • {country}: {count} authors")
        
        logger.info("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='IEEE Xplore Author Scraper - Extract author details from publications',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ieee_author_scraper.py
  python ieee_author_scraper.py --config config_test.json
  python ieee_author_scraper.py --config config.json --output custom_output.json
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '--output', '-o',
        default='results/authors_output.json',
        help='Path to output JSON file (default: results/authors_output.json)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--no-confirm',
        action='store_true',
        help='Skip confirmation prompt before scraping (for automated runs)'
    )
    
    parser.add_argument(
        '--single-page',
        action='store_true',
        help='Only collect first page of results (faster for testing)'
    )
    
    args = parser.parse_args()
    
    # Update logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        app = IEEEAuthorScraperApp(config_path=args.config)
        app.output_file = args.output
        
        # Run with appropriate settings
        app.run(
            skip_confirmation=args.no_confirm,
            collect_all_pages=not args.single_page
        )
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

