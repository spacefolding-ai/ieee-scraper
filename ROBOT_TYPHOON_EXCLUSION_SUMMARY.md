# Robot & Typhoon HIL Exclusion - Final Summary

**Date:** November 17, 2025  
**Action:** Excluded 563 authors with "robot" or "typhoon hil" mentions in biography/affiliation

---

## ✅ Exclusion Complete

### Exclusion Criteria:
- Authors with "robot" (or robotics, robotic, etc.) in their **biography** or **affiliation** fields
- Authors with "typhoon hil" in their **biography** or **affiliation** fields
- **Note:** Publication abstracts were NOT searched (only author's own fields)

---

## 📊 Exclusion Statistics

### By File:

| File | Original | Excluded | Kept | Exclusion Rate |
|------|----------|----------|------|----------------|
| **Non-DACH** | 4,959 | 447 | **4,512** | 9.01% |
| **DACH** | 1,211 | 116 | **1,095** | 9.58% |
| **TOTAL** | **6,170** | **563** | **5,607** | **9.12%** |

### By Reason:

| Reason | Count | Percentage |
|--------|-------|------------|
| **"robot" only** | 562 | 99.82% |
| **"typhoon hil" only** | 1 | 0.18% |
| **Both** | 0 | 0.00% |

---

## 📝 Exclusion Breakdown

### Non-DACH File: 447 exclusions
- **Belgium** - Large number of robotics researchers (BruBotics, KU Leuven Robot-Assisted Surgery, etc.)
- **Denmark** - 1 author (Typhoon HIL mention)
- **Turkey** - Multiple robotics labs
- **Netherlands** - TU Delft robotics programs
- **United Kingdom** - Various robotics research centers
- And others...

### DACH File: 116 exclusions
- **Germany** - Major robotics centers:
  - German Aerospace Center (DLR) - Institute of Robotics and Mechatronics
  - Munich Institute of Robotics and Machine Intelligence (MIRMI)
  - University of Bonn - Humanoid Robots Lab
  - Technical University of Munich - Robotics programs
  - University of Stuttgart - Socially Intelligent Robotics Lab
- **Austria** - Robotics research
- **Switzerland** - ETH Zürich and other robotics programs

---

## 📁 Output Files Created

### New Files (without robot/typhoon mentions):

1. **`european_authors_non_dach_no_france_merged_no_robots.csv`**
   - **4,512 authors** (447 excluded)
   - 52 MB file size
   - 7,874 lines (including multi-line CSV records)

2. **`european_authors_dach_simple_no_robots.csv`**
   - **1,095 authors** (116 excluded)
   - 11 MB file size
   - 1,873 lines (including multi-line CSV records)

---

## ✓ Verification

The exclusion was verified to ensure:
- ✅ Authors with "robot" in biography/affiliation were excluded
- ✅ Authors with "robot" only in publication abstracts were KEPT
- ✅ The CSV structure and data integrity maintained
- ✅ No data corruption or formatting issues

**Example verification:**
- **Tuân-Tú Huỳnh** (Albania) - KEPT
  - Affiliation: Faculty of Mechatronics and Electronics, Lac Hong University
  - No "robot" in their own biography/affiliation
  - Publications mention "robotic systems" but that's in abstract (not author's field)
  - ✅ Correctly kept

---

## 🎯 Impact Analysis

### Who Was Excluded?

**Robotics Researchers** working in:
- Humanoid robots
- Industrial robotics
- Robot-assisted surgery
- Mobile robotics
- Robotic systems and mechatronics
- Human-robot interaction
- Robotic manipulation
- Autonomous robots

### Examples of Excluded Authors:

**Belgium:**
- Guillaume Crevecoeur - Dynamical Systems and Control Research Group
- Joris De Schutter - KU Leuven Robotics
- Mouloud Ourak - Robot-Assisted Surgery Group, KU Leuven
- Bram Vanderborght - BruBotics, VU Brussels

**Germany:**
- Sicong Pan - Humanoid Robots Lab, University of Bonn
- Robin Kirschner - Munich Institute of Robotics and Machine Intelligence
- Peter Schmaus - German Aerospace Center (DLR)
- Jörn Vogel - DLR Robotics and Mechatronics Center

**Typhoon HIL:**
- Kaio V. Vilerá (Denmark) - DTU Wind and Energy Systems
  - Mentioned Typhoon HIL testing equipment (likely in research context)

---

## 🤔 Consideration

### Should Robotics Researchers Be Excluded?

**Arguments FOR exclusion:**
- Your focus may be on power systems, energy, or other non-robotics fields
- Robotics is a distinct research domain
- Reduces dataset size by ~9% for more targeted outreach

**Arguments AGAINST exclusion:**
- Many robotics researchers work on **power electronics** for robot actuators
- **Control systems** in robotics overlap with power system control
- **Autonomous vehicles** and **mobile robots** use battery management systems
- **Robot-assisted surgery** may involve medical electronics
- These researchers might be valuable contacts depending on your use case

---

## 💡 Recommendation

If your goal is to target:
- ✅ **Power systems, energy, grid technology** → Use the files WITHOUT robots
- ✅ **Specific non-robotics domains** → Use the files WITHOUT robots
- ⚠️ **Broader electromechanical/control systems** → Consider keeping robotics researchers
- ⚠️ **Mechatronics, automation, control theory** → Consider keeping robotics researchers

---

## 📈 Final Dataset Statistics

### After All Exclusions (Competitor + Robot/Typhoon):

**Starting point:** 6,174 authors (original dataset)  
**After competitor exclusion:** 6,170 authors (-4, 0.06%)  
**After robot/typhoon exclusion:** **5,607 authors** (-563, 9.12%)  

**Total excluded:** 567 authors (9.18% of original dataset)  
**Total retained:** 5,607 authors (90.82% of original dataset)

---

## 📚 File Lineage

Evolution of files:

1. **Original files:**
   - `european_authors_non_dach_no_france_merged.csv` (4,959 authors)
   - `european_authors_dach_simple.csv` (1,215 authors)

2. **After competitor exclusion (_cleaned):**
   - `european_authors_non_dach_no_france_merged_cleaned.csv` (4,959 authors, 0 excluded)
   - `european_authors_dach_simple_cleaned.csv` (1,211 authors, 4 excluded)

3. **After robot/typhoon exclusion (_no_robots):** ⭐ **CURRENT**
   - `european_authors_non_dach_no_france_merged_no_robots.csv` (4,512 authors, 447 excluded)
   - `european_authors_dach_simple_no_robots.csv` (1,095 authors, 116 excluded)

---

## ✅ Next Steps

Your cleaned dataset is ready:
- **Total authors: 5,607**
- **Free of competitor companies** (Keysight, OPAL-RT, Plexim, dSPACE, etc.)
- **Free of robotics researchers**
- **Free of Typhoon HIL mentions**

The `*_no_robots.csv` files are your final, cleaned datasets ready for use!

---

*Exclusion performed by: `exclude_robot_typhoon.py`*  
*Search analysis available in: `search_robot_typhoon.py`*  
*Previous exclusions documented in: `COMPETITOR_EXCLUSION_SUMMARY.md`*

