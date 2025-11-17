# Department Extraction from Email Citations - Summary

## What We Discovered

### Coverage
- **4,958 authors (99.98%)** have email citation URLs
- **1,153 authors (26.6%)** need department extraction (currently missing)
- **3,188 authors (73.4%)** already have department from biography/affiliation

### Best Sources for Department Info

#### 1. University Profile Pages ⭐⭐⭐⭐⭐ (Most Reliable)
**Coverage:** 2,009 authors (46.3%)

**Example:** Patrizio Manganiello
- URL: `https://www.uhasselt.be/en/who-is-who/detail/patrizio-manganiello`
- **Extracted:**
  - Position: Associate Professor
  - Faculty: **Faculty of Engineering Technology**
  - Research group: **Engineering Materials and Applications**
  - Institute: Institute for Materials Research
  
**What to extract:**
- Department/Faculty name
- Research group
- Current position/title
- Contact information

---

#### 2. Google Scholar ⭐⭐⭐⭐ (Very Reliable)
**Coverage:** 4,181 authors (87.9%)

**Example:** Wenzhi Liao
- URL: `https://scholar.google.com/citations?user=a9O1t1cAAAAJ`
- **Extracted:** "Professor in Statistical Image Modeling, Ghent University"

**Example:** Patrizio Manganiello
- URL: `https://scholar.google.com/citations?user=BJxnIpgAAAAJ`
- **Extracted:** "Hasselt University" (verified email)

**What to extract:**
- Affiliation line (usually shows department + university)
- Current position if listed
- Verified institution

---

#### 3. ORCID ⭐⭐⭐⭐ (Reliable)
**Coverage:** 633 authors (14.5%)

**What to extract:**
- Employment history with dates
- Current position
- Department/organization name

---

## Extraction Strategy

### Priority Order for Each Author:
1. **Try university profile first** (if available)
   - Most detailed and accurate
   - Shows current department explicitly
   
2. **Fall back to Google Scholar**
   - Usually shows affiliation line
   - Good for current position
   
3. **Try ORCID as last resort**
   - Has employment history
   - Can identify current position

### Department Extraction Patterns

From text content, look for:
```regex
- Department of ([^,\.;]+)
- Faculty of ([^,\.;]+)
- School of ([^,\.;]+)
- Institute of ([^,\.;]+)
- Research group ([^,\.;]+)
- Division of ([^,\.;]+)
```

### Expected Results

Based on browser testing:
- **University profiles:** ~90% success rate for department name
- **Google Scholar:** ~70% success rate for department/faculty info
- **ORCID:** ~60% success rate

**Combined approach:** Expected to find department for ~80-85% of the 1,153 missing

## Implementation Approach

### Option A: Automated Browser-Based Extraction (Recommended)
Similar to previous author_type enrichment:
- Process in batches of 50-100
- Visit top 2-3 priority URLs per author
- Extract department using patterns
- Save progress for resume capability
- Estimate time: 4-6 hours for 1,153 authors

### Option B: Manual Verification
- Focus on high-priority authors
- Use browser to verify department
- Update records manually

### Option C: Hybrid
- Automated extraction for authors with university profiles
- Manual review for ambiguous cases
- Validate against primary_affiliation field

## Example Extraction Results

| Author | Source | Extracted Department |
|--------|--------|---------------------|
| Wenzhi Liao | Google Scholar | Statistical Image Modeling (Ghent University) |
| Patrizio Manganiello | University Profile | Faculty of Engineering Technology |
| Mouloud Ourak | Primary Affiliation | Department of Mechanical Engineering |

## Next Steps

1. **Prioritize primary_affiliation** in current extraction logic
2. **Run browser-based extraction** for 1,153 missing departments
3. **Validate results** against all_affiliations
4. **Update all *_simple.json and *_simple.csv files**
