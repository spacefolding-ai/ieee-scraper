"""
Data Aggregator Module
Aggregates and deduplicates author data from multiple publications.
"""

import logging
from collections import defaultdict


logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregate and deduplicate author data."""
    
    def __init__(self):
        """Initialize the data aggregator."""
        self.authors_map = {}  # Maps author identifiers to author data
        self.name_to_id = {}   # Maps normalized names to author IDs
    
    def add_author(self, author_details, publication_doi):
        """
        Add an author and their publication to the aggregated data.
        
        Args:
            author_details (dict): Author information
            publication_doi (str): DOI or URL of the publication
        """
        # Create a unique identifier for the author
        author_id = self._get_author_identifier(author_details)
        
        if author_id in self.authors_map:
            # Author already exists, add publication
            existing_author = self.authors_map[author_id]
            
            # Add publication if not already present
            if publication_doi and publication_doi not in existing_author['Publications']:
                existing_author['Publications'].append(publication_doi)
            
            # Update missing fields with new data
            self._merge_author_data(existing_author, author_details)
            
        else:
            # New author, create entry
            author_entry = {
                'Full_name': author_details.get('full_name', ''),
                'Email': author_details.get('email', ''),
                'Title': author_details.get('title', ''),
                'Role': author_details.get('role', ''),
                'Field_of_study': author_details.get('field_of_study', ''),
                'university': author_details.get('university', ''),
                'research_institution': author_details.get('research_institution', ''),
                'city': author_details.get('city', ''),
                'country': author_details.get('country', ''),
                'publication_topics': author_details.get('publication_topics', []),
                'biography': author_details.get('biography', ''),
                'publication_count': author_details.get('publication_count', None),
                'author_publications': author_details.get('author_publications', []),
                'profile_url': author_details.get('profile_url', ''),
                'Publications': [publication_doi] if publication_doi else []
            }
            
            self.authors_map[author_id] = author_entry
            
            # Map normalized name to ID
            normalized_name = self._normalize_name(author_details.get('full_name', ''))
            if normalized_name:
                self.name_to_id[normalized_name] = author_id
        
        logger.debug(f"Added/updated author: {author_details.get('full_name')}")
    
    def _get_author_identifier(self, author_details):
        """
        Create a unique identifier for an author.
        
        Args:
            author_details (dict): Author information
            
        Returns:
            str: Unique identifier
        """
        # Use author ID from IEEE if available
        if author_details.get('author_id'):
            return f"ieee_{author_details['author_id']}"
        
        # Otherwise use normalized name + affiliation
        name = self._normalize_name(author_details.get('full_name', ''))
        affiliation = author_details.get('affiliation_raw', '')
        
        # Create a simple hash-like identifier
        identifier = f"{name}_{affiliation[:50]}"
        
        # Check if this name already exists with similar affiliation
        normalized_name = self._normalize_name(author_details.get('full_name', ''))
        if normalized_name in self.name_to_id:
            existing_id = self.name_to_id[normalized_name]
            existing_author = self.authors_map.get(existing_id)
            
            if existing_author and self._are_same_author(existing_author, author_details):
                return existing_id
        
        return identifier
    
    def _normalize_name(self, name):
        """
        Normalize author name for comparison.
        
        Args:
            name (str): Author name
            
        Returns:
            str: Normalized name
        """
        if not name:
            return ''
        
        # Convert to lowercase, remove extra spaces, remove punctuation
        normalized = name.lower()
        normalized = normalized.replace('.', '').replace(',', '')
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _are_same_author(self, author1, author2):
        """
        Check if two author records refer to the same person.
        
        Args:
            author1 (dict): First author data
            author2 (dict): Second author data
            
        Returns:
            bool: True if likely the same author
        """
        name1 = self._normalize_name(author1.get('Full_name', ''))
        name2 = self._normalize_name(author2.get('full_name', ''))
        
        # Names must match
        if name1 != name2:
            return False
        
        # If both have emails and they match, definitely same author
        email1 = author1.get('Email', '')
        email2 = author2.get('email', '')
        if email1 and email2 and email1 == email2:
            return True
        
        # If affiliations are similar, likely same author
        affil1 = author1.get('university', '') or author1.get('research_institution', '')
        affil2 = author2.get('university', '') or author2.get('research_institution', '')
        
        if affil1 and affil2:
            # Simple similarity check
            affil1_norm = affil1.lower()
            affil2_norm = affil2.lower()
            
            if affil1_norm in affil2_norm or affil2_norm in affil1_norm:
                return True
        
        # Default to treating as same author if name matches
        return True
    
    def _merge_author_data(self, existing, new_data):
        """
        Merge new author data into existing record, filling in missing fields.
        
        Args:
            existing (dict): Existing author data (modified in place)
            new_data (dict): New author data to merge
        """
        # Update empty fields with new data
        if not existing.get('Email') and new_data.get('email'):
            existing['Email'] = new_data['email']
        
        if not existing.get('Title') and new_data.get('title'):
            existing['Title'] = new_data['title']
        
        if not existing.get('Role') and new_data.get('role'):
            existing['Role'] = new_data['role']
        
        if not existing.get('Field_of_study') and new_data.get('field_of_study'):
            existing['Field_of_study'] = new_data['field_of_study']
        
        if not existing.get('university') and new_data.get('university'):
            existing['university'] = new_data['university']
        
        if not existing.get('research_institution') and new_data.get('research_institution'):
            existing['research_institution'] = new_data['research_institution']
        
        if not existing.get('city') and new_data.get('city'):
            existing['city'] = new_data['city']
        
        if not existing.get('country') and new_data.get('country'):
            existing['country'] = new_data['country']
        
        if not existing.get('biography') and new_data.get('biography'):
            existing['biography'] = new_data['biography']
        
        if not existing.get('publication_count') and new_data.get('publication_count'):
            existing['publication_count'] = new_data['publication_count']
        
        if not existing.get('profile_url') and new_data.get('profile_url'):
            existing['profile_url'] = new_data['profile_url']
        
        # Merge publication topics (combine unique topics)
        if new_data.get('publication_topics'):
            existing_topics = existing.get('publication_topics', [])
            for topic in new_data['publication_topics']:
                if topic not in existing_topics:
                    existing_topics.append(topic)
            existing['publication_topics'] = existing_topics
        
        # Merge author publications (combine unique publications)
        if new_data.get('author_publications'):
            existing_pubs = existing.get('author_publications', [])
            for pub in new_data['author_publications']:
                # Check if not already in list (by URL)
                if not any(p.get('url') == pub.get('url') for p in existing_pubs):
                    existing_pubs.append(pub)
            existing['author_publications'] = existing_pubs
    
    def get_aggregated_authors(self):
        """
        Get the final aggregated list of authors.
        
        Returns:
            list: List of author dictionaries
        """
        authors_list = list(self.authors_map.values())
        
        # Sort by number of publications (descending) and then by name
        authors_list.sort(
            key=lambda x: (-len(x.get('Publications', [])), x.get('Full_name', ''))
        )
        
        logger.info(f"Aggregated {len(authors_list)} unique authors")
        
        return authors_list
    
    def get_statistics(self):
        """
        Get statistics about the aggregated data.
        
        Returns:
            dict: Statistics
        """
        total_authors = len(self.authors_map)
        authors_with_email = sum(1 for a in self.authors_map.values() if a.get('Email'))
        authors_with_university = sum(1 for a in self.authors_map.values() 
                                     if a.get('university') or a.get('research_institution'))
        
        total_publications = sum(len(a.get('Publications', [])) 
                               for a in self.authors_map.values())
        
        return {
            'total_authors': total_authors,
            'authors_with_email': authors_with_email,
            'authors_with_university': authors_with_university,
            'total_publications': total_publications,
            'email_coverage': f"{(authors_with_email/total_authors*100):.1f}%" if total_authors > 0 else "0%"
        }

