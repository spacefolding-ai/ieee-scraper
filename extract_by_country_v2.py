#!/usr/bin/env python3
"""
Extract authors by country from the CLEANED European dataset.
Version 2: Works with the properly cleaned dataset.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# European countries to extract
EUROPEAN_COUNTRIES = {
    'Albania': ['Albania', 'Tirana'],
    'Armenia': ['Armenia', 'Yerevan'],
    'Austria': ['Austria', 'Vienna', 'Graz', 'Linz', 'Salzburg', 'Innsbruck'],
    'Belarus': ['Belarus', 'Minsk'],
    'Belgium': ['Belgium', 'Brussels', 'Antwerp', 'Ghent', 'Leuven', 'Liège'],
    'Bosnia and Herzegovina': ['Bosnia', 'Herzegovina', 'Sarajevo', 'Banja Luka'],
    'Bulgaria': ['Bulgaria', 'Sofia', 'Plovdiv', 'Varna'],
    'Croatia': ['Croatia', 'Zagreb', 'Split', 'Rijeka'],
    'Cyprus': ['Cyprus', 'Nicosia', 'Limassol'],
    'Czech Republic': ['Czech Republic', 'Czechia', 'Prague', 'Brno', 'Ostrava'],
    'Denmark': ['Denmark', 'Copenhagen', 'Aarhus', 'Odense', 'Aalborg'],
    'Estonia': ['Estonia', 'Tallinn', 'Tartu'],
    'Finland': ['Finland', 'Helsinki', 'Espoo', 'Tampere', 'Turku', 'Oulu'],
    'Georgia': ['Georgia', 'Tbilisi'],
    'Germany': ['Germany', 'Berlin', 'Munich', 'Hamburg', 'Frankfurt', 'Cologne', 'Stuttgart', 
                'Düsseldorf', 'Dortmund', 'Essen', 'Leipzig', 'Bremen', 'Dresden', 'Hannover',
                'Nuremberg', 'Duisburg', 'Bochum', 'Wuppertal', 'Bielefeld', 'Bonn', 'Münster',
                'Karlsruhe', 'Mannheim', 'Augsburg', 'Wiesbaden', 'Mönchengladbach', 'Gelsenkirchen',
                'Aachen', 'Braunschweig', 'Chemnitz', 'Kiel', 'Magdeburg', 'Freiburg', 'Lübeck',
                'Erfurt', 'Oberhausen', 'Rostock', 'Kassel', 'Hagen', 'Potsdam', 'Saarbrücken',
                'Hamm', 'Ludwigshafen', 'Oldenburg', 'Osnabrück', 'Leverkusen', 'Solingen', 'Heidelberg',
                'Darmstadt', 'Paderborn', 'Regensburg', 'Würzburg', 'Ingolstadt', 'Ulm', 'Heilbronn',
                'Pforzheim', 'Wolfsburg', 'Göttingen', 'Reutlingen', 'Koblenz', 'Erlangen', 'Siegen'],
    'Greece': ['Greece', 'Athens', 'Thessaloniki', 'Patras', 'Heraklion', 'Larissa'],
    'Hungary': ['Hungary', 'Budapest', 'Debrecen', 'Szeged', 'Miskolc', 'Pécs'],
    'Iceland': ['Iceland', 'Reykjavik'],
    'Ireland': ['Ireland', 'Dublin', 'Cork', 'Limerick', 'Galway'],
    'Italy': ['Italy', 'Rome', 'Milan', 'Naples', 'Turin', 'Palermo', 'Genoa', 'Bologna',
              'Florence', 'Bari', 'Catania', 'Venice', 'Verona', 'Messina', 'Padua', 'Trieste',
              'Brescia', 'Prato', 'Parma', 'Modena', 'Reggio Calabria', 'Reggio Emilia', 'Perugia',
              'Ravenna', 'Livorno', 'Cagliari', 'Foggia', 'Rimini', 'Salerno', 'Ferrara', 'Sassari',
              'Monza', 'Latina', 'Giugliano', 'Bergamo', 'Forlì', 'Trento', 'Vicenza', 'Treviso',
              'Pisa', 'Bolzano', 'Ancona', 'Udine', 'Arezzo', 'Cesena', 'Lecce', 'Pesaro', 'Pavia',
              'Milano', 'Torino', 'Firenze', 'Venezia', 'Napoli', 'Genova', 'Pordenone'],
    'Kosovo': ['Kosovo', 'Pristina'],
    'Latvia': ['Latvia', 'Riga', 'Daugavpils', 'Liepāja'],
    'Lithuania': ['Lithuania', 'Vilnius', 'Kaunas', 'Klaipėda'],
    'Luxembourg': ['Luxembourg'],
    'Malta': ['Malta', 'Valletta'],
    'Moldova': ['Moldova', 'Chișinău'],
    'Montenegro': ['Montenegro', 'Podgorica'],
    'Netherlands': ['Netherlands', 'Amsterdam', 'Rotterdam', 'The Hague', 'Utrecht', 'Eindhoven',
                     'Tilburg', 'Groningen', 'Almere', 'Breda', 'Nijmegen', 'Enschede', 'Apeldoorn',
                     'Haarlem', 'Arnhem', 'Zaanstad', 'Haarlemmermeer', 'Delft', 'Leiden', 'Maastricht'],
    'North Macedonia': ['North Macedonia', 'Macedonia', 'Skopje'],
    'Norway': ['Norway', 'Oslo', 'Bergen', 'Trondheim', 'Stavanger', 'Drammen', 'Tromsø'],
    'Poland': ['Poland', 'Warsaw', 'Kraków', 'Łódź', 'Wrocław', 'Poznań', 'Gdańsk', 'Szczecin',
               'Bydgoszcz', 'Lublin', 'Katowice', 'Białystok', 'Gdynia', 'Częstochowa', 'Radom',
               'Sosnowiec', 'Toruń', 'Kielce', 'Gliwice', 'Zabrze', 'Bytom', 'Olsztyn', 'Rzeszów',
               'Bielsko-Biała', 'Ruda Śląska', 'Rybnik', 'Tychy', 'Gorzów Wielkopolski', 'Dąbrowa Górnicza'],
    'Portugal': ['Portugal', 'Lisbon', 'Porto', 'Braga', 'Coimbra', 'Funchal', 'Lisboa'],
    'Romania': ['Romania', 'Bucharest', 'Cluj-Napoca', 'Timișoara', 'Iași', 'Constanța', 'Craiova', 'Brașov'],
    'Serbia': ['Serbia', 'Belgrade', 'Novi Sad', 'Niš'],
    'Slovakia': ['Slovakia', 'Bratislava', 'Košice'],
    'Slovenia': ['Slovenia', 'Ljubljana', 'Maribor'],
    'Spain': ['Spain', 'Madrid', 'Barcelona', 'Valencia', 'Seville', 'Zaragoza', 'Málaga', 'Murcia',
              'Palma', 'Las Palmas', 'Bilbao', 'Alicante', 'Córdoba', 'Valladolid', 'Vigo', 'Gijón',
              'Hospitalet', "L'Hospitalet", 'Vitoria', 'A Coruña', 'Granada', 'Elche', 'Oviedo', 'Badalona',
              'Cartagena', 'Terrassa', 'Jerez', 'Sabadell', 'Móstoles', 'Santa Cruz', 'Pamplona',
              'Almería', 'Fuenlabrada', 'Leganés', 'Donostia', 'San Sebastián', 'Burgos', 'Santander',
              'Castellón', 'Alcalá', 'Getafe', 'Salamanca', 'Logroño', 'Badajoz', 'Huelva', 'Tarragona',
              'Lleida', 'Marbella', 'León', 'Cadiz', 'Dos Hermanas', 'Alcorcón', 'Sevilla'],
    'Sweden': ['Sweden', 'Stockholm', 'Gothenburg', 'Göteborg', 'Malmö', 'Uppsala', 'Linköping', 'Örebro', 'Västerås', 'Lund'],
    'Switzerland': ['Switzerland', 'Zürich', 'Geneva', 'Basel', 'Lausanne', 'Bern', 'Winterthur', 'Lucerne', 'St. Gallen'],
    'Turkey': ['Turkey', 'Istanbul', 'Ankara', 'Izmir', 'Bursa', 'Adana', 'Gaziantep', 'Konya'],
    'Ukraine': ['Ukraine', 'Kyiv', 'Kiev', 'Kharkiv', 'Odessa', 'Dnipro', 'Donetsk', 'Zaporizhzhia', 'Lviv'],
    'United Kingdom': ['United Kingdom', 'UK', 'U.K.', 'England', 'Scotland', 'Wales', 'Northern Ireland',
                       'London', 'Birmingham', 'Manchester', 'Glasgow', 'Liverpool', 'Leeds', 'Sheffield',
                       'Edinburgh', 'Bristol', 'Cardiff', 'Belfast', 'Newcastle', 'Nottingham', 'Southampton',
                       'Leicester', 'Coventry', 'Bradford', 'Hull', 'Wolverhampton', 'Plymouth', 'Stoke',
                       'Derby', 'Swansea', 'Reading', 'Northampton', 'Luton', 'Portsmouth', 'Preston',
                       'Aberdeen', 'Milton Keynes', 'Sunderland', 'Norwich', 'Dudley', 'Cambridge',
                       'Oxford', 'Brighton', 'Bournemouth', 'Swindon', 'Warrington', 'Huddersfield',
                       'Poole', 'York', 'Peterborough', 'Lancaster', 'Exeter', 'Bath', 'Canterbury',
                       'Guildford', 'Loughborough', 'Cranfield', 'Surrey', 'Imperial', 'Strathclyde']
}

def extract_country(affiliation):
    """Extract country from affiliation string"""
    if not affiliation:
        return 'Unknown'
    
    aff_lower = affiliation.lower()
    
    # Check each country and its cities
    for country, patterns in EUROPEAN_COUNTRIES.items():
        for pattern in patterns:
            # Use word boundaries for more accurate matching
            if re.search(r'\b' + re.escape(pattern.lower()) + r'\b', aff_lower):
                return country
    
    return 'Unknown'

def main():
    input_path = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/european_authors_with_emails_academic_only_cleaned.json')
    output_dir = Path('/Users/miroslavjugovic/Projects/ieee-scraper/results/by_country')
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    print("="*80)
    print("Extracting Authors by Country (from CLEANED dataset)")
    print("="*80)
    
    # Load data
    print(f"\nLoading: {input_path}")
    with open(input_path, 'r') as f:
        data = json.load(f)
    
    total_authors = len(data['authors'])
    print(f"Total authors: {total_authors}")
    
    # Group authors by country
    authors_by_country = defaultdict(dict)
    country_stats = defaultdict(int)
    
    print("\nExtracting countries from affiliations...")
    for author_id, author_data in data['authors'].items():
        primary_aff = author_data.get('primary_affiliation', '')
        country = extract_country(primary_aff)
        
        authors_by_country[country][author_id] = author_data
        country_stats[country] += 1
    
    # Save each country to a separate file
    print(f"\nSaving {len(authors_by_country)} country files...")
    
    for country, authors in authors_by_country.items():
        # Create metadata
        country_data = {
            'metadata': {
                'dataset_name': f'European Authors - {country}',
                'description': f'Academic authors from {country} with institutional emails',
                'created_date': datetime.now().isoformat(),
                'source': 'european_authors_with_emails_academic_only_cleaned.json',
                'country': country,
                'total_authors': len(authors),
                'filters_applied': [
                    'European affiliations only',
                    'Institutional emails only',
                    'No HubSpot duplicates',
                    'No commercial domains',
                    'No non-European primary affiliations',
                    f'Country: {country}'
                ],
                'notes': []
            },
            'authors': authors
        }
        
        # Save to file
        safe_country = country.replace(' ', '_').replace('/', '_')
        output_file = output_dir / f'european_authors_{safe_country.lower()}.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(country_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {country}: {len(authors)} authors → {output_file.name}")
    
    # Create DACH combined file (Germany + Austria + Switzerland)
    print(f"\nCreating DACH combined file...")
    dach_authors = {}
    dach_stats = {}
    
    for country in ['Germany', 'Austria', 'Switzerland']:
        if country in authors_by_country:
            dach_authors.update(authors_by_country[country])
            dach_stats[country] = len(authors_by_country[country])
    
    if dach_authors:
        dach_data = {
            'metadata': {
                'dataset_name': 'European Authors - DACH',
                'description': 'Academic authors from DACH region (Germany, Austria, Switzerland) with institutional emails',
                'created_date': datetime.now().isoformat(),
                'source': 'european_authors_with_emails_academic_only_cleaned.json',
                'region': 'DACH',
                'total_authors': len(dach_authors),
                'filters_applied': [
                    'European affiliations only',
                    'Institutional emails only',
                    'No HubSpot duplicates',
                    'No commercial domains',
                    'No non-European primary affiliations',
                    'Region: DACH (Germany, Austria, Switzerland)'
                ],
                'breakdown': dach_stats,
                'notes': [
                    'DACH = Deutschland (Germany), Austria, Confoederatio Helvetica (Switzerland)'
                ]
            },
            'authors': dach_authors
        }
        
        dach_file = output_dir / 'european_authors_dach.json'
        with open(dach_file, 'w', encoding='utf-8') as f:
            json.dump(dach_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ DACH: {len(dach_authors)} authors → {dach_file.name}")
        for country, count in dach_stats.items():
            print(f"      - {country}: {count} authors")
    else:
        print(f"  ⚠ No DACH countries found in dataset")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY BY COUNTRY")
    print(f"{'='*80}")
    
    # Sort by count (descending)
    sorted_stats = sorted(country_stats.items(), key=lambda x: x[1], reverse=True)
    
    total_classified = sum(count for country, count in sorted_stats if country != 'Unknown')
    unknown_count = country_stats.get('Unknown', 0)
    
    print(f"\nTop 20 Countries:")
    for i, (country, count) in enumerate(sorted_stats[:20], 1):
        percentage = (count / total_authors) * 100
        emoji = "⭐" if country in ['Germany', 'United Kingdom', 'Italy'] else "  "
        print(f"{emoji} {i:2d}. {country:20s}: {count:4d} authors ({percentage:5.2f}%)")
    
    if len(sorted_stats) > 20:
        print(f"\n... and {len(sorted_stats) - 20} more countries")
    
    print(f"\n{'='*80}")
    print(f"Total classified:  {total_classified} authors ({(total_classified/total_authors)*100:.1f}%)")
    print(f"Unknown:           {unknown_count} authors ({(unknown_count/total_authors)*100:.1f}%)")
    print(f"Total:             {total_authors} authors")
    print(f"{'='*80}")
    
    # Note about Unknown category
    if unknown_count > 0:
        print(f"\nNote: The 'Unknown' category now contains only {unknown_count} authors")
        print("      (down from 52 before cleaning, which included non-European authors)")
    
    print("\n✓ Extraction completed successfully!")
    print(f"  Files saved to: {output_dir}/")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()

