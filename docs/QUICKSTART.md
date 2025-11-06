# Quick Start Guide

Get started with the IEEE Xplore Author Scraper in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- Internet connection

## Setup (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- requests (HTTP library)
- beautifulsoup4 (HTML parsing)
- selenium (Browser automation)
- lxml (XML/HTML parser)
- pycountry (Country data)
- webdriver-manager (Chrome driver management)

### Step 2: Verify Setup

```bash
python verify_setup.py
```

This will check:
- ✓ Python version (3.8+)
- ✓ All required packages
- ✓ Chrome/Chromium availability
- ✓ Project files

## Running the Scraper

### Option 1: Quick Test Run (Recommended for First Time)

Use the test configuration with fewer search terms:

```bash
python ieee_author_scraper.py
```

This will:
1. Search IEEE Xplore for publications (using test config with limited queries)
2. Extract author information
3. Filter for European authors (excluding France)
4. Save results to `authors_output.json`

**Expected time**: 10-30 minutes depending on results

### Option 2: Full Run

Use the full configuration with all search terms:

```bash
# Edit config.json first if needed
python ieee_author_scraper.py
```

**Expected time**: 1-3 hours depending on results

## Monitoring Progress

### Console Output
Watch real-time progress in your terminal:
```
[INFO] Searching category: power_electronics
[INFO]   Query: multilevel inverter
[INFO]     Found 15 publications
[INFO] Processing publication 1/15: Design and Control of...
[INFO]   ✓ European author found: Dr. Max Mustermann (Germany)
```

### Log File
Check `ieee_scraper.log` for detailed information:
```bash
tail -f ieee_scraper.log
```

## Viewing Results

### JSON Output
Results are saved to `authors_output.json`:

```json
[
  {
    "Full_name": "Max Mustermann",
    "Email": "max.mustermann@university.de",
    "Title": "Dr.-Ing.",
    "Role": "Professor",
    "Field_of_study": "Power Electronics",
    "university": "Technical University of Munich",
    "research_institution": "",
    "Publications": [
      "https://doi.org/10.1109/..."
    ]
  }
]
```

### Statistics
At the end of the run, you'll see statistics:
```
SCRAPING STATISTICS
=====================
Duration: 0:15:42
Queries executed: 3
Total publications found: 45
Publications processed: 45
European authors found: 23
Unique authors aggregated: 18
Authors with email: 12 (66.7%)
```

## Customizing Your Search

### Edit Search Terms
Open `config.json` and modify the search terms:

```json
{
  "search_terms": {
    "power_electronics": [
      "your custom term here",
      "another search term"
    ]
  },
  "delay_between_requests": 2,
  "max_results_per_query": 100
}
```

### Adjust Rate Limiting
To be more respectful or avoid blocking:
```json
{
  "delay_between_requests": 5,
  "max_results_per_query": 50
}
```

## Troubleshooting

### "No publications found"
- Check your internet connection
- Verify IEEE Xplore is accessible: https://ieeexplore.ieee.org/
- Try simpler search terms in `config.json`

### "Chrome driver error"
```bash
pip install --upgrade webdriver-manager
```

### "Timeout errors"
Increase delays in `config.json`:
```json
{
  "delay_between_requests": 5
}
```

### Scraper stopped unexpectedly
Don't worry! Partial results are automatically saved:
- Look for `authors_output_partial_TIMESTAMP.json`

## Tips for Best Results

1. **Start Small**: Use `config_test.json` for your first run
2. **Be Patient**: Web scraping takes time, especially with rate limiting
3. **Monitor Logs**: Keep an eye on `ieee_scraper.log` for issues
4. **Respect Limits**: Don't reduce delays too much or you may get blocked
5. **Save Progress**: The scraper automatically saves progress every 10 publications

## Next Steps

After your first successful run:

1. Review the results in `authors_output.json`
2. Adjust search terms in `config.json` based on your needs
3. Run a full scrape with all search terms
4. Process the data further (import into Excel, database, etc.)

## Need Help?

Check the full documentation in `README.md` for:
- Detailed architecture
- Advanced configuration
- API alternatives
- Legal considerations

---

**Remember**: Web scraping should be done responsibly. Always:
- Respect rate limits
- Follow Terms of Service
- Consider using official APIs when available
- Use data ethically and legally

