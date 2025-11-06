# 🏛️ Institution Types Included

## ✅ What the Scraper Recognizes

The scraper is configured to identify and include authors from these types of European institutions:

---

### **1. Technical Universities** 🎓
- TU Munich (Technische Universität München)
- ETH Zurich (Swiss Federal Institute of Technology)
- TU Dresden, TU Delft, TU Vienna, etc.
- RWTH Aachen
- Any institution with "Technical University" or "TU" in the name

---

### **2. Applied Science Universities** 🔬
- Universities of Applied Sciences (Hochschule)
- Polytechnics
- Applied research universities

---

### **3. Research Institutes** 🏢
- Fraunhofer Institutes (Germany)
- Max Planck Institutes (Germany)
- National research institutes
- Independent research organizations

---

### **4. Universities with Engineering Faculties** 🎓
- Traditional universities with engineering departments
- Faculty of Engineering
- School of Engineering

---

### **5. EU Research Centers** 🇪🇺
- European research facilities
- Joint research centers
- Innovation centers

---

### **6. Industrial R&D Labs** 🔧
Examples that ARE included:
- ✅ Siemens R&D Center
- ✅ ABB Research Center  
- ✅ Typhoon HIL, Inc. (Hardware-in-Loop testing)
- ✅ Bosch Engineering Center
- ✅ Any company with "R&D", "Research Center", "Innovation Lab"

Examples that are NOT included:
- ❌ Pure manufacturing companies
- ❌ Sales offices
- ❌ Companies without research keywords

---

## 🔍 Detection Keywords

The scraper looks for these keywords in affiliations:

### Universities & Colleges
- university, college, academy
- technical university, polytechnic
- ETH, TU, TUM, MIT, EPFL, RWTH (abbreviations)
- hochschule, universidad, università

### Research Institutions
- institute, research center, research institute
- laboratory, lab, research facility

### Industrial R&D
- R&D, research and development
- technology center, innovation center
- engineering center, development center
- testing center, simulation center

### Technology Companies
- systems, technologies, solutions
- HIL, hardware-in-loop

---

## 🌍 Geographic Coverage

**43 European Countries** (excluding France):

Albania, Armenia, Austria, Belarus, Belgium, Bosnia and Herzegovina, Bulgaria, Croatia, Cyprus, Czech Republic, Czechia, Denmark, Estonia, Finland, Georgia, Germany, Greece, Hungary, Iceland, Ireland, Italy, Kosovo, Latvia, Lithuania, Luxembourg, Malta, Moldova, Montenegro, Netherlands, North Macedonia, Norway, Poland, Portugal, Romania, Serbia, Slovakia, Slovenia, Spain, Sweden, Switzerland, Turkey, Ukraine, United Kingdom

**Priority Countries** (highlighted in results):
- ⭐ Germany
- ⭐ United Kingdom  
- ⭐ Italy

---

## 📊 Examples from Your Screenshot

From the IEEE publication you showed:

```
Authors:
✅ Caio R. D. Osório - Typhoon HIL, Inc., Novi Sad, Serbia
✅ Milos Miletic - Typhoon HIL, Inc., Novi Sad, Serbia
✅ Jovan Zelic - Typhoon HIL, Inc., Novi Sad, Serbia
✅ Dusan Majstorovic - Typhoon HIL, Inc., Novi Sad, Serbia
✅ Ognjen Gagrica - Typhoon HIL, Inc., Novi Sad, Serbia
```

**All 5 authors WILL be included** because:
1. ✅ Affiliation contains "HIL" → recognized as R&D lab
2. ✅ Location is "Serbia" → in the 43-country list
3. ✅ Meets both criteria → eligible for extraction

---

## 🚀 How It Works

### Stage 1: Quick Check (Fast)
```
For each publication:
  1. Expand "Authors" section on IEEE page
  2. Read all affiliations (e.g., "Typhoon HIL, Inc., Novi Sad, Serbia")
  3. Check: Contains research keyword? (HIL ✓)
  4. Check: From European country? (Serbia ✓)
  5. Decision:
     ✅ Both = Process publication
     ❌ Either missing = Skip publication
```

### Stage 2: Detailed Extraction (Slow)
```
Only for publications with European research authors:
  • Extract full publication details
  • Visit each author's profile page
  • Get biography, topics, email, publications
  • Aggregate and save to JSON
```

---

## 📝 Configuration

Both `config.json` and `config_test.json` are updated with:

```json
{
  "european_countries_exclude_france": [
    "Albania", "Armenia", "Austria", ...
  ],
  "priority_countries": ["Germany", "United Kingdom", "Italy"],
  "research_institution_keywords": [
    "university", "institute", "lab",
    "eth", "tu", "tum", "mit",
    "r&d", "hil", "systems", ...
  ]
}
```

---

## ✅ Ready to Use!

The scraper is now configured to recognize:
- All major European technical universities
- Research institutes and labs
- Industrial R&D facilities
- Including abbreviated names (ETH, TU, etc.)
- Including technology companies with research operations (HIL, R&D, etc.)

Just run:
```bash
python3 ieee_author_scraper.py --config config_test.json
```

And it will correctly identify authors from institutions like Typhoon HIL! 🎉

