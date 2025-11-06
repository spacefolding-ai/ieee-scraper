# 🔬 Hardware-in-Loop (HIL) Keyword Test

## Quick Test to Verify HIL Institution Detection

This test configuration helps verify that the scraper correctly identifies authors from Hardware-in-Loop (HIL) research institutions like Typhoon HIL.

---

## 🚀 How to Run

### Option 1: Using the GUI Launcher
```bash
./run_scraper.command
```

Then select:
```
Which configuration would you like to use?
  1) config_test.json (3 queries, ~5 minutes)
  2) config.json (50 queries, ~2-3 hours)
  3) config_hil_test.json (Hardware-in-Loop test, 4 queries, ~20 publications)

Enter choice (1-3): 3  ← Choose option 3
```

### Option 2: Command Line
```bash
python3 ieee_author_scraper.py --config config_hil_test.json
```

---

## 📋 What It Tests

### Search Queries (4 queries):
1. `"hardware-in-the-loop"` - With hyphens
2. `"hardware in loop"` - Without hyphens
3. `"HIL testing"` - Abbreviated form + testing
4. `"HIL simulation"` - Abbreviated form + simulation

### Settings:
- **Max results per query:** 20 publications
- **Expected total:** ~80 publications
- **Target institutions:** Companies and research labs working with HIL systems
- **Estimated time:** 5-10 minutes

---

## ✅ Expected Results

### Publications Should Include Authors From:

**✅ Industrial R&D Labs:**
- Typhoon HIL, Inc. (Serbia)
- dSPACE GmbH (Germany)
- OPAL-RT Technologies (if European office)
- National Instruments R&D Labs (European offices)

**✅ Universities with HIL Labs:**
- Technical universities with HIL testing facilities
- Power electronics research labs
- Control systems departments

**✅ Research Institutes:**
- Fraunhofer institutes with HIL systems
- National research centers

---

## 📊 What You'll See

### Collection Phase:
```
STEP 1: Collecting publications from IEEE Xplore...

[1/1] Searching category: hardware_in_loop
  Query: hardware-in-the-loop
  Total results available: 1,234
  Will collect from 1 page(s)
  Collected 20 publications from page 1
  
  Query: hardware in loop
  Total results available: 987
  Collected 20 publications from page 1
  
  Query: HIL testing
  ...

Deduplication: 80 total → 65 unique

======================================================================
📊 COLLECTION COMPLETE
======================================================================
✅ Total publications found: 65
```

### Processing Phase:
```
Processing publication 5/65: Real-Time HIL Testing of Power Converters
  ✓ Found European author(s) from: Serbia
  ✓ European author found: Milos Miletic (Serbia)
    Email: milos.miletic@typhoon-hil.com
    Institution: Typhoon HIL, Inc.
```

### Statistics:
```
======================================================================
SCRAPING STATISTICS
======================================================================
Publications with European authors: 15
Publications skipped (no European authors): 50
European authors found: 32

COUNTRY DISTRIBUTION (Authors)
----------------------------------------------------------------------
  ⭐ Germany: 12 authors
  • Serbia: 8 authors
  ⭐ Italy: 5 authors
  • Switzerland: 4 authors
  • Sweden: 3 authors
======================================================================
```

---

## 🎯 Success Criteria

The test is successful if:

1. ✅ Finds publications with "HIL" keyword variations
2. ✅ Detects "Typhoon HIL, Inc." as a research institution
3. ✅ Recognizes Serbian authors as European
4. ✅ Extracts complete author profiles
5. ✅ Shows Serbia in country distribution

---

## 🔍 Verification Checklist

After the test completes, check the output files:

### `results/publications_with_authors.json`
```json
{
  "publication": {
    "title": "...",
    "abstract": "... hardware-in-the-loop testing ..."
  },
  "authors": [
    {
      "Full_name": "Milos Miletic",
      "university": "",
      "research_institution": "Typhoon HIL, Inc.",
      "city": "Novi Sad",
      "country": "Serbia"
    }
  ]
}
```

**Verify:**
- ✅ Publications contain HIL keywords
- ✅ Authors from Typhoon HIL are included
- ✅ Serbia is correctly identified
- ✅ Institution name is extracted

---

## 🐛 Troubleshooting

### Issue: No publications found
**Solution:** Check internet connection and IEEE Xplore access

### Issue: Publications found but no European authors
**Possible reasons:**
- Most HIL research is from USA/Asia
- Try expanding search to more generic power electronics queries
- This is normal - the filter is working correctly

### Issue: Typhoon HIL not recognized as research institution
**Check:**
1. Open `scraper/affiliation_parser.py`
2. Verify "hil" is in `RESEARCH_KEYWORDS` list
3. Run the keyword test again

---

## 📈 Interpretation Guide

### High Success Rate (>30% with European authors):
✅ Excellent! HIL research is strong in Europe

### Medium Success Rate (10-30% with European authors):
✅ Good! Finding relevant European authors

### Low Success Rate (<10% with European authors):
⚠️ Normal for specialized topics. Most HIL research is outside Europe.

---

## 🔄 Next Steps After Testing

### If Test Successful:
1. Run full scraper with `config.json`
2. Expect similar detection for HIL institutions
3. Results will include all matching authors

### If Issues Found:
1. Review `results/ieee_scraper.log` for errors
2. Check keyword matches in console output
3. Adjust keywords in config if needed

---

## 💡 Tips

**Fast Testing:**
```bash
# Run with debug logging to see keyword matches
python3 ieee_author_scraper.py --config config_hil_test.json --log-level DEBUG
```

**Skip Confirmation:**
```bash
# For automated testing
python3 ieee_author_scraper.py --config config_hil_test.json --no-confirm
```

**Single Page Only:**
```bash
# Even faster test
python3 ieee_author_scraper.py --config config_hil_test.json --single-page
```

---

## ✅ Expected Output Files

After successful run:

1. `results/publications_with_authors.json` - HIL publications with European authors
2. `results/authors_output.json` - Unique European authors from HIL field
3. `results/ieee_scraper.log` - Detailed log with keyword matches

---

**Happy Testing!** 🚀

If Typhoon HIL authors appear in the results, the keyword detection is working perfectly! 🎉

