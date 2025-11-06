# IEEE Xplore Author Scraper

A comprehensive Python scraper that extracts detailed author information from IEEE Xplore publications, focusing on European universities and research institutions (excluding France).

## 🎯 Features

### Publication Data Extraction
- **Title**, **URL**, **Year**, **Type** (Conference/Journal)
- **DOI** and DOI URL
- **Abstract** (full text)
- **Conference** or **Journal** name
- **Publisher** information

### Author Profile Extraction
- Full author details from IEEE profile pages
- **Affiliation** with city and country
- **Publication topics** and research interests
- **Biography**
- **Email** (when available)
- **Publication count**
- **List of author's publications** (up to 20 recent works)

### Smart Filtering
- European universities and research institutions only (excluding France)
- Automatic affiliation parsing and country detection
- Deduplication of authors across publications

### Pagination Support
- Collects publications from **all paginated pages**
- Shows total count before scraping
- User confirmation before starting detailed extraction

## 🚀 Quick Start

### Option 1: Double-Click Launch (macOS)
1. Double-click `run_scraper.command`
2. Choose test config (3 queries) or full config (50 queries)
3. Wait for publication collection
4. Review the count and confirm to proceed

### Option 2: Command Line

```bash
# Test run (3 queries, ~5 minutes)
python3 ieee_author_scraper.py --config config_test.json

# Full run (50 queries, ~2-3 hours)
python3 ieee_author_scraper.py --config config.json

# Skip confirmation prompt (automated runs)
python3 ieee_author_scraper.py --config config.json --no-confirm

# Only collect first page (faster testing)
python3 ieee_author_scraper.py --config config_test.json --single-page
```

## 📦 Installation

```bash
pip install -r requirements.txt
```

## 📊 Output Files

### 1. `results/publications_with_authors.json`
Publications grouped with their European authors:
```json
[
  {
    "publication": {
      "title": "Matrix Inverter: A Multilevel Inverter...",
      "url": "https://ieeexplore.ieee.org/document/9320121",
      "year": 2020,
      "type": "Conference Paper",
      "doi": "10.1109/EPEC48502.2020.9320121",
      "abstract": "This paper presents a novel...",
      "conference": "2019 IEEE PES Asia-Pacific Power and Energy..."
    },
    "authors": [
      {
        "Full_name": "Prof. Dr.-Ing. Martin Doppelbauer",
        "Email": "martin.doppelbauer@kit.edu",
        "Title": "Prof. Dr.-Ing.",
        "Role": "Professor",
        "Field_of_study": "Power Electronics",
        "university": "Karlsruhe Institute of Technology",
        "city": "Karlsruhe",
        "country": "Germany",
        "publication_topics": ["Power Electronics", "Electric Drives"],
        "biography": "Prof. Doppelbauer received his degree...",
        "author_publications": [
          {
            "title": "Design and Control of...",
            "url": "https://ieeexplore.ieee.org/document/...",
            "year": 2019
          }
        ]
      }
    ]
  }
]
```

### 2. `results/authors_output.json`
Unique authors aggregated across all publications with full details.

### 3. `results/ieee_scraper.log`
Detailed execution log.

## ⚙️ Command-Line Options

| Option | Description |
|--------|-------------|
| `--config`, `-c` | Path to configuration file (default: `config.json`) |
| `--output`, `-o` | Path to output JSON file (default: `results/authors_output.json`) |
| `--no-confirm` | Skip confirmation prompt before scraping |
| `--single-page` | Only collect first page of results (faster testing) |
| `--log-level` | Logging level: DEBUG, INFO, WARNING, ERROR |

## 🔧 Configuration

Edit `config.json` to customize:
- **search_queries**: Topics and search terms by category
- **max_results_per_query**: Maximum results per search query (default: 20)
- **delay_between_requests**: Delay in seconds between requests (default: 2)
- **european_countries_exclude_france**: List of European countries to include
- **research_institution_keywords**: Keywords to identify research institutions

## 🎓 Focus Areas

The scraper targets these research domains:
- Power Electronics & Power Systems
- Energy Systems & Renewable Energy
- Electric Drives & Motors
- Battery Systems & E-Mobility
- Control Systems & Automation
- Embedded Systems & Real-Time
- Mechatronics & Robotics

## 📝 How It Works

### Stage 1: Collection (with pagination)
1. Execute all search queries from config
2. Collect publications from **all paginated pages**
3. Extract total results count
4. Deduplicate publications
5. **Show summary and ask for confirmation**

### Stage 2: Scraping (after user confirms)
1. Visit each publication page
2. Extract publication details (title, abstract, DOI, etc.)
3. Extract author names and affiliations
4. Filter European authors only
5. Visit each author's profile page
6. Extract detailed author information
7. Aggregate and deduplicate authors
8. Save to JSON files

## 🛡️ Anti-Bot Detection Handling

The scraper uses:
- Realistic user-agent strings
- Appropriate delays between requests
- Headless browser fingerprinting mitigation
- Dynamic content waiting and scrolling
- "Show More" button clicking for expanded content

## 🐛 Troubleshooting

### Chrome Driver Issues (macOS ARM64)
The scraper automatically finds the correct `chromedriver` executable. If you encounter issues:
```bash
rm -rf ~/.wdm/drivers/chromedriver
```
Then run the scraper again.

### No Results Found
- Check if IEEE Xplore is accessible
- Try with `--single-page` flag first
- Review `results/ieee_scraper.log` for errors

### Selenium Errors
- Ensure Chrome/Chromium is installed
- Update Chrome to the latest version
- Clear webdriver-manager cache (see above)

## 📄 License

This is a research tool for academic purposes. Respect IEEE Xplore's terms of service and use responsibly with appropriate rate limiting.

## 🤝 Contributing

Feel free to open issues or submit pull requests for improvements.

---

**Note**: This scraper is designed for research and educational purposes. Always respect website terms of service and implement appropriate rate limiting.
