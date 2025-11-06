"""
Author Extractor Module

Extracts and enriches author details from publication data.
Parses titles, roles, fields of study, and contact information.
"""

import re
import logging

logger = logging.getLogger(__name__)


class AuthorExtractor:
    """Extract detailed author information."""
    
    # Common academic titles
    TITLES = [
        'Prof.', 'Dr.', 'Ph.D.', 'M.Sc.', 'B.Sc.', 'Dipl.-Ing.', 'Dr.-Ing.',
        'Professor', 'Dr. rer. nat.', 'Dr. phil.', 'Ir.', 'Eng.'
    ]
    
    # Role keywords
    ROLE_KEYWORDS = {
        'professor': 'Professor',
        'lecturer': 'Lecturer',
        'researcher': 'Researcher',
        'scientist': 'Scientist',
        'engineer': 'Engineer',
        'head': 'Department Head',
        'director': 'Director',
        'chair': 'Chair',
        'dean': 'Dean'
    }
    
    def __init__(self, config):
        """
        Initialize author extractor.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
    
    def extract_author_details(self, author_data, ieee_profile_data=None):
        """
        Extract detailed author information.
        
        Args:
            author_data (dict): Basic author data from publication
            ieee_profile_data (dict): Data from IEEE profile (if available)
        
        Returns:
            dict: Enhanced author information
        """
        details = {
            'full_name': author_data.get('name', ''),
            'email': None,
            'title': None,
            'role': None,
            'field_of_study': None,
            'university': None,
            'research_institution': None,
            'city': None,
            'country': None,
            'affiliation_raw': author_data.get('affiliation', ''),
            'profile_url': author_data.get('profile_url', ''),
            'author_id': author_data.get('author_id', ''),
            'publication_topics': [],
            'biography': None,
            'publication_count': None,
            'author_publications': []
        }
        
        # Extract title from name
        details['title'] = self._extract_title(details['full_name'])
        
        # Clean name (remove title)
        details['full_name'] = self._clean_name(details['full_name'])
        
        # Extract from IEEE profile data (from author profile page)
        if ieee_profile_data:
            # Email
            if ieee_profile_data.get('email'):
                details['email'] = ieee_profile_data['email']
            
            # Affiliation from profile (usually more complete with city, country)
            if ieee_profile_data.get('affiliation'):
                details['affiliation_raw'] = ieee_profile_data['affiliation']
                # Parse city and country from affiliation
                city_country = self._extract_city_country(ieee_profile_data['affiliation'])
                if city_country:
                    details['city'] = city_country.get('city')
                    details['country'] = city_country.get('country')
            
            # Publication topics
            if ieee_profile_data.get('publication_topics'):
                details['publication_topics'] = ieee_profile_data['publication_topics']
                # Use topics to determine field of study if not set
                if not details.get('field_of_study') and details['publication_topics']:
                    field = self._extract_field_of_study(', '.join(details['publication_topics']))
                    if field:
                        details['field_of_study'] = field
            
            # Biography
            if ieee_profile_data.get('biography'):
                details['biography'] = ieee_profile_data['biography']
                # Try to extract role from bio
                if not details.get('role'):
                    role = self._extract_role(ieee_profile_data['biography'])
                    if role:
                        details['role'] = role
            
            # Publication count
            if ieee_profile_data.get('publication_count'):
                details['publication_count'] = ieee_profile_data['publication_count']
            
            # Author's publications
            if ieee_profile_data.get('author_publications'):
                details['author_publications'] = ieee_profile_data['author_publications']
        
        # Parse affiliation for university/research institution
        affiliation_to_parse = details.get('affiliation_raw') or author_data.get('affiliation', '')
        if affiliation_to_parse:
            institution_info = self._parse_institution_from_affiliation(affiliation_to_parse)
            details['university'] = institution_info.get('university')
            details['research_institution'] = institution_info.get('research_institution')
            
            # If city/country not yet extracted, try from affiliation
            if not details.get('city') or not details.get('country'):
                city_country = self._extract_city_country(affiliation_to_parse)
                if city_country:
                    if not details.get('city'):
                        details['city'] = city_country.get('city')
                    if not details.get('country'):
                        details['country'] = city_country.get('country')
        
        return details
    
    def _extract_title(self, name):
        """
        Extract academic title from name.
        
        Args:
            name (str): Full name with potential title
            
        Returns:
            str or None: Academic title
        """
        if not name:
            return None
        
        for title in self.TITLES:
            if title in name:
                return title
        
        # Check for common patterns
        title_pattern = r'\b(Prof\.|Dr\.|Ph\.D\.|M\.Sc\.|B\.Sc\.)\b'
        match = re.search(title_pattern, name)
        if match:
            return match.group(1)
        
        return None
    
    def _clean_name(self, name):
        """
        Remove title from name.
        
        Args:
            name (str): Full name with potential title
            
        Returns:
            str: Clean name
        """
        if not name:
            return name
        
        clean = name
        for title in self.TITLES:
            clean = clean.replace(title, '')
        
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        
        return clean.strip()
    
    def _extract_role(self, text):
        """
        Extract professional role from text (biography, etc.).
        
        Args:
            text (str): Text to search
            
        Returns:
            str or None: Role
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        for keyword, role in self.ROLE_KEYWORDS.items():
            if keyword in text_lower:
                return role
        
        return None
    
    def _extract_field_of_study(self, text):
        """
        Infer field of study from publication topics or other text.
        
        Args:
            text (str): Text containing topics/keywords
            
        Returns:
            str or None: Field of study
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Map keywords to fields
        field_keywords = {
            'Power Electronics': ['power electronics', 'converter', 'inverter', 'rectifier', 'igbt', 'mosfet'],
            'Electric Drives': ['motor', 'drive', 'electric machine', 'pmsm', 'bldc'],
            'Renewable Energy': ['solar', 'wind', 'renewable', 'photovoltaic', 'pv'],
            'Energy Storage': ['battery', 'energy storage', 'bms'],
            'Control Systems': ['control', 'automation', 'mpc', 'pid'],
            'Embedded Systems': ['embedded', 'real-time', 'hardware-in-the-loop', 'hil'],
            'Robotics': ['robot', 'mechatronic', 'automation']
        }
        
        for field, keywords in field_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return field
        
        return None
    
    def _parse_institution_from_affiliation(self, affiliation):
        """
        Parse institution name from affiliation string.
        
        Args:
            affiliation (str): Affiliation string
            
        Returns:
            dict: {'university': str, 'research_institution': str}
        """
        result = {
            'university': None,
            'research_institution': None
        }
        
        if not affiliation:
            return result
        
        affiliation_lower = affiliation.lower()
        
        # Check if it's a university
        if 'university' in affiliation_lower or 'universit' in affiliation_lower:
            # Extract the university name (usually first part before comma)
            parts = affiliation.split(',')
            result['university'] = parts[0].strip() if parts else affiliation
        
        # Check if it's a research institute
        elif any(keyword in affiliation_lower for keyword in ['institute', 'institut', 'laboratory', 'lab', 'center', 'centre']):
            parts = affiliation.split(',')
            result['research_institution'] = parts[0].strip() if parts else affiliation
        
        return result
    
    def _extract_city_country(self, affiliation):
        """
        Extract city and country from affiliation string.
        Format: "Institution, City, Country" or "Dept, Institution, City, Country"
        
        Args:
            affiliation (str): Affiliation string
            
        Returns:
            dict: {'city': str, 'country': str} or None
        """
        if not affiliation:
            return None
        
        # Split by comma
        parts = [p.strip() for p in affiliation.split(',')]
        
        if len(parts) < 2:
            return None
        
        result = {}
        
        # Country is typically the last part
        country = parts[-1].strip()
        if country:
            result['country'] = country
        
        # City is typically second-to-last
        if len(parts) >= 2:
            city = parts[-2].strip()
            # Validate it looks like a city (not too long, not institution-like)
            if city and len(city) < 50 and not any(keyword in city.lower() for keyword in
                                                   ['university', 'institute', 'college', 'department']):
                result['city'] = city
        
        return result if result else None

