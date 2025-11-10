#!/usr/bin/env python3
"""
Add all publications to remaining European authors dataset
Includes publications where they are not first author
"""

import json
from datetime import datetime
from pathlib import Path

def main():
    print("🔄 Adding all publications to remaining European authors...")
    print("=" * 70)
    
    # Load the complete dataset
    print("Loading remaining_european_authors_complete_dataset.json...")
    with open('results/remaining_european_authors_complete_dataset.json', 'r') as f:
        complete_data = json.load(f)
    
    # Load unique_authors.json to get all publications
    print("Loading unique_authors.json...")
    with open('results/unique_authors.json', 'r') as f:
        unique_data = json.load(f)
    
    unique_authors = unique_data.get('authors', {})
    complete_authors = complete_data.get('authors', {})
    
    print(f"\nProcessing {len(complete_authors):,} authors...")
    
    # Update each author with their publications
    authors_with_pubs = 0
    total_pubs_added = 0
    
    for author_id, author in complete_authors.items():
        # Get publications from unique_authors
        unique_author = unique_authors.get(author_id, {})
        publications = unique_author.get('publications', [])
        
        if not publications:
            continue
        
        authors_with_pubs += 1
        
        # Process each publication
        all_publications = []
        publication_titles = []
        publication_years = []
        publication_dois = []
        first_author_pubs = []
        non_first_author_pubs = []
        
        for pub in publications:
            # Check if this author is first author
            authors_list = pub.get('all_coauthors', [])
            is_first_author = False
            
            if authors_list:
                first_author_id = str(authors_list[0].get('id', ''))
                is_first_author = (first_author_id == author_id)
            
            # Create publication record (use correct field names from unique_authors.json)
            pub_record = {
                'article_number': pub.get('article_number'),
                'title': pub.get('article_title'),
                'year': pub.get('publication_year'),
                'doi': pub.get('doi'),
                'publication_title': pub.get('publication_title'),
                'display_publication_title': pub.get('display_publication_title'),
                'volume': pub.get('volume'),
                'issue': pub.get('issue'),
                'start_page': pub.get('start_page'),
                'end_page': pub.get('end_page'),
                'authors': pub.get('all_coauthors', []),  # Use all_coauthors from unique_authors
                'first_author': is_first_author,
                'author_position': 1 if is_first_author else (
                    next((i+1 for i, a in enumerate(pub.get('all_coauthors', [])) if str(a.get('id')) == author_id), None)
                ),
                'total_authors': len(pub.get('all_coauthors', [])),
                'abstract': pub.get('abstract', ''),
                'pdf_url': pub.get('pdf_link'),
                'pdf_size': pub.get('pdf_size'),
                'document_link': pub.get('document_link'),
                'content_type': pub.get('content_type'),
                'access_type': pub.get('access_type'),
                'is_open_access': pub.get('is_open_access'),
                'citation_count': pub.get('citation_count', 0),
                'download_count': pub.get('download_count', 0),
                'patent_citation_count': pub.get('patent_citation_count', 0)
            }
            
            all_publications.append(pub_record)
            publication_titles.append(pub.get('article_title', ''))
            publication_years.append(pub.get('publication_year'))
            publication_dois.append(pub.get('doi', ''))
            
            if is_first_author:
                first_author_pubs.append(pub_record)
            else:
                non_first_author_pubs.append(pub_record)
        
        # Update author record
        author['all_publications'] = all_publications
        author['publications_as_first_author'] = first_author_pubs
        author['publications_as_non_first_author'] = non_first_author_pubs
        
        author['total_publications'] = len(all_publications)
        author['total_first_author_pubs'] = len(first_author_pubs)
        author['total_non_first_author_pubs'] = len(non_first_author_pubs)
        
        author['publication_titles'] = publication_titles
        author['publication_years'] = publication_years
        author['publication_dois'] = publication_dois
        
        # Calculate total citations and downloads
        author['total_citations'] = sum(p.get('citation_count', 0) for p in all_publications)
        author['total_downloads'] = sum(p.get('download_count', 0) for p in all_publications)
        
        # Update abstracts
        author['abstracts'] = [p.get('abstract', '') for p in all_publications]
        
        total_pubs_added += len(all_publications)
        
        # Progress indicator
        if authors_with_pubs % 100 == 0:
            print(f"  Processed {authors_with_pubs:,} authors with publications...")
    
    # Update metadata
    metadata = complete_data['metadata']
    metadata['last_updated'] = datetime.now().isoformat()
    metadata['publications_added'] = True
    metadata['statistics']['with_publications'] = authors_with_pubs
    metadata['statistics']['total_publications'] = total_pubs_added
    metadata['statistics']['authors_without_publications'] = len(complete_authors) - authors_with_pubs
    
    # Add publication coverage to metadata
    metadata['coverage']['authors_with_publications'] = f"{authors_with_pubs}/{len(complete_authors)} ({authors_with_pubs/len(complete_authors)*100:.1f}%)"
    
    metadata['description'] = 'Complete dataset for remaining European authors with email addresses, affiliations, biographies, and ALL publications (first author and non-first author)'
    
    # Save updated file
    output_file = 'results/remaining_european_authors_complete_dataset.json'
    print("\n💾 Saving updated dataset...")
    with open(output_file, 'w') as f:
        json.dump(complete_data, f, indent=2)
    
    print("\n✅ PUBLICATIONS ADDED SUCCESSFULLY")
    print("=" * 70)
    print(f"Authors with publications: {authors_with_pubs:,}")
    print(f"Authors without publications: {len(complete_authors) - authors_with_pubs:,}")
    print(f"Total publications added: {total_pubs_added:,}")
    print(f"File size: {Path(output_file).stat().st_size / 1024 / 1024:.1f} MB")
    print(f"Output: {output_file}")
    print("=" * 70)
    
    # Show sample
    print("\n📋 Sample author with publications:")
    print("-" * 70)
    for author_id, author in complete_authors.items():
        if author.get('total_publications', 0) > 0:
            print(f"Name: {author['name']}")
            print(f"Total publications: {author['total_publications']}")
            print(f"  - As first author: {author['total_first_author_pubs']}")
            print(f"  - As non-first author: {author['total_non_first_author_pubs']}")
            if author.get('all_publications'):
                sample_pub = author['all_publications'][0]
                title = sample_pub.get('title') or 'No title'
                print(f"\nSample publication:")
                print(f"  Title: {title[:70]}...")
                print(f"  Year: {sample_pub.get('year', 'N/A')}")
                print(f"  First author: {sample_pub.get('first_author', False)}")
                print(f"  Author position: {sample_pub.get('author_position', 'N/A')}/{sample_pub.get('total_authors', 'N/A')}")
                print(f"  Citations: {sample_pub.get('citation_count', 0)}")
            break
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()

