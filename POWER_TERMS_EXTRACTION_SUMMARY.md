# Power Electronics Terms Extraction - Summary

**Date:** November 17, 2025  
**Action:** Split datasets into WITH and WITHOUT power electronics terms

---

## ✅ Extraction Complete

### 4 Files Created:

1. **`non_dach_with_power_terms.csv`** - 3,014 authors (39 MB)
2. **`non_dach_without_power_terms.csv`** - 1,498 authors (12 MB)
3. **`dach_with_power_terms.csv`** - 632 authors (7.1 MB)
4. **`dach_without_power_terms.csv`** - 463 authors (3.8 MB)

---

## 📊 Statistics

### By Dataset:

| Dataset | Total Authors | WITH Power Terms | WITHOUT Power Terms |
|---------|---------------|------------------|---------------------|
| **Non-DACH** | 4,512 | 3,014 (66.8%) | 1,498 (33.2%) |
| **DACH** | 1,095 | 632 (57.7%) | 463 (42.3%) |
| **TOTAL** | **5,607** | **3,646 (65.0%)** | **1,961 (35.0%)** |

---

## 🔍 Search Terms Used

Authors were classified as "WITH power terms" if their affiliation, biography, or publications mentioned ANY of these terms:

1. **verter** (converter, inverter)
2. **switch** (switching, switches)
3. **power** (power electronics, power systems, etc.)
4. **motor** (motors, motor drives)
5. **grid** (smart grid, power grid, grid-connected)
6. **charging** (EV charging, battery charging)
7. **charger** (battery charger, chargers)
8. **bms** (Battery Management System)
9. **battery management**
10. **active filter** (active power filter)
11. **bess** (Battery Energy Storage System)
12. **energy storage system**
13. **electric drive** (electric drives, drive systems)

---

## 📁 File Descriptions

### WITH Power Terms (3,646 authors total - 65%)

**Non-DACH: 3,014 authors**
- Power electronics researchers
- Grid technology specialists
- Energy conversion experts
- EV charging infrastructure
- Battery management systems
- Motor drive specialists
- Energy storage systems

**DACH: 632 authors**
- German power electronics industry
- Austrian energy systems
- Swiss power technology research
- Strong converter/inverter focus
- Grid integration specialists

**Top Terms in "WITH" Group:**
- Power: 85.5% of matches
- Grid: 47.8% of matches
- Verter (converter/inverter): 44.9% of matches
- Switch: 23.0% of matches
- Energy storage system: 16.8% of matches

---

### WITHOUT Power Terms (1,961 authors total - 35%)

**Non-DACH: 1,498 authors**
- Communications & RF
- Signal processing
- Microelectronics
- Semiconductor devices
- Medical electronics
- Instrumentation
- Control systems (non-power)
- Computer engineering

**DACH: 463 authors**
- Automation & control
- Embedded systems
- RF & wireless
- Digital electronics
- Sensor systems
- Measurement technology
- Mixed signal design

---

## 💡 Use Cases

### Target "WITH Power Terms" Files When:
✅ Marketing power electronics products/services  
✅ Recruiting for energy/power companies  
✅ Organizing power electronics conferences  
✅ Grid technology partnerships  
✅ EV charging infrastructure projects  
✅ Battery management system development  
✅ Renewable energy integration  

**Primary domains:** Power conversion, energy systems, grid technology, EV charging, energy storage

---

### Target "WITHOUT Power Terms" Files When:
✅ Broader electrical engineering outreach  
✅ Communications/RF technology  
✅ Semiconductor/IC design  
✅ Signal processing applications  
✅ Medical device electronics  
✅ Instrumentation & measurement  
✅ General automation/control systems  

**Primary domains:** Communications, RF, digital electronics, signal processing, instrumentation, embedded systems

---

## 📈 Quality Insights

### Power Electronics Concentration:
- **Non-DACH regions (66.8%):** Higher concentration of power electronics researchers
  - Strong representation from Belgium, Netherlands, Turkey, Denmark, UK
  - Many academic research groups in power systems
  
- **DACH regions (57.7%):** Good but slightly lower concentration
  - Strong industrial presence (Siemens, Bosch, ABB research)
  - More diverse electrical engineering focus
  - Significant automation and control systems representation

### Why 35% Don't Have Power Terms?
These 1,961 authors work in complementary electrical engineering domains:
- **Valid researchers** in communications, RF, digital design, etc.
- **Not errors** - they simply work in non-power electronics domains
- **Still valuable** for broader electrical engineering outreach

---

## 🎯 Recommendations

### For Power Electronics/Energy Focus:
**Use:** `non_dach_with_power_terms.csv` (3,014) + `dach_with_power_terms.csv` (632)  
**Total:** 3,646 highly targeted authors (65% of dataset)

### For Broader Electrical Engineering:
**Use:** All original files (5,607 authors)  
**Benefit:** Maximum reach across all EE domains

### For Non-Power Electronics:
**Use:** `non_dach_without_power_terms.csv` (1,498) + `dach_without_power_terms.csv` (463)  
**Total:** 1,961 authors in other EE domains (35% of dataset)

---

## 📊 Dataset Evolution Summary

**Original dataset:**
- 6,174 authors (before any filtering)

**After competitor exclusion:**
- 6,170 authors (-4, removed Keysight, OPAL-RT, Plexim, dSPACE employees)

**After robot/typhoon exclusion:**
- 5,607 authors (-563, removed robotics researchers)

**Final split by power electronics terms:**
- **WITH power terms:** 3,646 authors (65.0%)
- **WITHOUT power terms:** 1,961 authors (35.0%)

---

## ✅ Final Dataset Quality

Your cleaned and split datasets are now:
- ✅ Free of competitor companies
- ✅ Free of robotics researchers  
- ✅ Free of Typhoon HIL mentions
- ✅ Segmented by power electronics focus
- ✅ Ready for targeted outreach

**Total usable authors:** 5,607 across 4 segmented files

---

## 📍 File Locations

All files are in: `/Users/miroslavjugovic/Projects/ieee-scraper/results/final_results/`

**Power Electronics Focused (recommended for your use case):**
- `non_dach_with_power_terms.csv` (3,014 authors, 39 MB)
- `dach_with_power_terms.csv` (632 authors, 7.1 MB)

**Other Electrical Engineering Domains:**
- `non_dach_without_power_terms.csv` (1,498 authors, 12 MB)
- `dach_without_power_terms.csv` (463 authors, 3.8 MB)

---

*Extraction performed by: `extract_by_power_terms.py`*  
*Search analysis available in: `search_power_electronics_terms.py`*  
*Previous filtering documented in: `COMPETITOR_EXCLUSION_SUMMARY.md` and `ROBOT_TYPHOON_EXCLUSION_SUMMARY.md`*

