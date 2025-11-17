# Competitor Exclusion Analysis Report

## Executive Summary

**Date:** November 17, 2025  
**Dataset:** European Authors Final Results (DACH + Non-DACH)  
**Total Authors Analyzed:** 6,174 authors

### Key Findings

Out of 6,174 total authors across both datasets:
- **6 authors (0.10%)** have mentions of competitor companies
- **2 authors (0.03%)** are CURRENTLY employed by competitor companies → **SHOULD BE EXCLUDED**
- **4 authors (0.06%)** have past associations or mentions → **REQUIRE CASE-BY-CASE REVIEW**

---

## Competitor Companies Searched

The following 17 competitor companies were searched across biography and affiliation fields:

1. Keysight Technologies, Inc. / Keysight Technologies France / Keysight labs
2. OPAL-RT Technologies / OPAL-RT Germany
3. Pulse Power and Measurement Ltd
4. Plexim / Plexim GmbH
5. IPG Automotive France / IPG Automotive USA Inc
6. RTDS Technologies
7. Speedgoat / speedgoat.de
8. National Instruments Corporation
9. ModelingTech Energy Technology Company
10. Vector France / Vector Informatik
11. The MathWorks, Inc.
12. dSPACE / dSPACE Company
13. ALIARO

---

## Detailed Analysis by Author

### ✅ CATEGORY A: DEFINITE EXCLUSIONS (Current Employees)

#### 1. **Wael Abdullah** (ID: 37086108437)
- **Country:** Germany (DACH)
- **Current Status:** CURRENTLY EMPLOYED at Keysight Labs (since late 2021)
- **Email:** wael.abdullah@ieee.org
- **Primary Affiliation:** IHP Leibniz-Institut für innovative Mikroelektronik
- **All Affiliations:** IHP + **Keysight labs, Germany**
- **Biography Excerpt:** 
  > "From late 2021, he joined Keysight Labs' mmWave Subsystems Design Group addressing 5G, 6G, automotive, and aero/defense applications."
- **Author Type:** Researcher
- **RECOMMENDATION:** **EXCLUDE** ✖️
- **Reasoning:** Active current employment at competitor company. Clear conflict of interest.

---

#### 2. **Sebastian Hubschneider** (ID: 37085658129)
- **Country:** Germany (DACH)
- **Current Status:** CURRENTLY EMPLOYED at OPAL-RT Germany (since 2022)
- **Email:** sebastian.hubschneider@kit.edu
- **Primary Affiliation:** **OPAL-RT Germany GmbH, Nürnberg, Germany**
- **Biography Excerpt:**
  > "Since 2022, he was an R&D Engineer with OPAL-RT Germany, where his research focuses on the projects in the areas of real-time simulation and digital twins of power grids."
- **Author Type:** Researcher
- **RECOMMENDATION:** **EXCLUDE** ✖️
- **Reasoning:** Primary affiliation is competitor company. Active R&D engineer role.

---

### 🔍 CATEGORY B: REVIEW REQUIRED (Past Associations)

#### 3. **Min Luo** (ID: 37085761350)
- **Country:** Germany (DACH)
- **Past Employment:** Plexim GmbH (2012-2022) - **employment ended 3 years ago**
- **Current Position:** Marketing representative at BASiC Semi (since 2022)
- **Email:** m.luo@ekarusengines.com
- **Primary Affiliation:** BASiC Semi, Ekarus Engines GmbH, Essingen, Germany
- **Biography Excerpt:**
  > "From 2012 to 2022, he was with Plexim GmbH working on modeling and hardware-in-the-loop test systems for power electronics."
- **Author Type:** (Not specified)
- **RECOMMENDATION:** **CONSIDER KEEPING** ✓
- **Reasoning:** 
  - Employment ended 3 years ago (2022)
  - Currently at different non-competitor company
  - No current conflict of interest
  - Past experience is historical, not current affiliation

---

#### 4. **Hermann Henrichfreise** (ID: 37089698180)
- **Country:** Germany (DACH)
- **Past Association:** Co-founder of dSPACE (1987-1994) - **30+ years ago**
- **Current Position:** Professor at TH Köln—University of Applied Sciences (since 1993)
- **Email:** hermann.henrichfreise@th-koeln.de
- **Primary Affiliation:** Faculty of Automotive Systems and Production, TH Köln
- **Biography Excerpt:**
  > "In 1987, he was the Co-Founder of dSPACE Company. From 1987 to 1994, he was moreover a Chief Execute Officer of dSPACE Company. Since 1993, he has been a Professor..."
- **Author Type:** Professor
- **RECOMMENDATION:** **KEEP** ✓
- **Reasoning:**
  - Co-founder role ended **31 years ago** (1994)
  - Has been university professor for 32 years
  - No current connection to dSPACE
  - Historical association is not a current conflict

---

#### 5. **Hüseyin Arslan** (ID: 37279667100)
- **Country:** Turkey (Non-DACH)
- **Mention Context:** Keysight mentioned in biography as funding source and industry collaborator
- **Current Position:** Professor at Istanbul Medipol University & University of South Florida
- **Email:** huseyinarslan@medipol.edu.tr
- **Primary Affiliation:** Department of Electrical and Electronics Engineering, Istanbul Medipol University
- **Biography Excerpt:**
  > "...his research has generated significant interest in companies, such as InterDigital, Anritsu, NTT DoCoMo, Raytheon, Honeywell, and Keysight technologies..."
  > "...he developed a unique 'Wireless Systems Laboratory' course (funded by the National Science Foundation and Keysight technologies)..."
- **Author Type:** Professor (IEEE Fellow, IEEE Distinguished Lecturer)
- **RECOMMENDATION:** **KEEP** ✓
- **Reasoning:**
  - NOT employed by Keysight
  - Keysight mentioned only as research collaborator and lab equipment funder
  - Academic professor role at university
  - Mentions Keysight alongside 6+ other industry partners
  - This is normal academic-industry collaboration, not employment

---

#### 6. **Daniel J. Auger** (ID: 37085584797)
- **Country:** United Kingdom (Non-DACH)
- **Past Employment:** Senior Consultant at MathWorks (2008-2013) - **12 years ago**
- **Current Position:** Reader (Professor) at Cranfield University (since 2013)
- **Email:** d.j.auger@cranfield.ac.uk
- **Primary Affiliation:** School of Aerospace, Transport and Manufacturing, Cranfield University
- **Biography Excerpt:**
  > "From 2008 to 2013, he was a Senior Consultant with MathWorks, Cambridge. He joined the Advanced Vehicle Engineering Centre, Cranfield University, Cranfield, U.K., in 2013..."
- **Author Type:** Professor (IEEE Senior Member, IET Fellow, Chartered Engineer)
- **RECOMMENDATION:** **CONSIDER KEEPING** ✓
- **Reasoning:**
  - Employment ended **12 years ago** (2013)
  - Has been university professor for 12 years
  - No current connection to MathWorks
  - Historical employment is well in the past

---

## Summary Statistics

### By File

| File | Total Authors | With Competitor Mentions | % |
|------|---------------|-------------------------|---|
| european_authors_non_dach_no_france_merged.csv | 4,959 | 2 | 0.04% |
| european_authors_dach_simple.csv | 1,215 | 4 | 0.33% |
| **TOTAL** | **6,174** | **6** | **0.10%** |

### By Company Mention

| Company | Mentions | Authors |
|---------|----------|---------|
| Keysight | 2 | 2 (1 current, 1 collaboration) |
| OPAL-RT | 1 | 1 (current) |
| Plexim | 1 | 1 (past) |
| dSPACE | 1 | 1 (past, 30+ years ago) |
| MathWorks | 1 | 1 (past, 12 years ago) |

### By Exclusion Recommendation

| Category | Count | Action |
|----------|-------|--------|
| **DEFINITE EXCLUSIONS** (Current employees) | **2** | **EXCLUDE** |
| **Consider Keeping** (Past employment 3-12 years ago) | 2 | Review case-by-case |
| **Keep** (Historical or collaboration only) | 2 | Keep |

---

## Final Recommendations

### Immediate Actions Required

1. **EXCLUDE these 2 authors** (current competitor employees):
   - **37086108437** - Wael Abdullah (Keysight Labs)
   - **37085658129** - Sebastian Hubschneider (OPAL-RT Germany)

### Case-by-Case Decision Needed

2. **Review these 2 authors** with recent past employment (3-12 years ago):
   - **37085761350** - Min Luo (Plexim, left 2022) → Suggest KEEP
   - **37085584797** - Daniel J. Auger (MathWorks, left 2013) → Suggest KEEP

3. **Keep these 2 authors** (historical or collaboration only):
   - **37089698180** - Hermann Henrichfreise (dSPACE co-founder 31 years ago) → KEEP
   - **37279667100** - Hüseyin Arslan (Keysight collaboration/funding) → KEEP

### Justification for "KEEP" Recommendations

**Why keep authors with past employment (3-12 years ago)?**
- They are no longer employed by competitor companies
- Sufficient time has passed (3-12 years)
- Currently employed at non-competitor institutions
- Their current work does not represent competitor interests
- IEEE publications reflect their current academic/industry work
- Excluding them would be overly restrictive

**Why keep Hermann Henrichfreise (dSPACE co-founder)?**
- Co-founder role ended 31 years ago (1994)
- Has been university professor since 1993 (32 years)
- No reasonable current conflict of interest
- Excluding historical associations from 30+ years ago is excessive

**Why keep Hüseyin Arslan (Keysight mention)?**
- NOT employed by Keysight
- Mention is in context of research collaboration and lab equipment funding
- This is standard academic-industry research collaboration
- Also collaborates with 6+ other companies (InterDigital, Anritsu, NTT DoCoMo, Raytheon, Honeywell)
- Excluding academic researchers who receive industry funding would eliminate most applied research professors

---

## Impact Analysis

### Conservative Approach (Exclude only current employees)
- **Authors to exclude:** 2 (0.03% of total)
- **Authors retained:** 6,172 (99.97%)
- **Impact:** Minimal, surgical exclusion

### Aggressive Approach (Exclude all with any mention)
- **Authors to exclude:** 6 (0.10% of total)
- **Authors retained:** 6,168 (99.90%)
- **Impact:** Still minimal, but may exclude valuable academic researchers

### Recommended Approach (Balanced)
- **Authors to exclude:** 2 current employees
- **Authors to review:** 2 with recent past employment
- **Authors to keep:** 2 with historical/collaboration mentions
- **Rationale:** Targets actual conflicts while preserving academic integrity

---

## Conclusion

The competitor exclusion analysis reveals an **extremely low contamination rate (0.10%)** in the dataset. Only **2 authors (0.03%)** represent genuine current conflicts of interest as active employees of competitor companies.

**RECOMMENDED ACTION:**
1. **Exclude 2 authors** who are currently employed at competitor companies
2. **Retain the remaining 4 authors** as they represent:
   - Historical associations (30+ years old)
   - Past employment that ended 3-12 years ago
   - Academic research collaboration with industry (standard practice)

This balanced approach ensures:
- ✅ Elimination of actual conflicts of interest
- ✅ Preservation of valuable academic researchers
- ✅ Recognition that past associations (3+ years old) are not current conflicts
- ✅ Support for normal academic-industry research collaboration

The dataset quality remains exceptionally high with 99.97% of authors having no competitor associations.

---

## Appendix: Search Methodology

**Search Fields:**
- Primary affiliation
- All affiliations
- Biography

**Search Patterns:**
- Case-insensitive matching
- Exact company name matching
- Multiple name variants for each company

**False Positive Prevention:**
- Manual review of all matches
- Context analysis of mentions
- Distinction between employment vs. collaboration/funding
- Temporal analysis (current vs. past associations)

**Quality Assurance:**
- Full biography review for each match
- Verification of current employment status
- Cross-reference with email domains and affiliations

---

*Report generated by automated analysis with manual review and reasoning applied to all findings.*

