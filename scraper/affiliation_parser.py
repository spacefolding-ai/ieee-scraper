"""
Affiliation Parser Module

Parses author affiliation strings to extract:
- Country information
- Institution name
- Determines if European (excluding France)
- Determines if research institution
"""

import re
import logging

try:
    import pycountry
    PYCOUNTRY_AVAILABLE = True
except ImportError:
    PYCOUNTRY_AVAILABLE = False
    logging.warning("pycountry not available. Country detection may be limited.")

logger = logging.getLogger(__name__)


class AffiliationParser:
    """Parse and validate author affiliations."""
    
    # Default European countries (excluding France) - can be overridden by config
    DEFAULT_EUROPEAN_COUNTRIES = [
        "Albania", "Armenia", "Austria", "Belarus", "Belgium", "Bosnia and Herzegovina",
        "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Czechia", "Denmark",
        "Estonia", "Finland", "Georgia", "Germany", "Greece", "Hungary",
        "Iceland", "Ireland", "Italy", "Kosovo", "Latvia", "Lithuania",
        "Luxembourg", "Malta", "Moldova", "Montenegro", "Netherlands",
        "North Macedonia", "Norway", "Poland", "Portugal", "Romania",
        "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland",
        "Turkey", "Ukraine", "United Kingdom"
    ]
    
    # Common country name variations
    COUNTRY_VARIATIONS = {
        "UK": "United Kingdom",
        "Czech Republic": "Czech Republic",
        "Czechia": "Czech Republic",
        "Holland": "Netherlands"
    }
    
    # Keywords that indicate research institutions (including industrial R&D labs)
    RESEARCH_KEYWORDS = [
        # Universities and colleges
        "university", "universit", "college", "academy",
        "technical university", "applied science",
        "polytechnic", "hochschule", "universidad", "università",
        "school of", "faculty of", "department of",
        # Common university abbreviations
        "eth", "tu ", "tum", "tu-", "tu/", "mit", "epfl", "rwth",
        # Research institutions
        "institute", "institut", "research center", "research centre",
        "research institute", "research facility", "research lab",
        "laboratory", "lab", "labs", "laborator",
        # Industrial R&D
        "r&d", "research and development",
        "technology center", "innovation center", "innovation lab",
        "engineering center", "development center",
        "testing center", "simulation center",
        # Technology companies with R&D
        "systems", "technologies", "solutions",
        "hil", "hardware-in-loop", "hardware in loop"
    ]
    
    def __init__(self, config=None):
        """
        Initialize affiliation parser.
        
        Args:
            config (dict, optional): Configuration dictionary with country list
        """
        # Load European countries from config or use default
        if config and 'european_countries_exclude_france' in config:
            self.EUROPEAN_COUNTRIES = config['european_countries_exclude_france']
        else:
            self.EUROPEAN_COUNTRIES = self.DEFAULT_EUROPEAN_COUNTRIES
    
    def parse_affiliation(self, affiliation_string):
        """
        Parse affiliation string and extract relevant information.
        
        Args:
            affiliation_string (str): Raw affiliation text
            
        Returns:
            dict: Parsed affiliation data with keys:
                - country: str or None
                - institution: str or None
                - is_european: bool
                - is_research_institution: bool
        """
        result = {
            'country': None,
            'institution': None,
            'is_european': False,
            'is_research_institution': False
        }
        
        if not affiliation_string:
            return result
        
        # Extract country
        country = self._extract_country(affiliation_string)
        result['country'] = country
        
        # Check if European
        if country:
            result['is_european'] = self.is_european_country(country)
        
        # Extract institution name
        institution = self._extract_institution(affiliation_string)
        result['institution'] = institution
        
        # Check if research institution
        result['is_research_institution'] = self._is_research_institution(affiliation_string)
        
        return result
    
    def is_european_affiliation(self, affiliation_string, country=None):
        """
        Check if affiliation is from a European country (excluding France).
        
        Args:
            affiliation_string (str): Affiliation text
            country (str, optional): Pre-extracted country name
            
        Returns:
            bool: True if European (excluding France)
        """
        if not country:
            country = self._extract_country(affiliation_string)
        
        if not country:
            return False
        
        return self.is_european_country(country)
    
    def is_european_country(self, country_name):
        """
        Check if a country is European (excluding France).
        
        Args:
            country_name (str): Country name
            
        Returns:
            bool: True if European (excluding France)
        """
        if not country_name:
            return False
        
        # Normalize country name
        country_normalized = self.COUNTRY_VARIATIONS.get(country_name, country_name)
        
        # Check against European countries list
        for euro_country in self.EUROPEAN_COUNTRIES:
            if euro_country.lower() == country_normalized.lower():
                return True
            if euro_country.lower() in country_normalized.lower():
                return True
        
        return False
    
    def _extract_country(self, affiliation_string):
        """
        Extract country name from affiliation string.
        Country is typically at the END of the affiliation string.
        
        Args:
            affiliation_string (str): Affiliation text
            
        Returns:
            str or None: Country name if found
        """
        if not affiliation_string:
            return None
        
        affiliation_lower = affiliation_string.lower()
        
        # Split by common delimiters (country is usually last part after comma)
        parts = re.split(r'[,;]', affiliation_string)
        
        # Check the LAST part first (most likely to contain country)
        if parts:
            last_part = parts[-1].strip()
            
            # Direct match with European countries
            for country in self.EUROPEAN_COUNTRIES:
                if country.lower() == last_part.lower() or country.lower() in last_part.lower():
                    # Normalize country name
                    return self.COUNTRY_VARIATIONS.get(country, country)
            
            # Try pycountry for the last part
            if PYCOUNTRY_AVAILABLE:
                try:
                    country_obj = pycountry.countries.search_fuzzy(last_part)
                    if country_obj:
                        country_name = country_obj[0].name
                        # Check if it's European
                        for euro_country in self.EUROPEAN_COUNTRIES:
                            if euro_country.lower() in country_name.lower() or country_name.lower() in euro_country.lower():
                                return self.COUNTRY_VARIATIONS.get(euro_country, euro_country)
                except (LookupError, AttributeError):
                    pass
        
        # Fallback: check all parts from end to beginning
        for part in reversed(parts):
            part = part.strip()
            
            # Try matching European countries
            for country in self.EUROPEAN_COUNTRIES:
                if country.lower() == part.lower():
                    return self.COUNTRY_VARIATIONS.get(country, country)
            
            # Try pycountry
            if PYCOUNTRY_AVAILABLE:
                try:
                    country_obj = pycountry.countries.search_fuzzy(part)
                    if country_obj:
                        country_name = country_obj[0].name
                        for euro_country in self.EUROPEAN_COUNTRIES:
                            if euro_country.lower() in country_name.lower():
                                return self.COUNTRY_VARIATIONS.get(euro_country, euro_country)
                except (LookupError, AttributeError):
                    continue
        
        return None
    
    def _extract_institution(self, affiliation_string):
        """
        Extract institution name from affiliation string.
        
        Args:
            affiliation_string (str): Affiliation text
            
        Returns:
            str or None: Institution name
        """
        if not affiliation_string:
            return None
        
        # Split by comma and get the first substantial part
        parts = [p.strip() for p in affiliation_string.split(',')]
        
        # Look for parts containing institution keywords
        for part in parts:
            if any(keyword in part.lower() for keyword in self.RESEARCH_KEYWORDS):
                return part
        
        # If no keyword found, return first part (likely institution name)
        if parts:
            return parts[0]
        
        return None
    
    def _is_research_institution(self, affiliation_string):
        """
        Check if affiliation represents a research institution.
        
        Args:
            affiliation_string (str): Affiliation text
            
        Returns:
            bool: True if research institution
        """
        if not affiliation_string:
            return False
        
        affiliation_lower = affiliation_string.lower()
        
        # Check for research keywords
        for keyword in self.RESEARCH_KEYWORDS:
            if keyword in affiliation_lower:
                return True
        
        return False

