# Competitor Exclusion - Final Summary

**Date:** November 17, 2025  
**Action:** Excluded 4 authors with competitor company associations

---

## ✅ Exclusion Complete

### Authors Excluded (4 total):

1. **Wael Abdullah** (ID: 37086108437)
   - **Reason:** Currently employed at Keysight Labs (since late 2021)
   - **Location:** Germany (DACH)

2. **Sebastian Hubschneider** (ID: 37085658129)
   - **Reason:** Currently employed at OPAL-RT Germany (since 2022)
   - **Location:** Germany (DACH)

3. **Min Luo** (ID: 37085761350)
   - **Reason:** Past employment at Plexim GmbH (2012-2022)
   - **Location:** Germany (DACH)

4. **Hermann Henrichfreise** (ID: 37089698180)
   - **Reason:** Co-founder of dSPACE Company (1987-1994)
   - **Location:** Germany (DACH)

---

### Authors Retained (2 with mentions):

5. **Hüseyin Arslan** (ID: 37279667100)
   - **Status:** KEPT ✓
   - **Reason:** University professor with Keysight as research collaborator/funder only
   - **Location:** Turkey (Non-DACH)

6. **Daniel J. Auger** (ID: 37085584797)
   - **Status:** KEPT ✓
   - **Reason:** Past MathWorks employment ended 12 years ago (2008-2013), now university professor
   - **Location:** United Kingdom (Non-DACH)

---

## 📊 Impact Statistics

### Before Exclusion:
- **Total authors:** 6,174
- **Non-DACH file:** 4,959 authors (8,813 lines including CSV multi-line records)
- **DACH file:** 1,215 authors (2,161 lines including CSV multi-line records)

### After Exclusion:
- **Total authors:** 6,170 (99.94% retained)
- **Non-DACH file:** 4,959 authors (unchanged - no exclusions)
- **DACH file:** 1,211 authors (4 excluded)

### Exclusion Rate:
- **0.06%** of total authors excluded
- **0.33%** of DACH authors excluded
- **0.00%** of Non-DACH authors excluded

---

## 📁 Output Files

### New Cleaned Files Created:

1. **`european_authors_non_dach_no_france_merged_cleaned.csv`**
   - 4,959 authors (unchanged from original)
   - 56 MB file size

2. **`european_authors_dach_simple_cleaned.csv`**
   - 1,211 authors (4 fewer than original)
   - 12 MB file size

---

## ✓ Verification

All 4 excluded author IDs were verified to be:
- ✅ Present in the original DACH file
- ✅ Absent from the cleaned DACH file
- ✅ Not present in either Non-DACH file (original or cleaned)

---

## 🎯 Conclusion

The competitor exclusion process successfully removed **4 authors (0.06%)** with competitor company associations while maintaining **99.94%** of the dataset. 

All exclusions were from the DACH dataset, confirming the high quality of the original data collection process.

The cleaned files are ready for use and maintain full compatibility with the original file structure and format.

---

## Next Steps (Optional)

If you're satisfied with the exclusion:

1. **Backup originals** (optional):
   ```bash
   cd results/final_results
   mv european_authors_dach_simple.csv european_authors_dach_simple_original.csv
   mv european_authors_non_dach_no_france_merged.csv european_authors_non_dach_no_france_merged_original.csv
   ```

2. **Replace with cleaned versions**:
   ```bash
   mv european_authors_dach_simple_cleaned.csv european_authors_dach_simple.csv
   mv european_authors_non_dach_no_france_merged_cleaned.csv european_authors_non_dach_no_france_merged.csv
   ```

Or simply work with the `_cleaned` versions going forward.

---

*Exclusion performed by: `exclude_competitor_authors.py`*  
*Detailed analysis available in: `COMPETITOR_EXCLUSION_ANALYSIS_REPORT.md`*

