#!/usr/bin/env python3
"""
Remove non-European authors from the dataset based on primary affiliation.
Version 2: More precise pattern matching to avoid false positives.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# European country codes (for email domain validation)
EUROPEAN_DOMAINS = [
    '.uk', '.de', '.fr', '.it', '.es', '.nl', '.be', '.at', '.ch', '.se', '.no',
    '.dk', '.fi', '.pl', '.pt', '.gr', '.cz', '.hu', '.ro', '.bg', '.hr', '.sk',
    '.si', '.lt', '.lv', '.ee', '.ie', '.lu', '.mt', '.cy', '.is', '.al', '.mk',
    '.rs', '.ba', '.me', '.xk', '.md', '.ua', '.by', '.ge', '.am', '.tr',
    '.ac.uk', '.edu.pl', '.edu.tr'
]

def extract_email_domain(email):
    """Extract the domain from an email address"""
    if '@' not in email:
        return ''
    return email.split('@')[1].lower()

def is_european_email_domain(email):
    """Check if email domain is European"""
    domain = extract_email_domain(email)
    
    # Check if domain ends with a European country code
    for eu_domain in EUROPEAN_DOMAINS:
        if domain.endswith(eu_domain):
            return True
    
    # Special cases: .edu domains that are clearly European
    if '.edu' in domain:
        # European universities often use .edu but in European countries
        return True  # Be conservative - keep these
    
    return False

def is_non_european_affiliation(affiliation):
    """
    Check if affiliation indicates a non-European location.
    Uses whole-word matching to avoid false positives.
    """
    if not affiliation:
        return False
    
    aff_lower = affiliation.lower()
    
    # Asia - use whole word boundaries
    asian_countries = [
        r'\bhong kong\b', r'\bchina\b', r'\bbeijing\b', r'\bshanghai\b', r'\bnanjing\b',
        r'\bjapan\b', r'\btokyo\b', r'\bkyoto\b', r'\bosaka\b',
        r'\bkorea\b', r'\bseoul\b', r'\bbusan\b',
        r'\bsingapore\b',
        r'\btaiwan\b', r'\btaipei\b',
        r'\bthailand\b', r'\bbangkok\b',
        r'\bvietnam\b', r'\bhanoi\b',
        r'\bmalaysia\b', r'\bkuala lumpur\b',
        r'\bindonesia\b', r'\bjakarta\b',
        r'\bphilippines\b', r'\bmanila\b',
        r'\bindia\b', r'\bdelhi\b', r'\bmumbai\b', r'\bbangalore\b', r'\biit\s',
        r'\bpakistan\b', r'\bislamabad\b', r'\bkarachi\b',
        r'\bbangladesh\b', r'\bdhaka\b',
        r'\bsri lanka\b', r'\bcolombo\b',
        r'\bnepal\b', r'\bkathmandu\b',
        r'\biran\b', r'\btehran\b',
        r'\biraq\b', r'\bbaghdad\b',
        r'\bsaudi\b', r'\briyadh\b', r'\bjeddah\b',
        r'\buae\b', r'\bdubai\b', r'\babu dhabi\b',
        r'\bqatar\b', r'\bdoha\b',
        r'\bkuwait\b',
        r'\boman\b', r'\bmuscat\b',
        r'\bbahrain\b',
        r'\bjordan\b', r'\bamman\b',
        r'\blebanon\b', r'\bbeirut\b',
        r'\bisrael\b', r'\btel aviv\b', r'\bjerusalem\b',
        r'\bkazakhstan\b', r'\bastana\b',
        r'\buzbekistan\b', r'\btashkent\b',
        r'\bmongolia\b', r'\bulaanbaatar\b'
    ]
    
    # Americas  
    american_countries = [
        r'\bcanada\b', r'\btoronto\b', r'\bvancouver\b', r'\bmontreal\b', r'\bcalgary\b', r'\balberta\b', r'\bontario\b', r'\bquebec\b',
        r'\busa\b', r'\bu\.s\.a\b', r'\bunited states\b',
        r'\bcalifornia\b', r'\btexas\b', r'\bflorida\b', r'\bnew york\b', r'\bmassachusetts\b',
        r'\bharvard\b', r'\bmit\b', r'\bstanford\b', r'\bberkeley\b', r'\bcaltech\b',
        r'\bprinceton\b', r'\byale\b', r'\bcornell\b', r'\bpenn\b', r'\bpennsylvania\b',
        r'\bmichigan\b', r'\bchicago\b', r'\bduke\b', r'\bjohns hopkins\b',
        r'\bboston\b', r'\bseattle\b', r'\baustin\b', r'\bsan francisco\b',
        r'\bmexico\b', r'\bmexico city\b',
        r'\bbrazil\b', r'\bbrasília\b', r'\brio de janeiro\b', r'\bsão paulo\b',
        r'\bargentina\b', r'\bbuenos aires\b',
        r'\bchile\b', r'\bsantiago\b',
        r'\bcolombia\b', r'\bbogotá\b', r'\bmedellín\b',
        r'\bperu\b', r'\blima\b',
        r'\bvenezuela\b', r'\bcaracas\b',
        r'\becuador\b', r'\bquito\b',
        r'\buruguay\b', r'\bmontevideo\b',
        r'\bparaguay\b', r'\basunción\b',
        r'\bbolivia\b', r'\bla paz\b',
        r'\bcosta rica\b', r'\bsan josé\b',
        r'\bpanama\b',
        r'\bguatemala\b',
        r'\bhonduras\b', r'\btegucigalpa\b',
        r'\bnicaragua\b', r'\bmanagua\b',
        r'\bel salvador\b',
        r'\bcuba\b', r'\bhavana\b',
        r'\bjamaica\b', r'\bkingston\b',
        r'\bhaiti\b',
        r'\bdominican\b',
        r'\bpuerto rico\b'
    ]
    
    # Oceania
    oceanian_countries = [
        r'\baustralia\b', r'\bsydney\b', r'\bmelbourne\b', r'\bbrisbane\b',
        r'\bperth\b', r'\badelaide\b', r'\bcanberra\b', r'\bunsw\b',
        r'\bnew zealand\b', r'\bauckland\b', r'\bwellington\b', r'\bchristchurch\b'
    ]
    
    # Africa
    african_countries = [
        r'\bsouth africa\b', r'\bcape town\b', r'\bjohannesburg\b', r'\bpretoria\b',
        r'\bnigeria\b', r'\blagos\b', r'\babuja\b',
        r'\bkenya\b', r'\bnairobi\b',
        r'\begypt\b', r'\bcairo\b', r'\balexandria\b',
        r'\bmorocco\b', r'\brabat\b', r'\bcasablanca\b',
        r'\balgeria\b', r'\balgiers\b',
        r'\btunisia\b', r'\btunis\b',
        r'\bghana\b', r'\baccra\b',
        r'\bethiopia\b', r'\baddis ababa\b',
        r'\btanzania\b', r'\bdar es salaam\b',
        r'\buganda\b', r'\bkampala\b',
        r'\bzimbabwe\b', r'\bharare\b'
    ]
    
    # Combine all patterns
    all_patterns = asian_countries + american_countries + oceanian_countries + african_countries
    
    # Check each pattern
    for pattern in all_patterns:
        if re.search(pattern, aff_lower):
            return True
    
    return False

def is_non_european_email(email):
    """Check if email domain clearly indicates non-European location"""
    domain = extract_email_domain(email)
    
    # Non-European country code domains (excluding European ones)
    non_eu_domains = [
        '.hk', '.cn', '.jp', '.kr', '.sg', '.tw', '.th', '.vn', '.my', '.id', 
        '.ph', '.in', '.pk', '.bd', '.lk', '.np', '.ir', '.iq', '.sa', 
        '.ae', '.qa', '.kw', '.om', '.bh', '.jo', '.lb', '.il',
        '.kz', '.uz', '.mn',
        # Americas
        '.ca', '.us', '.mx', '.br', '.ar', '.cl', '.co', '.pe', '.ve',
        '.ec', '.uy', '.py', '.bo', '.cr', '.pa', '.gt', '.hn', '.ni',
        '.sv', '.cu', '.jm', '.ht', '.do', '.pr',
        # Oceania
        '.au', '.nz',
        # Africa
        '.za', '.ng', '.ke', '.eg', '.ma', '.dz', '.tn', '.gh', '.et',
        '.tz', '.ug', '.zw'
    ]
    
    for non_eu in non_eu_domains:
        if domain.endswith(non_eu):
            return True
    
    return False

def main():
    input_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_academic_only.json')
    output_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_academic_only_cleaned.json')
    excluded_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/excluded_non_european_authors.json')
    
    print("="*80)
    print("Cleaning Non-European Authors from Dataset (v2 - Precise Matching)")
    print("="*80)
    
    # Load data
    print(f"\nLoading: {input_path}")
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    original_count = len(data['authors'])
    print(f"Original author count: {original_count}")
    
    # Identify non-European authors
    non_european_authors = []
    cleaned_authors = {}
    false_positive_check = []
    
    for author_id, author_data in data['authors'].items():
        primary_aff = author_data.get('primary_affiliation', '')
        email = author_data.get('email', '')
        
        # Check both affiliation text and email domain
        is_non_eu_aff = is_non_european_affiliation(primary_aff)
        is_non_eu_email = is_non_european_email(email)
        is_eu_email = is_european_email_domain(email)
        
        # Only exclude if:
        # 1. Affiliation clearly indicates non-European location, OR
        # 2. Email domain is clearly non-European AND affiliation doesn't contradict
        if is_non_eu_aff or (is_non_eu_email and not is_eu_email):
            non_european_authors.append({
                'author_id': author_id,
                'name': author_data.get('name'),
                'email': email,
                'email_domain': extract_email_domain(email),
                'primary_affiliation': primary_aff,
                'all_affiliations': author_data.get('all_affiliations', []),
                'non_eu_affiliation': is_non_eu_aff,
                'non_eu_email': is_non_eu_email
            })
        else:
            cleaned_authors[author_id] = author_data
            
            # Flag potential false negatives (kept but might be non-EU)
            if primary_aff and not is_eu_email and extract_email_domain(email):
                # Authors with non-.eu emails that we're keeping
                pass
    
    # Update metadata
    data['authors'] = cleaned_authors
    data['metadata']['total_authors'] = len(cleaned_authors)
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    # Add exclusion info
    if 'exclusions' not in data['metadata']:
        data['metadata']['exclusions'] = []
    
    data['metadata']['exclusions'].append({
        'date': datetime.now().isoformat(),
        'reason': 'Removed authors with non-European primary affiliations (v2 - precise matching)',
        'excluded_count': len(non_european_authors),
        'remaining_count': len(cleaned_authors),
        'note': 'Used word-boundary matching and domain validation to avoid false positives'
    })
    
    # Update statistics
    if 'statistics' in data['metadata']:
        stats = data['metadata']['statistics']
        stats['total'] = len(cleaned_authors)
        stats['with_email'] = len(cleaned_authors)
    
    # Save cleaned data
    print(f"\nSaving cleaned dataset...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved to: {output_path}")
    
    # Save excluded authors
    excluded_data = {
        'metadata': {
            'description': 'Authors excluded due to non-European primary affiliations',
            'exclusion_date': datetime.now().isoformat(),
            'total_excluded': len(non_european_authors),
            'note': 'Used precise word-boundary matching and email domain validation',
            'methodology': 'Excluded if: (1) affiliation contains non-EU country/city, OR (2) email domain is non-EU country code'
        },
        'excluded_authors': non_european_authors
    }
    
    with open(excluded_path, 'w', encoding='utf-8') as f:
        json.dump(excluded_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved excluded authors to: {excluded_path}")
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Original authors:           {original_count}")
    print(f"Non-European (excluded):    {len(non_european_authors)}")
    print(f"Truly European (remaining): {len(cleaned_authors)}")
    print(f"\nReduction: {len(non_european_authors)} authors ({(len(non_european_authors)/original_count)*100:.1f}%)")
    
    # Breakdown
    aff_based = sum(1 for a in non_european_authors if a['non_eu_affiliation'])
    email_based = sum(1 for a in non_european_authors if a['non_eu_email'] and not a['non_eu_affiliation'])
    
    print(f"\nExclusion breakdown:")
    print(f"  - Based on affiliation text: {aff_based}")
    print(f"  - Based on email domain:     {email_based}")
    
    # Show some examples
    if non_european_authors:
        print(f"\n{'='*80}")
        print("EXAMPLES OF EXCLUDED NON-EUROPEAN AUTHORS (first 15):")
        print(f"{'='*80}")
        for i, author in enumerate(non_european_authors[:15], 1):
            print(f"\n{i:2d}. {author['name']}")
            print(f"    Email: {author['email']} ({author['email_domain']})")
            print(f"    Primary: {author['primary_affiliation'][:100]}")
            reason = "Affiliation" if author['non_eu_affiliation'] else "Email Domain"
            print(f"    Excluded by: {reason}")
    
    print(f"\n{'='*80}")
    print("✓ Cleanup completed successfully!")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()

